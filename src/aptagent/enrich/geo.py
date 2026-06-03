"""Geographic signals: distance to Link light rail, preferred/avoided
neighborhoods, and major parks.

Coordinates are hardcoded (small, stable reference sets) so these signals are
free, fast, and offline. Distances are in miles via the haversine formula.
Grocery proximity is handled separately in :mod:`aptagent.enrich.groceries`
(data pulled from OpenStreetMap, since store locations change).
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

# Sound Transit Link stations. 1 Line (Lynnwood <-> Angle Lake, north->south)
# and 2 Line (Eastside / Bellevue / Redmond). north/west -> south/east.
LINK_STATIONS: dict[str, tuple[float, float]] = {
    # --- 1 Line ---
    "Lynnwood City Center": (47.8154, -122.2961),
    "Mountlake Terrace": (47.7857, -122.3140),
    "Shoreline North/185th": (47.7556, -122.3013),
    "Shoreline South/148th": (47.7339, -122.3013),
    "Northgate": (47.7036, -122.3286),
    "Roosevelt": (47.6764, -122.3174),
    "U District": (47.6603, -122.3138),
    "University of Washington": (47.6498, -122.3036),
    "Capitol Hill": (47.6190, -122.3206),
    "Westlake": (47.6115, -122.3375),
    "Symphony": (47.6076, -122.3353),
    "Pioneer Square": (47.6022, -122.3319),
    "Intl District/Chinatown": (47.5980, -122.3277),
    "Stadium": (47.5915, -122.3274),
    "SODO": (47.5817, -122.3273),
    "Beacon Hill": (47.5792, -122.3115),
    "Mount Baker": (47.5765, -122.2975),
    "Columbia City": (47.5601, -122.2925),
    "Othello": (47.5378, -122.2814),
    "Rainier Beach": (47.5224, -122.2796),
    "Tukwila Intl Blvd": (47.4639, -122.2880),
    "SeaTac/Airport": (47.4452, -122.2966),
    "Angle Lake": (47.4225, -122.2978),
    # --- 2 Line (Eastside) ---
    "Judkins Park": (47.5905, -122.2965),
    "Mercer Island": (47.5876, -122.2316),
    "South Bellevue": (47.5860, -122.1916),
    "East Main": (47.6090, -122.1905),
    "Bellevue Downtown": (47.6150, -122.1920),
    "Wilburton": (47.6160, -122.1860),
    "Spring District": (47.6260, -122.1770),
    "BelRed": (47.6280, -122.1650),
    "Overlake Village": (47.6360, -122.1360),
    "Redmond Technology": (47.6430, -122.1370),
}

# "Heart of the city" anchor (Westlake / downtown retail core). Kept for
# reference; the scorer favors preferred neighborhoods over raw centrality.
DOWNTOWN_CORE = (47.6115, -122.3375)

# Neighborhood centroids referenced by name from preferences.yaml
# (preferred = bonus, avoid = penalty).
NEIGHBORHOODS: dict[str, tuple[float, float]] = {
    "Capitol Hill": (47.6190, -122.3120),
    "Downtown Seattle": (47.6080, -122.3350),
    "Northgate": (47.7060, -122.3260),
    "Green Lake": (47.6790, -122.3280),
    "Roosevelt": (47.6760, -122.3170),
    "Maple Leaf": (47.6920, -122.3170),
    "Wallingford": (47.6610, -122.3340),
    "Ballard": (47.6680, -122.3840),
    "Shoreline": (47.7560, -122.3410),
    "Mountlake Terrace": (47.7880, -122.3090),
    "Lynnwood": (47.8279, -122.3051),
    "Bellevue": (47.6150, -122.1920),
}

# A handful of major Seattle parks.
MAJOR_PARKS: dict[str, tuple[float, float]] = {
    "Discovery Park": (47.6580, -122.4055),
    "Green Lake": (47.6806, -122.3287),
    "Volunteer Park": (47.6300, -122.3155),
    "Gas Works Park": (47.6456, -122.3344),
    "Seward Park": (47.5510, -122.2580),
    "Washington Park Arboretum": (47.6398, -122.2960),
    "Cal Anderson Park": (47.6175, -122.3197),
    "Magnuson Park": (47.6803, -122.2580),
    "Lincoln Park": (47.5300, -122.3940),
    "Jefferson Park": (47.5680, -122.3100),
    "Bellevue Downtown Park": (47.6125, -122.2030),
}


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def _nearest(lat, lon, points: dict[str, tuple[float, float]]):
    if lat is None or lon is None or not points:
        return None, None
    best_name, best_dist = None, float("inf")
    for name, (plat, plon) in points.items():
        d = haversine_miles(lat, lon, plat, plon)
        if d < best_dist:
            best_name, best_dist = name, d
    return best_name, best_dist


def nearest_station(lat, lon) -> tuple[str | None, float | None]:
    return _nearest(lat, lon, LINK_STATIONS)


def nearest_park(lat, lon) -> tuple[str | None, float | None]:
    return _nearest(lat, lon, MAJOR_PARKS)


def distance_to_downtown(lat, lon) -> float | None:
    if lat is None or lon is None:
        return None
    return haversine_miles(lat, lon, *DOWNTOWN_CORE)


def nearest_named(lat, lon, names: list[str]) -> tuple[str | None, float | None]:
    """Nearest of a named subset of NEIGHBORHOODS to the point."""
    subset = {n: NEIGHBORHOODS[n] for n in names if n in NEIGHBORHOODS}
    return _nearest(lat, lon, subset)
