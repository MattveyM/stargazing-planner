"""Real drive times from a starting point to every site, using OpenRouteService (ORS).

One ORS "matrix" request gets the drive time from the starting point to all 38 sites at once.
Results are cached for 24 hours per starting point, so repeat searches don't use up the free daily limit.

If there's no ORS_API_KEY in backend/.env, or ORS can't be reached, we fall back to an estimate
(straight-line distance x 1.3 at 50 mph) and mark those times as estimated, so the app still works.
"""
import logging
import math
import os
import time

import httpx

ORS_MATRIX_URL = "https://api.openrouteservice.org/v2/matrix/driving-car"
MAX_ATTEMPTS = 2
CACHE_SECONDS = 24 * 60 * 60

# Fallback estimate (the same rule the browser used in Weeks 3-5)
ROAD_FACTOR = 1.3   # roads are about 1.3x longer than a straight line
AVERAGE_MPH = 50
EARTH_RADIUS_MILES = 3958.8
METERS_PER_MILE = 1609.344

log = logging.getLogger("drive_times")

# (rounded latitude, rounded longitude) -> (time saved, {site_id: drive info})
_cache: dict[tuple[float, float], tuple[float, dict]] = {}


def clear_cache():
    _cache.clear()


def straight_line_miles(lat1, lon1, lat2, lon2) -> float:
    """Distance "as the crow flies" between two points (haversine formula)."""
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def estimate_drive(lat, lon, site) -> dict:
    """Rough drive time when real routing isn't available."""
    road_miles = straight_line_miles(lat, lon, site["latitude"], site["longitude"]) * ROAD_FACTOR
    return {"minutes": round(road_miles / AVERAGE_MPH * 60), "miles": round(road_miles, 1), "estimated": True}


def fetch_ors_matrix(client: httpx.Client, api_key: str, lat: float, lon: float, sites: list[dict]) -> dict:
    """Ask ORS for drive time + distance from (lat, lon) to every site in one request.

    Returns {site_id: {"minutes", "miles", "estimated": False}}. A site ORS can't route to is left out.
    """
    body = {
        # ORS wants [longitude, latitude]. Index 0 is the starting point; 1..n are the sites.
        "locations": [[lon, lat]] + [[s["longitude"], s["latitude"]] for s in sites],
        "sources": [0],
        "destinations": list(range(1, len(sites) + 1)),
        "metrics": ["duration", "distance"],
        "units": "m",
    }
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.post(ORS_MATRIX_URL, json=body, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            break
        except httpx.HTTPError:
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(1)

    seconds_row = data["durations"][0]   # one row: from the start to each site, in seconds
    meters_row = data["distances"][0]    # in meters
    results = {}
    for site, seconds, meters in zip(sites, seconds_row, meters_row):
        if seconds is None or meters is None:   # no road route found
            continue
        results[site["id"]] = {
            "minutes": round(seconds / 60),
            "miles": round(meters / METERS_PER_MILE, 1),
            "estimated": False,
        }
    return results


def get_drive_times(lat: float, lon: float, sites: list[dict], client: httpx.Client | None = None) -> dict:
    """Drive info for every site: real ORS times when possible, estimates otherwise."""
    key = (round(lat, 3), round(lon, 3))   # about 100 m: nearby searches share the cache
    cached = _cache.get(key)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]

    real = {}
    api_key = os.getenv("ORS_API_KEY")
    if api_key:
        try:
            if client is None:
                with httpx.Client() as new_client:
                    real = fetch_ors_matrix(new_client, api_key, lat, lon, sites)
            else:
                real = fetch_ors_matrix(client, api_key, lat, lon, sites)
        except Exception as error:   # ORS down, bad key, daily limit reached...
            log.warning("OpenRouteService failed, using estimated drive times: %s", error)

    drive = {s["id"]: real.get(s["id"]) or estimate_drive(lat, lon, s) for s in sites}
    if real:   # only cache real answers, so we try ORS again next time if it failed
        _cache[key] = (time.time(), drive)
    return drive
