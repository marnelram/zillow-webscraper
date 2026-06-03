"""Fetch a listing's Zillow detail page via Apify (rich description + amenities).

Search cards are thin; the detail page is where the full description (and thus
any rent specials/concessions) and the resoFacts amenity data live. We fetch
this only for the handful of listings we deep-dive, so cost stays low.
"""

from __future__ import annotations

import httpx

from aptagent.settings import get_settings
from aptagent.util import clean_list

_APIFY_BASE = "https://api.apify.com/v2"

# resoFacts list-typed fields worth surfacing as amenities.
_RESO_LIST_FIELDS = (
    "appliances", "laundryFeatures", "parkingFeatures", "communityFeatures",
    "exteriorFeatures", "interiorFeatures", "associationAmenities", "poolFeatures",
    "flooring", "heating", "cooling", "spaFeatures", "patioAndPorchFeatures",
    "securityFeatures", "accessibilityFeatures",
)


def amenities_from_resofacts(reso: dict | None) -> list[str]:
    """Flatten the list-typed resoFacts fields into a deduped amenity list."""
    if not reso:
        return []
    out: list[str] = []
    for field in _RESO_LIST_FIELDS:
        out += clean_list(reso.get(field))
    seen, deduped = set(), []
    for a in out:
        if a.lower() not in seen:
            seen.add(a.lower())
            deduped.append(a)
    return deduped


def fetch_detail(url: str, timeout: float = 240.0) -> dict | None:
    """Run the detail actor for one listing URL; return the first result item."""
    settings = get_settings()
    if not settings.apify_token:
        raise RuntimeError("APIFY_TOKEN is not set; cannot run the detail actor.")
    api = f"{_APIFY_BASE}/acts/{settings.apify_detail_actor}/run-sync-get-dataset-items"
    run_input = {"startUrls": [{"url": url}]}
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(api, params={"token": settings.apify_token, "maxItems": 1}, json=run_input)
        resp.raise_for_status()
        items = resp.json()
    if isinstance(items, list) and items:
        return items[0]
    return None


def detail_to_fields(item: dict) -> dict:
    """Extract the fields we persist from a detail-actor item."""
    reso = item.get("resoFacts") or {}
    return {
        "description": item.get("description"),
        "amenities": amenities_from_resofacts(reso),
    }
