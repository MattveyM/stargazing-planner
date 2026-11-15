"""Tests for drive times and the rankings endpoints. Run from the backend folder with:  pytest

None of these call the real OpenRouteService: they either remove the API key (so estimates are used)
or give the code a fake ORS server (httpx.MockTransport) that answers with sample data.
"""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

import drive_times
from main import app
from rankings import rank_score, rank_sites

client = TestClient(app)
BOTHELL = {"lat": 47.76232, "lon": -122.2054}

SITES = [
    {"id": 1, "name": "Near", "latitude": 47.9, "longitude": -122.0},
    {"id": 2, "name": "Far", "latitude": 47.9, "longitude": -123.5},
    {"id": 3, "name": "No road", "latitude": 48.5, "longitude": -121.0},
]


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    """Start every test with an empty cache and no real API key (so nothing goes to the internet)."""
    drive_times.clear_cache()
    monkeypatch.delenv("ORS_API_KEY", raising=False)
    yield
    drive_times.clear_cache()


def fake_ors(handler_log):
    """A pretend ORS server: 30 min / 25 mi to site 1, 120 min / 95 mi to site 2, no route to site 3."""
    def handler(request: httpx.Request):
        handler_log.append(request)
        return httpx.Response(200, json={
            "durations": [[1800.0, 7200.0, None]],
            "distances": [[40233.6, 152888.7, None]],
        })
    return httpx.Client(transport=httpx.MockTransport(handler))


# ---------- Ranking rules ----------

def test_rank_score_takes_off_up_to_10_points_for_drive_time():
    assert rank_score(80, 0, 120) == 80
    assert rank_score(80, 60, 120) == 75       # half the max drive -> 5 points off
    assert rank_score(80, 120, 120) == 70      # at the max drive -> 10 points off
    assert rank_score(None, 30, 120) is None   # not scored yet


def test_rank_sites_drops_sites_past_the_drive_limit_and_sorts_best_first():
    rows = [
        {"id": 1, "name": "Close but cloudy", "score": 50},
        {"id": 2, "name": "Farther but clear", "score": 85},
        {"id": 3, "name": "Too far", "score": 99},
        {"id": 4, "name": "Not scored yet", "score": None},
    ]
    drive = {
        1: {"minutes": 20, "miles": 15, "estimated": False},
        2: {"minutes": 100, "miles": 80, "estimated": False},
        3: {"minutes": 200, "miles": 170, "estimated": False},
        4: {"minutes": 10, "miles": 5, "estimated": False},
    }
    ranked = rank_sites(rows, drive, max_drive_minutes=120)
    assert [s["name"] for s in ranked] == ["Farther but clear", "Close but cloudy", "Not scored yet"]
    assert [s["rank"] for s in ranked] == [1, 2, 3]


# ---------- Drive times ----------

def test_estimates_are_used_when_there_is_no_api_key():
    drive = drive_times.get_drive_times(BOTHELL["lat"], BOTHELL["lon"], SITES)
    assert all(info["estimated"] for info in drive.values())
    assert drive[1]["minutes"] < drive[2]["minutes"]   # the nearer site is a shorter drive


def test_ors_answer_is_turned_into_minutes_and_miles(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "test-key")
    calls = []
    drive = drive_times.get_drive_times(BOTHELL["lat"], BOTHELL["lon"], SITES, client=fake_ors(calls))
    assert drive[1] == {"minutes": 30, "miles": 25.0, "estimated": False}
    assert drive[2] == {"minutes": 120, "miles": 95.0, "estimated": False}
    assert drive[3]["estimated"] is True                          # no route -> falls back to an estimate
    assert calls[0].headers["Authorization"] == "test-key"
    assert json.loads(calls[0].content)["locations"][0] == [-122.2054, 47.76232]  # ORS wants [lon, lat]


def test_ors_failure_falls_back_to_estimates(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "test-key")
    monkeypatch.setattr(drive_times.time, "sleep", lambda seconds: None)  # don't wait between retries
    broken = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503)))
    drive = drive_times.get_drive_times(BOTHELL["lat"], BOTHELL["lon"], SITES, client=broken)
    assert all(info["estimated"] for info in drive.values())


def test_repeat_searches_use_the_cache(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "test-key")
    calls = []
    fake = fake_ors(calls)
    drive_times.get_drive_times(BOTHELL["lat"], BOTHELL["lon"], SITES, client=fake)
    drive_times.get_drive_times(BOTHELL["lat"] + 0.0001, BOTHELL["lon"], SITES, client=fake)  # ~10 m away
    assert len(calls) == 1


# ---------- Endpoints ----------

def test_rankings_endpoint_returns_sites_in_range_best_first():
    response = client.get("/api/rankings", params={**BOTHELL, "max_drive": 120})
    assert response.status_code == 200
    body = response.json()
    results = body["results"]
    assert body["drive_source"] == "estimate"
    assert all(site["drive_minutes"] <= 120 for site in results)
    assert [site["rank"] for site in results] == list(range(1, len(results) + 1))
    scored = [site["rank_score"] for site in results if site["rank_score"] is not None]
    assert scored == sorted(scored, reverse=True)


def test_rankings_endpoint_rejects_bad_input():
    assert client.get("/api/rankings", params={"lat": 200, "lon": -122}).status_code == 422
    assert client.get("/api/rankings", params={**BOTHELL, "max_drive": 5}).status_code == 422
    assert client.get("/api/rankings", params={**BOTHELL, "night": "2099-01-01"}).status_code == 422


def test_calendar_endpoint_gives_the_next_7_nights():
    response = client.get("/api/rankings/nights", params={**BOTHELL, "max_drive": 120})
    assert response.status_code == 200
    nights = response.json()
    assert len(nights) == 7
    assert [n["night"] for n in nights] == sorted(n["night"] for n in nights)
    for night in nights:
        assert night["best_score"] is None or 0 <= night["best_score"] <= 100
