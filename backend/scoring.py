"""The 0-100 stargazing score for one site on one night.

Points:  clouds 50  +  moonlight 20  +  length of darkness 15  +  light pollution 15  =  100
Drive time is NOT in this score: it depends on where each user starts, so it's applied at search time.
"""
from statistics import mean

POINTS = {"cloud": 50, "moon": 20, "darkness": 15, "light": 15}
FULL_DARKNESS_HOURS = 8   # 8+ hours of full darkness earns all darkness points


def effective_cloud(low, mid, high, total=None):
    """How much cloud actually blocks the stars (0-100).

    The thickest layer matters most; thin high clouds (cirrus) only count half.
    Falls back to total cloud cover if the layers are missing.
    """
    layers = [low, mid, None if high is None else high * 0.5]
    layers = [value for value in layers if value is not None]
    if layers:
        return min(100, max(layers))
    return total


def score_night(hours: list[dict], dark_hours: float, bortle: int):
    """Score one night.

    hours: one dict per dark hour with "cloud" (effective %, or None if no forecast),
           "moon_alt" (degrees) and "moon_lit" (0-1).
    Returns the score and its parts, or None if there's no forecast to judge the clouds.
    """
    clouds = [h["cloud"] for h in hours if h["cloud"] is not None]
    if not clouds:
        return None

    avg_cloud = mean(clouds)
    cloud_points = round(POINTS["cloud"] * (100 - avg_cloud) / 100)

    # Moonlight only matters while the moon is above the horizon.
    moon_glare = mean(h["moon_lit"] if h["moon_alt"] > 0 else 0 for h in hours)
    moon_points = round(POINTS["moon"] * (1 - moon_glare))

    darkness_points = round(POINTS["darkness"] * min(dark_hours, FULL_DARKNESS_HOURS) / FULL_DARKNESS_HOURS)
    light_points = round(POINTS["light"] * (9 - bortle) / 8)   # Bortle 1 = 15 points, Bortle 9 = 0

    return {
        "score": cloud_points + moon_points + darkness_points + light_points,
        "cloud_score": cloud_points,
        "moon_score": moon_points,
        "darkness_score": darkness_points,
        "light_score": light_points,
        "avg_cloud": round(avg_cloud),
    }
