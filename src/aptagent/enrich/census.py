"""Neighborhood-feel proxy from US Census ACS data.

Interprets the user's "higher density of working class / lived-in, not sterile
luxury" preference as: higher renter share + mid (not ultra-high) median income,
by ZIP Code Tabulation Area (ZCTA). Requires CENSUS_API_KEY; degrades gracefully
to None (factor omitted from scoring) when unset or on any error. Results cached
to data/cache/census.json to avoid repeat calls.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from aptagent.settings import get_settings

_ACS_URL = "https://api.census.gov/data/2022/acs/acs5"
_CACHE_PATH = Path("data/cache/census.json")
_cache: dict[str, dict] | None = None


def _load_cache() -> dict[str, dict]:
    global _cache
    if _cache is None:
        if _CACHE_PATH.exists():
            _cache = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        else:
            _cache = {}
    return _cache


def _save_cache() -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(_cache or {}, indent=0), encoding="utf-8")


def zcta_profile(zipcode: str) -> dict | None:
    """Return {'median_income', 'renter_share'} for a ZIP, or None if unavailable."""
    if not zipcode:
        return None
    cache = _load_cache()
    if zipcode in cache:
        return cache[zipcode]

    key = get_settings().census_api_key
    if not key:
        return None

    params = {
        # median household income, owner-occupied, renter-occupied
        "get": "B19013_001E,B25003_002E,B25003_003E",
        "for": f"zip code tabulation area:{zipcode}",
        "key": key,
    }
    try:
        resp = httpx.get(_ACS_URL, params=params, timeout=20.0)
        resp.raise_for_status()
        rows = resp.json()
    except (httpx.HTTPError, ValueError):
        return None
    if not rows or len(rows) < 2:
        return None

    header, values = rows[0], rows[1]
    rec = dict(zip(header, values))
    try:
        income = float(rec["B19013_001E"])
        owners = float(rec["B25003_002E"])
        renters = float(rec["B25003_003E"])
    except (KeyError, ValueError, TypeError):
        return None
    occupied = owners + renters
    profile = {
        "median_income": income if income > 0 else None,
        "renter_share": (renters / occupied) if occupied > 0 else None,
    }
    cache[zipcode] = profile
    _save_cache()
    return profile


def neighborhood_feel_score(zipcode: str | None) -> float | None:
    """0..1: higher = more renter-dense and mid-income. None if no data."""
    if not zipcode:
        return None
    profile = zcta_profile(zipcode)
    if not profile:
        return None
    renter_share = profile.get("renter_share")
    income = profile.get("median_income")
    if renter_share is None and income is None:
        return None
    # Renter density is the primary signal; temper by "not ultra-luxury" income.
    renter_component = renter_share if renter_share is not None else 0.5
    if income is None:
        income_component = 0.5
    else:
        # Peak around mid income; fall off toward very high income.
        # 40k -> 1.0, 150k+ -> ~0.0
        income_component = max(0.0, min(1.0, (150_000 - income) / (150_000 - 40_000)))
    return round(0.7 * renter_component + 0.3 * income_component, 4)
