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


def _jpeg_from_mixed(photo: dict) -> str | None:
    """Pull a reasonably-sized JPEG URL from a Zillow photo object."""
    if not isinstance(photo, dict):
        return None
    mixed = photo.get("mixedSources") or {}
    jpegs = mixed.get("jpeg") or []
    if jpegs:
        # pick a mid/large variant (last is usually largest)
        return jpegs[-1].get("url")
    return photo.get("url")


def photo_urls(item: dict, limit: int = 4) -> list[str]:
    """Extract up to `limit` photo URLs from a detail item across known shapes."""
    out: list[str] = []
    for key in ("responsivePhotos", "photos", "originalPhotos"):
        for p in item.get(key) or []:
            u = _jpeg_from_mixed(p)
            if u and u.startswith("http"):
                out.append(u)
            if len(out) >= limit:
                return out
    for key in ("hiResImageLink", "desktopWebHdpImageLink", "imgSrc"):
        u = item.get(key)
        if isinstance(u, str) and u.startswith("http") and u not in out:
            out.append(u)
        if len(out) >= limit:
            break
    return out[:limit]


def in_unit_laundry_from_reso(reso: dict | None) -> bool | None:
    """Best-effort in-unit washer/dryer detection from resoFacts."""
    if not reso:
        return None
    if reso.get("hasInUnitLaundry") is True:
        return True
    feats = " ".join(str(x) for x in (reso.get("laundryFeatures") or [])).lower()
    if not feats:
        return None
    if "in unit" in feats or "in-unit" in feats or "washer/dryer in" in feats or "washer and dryer in" in feats:
        return True
    if "shared" in feats or "common" in feats or "hookup" in feats or "none" in feats:
        return False
    return None


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
    """Extract the fields we use/persist from a detail-actor item."""
    reso = item.get("resoFacts") or {}
    return {
        "description": item.get("description"),
        "amenities": amenities_from_resofacts(reso),
        "photos": photo_urls(item),
        "in_unit_laundry": in_unit_laundry_from_reso(reso),
    }
