"""Apify-backed Zillow fetcher.

Runs a managed Zillow scraper actor (default ``maxcopell~zillow-scraper``) which
handles anti-bot/proxies for us, then normalizes its search-card output into
:class:`Listing` objects. The actor returns shallower data than the GraphQL
building payload (no walk/transit scores, amenities, or floor plans), but enough
for the geo/affordability/neighborhood/grocery/bedroom factors; the LLM
enrichment pass fills the rest from each listing's detailUrl.

Actor output fields used (per Apify docs; not 100% guaranteed stable):
  zpid, unformattedPrice, address, addressCity/State/Zipcode, beds, baths, area,
  latLong{latitude,longitude}, detailUrl.
"""

from __future__ import annotations

import httpx

from aptagent.fetchers.base import Fetcher
from aptagent.fetchers.zillow import ZillowFetcher
from aptagent.schemas import Listing
from aptagent.settings import get_settings
from aptagent.util import epoch_ms_to_date, parse_address, parse_price, safe_int

_APIFY_BASE = "https://api.apify.com/v2"


def _first(*values):
    for v in values:
        if v is not None:
            return v
    return None


def _avail_date(value):
    """availabilityDate may be epoch-ms or an ISO 'YYYY-MM-DD' string."""
    if value is None:
        return None
    d = epoch_ms_to_date(value)
    if d:
        return d
    try:
        from datetime import date as _date
        return _date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def normalize_apify_item(item: dict) -> Listing | None:
    """Map one Apify Zillow result into a Listing.

    Handles both individual-home cards (zpid, beds, baths, area, baseRent) and
    building cards (buildingName, lotId, minBaseRent/minBeds/minBaths/minArea).
    Returns None if the item has neither an id nor a detail URL.
    """
    zpid = item.get("zpid")
    zpid = str(zpid) if zpid is not None else None
    building_id = _first(item.get("lotId"), item.get("buildingId"), item.get("plid"))

    detail = item.get("detailUrl")
    if detail and detail.startswith("/"):
        detail = "https://www.zillow.com" + detail
    if zpid is None and building_id is None and detail is None:
        return None

    latlong = item.get("latLong") or {}
    rent = _first(
        safe_int(item.get("baseRent")),
        safe_int(item.get("minBaseRent")),
        parse_price(item.get("price")),
    )
    city, state, zipcode = parse_address(item.get("address"))

    if zpid:
        listing_id = f"zillow:{zpid}"
    elif building_id is not None:
        listing_id = f"zillow:bld:{building_id}"
    else:
        listing_id = f"zillow:apify:{abs(hash(detail)) % (10**12)}"

    return Listing(
        listing_id=listing_id,
        source="zillow",
        zpid=zpid,
        url=detail,
        address=item.get("address"),
        city=city,
        state=state or item.get("addressState"),
        zipcode=zipcode,
        latitude=latlong.get("latitude"),
        longitude=latlong.get("longitude"),
        rent=rent,
        beds=_first(item.get("beds"), item.get("minBeds")),
        baths=_first(item.get("baths"), item.get("minBaths")),
        sqft=safe_int(_first(item.get("area"), item.get("minArea"))),
        building_name=item.get("buildingName"),
        available_from=_avail_date(item.get("availabilityDate")),
        raw=item,
    )


def normalize_apify_items(items: list[dict]) -> list[Listing]:
    out = []
    for item in items:
        ls = normalize_apify_item(item)
        if ls is not None:
            out.append(ls)
    return out


class ApifyFetcher(Fetcher):
    source = "zillow"

    def __init__(
        self,
        token: str | None = None,
        actor: str | None = None,
        city: str = "seattle-wa",
        timeout: float = 300.0,
    ):
        settings = get_settings()
        self.token = token if token is not None else settings.apify_token
        self.actor = actor or settings.apify_zillow_actor
        # Reuse the Zillow fetcher purely to build the area/rent-band search URLs.
        self._zillow = ZillowFetcher(city=city)
        self.timeout = timeout

    def fetch(self, max_pages: int = 20, max_items: int | None = None) -> list[Listing]:
        if not self.token:
            raise RuntimeError("APIFY_TOKEN is not set; cannot run the Apify actor.")
        search_urls = self._zillow.build_search_urls()
        run_input = {
            "searchUrls": [{"url": u} for u in search_urls],
            "extractionMethod": "MAP_MARKERS",
        }
        url = f"{_APIFY_BASE}/acts/{self.actor}/run-sync-get-dataset-items"
        params = {"token": self.token}
        if max_items is not None:
            params["maxItems"] = max_items

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, params=params, json=run_input)
            resp.raise_for_status()
            items = resp.json()
        if not isinstance(items, list):
            return []
        return normalize_apify_items(items)
