"""Geographic signals: distance to Link light rail, downtown core, and major parks.

Coordinates are hardcoded (small, stable reference sets) so these signals are free,
fast, and offline. Distances are in miles via the haversine formula.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

# Sound Transit Link 1 Line stations (incl. 2024 Lynnwood extension and the
# south end through Tukwila). north -> south.
LINK_STATIONS: dict[str, tuple[float, float]] = {
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
}

# "Heart of the city" anchor (Westlake / downtown retail core).
DOWNTOWN_CORE = (47.6115, -122.3375)

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
}


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def _nearest(lat: float | None, lon: float | None, points: dict[str, tuple[float, float]]):
    if lat is None or lon is None:
        return None, None
    best_name, best_dist = None, float("inf")
    for name, (plat, plon) in points.items():
        d = haversine_miles(lat, lon, plat, plon)
        if d < best_dist:
            best_name, best_dist = name, d
    return best_name, best_dist


def nearest_station(lat: float | None, lon: float | None) -> tuple[str | None, float | None]:
    return _nearest(lat, lon, LINK_STATIONS)


def nearest_park(lat: float | None, lon: float | None) -> tuple[str | None, float | None]:
    return _nearest(lat, lon, MAJOR_PARKS)


def distance_to_downtown(lat: float | None, lon: float | None) -> float | None:
    if lat is None or lon is None:
        return None
    return haversine_miles(lat, lon, *DOWNTOWN_CORE)
