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
from aptagent.util import safe_int

_APIFY_BASE = "https://api.apify.com/v2"


def normalize_apify_item(item: dict) -> Listing | None:
    """Map one Apify Zillow result object into a Listing (None if unusable)."""
    zpid = item.get("zpid") or item.get("id")
    zpid = str(zpid) if zpid is not None else None
    rent = safe_int(item.get("unformattedPrice"))
    latlong = item.get("latLong") or {}
    detail = item.get("detailUrl")
    if detail and detail.startswith("/"):
        detail = "https://www.zillow.com" + detail

    if zpid is None and detail is None:
        return None

    return Listing(
        listing_id=f"zillow:{zpid}" if zpid else f"zillow:apify:{abs(hash(detail)) % (10**12)}",
        source="zillow",
        zpid=zpid,
        url=detail,
        address=item.get("address"),
        city=item.get("addressCity"),
        state=item.get("addressState"),
        zipcode=item.get("addressZipcode"),
        latitude=latlong.get("latitude"),
        longitude=latlong.get("longitude"),
        rent=rent,
        beds=item.get("beds"),
        baths=item.get("baths"),
        sqft=safe_int(item.get("area")),
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
