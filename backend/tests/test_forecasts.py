"""Tests for the weather download job and the forecast endpoint. Run from the backend folder with:  pytest

These tests don't call the real weather service: they use a small sample of Open-Meteo's response,
and any rows they save are rolled back (undone) so the real database isn't changed.
"""
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from db import get_connection
from jobs.download_forecasts import parse_forecast, save_forecasts, to_percent
from main import app

client = TestClient(app)

# A tiny example of what Open-Meteo sends back (3 hours, far in the future so it can't clash with real data)
SAMPLE_RESPONSE = {
    "hourly": {
        "time": ["2099-01-01T00:00", "2099-01-01T01:00", "2099-01-01T02:00"],
        "cloud_cover": [10, 55.4, None],
        "cloud_cover_low": [0, 40, None],
        "cloud_cover_mid": [5, 20, None],
        "cloud_cover_high": [10, 0, None],
        "relative_humidity_2m": [70, 82, 90],
    }
}


def test_to_percent_rounds_and_limits():
    assert to_percent(55.4) == 55
    assert to_percent(-3) == 0
    assert to_percent(120) == 100
    assert to_percent(None) is None


def test_parse_forecast_makes_one_row_per_hour():
    rows = parse_forecast(SAMPLE_RESPONSE, site_id=1)
    assert len(rows) == 3
    assert rows[0]["forecast_hour"] == datetime(2099, 1, 1, 0, tzinfo=timezone.utc)
    assert rows[1]["cloud_total"] == 55
    assert rows[2]["cloud_total"] is None      # missing values stay empty instead of crashing


def test_save_forecasts_replaces_old_forecast_for_same_hour():
    with get_connection() as conn:
        try:
            site_id = conn.execute("SELECT id FROM sites ORDER BY id LIMIT 1").fetchone()["id"]
            rows = parse_forecast(SAMPLE_RESPONSE, site_id)
            save_forecasts(conn, rows)

            rows[0]["cloud_total"] = 90            # a newer forecast for the same hour
            save_forecasts(conn, rows)

            saved = conn.execute(
                "SELECT forecast_hour, cloud_total FROM forecasts "
                "WHERE site_id = %s AND forecast_hour >= '2099-01-01 00:00+00' ORDER BY forecast_hour",
                (site_id,),
            ).fetchall()
            assert len(saved) == 3                 # still 3 rows, not 6
            assert saved[0]["cloud_total"] == 90   # the newer value replaced the old one
        finally:
            conn.rollback()                        # undo the test rows


def test_forecast_endpoint_returns_a_list():
    site_id = client.get("/api/sites").json()[0]["id"]
    response = client.get(f"/api/sites/{site_id}/forecast?hours=24")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 24


def test_forecast_for_missing_site_returns_404():
    assert client.get("/api/sites/999999/forecast").status_code == 404
