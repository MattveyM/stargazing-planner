"""Check the darkness times against a published almanac, and sanity-check the moon data.

Reference times (Seattle, PST) from sunrise-sunset.org, December 2026:
  Dec 1  astronomical twilight ends  6:10:44 pm   (full darkness starts)
  Dec 15 astronomical twilight starts 5:58:11 am  (full darkness ends)
Goal from the project plan: within 2 minutes.
"""
from datetime import date, datetime

from astronomy import LOCAL_TZ, dark_hours_list, moon_at, night_window

SEATTLE = (47.6062, -122.3321)
TWO_MINUTES = 120  # seconds


def seconds_apart(a: datetime, b: datetime) -> float:
    return abs((a - b).total_seconds())


def test_darkness_starts_within_2_minutes_of_almanac():
    dark_start, _ = night_window(*SEATTLE, date(2026, 12, 1))
    expected = datetime(2026, 12, 1, 18, 10, 44, tzinfo=LOCAL_TZ)
    assert seconds_apart(dark_start, expected) <= TWO_MINUTES


def test_darkness_ends_within_2_minutes_of_almanac():
    _, dark_end = night_window(*SEATTLE, date(2026, 12, 14))      # the night of Dec 14 ends the morning of Dec 15
    expected = datetime(2026, 12, 15, 5, 58, 11, tzinfo=LOCAL_TZ)
    assert seconds_apart(dark_end, expected) <= TWO_MINUTES


def test_dark_hours_are_whole_hours_inside_the_window():
    dark_start, dark_end = night_window(*SEATTLE, date(2026, 12, 1))
    hours = dark_hours_list(dark_start, dark_end)
    assert 10 <= len(hours) <= 13                                 # long December nights
    assert all(h.minute == 0 and dark_start <= h < dark_end for h in hours)


def test_moon_values_are_in_range():
    dark_start, dark_end = night_window(*SEATTLE, date(2026, 12, 1))
    for altitude, lit in moon_at(*SEATTLE, dark_hours_list(dark_start, dark_end)):
        assert -90 <= altitude <= 90
        assert 0 <= lit <= 1
