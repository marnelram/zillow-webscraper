"""Apify output normalization tests (pure, no network)."""

from __future__ import annotations

from aptagent.fetchers.apify import normalize_apify_item, normalize_apify_items

SAMPLE = {
    "zpid": "12345678",
    "unformattedPrice": 1895,
    "price": "$1,895/mo",
    "address": "123 NE 1st St, Seattle, WA 98115",
    "addressCity": "Seattle",
    "addressState": "WA",
    "addressZipcode": "98115",
    "beds": 1,
    "baths": 1,
    "area": 650,
    "latLong": {"latitude": 47.706, "longitude": -122.326},
    "detailUrl": "/homedetails/12345678_zpid/",
}


def test_maps_core_fields():
    ls = normalize_apify_item(SAMPLE)
    assert ls is not None
    assert ls.listing_id == "zillow:12345678"
    assert ls.zpid == "12345678"
    assert ls.rent == 1895
    assert ls.beds == 1 and ls.baths == 1 and ls.sqft == 650
    assert ls.city == "Seattle" and ls.zipcode == "98115"
    assert ls.latitude == 47.706 and ls.longitude == -122.326
    assert ls.url == "https://www.zillow.com/homedetails/12345678_zpid/"


def test_absolute_detail_url_kept():
    item = dict(SAMPLE, detailUrl="https://www.zillow.com/b/foo/")
    assert normalize_apify_item(item).url == "https://www.zillow.com/b/foo/"


def test_unusable_item_dropped():
    assert normalize_apify_item({"beds": 1}) is None  # no zpid and no detailUrl


def test_batch_filters_unusable():
    items = [SAMPLE, {"beds": 2}, dict(SAMPLE, zpid="999", detailUrl=None)]
    out = normalize_apify_items(items)
    assert len(out) == 2  # the {"beds": 2} item is dropped
