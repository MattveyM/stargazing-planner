"""Tests for GET /api/sites/{id}/nights."""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_nights_endpoint_returns_up_to_7_nights():
    site_id = client.get("/api/sites").json()[0]["id"]
    response = client.get(f"/api/sites/{site_id}/nights")
    assert response.status_code == 200
    nights = response.json()
    assert len(nights) <= 7
    for night in nights:
        assert 0 <= night["score"] <= 100


def test_score_parts_add_up_to_the_total():
    site_id = client.get("/api/sites").json()[0]["id"]
    for night in client.get(f"/api/sites/{site_id}/nights").json():
        parts = night["cloud_score"] + night["moon_score"] + night["darkness_score"] + night["light_score"]
        assert parts == night["score"]


def test_nights_for_missing_site_returns_404():
    assert client.get("/api/sites/999999/nights").status_code == 404
