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


class RankedSite(Site):
    rank: int                          # 1 = best pick
    score: int | None = None           # 0-100 nightly score (None if not scored yet)
    cloud_score: int | None = None
    moon_score: int | None = None
    darkness_score: int | None = None
    light_score: int | None = None
    dark_start: datetime | None = None
    dark_end: datetime | None = None
    moon_percent: int | None = None
    avg_cloud: int | None = None
    drive_minutes: int
    drive_miles: float
    drive_estimated: bool              # True = rough estimate, False = real route from OpenRouteService
    rank_score: float | None = None    # score minus the drive penalty (what the list is sorted by)


class Rankings(BaseModel):
    night: date
    max_drive_minutes: int
    drive_source: str                  # "openrouteservice", "estimate", or "mixed"
    results: list[RankedSite]


class CalendarNight(BaseModel):
    night: date
    sites_in_range: int
    best_site_id: int | None = None    # the #1 ranked site that night
    best_site_name: str | None = None
    best_score: int | None = None
