"""Tests for the sites API. Run from the backend folder with:  pytest"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_hello():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert "message" in response.json()


def test_list_sites_returns_30_or_more():
    response = client.get("/api/sites")
    assert response.status_code == 200
    assert len(response.json()) >= 30


def test_sites_have_valid_data():
    for site in client.get("/api/sites").json():
        assert site["name"]
        assert site["state"] in ("WA", "OR")
        assert 41 <= site["latitude"] <= 50          # Pacific Northwest
        assert -125 <= site["longitude"] <= -116
        assert 1 <= site["bortle"] <= 9
        assert site["road_access"] in ("Year-round", "Seasonal")


def test_get_one_site():
    first = client.get("/api/sites").json()[0]
    response = client.get(f"/api/sites/{first['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == first["name"]


def test_missing_site_returns_404():
    response = client.get("/api/sites/999999")
    assert response.status_code == 404
