"""Sun and moon calculations with Skyfield.

The planet-position file (de421.bsp) comes bundled in the skyfield-data package,
so nothing is downloaded while the app runs.
"""
import warnings
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from skyfield import almanac
from skyfield.api import Loader, wgs84

LOCAL_TZ = ZoneInfo("America/Los_Angeles")  # all sites are in WA and OR


@lru_cache(maxsize=1)
def _sky():
    """Load the timescale and planet positions once, then reuse them."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # skyfield-data warns about a file we don't use
        from skyfield_data import get_skyfield_data_path
        data_folder = get_skyfield_data_path()
    load = Loader(data_folder)
    return load.timescale(builtin=True), load("de421.bsp")


def night_window(latitude: float, longitude: float, night: date):
    """When it's fully dark (astronomical twilight: sun more than 18 degrees below the horizon).

    `night` is the local date of the evening. Returns (dark_start, dark_end) in UTC,
    or None if the sky never gets fully dark that night (possible in June up north).
    """
    ts, eph = _sky()
    place = wgs84.latlon(latitude, longitude)
    noon = datetime.combine(night, time(12), LOCAL_TZ)          # search from noon...
    next_noon = noon + timedelta(days=1)                        # ...to noon the next day
    sky_state = almanac.dark_twilight_day(eph, place)           # 0 = full dark ... 4 = daytime
    times, states = almanac.find_discrete(ts.from_datetime(noon), ts.from_datetime(next_noon), sky_state)

    dark_start = dark_end = None
    for moment, state in zip(times, states):
        if state == 0 and dark_start is None:
            dark_start = moment.utc_datetime()                  # just became fully dark
        elif state != 0 and dark_start is not None and dark_end is None:
            dark_end = moment.utc_datetime()                    # darkness just ended
    if dark_start is None:
        return None
    return dark_start, dark_end or next_noon.astimezone(timezone.utc)


def dark_hours_list(dark_start: datetime, dark_end: datetime) -> list[datetime]:
    """The whole hours (UTC) inside the dark window, e.g. 19:00, 20:00, ... These match forecast hours."""
    hour = dark_start.replace(minute=0, second=0, microsecond=0)
    if hour < dark_start:
        hour += timedelta(hours=1)
    hours = []
    while hour < dark_end:
        hours.append(hour)
        hour += timedelta(hours=1)
    return hours


def moon_at(latitude: float, longitude: float, moments: list[datetime]) -> list[tuple[float, float]]:
    """For each moment: (moon altitude in degrees, fraction of the moon that's lit from 0 to 1)."""
    if not moments:
        return []
    ts, eph = _sky()
    t = ts.from_datetimes(moments)
    observer = eph["earth"] + wgs84.latlon(latitude, longitude)
    altitude, _, _ = observer.at(t).observe(eph["moon"]).apparent().altaz()
    lit = almanac.fraction_illuminated(eph, "moon", t)
    return [(float(a), float(f)) for a, f in zip(altitude.degrees, lit)]
