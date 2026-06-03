"""Zillow rentals fetcher.

Two responsibilities:

1. ``normalize_building`` / ``normalize_buildings`` — turn a Zillow building-detail
   payload (the GraphQL ``BuildingQuery`` response shape, also what's saved in
   ``data/raw/*.json``) into flat per-unit :class:`Listing` objects. This is the
   pure, testable core and runs against fixtures with no network.

2. The live ``ZillowFetcher.fetch`` — search the mobile JSON endpoint (chunked by
   rent interval to stay under Zillow's ~800-result cap), collect building ids,
   pull each building via GraphQL, then normalize. Fragile and ToS-sensitive;
   isolated here so a paid API can replace it behind the same Fetcher ABC.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from aptagent.fetchers.base import Fetcher
from aptagent.schemas import Listing
from aptagent.settings import get_settings
from aptagent.util import clean_list, epoch_ms_to_date, safe_int, split_custom_amenities

_SCRAPERAPI_URL = "https://api.scraperapi.com/"

# Boolean buildingAttributes worth surfacing as amenities (flag -> label).
_BOOL_AMENITIES = {
    "hasElevator": "Elevator",
    "hasSwimmingPool": "Swimming pool",
    "hasHotTub": "Hot tub",
    "hasSauna": "Sauna",
    "hasFireplace": "Fireplace",
    "hasPatioBalcony": "Patio/balcony",
    "hasCeilingFan": "Ceiling fan",
    "hasBicycleStorage": "Bike storage",
    "hasStorage": "Storage",
    "hasPetPark": "Pet park",
    "hasBarbecue": "Barbecue",
    "hasGuestSuite": "Guest suite",
    "hasPackageService": "Package service",
    "hasValetTrash": "Valet trash",
    "hasTwentyFourHourMaintenance": "24h maintenance",
    "hasOnsiteManagement": "Onsite management",
    "hasDisabledAccess": "Disabled access",
}

_GRAPHQL_SHA = "ad04c9e688ad8981f898c335a89d09f9778804786b2211073ee12ff80e530a63"

_HEADERS = {
    "authority": "www.zillow.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
    ),
}


# --------------------------------------------------------------------------- #
# Normalization (pure, testable)
# --------------------------------------------------------------------------- #
def _building_amenities(building: dict) -> list[str]:
    ba = building.get("buildingAttributes") or {}
    amenities: list[str] = []
    amen_summary = building.get("amenitySummary") or {}
    amenities += clean_list(amen_summary.get("laundry"))
    amenities += clean_list(ba.get("appliances"))
    amenities += split_custom_amenities(ba.get("customAmenities"))
    amenities += clean_list(ba.get("outdoorCommonAreas"))
    amenities += clean_list(ba.get("communityRooms"))
    for flag, label in _BOOL_AMENITIES.items():
        if ba.get(flag) is True:
            amenities.append(label)
    # de-dupe, preserve order
    seen: set[str] = set()
    out = []
    for a in amenities:
        key = a.lower()
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out


def _building_costs(building: dict) -> dict:
    ba = building.get("buildingAttributes") or {}
    utilities = clean_list(ba.get("utilitiesIncluded"))
    return {
        "application_fee": safe_int(ba.get("applicationFee")),
        "deposit": safe_int(ba.get("depositFeeMin")) or safe_int(ba.get("depositFeeMax")),
        "utilities_included": True if utilities else None,
    }


def _address_str(building: dict) -> tuple[str | None, str | None, str | None, str | None]:
    addr = building.get("address") or {}
    street = addr.get("streetAddress")
    city = addr.get("city")
    state = addr.get("state")
    zipcode = addr.get("zipcode") or building.get("zipcode")
    parts = [p for p in (street, city, state, zipcode) if p]
    full = ", ".join(parts) if parts else None
    return full, city, state, zipcode


def normalize_building(building: dict) -> list[Listing]:
    """Flatten one building payload into per-unit Listings.

    A floor plan with explicit units yields one Listing per unit; a floor plan
    without units yields a single Listing priced at its minPrice.
    """
    full_addr, city, state, zipcode = _address_str(building)
    amenities = _building_amenities(building)
    costs = _building_costs(building)
    base = {
        "source": "zillow",
        "address": full_addr,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "latitude": building.get("latitude"),
        "longitude": building.get("longitude"),
        "building_name": building.get("buildingName"),
        "walk_score": (building.get("walkScore") or {}).get("walkscore"),
        "transit_score": (building.get("transitScore") or {}).get("transit_score"),
        "bike_score": (building.get("bikeScore") or {}).get("bikescore"),
        "amenities": amenities,
        "description": building.get("description"),
        **costs,
    }
    lot_id = building.get("lotId")
    listings: list[Listing] = []

    for fp in building.get("floorPlans") or []:
        fp_common = {
            "beds": fp.get("beds"),
            "baths": fp.get("baths"),
            "sqft": safe_int(fp.get("sqft")),
        }
        units = fp.get("units") or []
        if units:
            for unit in units:
                zpid = str(unit.get("zpid")) if unit.get("zpid") else None
                listings.append(
                    Listing(
                        listing_id=f"zillow:{zpid}" if zpid else f"zillow:{lot_id}:{fp.get('name')}:{unit.get('unitNumber')}",
                        zpid=zpid,
                        url=f"https://www.zillow.com/homedetails/{zpid}_zpid/" if zpid else None,
                        rent=safe_int(unit.get("price")) or safe_int(fp.get("minPrice")),
                        unit_number=unit.get("unitNumber"),
                        available_from=epoch_ms_to_date(unit.get("availableFrom")),
                        raw={"building_lotId": lot_id, "floorPlan": fp.get("name"), "unit": unit},
                        **base,
                        **fp_common,
                    )
                )
        else:
            listings.append(
                Listing(
                    listing_id=f"zillow:{lot_id}:{fp.get('name')}",
                    rent=safe_int(fp.get("minPrice")),
                    available_from=epoch_ms_to_date(fp.get("availableFrom")),
                    raw={"building_lotId": lot_id, "floorPlan": fp.get("name")},
                    **base,
                    **fp_common,
                )
            )
    return listings


def normalize_buildings(buildings: list[dict]) -> list[Listing]:
    out: list[Listing] = []
    for b in buildings:
        out.extend(normalize_building(b))
    return out


def load_fixture_buildings(path: str | Path) -> list[dict]:
    """Load saved building payloads (data/raw/*.json) for offline testing."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


# --------------------------------------------------------------------------- #
# Live fetch (network; fragile, ToS-sensitive)
# --------------------------------------------------------------------------- #
class ZillowFetcher(Fetcher):
    source = "zillow"

    # Map bounds covering Tukwila (south) -> Lynnwood (north), West Seattle ->
    # Bellevue/Redmond (east). Searching by mapBounds (no single regionId) so the
    # multi-city area is covered; the rent-band chunking keeps each query under cap.
    DEFAULT_MAP_BOUNDS = {
        "west": -122.46, "east": -122.05,
        "south": 47.40, "north": 47.86,
    }
    DEFAULT_REGION: list = []
    # Chunked rent bands keep each search under Zillow's ~800-result cap. Capped at
    # $2999 — anything above the user's $3k total-cost limit is rejected anyway, so
    # fetching it just wastes scraper credits.
    DEFAULT_RENT_INTERVALS = [
        (0, 1499), (1500, 1799), (1800, 2099), (2100, 2399), (2400, 2999)
    ]

    def __init__(
        self,
        city: str = "seattle-wa",
        rent_intervals: list[tuple[int, int]] | None = None,
        delay_seconds: float = 2.0,
        timeout: float = 60.0,
        scraperapi_key: str | None = None,
    ):
        self.city = city
        self.rent_intervals = rent_intervals or self.DEFAULT_RENT_INTERVALS
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        # When set, all Zillow requests are routed through ScraperAPI to bypass
        # anti-bot. Falls back to the (usually blocked) direct request if empty.
        self.scraperapi_key = scraperapi_key if scraperapi_key is not None else get_settings().scraperapi_key

    def build_search_urls(self) -> list[str]:
        """Zillow search URLs (one per rent band) with the searchQueryState fragment.

        Reused by the Apify fetcher so the managed actor runs the same searches.
        """
        urls = []
        base = f"https://www.zillow.com/{self.city}/rentals/"
        for min_rent, max_rent in self.rent_intervals:
            params = self._search_params(min_rent, max_rent, page=1)
            urls.append(str(httpx.URL(base).copy_merge_params({"searchQueryState": json.dumps(params)})))
        return urls

    def _search_params(self, min_rent: int, max_rent: int, page: int) -> dict:
        return {
            "mapBounds": self.DEFAULT_MAP_BOUNDS,
            "regionSelection": self.DEFAULT_REGION,
            "filterState": {
                "fr": {"value": True}, "ah": {"value": True},
                "fsba": {"value": False}, "fsbo": {"value": False},
                "nc": {"value": False}, "fore": {"value": False},
                "cmsn": {"value": False}, "auc": {"value": False},
                "mf": {"value": False}, "land": {"value": False}, "manu": {"value": False},
                "mp": {"max": max_rent, "min": min_rent},
            },
            "pagination": {"currentPage": page},
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def _get(self, client: httpx.Client, url: str, params: dict) -> httpx.Response:
        target = str(httpx.URL(url).copy_merge_params({"searchQueryState": json.dumps(params)}))
        if self.scraperapi_key:
            resp = client.get(
                _SCRAPERAPI_URL,
                params={"api_key": self.scraperapi_key, "url": target, "country_code": "us"},
            )
        else:
            resp = client.get(target)
        resp.raise_for_status()
        return resp

    def _collect_building_ids(self, max_pages: int) -> set[int]:
        """Scrape search pages and return building lotIds (deduped)."""
        ids: set[int] = set()
        with httpx.Client(headers=_HEADERS, timeout=self.timeout) as client:
            for min_rent, max_rent in self.rent_intervals:
                for page in range(1, max_pages + 1):
                    url = f"https://www.zillow.com/{self.city}/rentals/{page}_p/"
                    try:
                        resp = self._get(client, url, self._search_params(min_rent, max_rent, page))
                    except httpx.HTTPError:
                        break
                    results = _parse_search_results(resp.text)
                    if not results:
                        break
                    for r in results:
                        lot = r.get("lotId") or r.get("buildingId")
                        if lot:
                            ids.add(int(lot))
                    time.sleep(self.delay_seconds)
        return ids

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def _fetch_building(self, client: httpx.Client, lot_id: int) -> dict | None:
        payload = {
            "operationName": "BuildingQuery",
            "variables": {"cache": False, "latitude": None, "longitude": None,
                          "lotId": lot_id, "update": False},
            "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _GRAPHQL_SHA}},
        }
        graphql_url = "https://www.zillow.com/graphql/"
        if self.scraperapi_key:
            resp = client.post(
                _SCRAPERAPI_URL,
                params={"api_key": self.scraperapi_key, "url": graphql_url,
                        "keep_headers": "true", "country_code": "us"},
                json=payload,
            )
        else:
            resp = client.post(graphql_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("data") or {}).get("building")

    def fetch(self, max_pages: int = 20, max_buildings: int | None = None) -> list[Listing]:
        lot_ids = self._collect_building_ids(max_pages)
        if max_buildings is not None:
            lot_ids = set(list(lot_ids)[:max_buildings])
        buildings: list[dict] = []
        with httpx.Client(headers={**_HEADERS, "origin": "https://www.zillow.com"}, timeout=self.timeout) as client:
            for lot_id in lot_ids:
                try:
                    b = self._fetch_building(client, lot_id)
                except httpx.HTTPError:
                    continue
                if b:
                    buildings.append(b)
                time.sleep(self.delay_seconds)
        return normalize_buildings(buildings)


def _parse_search_results(html: str) -> list[dict]:
    """Extract the listResults array from a search page's embedded JSON."""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find(
        "script",
        {"data-zrr-shared-data-key": "mobileSearchPageStore", "type": "application/json"},
    )
    if tag is None:
        return []
    text = tag.text.replace("<!--", "").replace("-->", "")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    return (
        data.get("cat1", {})
        .get("searchResults", {})
        .get("listResults", [])
    )
