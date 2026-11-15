"""Stargazing Planner API (FastAPI back end)."""
from datetime import date, datetime, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from astronomy import LOCAL_TZ
from db import get_connection
from drive_times import get_drive_times
from models import CalendarNight, ForecastHour, NightScore, Rankings, Site
from rankings import rank_sites

app = FastAPI(
    title="Stargazing Planner API",
    description="Finds the best night and place to stargaze in the Pacific Northwest.",
    version="0.4.0",
)

# Allow the React app (running on port 5173) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SITE_COLUMNS = "id, name, region, state, latitude, longitude, elevation_ft, bortle, road_access, notes"


@app.get("/api/hello")
def hello():
    """Simple check that the server is running."""
    return {"message": "Hello from the Stargazing Planner back end"}


@app.get("/api/sites", response_model=list[Site])
def list_sites():
    """Return every dark-sky site in the database, sorted by name."""
    with get_connection() as conn:
        return conn.execute(f"SELECT {SITE_COLUMNS} FROM sites ORDER BY name").fetchall()


@app.get("/api/sites/{site_id}", response_model=Site)
def get_site(site_id: int):
    """Return one site by its id, or a 404 error if it doesn't exist."""
    with get_connection() as conn:
        site = conn.execute(f"SELECT {SITE_COLUMNS} FROM sites WHERE id = %s", (site_id,)).fetchone()
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@app.get("/api/sites/{site_id}/forecast", response_model=list[ForecastHour])
def get_site_forecast(site_id: int, hours: int = Query(48, ge=1, le=168, description="How many hours ahead to return")):
    """Return the saved hourly cloud forecast for one site, starting from the current hour."""
    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM sites WHERE id = %s", (site_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Site not found")
        return conn.execute(
            """
            SELECT forecast_hour, cloud_total, cloud_low, cloud_mid, cloud_high, humidity, downloaded_at
            FROM forecasts
            WHERE site_id = %s AND forecast_hour >= date_trunc('hour', NOW())
            ORDER BY forecast_hour
            LIMIT %s
            """,
            (site_id, hours),
        ).fetchall()


@app.get("/api/sites/{site_id}/nights", response_model=list[NightScore])
def get_site_nights(site_id: int):
    """Return the 0-100 score and its breakdown for each of the next 7 nights (newest prediction for each night)."""
    today = datetime.now(LOCAL_TZ).date()
    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM sites WHERE id = %s", (site_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Site not found")
        return conn.execute(
            """
            SELECT DISTINCT ON (night)
                   night, score, cloud_score, moon_score, darkness_score, light_score,
                   dark_start, dark_end, dark_hours, moon_percent, avg_cloud, predicted_on
            FROM predictions
            WHERE site_id = %s AND night >= %s
            ORDER BY night, predicted_on DESC
            LIMIT 7
            """,
            (site_id, today),
        ).fetchall()


# ---------- Rankings (Week 6): the search now runs on the server ----------

def _check_night(night: date | None) -> date:
    """Default to tonight; only allow the 7 nights we have forecasts for."""
    today = datetime.now(LOCAL_TZ).date()
    night = night or today
    if not today <= night <= today + timedelta(days=6):
        raise HTTPException(status_code=422, detail="night must be within the next 7 nights")
    return night


def _drive_source(results: list[dict]) -> str:
    estimated = {site["drive_estimated"] for site in results}
    if estimated == {False}:
        return "openrouteservice"
    return "estimate" if estimated == {True} else "mixed"


@app.get("/api/rankings", response_model=Rankings)
def get_rankings(
    lat: float = Query(..., ge=-90, le=90, description="Starting latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Starting longitude"),
    max_drive: int = Query(120, ge=15, le=480, description="Longest drive the user will make, in minutes"),
    night: date | None = Query(None, description="Which night (YYYY-MM-DD). Default: tonight"),
):
    """Sites within the drive limit, ranked best first by score and drive time for one night."""
    night = _check_night(night)
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.id, s.name, s.region, s.state, s.latitude, s.longitude, s.elevation_ft, s.bortle, s.road_access, s.notes,
                   p.score, p.cloud_score, p.moon_score, p.darkness_score, p.light_score,
                   p.dark_start, p.dark_end, p.moon_percent, p.avg_cloud
            FROM sites s
            LEFT JOIN LATERAL (            -- newest prediction for this site and night
                SELECT * FROM predictions
                WHERE site_id = s.id AND night = %s
                ORDER BY predicted_on DESC LIMIT 1
            ) p ON true
            """,
            (night,),
        ).fetchall()
    drive = get_drive_times(lat, lon, rows)
    results = rank_sites(rows, drive, max_drive)
    return {"night": night, "max_drive_minutes": max_drive, "drive_source": _drive_source(results), "results": results}


@app.get("/api/rankings/nights", response_model=list[CalendarNight])
def get_ranking_calendar(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    max_drive: int = Query(120, ge=15, le=480),
):
    """For each of the next 7 nights: the #1 site within the drive limit and its score (for the calendar)."""
    today = datetime.now(LOCAL_TZ).date()
    nights = [today + timedelta(days=i) for i in range(7)]
    with get_connection() as conn:
        sites = conn.execute(f"SELECT {SITE_COLUMNS} FROM sites").fetchall()
        predictions = conn.execute(
            """
            SELECT DISTINCT ON (site_id, night) site_id, night, score
            FROM predictions
            WHERE night BETWEEN %s AND %s
            ORDER BY site_id, night, predicted_on DESC
            """,
            (nights[0], nights[-1]),
        ).fetchall()
    drive = get_drive_times(lat, lon, sites)
    scores = {(p["site_id"], p["night"]): p["score"] for p in predictions}

    calendar = []
    for night in nights:
        rows = [{**site, "score": scores.get((site["id"], night))} for site in sites]
        ranked = rank_sites(rows, drive, max_drive)
        best = ranked[0] if ranked and ranked[0]["score"] is not None else None
        calendar.append({
            "night": night,
            "sites_in_range": len(ranked),
            "best_site_id": best["id"] if best else None,
            "best_site_name": best["name"] if best else None,
            "best_score": best["score"] if best else None,
        })
    return calendar
