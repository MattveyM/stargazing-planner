"""Stargazing Planner API (FastAPI back end)."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import get_connection
from models import Site

app = FastAPI(
    title="Stargazing Planner API",
    description="Finds the best night and place to stargaze in the Pacific Northwest.",
    version="0.1.0",
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
