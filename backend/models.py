"""Data shapes the API sends back. FastAPI uses these to check the data and build the /docs page."""
from pydantic import BaseModel


class Site(BaseModel):
    id: int
    name: str
    region: str
    state: str
    latitude: float
    longitude: float
    elevation_ft: int | None = None
    bortle: int
    road_access: str
    notes: str | None = None
