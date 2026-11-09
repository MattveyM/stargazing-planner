"""Data shapes the API sends back. FastAPI uses these to check the data and build the /docs page."""
from datetime import date, datetime

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


class NightScore(BaseModel):
    night: date                       # local date of the evening
    score: int                        # 0-100 total
    cloud_score: int | None = None    # out of 50
    moon_score: int | None = None     # out of 20
    darkness_score: int | None = None # out of 15
    light_score: int | None = None    # out of 15
    dark_start: datetime | None = None
    dark_end: datetime | None = None
    dark_hours: float | None = None
    moon_percent: int | None = None   # how much of the moon is lit (average over the dark hours)
    avg_cloud: int | None = None      # average cloud that blocks the stars (%)
    predicted_on: date
