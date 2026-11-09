"""Score every site for the next 7 nights and save the results in the predictions table.

Run once (from the backend folder):  python -m jobs.score_nights
The scheduler runs this right after each forecast download.
"""
import logging
from datetime import date, datetime, timedelta
from statistics import mean

from astronomy import LOCAL_TZ, dark_hours_list, moon_at, night_window
from db import get_connection
from scoring import effective_cloud, score_night

NIGHTS_AHEAD = 7
log = logging.getLogger("score_nights")


def score_site_night(conn, site: dict, night: date):
    """Work out one site's score for one night, or None if it can't be scored."""
    window = night_window(site["latitude"], site["longitude"], night)
    if window is None:
        return None                                   # never fully dark that night
    dark_start, dark_end = window
    hours = dark_hours_list(dark_start, dark_end)
    if not hours:
        return None

    rows = conn.execute(
        """
        SELECT forecast_hour, cloud_low, cloud_mid, cloud_high, cloud_total
        FROM forecasts
        WHERE site_id = %s AND forecast_hour >= %s AND forecast_hour <= %s
        """,
        (site["id"], hours[0], hours[-1]),
    ).fetchall()
    forecast_by_hour = {row["forecast_hour"]: row for row in rows}

    hourly = []
    for hour, (moon_alt, moon_lit) in zip(hours, moon_at(site["latitude"], site["longitude"], hours)):
        f = forecast_by_hour.get(hour)
        cloud = effective_cloud(f["cloud_low"], f["cloud_mid"], f["cloud_high"], f["cloud_total"]) if f else None
        hourly.append({"cloud": cloud, "moon_alt": moon_alt, "moon_lit": moon_lit})

    dark_hours = (dark_end - dark_start).total_seconds() / 3600
    result = score_night(hourly, dark_hours, site["bortle"])
    if result is None:
        return None                                   # no forecast for those hours yet
    result.update({
        "dark_start": dark_start,
        "dark_end": dark_end,
        "dark_hours": round(dark_hours, 1),
        "moon_percent": round(mean(h["moon_lit"] for h in hourly) * 100),
    })
    return result


def save_prediction(conn, site_id: int, night: date, result: dict) -> None:
    """Save today's prediction for that night. Re-running today replaces it instead of duplicating it."""
    conn.execute(
        """
        INSERT INTO predictions (site_id, night, score, cloud_score, moon_score, darkness_score, light_score,
                                 dark_start, dark_end, dark_hours, moon_percent, avg_cloud)
        VALUES (%(site_id)s, %(night)s, %(score)s, %(cloud_score)s, %(moon_score)s, %(darkness_score)s,
                %(light_score)s, %(dark_start)s, %(dark_end)s, %(dark_hours)s, %(moon_percent)s, %(avg_cloud)s)
        ON CONFLICT (site_id, night, predicted_on) DO UPDATE SET
            score = EXCLUDED.score, cloud_score = EXCLUDED.cloud_score, moon_score = EXCLUDED.moon_score,
            darkness_score = EXCLUDED.darkness_score, light_score = EXCLUDED.light_score,
            dark_start = EXCLUDED.dark_start, dark_end = EXCLUDED.dark_end, dark_hours = EXCLUDED.dark_hours,
            moon_percent = EXCLUDED.moon_percent, avg_cloud = EXCLUDED.avg_cloud
        """,
        {"site_id": site_id, "night": night, **result},
    )


def run() -> dict:
    """Score every site for the next 7 nights. One site failing doesn't stop the others."""
    today = datetime.now(LOCAL_TZ).date()
    saved, failed = 0, []
    with get_connection() as conn:
        sites = conn.execute("SELECT id, name, latitude, longitude, bortle FROM sites ORDER BY id").fetchall()
        for site in sites:
            try:
                for offset in range(NIGHTS_AHEAD):
                    night = today + timedelta(days=offset)
                    result = score_site_night(conn, site, night)
                    if result is not None:
                        save_prediction(conn, site["id"], night, result)
                        saved += 1
                conn.commit()
            except Exception as error:
                conn.rollback()
                failed.append(site["name"])
                log.warning("Could not score %s: %s", site["name"], error)
    log.info("Scoring done: %d site-nights scored, %d sites failed", saved, len(failed))
    return {"sites": len(sites), "scored": saved, "failed": failed}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()
