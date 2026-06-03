"""Apify output normalization tests (pure, no network) — real actor schema."""

from __future__ import annotations

from datetime import date

from aptagent.fetchers.apify import normalize_apify_item, normalize_apify_items
from aptagent.util import parse_address, parse_price

HOME = {
    "zpid": "2056093798",
    "price": "$1,454/mo",
    "baseRent": 1454,
    "beds": 0,
    "baths": 1,
    "area": 464,
    "availabilityDate": "2026-11-15",
    "address": "104 12th Ave #351, Seattle, WA 98122",
    "addressState": "WA",
    "latLong": {"latitude": 47.60192, "longitude": -122.316414},
    "detailUrl": "https://www.zillow.com/homedetails/104-12th-Ave-351-Seattle-WA-98122/2056093798_zpid/",
}

BUILDING = {
    "buildingName": "Tressa Apartments",
    "lotId": "95wkmV",
    "price": "$1,462+/mo",
    "minBaseRent": 1462,
    "minBeds": 0,
    "minBaths": 1,
    "minArea": 480,
    "address": "14200 Linden Ave N, Seattle, WA",
    "latLong": {"latitude": 47.731728, "longitude": -122.34696},
    "detailUrl": "https://www.zillow.com/apartments/seattle-wa/tressa-apartments/95wkmV/",
}


def test_home_card_maps():
    ls = normalize_apify_item(HOME)
    assert ls.listing_id == "zillow:2056093798"
    assert ls.rent == 1454
    assert ls.beds == 0 and ls.baths == 1 and ls.sqft == 464
    assert ls.city == "Seattle" and ls.state == "WA" and ls.zipcode == "98122"
    assert ls.latitude == 47.60192
    assert ls.available_from == date(2026, 11, 15)


def test_building_card_maps():
    ls = normalize_apify_item(BUILDING)
    assert ls.listing_id == "zillow:bld:95wkmV"
    assert ls.zpid is None
    assert ls.rent == 1462          # from minBaseRent
    assert ls.beds == 0 and ls.baths == 1 and ls.sqft == 480
    assert ls.building_name == "Tressa Apartments"
    assert ls.city == "Seattle"


def test_rent_falls_back_to_price_string():
    item = dict(HOME)
    item.pop("baseRent")
    assert normalize_apify_item(item).rent == 1454  # parsed from "$1,454/mo"


def test_unusable_item_dropped():
    assert normalize_apify_item({"beds": 1}) is None


def test_batch_filters_unusable():
    out = normalize_apify_items([HOME, {"beds": 2}, BUILDING])
    assert len(out) == 2


def test_parse_helpers():
    assert parse_price("$1,462+/mo") == 1462
    assert parse_address("104 12th Ave #351, Seattle, WA 98122") == ("Seattle", "WA", "98122")
    assert parse_address("14200 Linden Ave N, Seattle, WA") == ("Seattle", "WA", None)
