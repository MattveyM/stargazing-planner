"""Data shapes the API sends back. FastAPI uses these to check the data and build the /docs page."""
from datetime import datetime

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


class ForecastHour(BaseModel):
    forecast_hour: datetime          # the hour this forecast is for (UTC)
    cloud_total: int | None = None   # % of sky covered by any cloud
    cloud_low: int | None = None     # low clouds (worst for stargazing)
    cloud_mid: int | None = None
    cloud_high: int | None = None    # thin high clouds
    humidity: int | None = None
    downloaded_at: datetime
