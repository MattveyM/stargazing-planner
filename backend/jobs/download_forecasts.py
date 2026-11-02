"""Download hourly cloud forecasts from Open-Meteo for every site and save them in the database.

Run once (from the backend folder):     python -m jobs.download_forecasts
Run every 6 hours (leave it running):   python -m jobs.run_scheduler
"""
import logging
import time
from datetime import datetime, timezone

import httpx

from db import get_connection

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_VARIABLES = [
    "cloud_cover",          # total cloud cover (%)
    "cloud_cover_low",      # low clouds (%)
    "cloud_cover_mid",      # mid-level clouds (%)
    "cloud_cover_high",     # high clouds (%)
    "relative_humidity_2m", # humidity (%)
]
FORECAST_DAYS = 7
MAX_ATTEMPTS = 3

log = logging.getLogger("download_forecasts")


def fetch_forecast(client: httpx.Client, latitude: float, longitude: float) -> dict:
    """Ask Open-Meteo for one site's 7-day hourly forecast. Retries up to 3 times if the request fails."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_VARIABLES),
        "forecast_days": FORECAST_DAYS,
        "timezone": "GMT",  # all times come back in UTC
    }
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.get(FORECAST_URL, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(2 * attempt)  # wait 2s, then 4s, before trying again


def to_percent(value):
    """Turn an API value into a whole-number percent from 0 to 100 (or None if missing)."""
    if value is None:
        return None
    return max(0, min(100, round(value)))


def parse_forecast(data: dict, site_id: int) -> list[dict]:
    """Turn Open-Meteo's JSON (lists of values per variable) into one row per hour."""
    hourly = data["hourly"]
    rows = []
    for i, time_text in enumerate(hourly["time"]):
        rows.append({
            "site_id": site_id,
            "forecast_hour": datetime.fromisoformat(time_text).replace(tzinfo=timezone.utc),
            "cloud_total": to_percent(hourly["cloud_cover"][i]),
            "cloud_low": to_percent(hourly["cloud_cover_low"][i]),
            "cloud_mid": to_percent(hourly["cloud_cover_mid"][i]),
            "cloud_high": to_percent(hourly["cloud_cover_high"][i]),
            "humidity": to_percent(hourly["relative_humidity_2m"][i]),
        })
    return rows


def save_forecasts(conn, rows: list[dict]) -> int:
    """Insert forecast rows. If an hour is already saved for that site, replace it with the newer forecast."""
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO forecasts (site_id, forecast_hour, cloud_total, cloud_low, cloud_mid, cloud_high, humidity)
            VALUES (%(site_id)s, %(forecast_hour)s, %(cloud_total)s, %(cloud_low)s, %(cloud_mid)s, %(cloud_high)s, %(humidity)s)
            ON CONFLICT (site_id, forecast_hour) DO UPDATE SET
                cloud_total   = EXCLUDED.cloud_total,
                cloud_low     = EXCLUDED.cloud_low,
                cloud_mid     = EXCLUDED.cloud_mid,
                cloud_high    = EXCLUDED.cloud_high,
                humidity      = EXCLUDED.humidity,
                downloaded_at = NOW()
            """,
            rows,
        )
    return len(rows)


def run() -> dict:
    """Download and save forecasts for every site. One site failing doesn't stop the others."""
    saved_rows = 0
    failed_sites = []
    with get_connection() as conn, httpx.Client() as client:
        sites = conn.execute("SELECT id, name, latitude, longitude FROM sites ORDER BY id").fetchall()
        for site in sites:
            try:
                data = fetch_forecast(client, site["latitude"], site["longitude"])
                saved_rows += save_forecasts(conn, parse_forecast(data, site["id"]))
                conn.commit()  # save each site's forecast as soon as it's ready
            except Exception as error:  # log it and move on to the next site
                conn.rollback()
                failed_sites.append(site["name"])
                log.warning("Could not update %s: %s", site["name"], error)
    summary = {"sites": len(sites), "failed": failed_sites, "rows_saved": saved_rows}
    log.info("Forecast download done: %d sites, %d rows saved, %d failed",
             summary["sites"], saved_rows, len(failed_sites))
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()
