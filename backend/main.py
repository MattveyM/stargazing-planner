"""Stargazing Planner API (FastAPI back end)."""
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from astronomy import LOCAL_TZ
from db import get_connection
from models import ForecastHour, NightScore, Site

app = FastAPI(
    title="Stargazing Planner API",
    description="Finds the best night and place to stargaze in the Pacific Northwest.",
    version="0.3.0",
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
