"""Tests for the 0-100 score. Each test sets up a night where the right answer is obvious."""
from scoring import effective_cloud, score_night

CLEAR_DARK_HOUR = {"cloud": 0, "moon_alt": -30, "moon_lit": 0.0}   # no clouds, moon below the horizon


def test_perfect_night_scores_100():
    result = score_night([CLEAR_DARK_HOUR] * 10, dark_hours=10, bortle=1)
    assert result["score"] == 100


def test_fully_cloudy_night_gets_no_cloud_points():
    cloudy = [{**CLEAR_DARK_HOUR, "cloud": 100}] * 10
    result = score_night(cloudy, dark_hours=10, bortle=1)
    assert result["cloud_score"] == 0
    assert result["score"] == 50


def test_full_moon_up_all_night_gets_no_moon_points():
    full_moon = [{**CLEAR_DARK_HOUR, "moon_alt": 40, "moon_lit": 1.0}] * 10
    assert score_night(full_moon, dark_hours=10, bortle=1)["moon_score"] == 0


def test_full_moon_below_horizon_does_not_count():
    moon_down = [{**CLEAR_DARK_HOUR, "moon_alt": -10, "moon_lit": 1.0}] * 10
    assert score_night(moon_down, dark_hours=10, bortle=1)["moon_score"] == 20


def test_city_sky_gets_no_light_pollution_points():
    assert score_night([CLEAR_DARK_HOUR] * 10, dark_hours=10, bortle=9)["light_score"] == 0


def test_short_night_gets_fewer_darkness_points():
    assert score_night([CLEAR_DARK_HOUR] * 4, dark_hours=4, bortle=1)["darkness_score"] == 8   # 15 * 4/8, rounded


def test_thin_high_clouds_count_half():
    assert effective_cloud(low=0, mid=0, high=80) == 40
    assert effective_cloud(low=70, mid=20, high=80) == 70   # the thickest layer wins


def test_no_forecast_means_no_score():
    no_data = [{**CLEAR_DARK_HOUR, "cloud": None}] * 10
    assert score_night(no_data, dark_hours=10, bortle=1) is None
