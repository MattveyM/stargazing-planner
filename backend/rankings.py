"""Ranking: combine each site's nightly score (0-100) with how far the user has to drive.

The saved score doesn't include drive time, because drive time depends on where each user starts.
At search time we subtract a small drive penalty: up to 10 points for a site right at the max drive time.
So a site 2 hours away has to be about 10 points better than one next door to rank above it.
"""
DRIVE_PENALTY_MAX = 10


def rank_score(score: int | None, drive_minutes: int, max_drive_minutes: int) -> float | None:
    """Score minus the drive penalty (higher is better). None if the site has no score yet."""
    if score is None:
        return None
    penalty = DRIVE_PENALTY_MAX * min(drive_minutes, max_drive_minutes) / max_drive_minutes
    return round(score - penalty, 1)


def rank_sites(rows: list[dict], drive: dict, max_drive_minutes: int) -> list[dict]:
    """Keep sites within the drive limit, add drive info and rank, best first.

    rows:  sites from the database, each with a "score" (or None) for the chosen night
    drive: {site_id: {"minutes", "miles", "estimated"}} from drive_times.get_drive_times
    """
    in_range = []
    for row in rows:
        info = drive.get(row["id"])
        if info is None or info["minutes"] > max_drive_minutes:
            continue
        in_range.append({
            **row,
            "drive_minutes": info["minutes"],
            "drive_miles": info["miles"],
            "drive_estimated": info["estimated"],
            "rank_score": rank_score(row.get("score"), info["minutes"], max_drive_minutes),
        })

    # Best rank score first; sites without a score go last; ties go to the shorter drive.
    in_range.sort(key=lambda s: (s["rank_score"] is None, -(s["rank_score"] or 0), s["drive_minutes"]))
    for position, site in enumerate(in_range, start=1):
        site["rank"] = position
    return in_range
