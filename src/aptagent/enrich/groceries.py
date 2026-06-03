"""Grocery-store proximity via OpenStreetMap (Overpass API).

Store locations change, so unlike parks/Link these aren't hardcoded. We fetch all
supermarkets in the metro bounding box once, cache them to
``data/cache/groceries.json``, then compute nearest-distance per listing offline.
Degrades gracefully (returns None) if the fetch fails or yields nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from aptagent.enrich.geo import haversine_miles

# Several mirrors; tried in order until one returns JSON. A descriptive
# User-Agent is required — Overpass rejects/limits anonymous requests.
_OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)
_HEADERS = {"User-Agent": "aptagent/0.1 (personal apartment search; contact: local use)"}
_CACHE_PATH = Path("data/cache/groceries.json")

# Bounding box covering Tukwila (south) -> Lynnwood (north), west Seattle -> Bellevue/Redmond (east).
# (south, west, north, east)
_BBOX = (47.40, -122.46, 47.86, -122.05)

_stores: list[tuple[str, float, float]] | None = None


def _overpass_query() -> str:
    s, w, n, e = _BBOX
    return (
        "[out:json][timeout:60];"
        f'(node["shop"="supermarket"]({s},{w},{n},{e});'
        f' way["shop"="supermarket"]({s},{w},{n},{e}););'
        "out center;"
    )


def _fetch_stores() -> list[tuple[str, float, float]]:
    query = _overpass_query()
    elements: list = []
    for endpoint in _OVERPASS_ENDPOINTS:
        try:
            resp = httpx.post(endpoint, data={"data": query}, headers=_HEADERS, timeout=90.0)
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            if elements:
                break
        except (httpx.HTTPError, ValueError):
            continue
    stores: list[tuple[str, float, float]] = []
    for el in elements:
        name = (el.get("tags") or {}).get("name", "supermarket")
        if el.get("type") == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:  # way -> use computed center
            center = el.get("center") or {}
            lat, lon = center.get("lat"), center.get("lon")
        if lat is not None and lon is not None:
            stores.append((name, float(lat), float(lon)))
    return stores


def _load_stores(refresh: bool = False) -> list[tuple[str, float, float]]:
    global _stores
    if _stores is not None and not refresh:
        return _stores
    if _CACHE_PATH.exists() and not refresh:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        _stores = [tuple(x) for x in data]
        return _stores
    _stores = _fetch_stores()
    if _stores:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(_stores), encoding="utf-8")
    return _stores


def refresh_grocery_cache() -> int:
    """Force-refresh the grocery cache from Overpass; return store count."""
    return len(_load_stores(refresh=True))


def nearest_grocery(lat, lon) -> tuple[str | None, float | None]:
    """Nearest supermarket name + distance (miles), or (None, None)."""
    if lat is None or lon is None:
        return None, None
    stores = _load_stores()
    if not stores:
        return None, None
    best_name, best_dist = None, float("inf")
    for name, slat, slon in stores:
        d = haversine_miles(lat, lon, slat, slon)
        if d < best_dist:
            best_name, best_dist = name, d
    return best_name, best_dist
