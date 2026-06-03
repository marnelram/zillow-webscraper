"""Building-grouping and detail-extraction tests (pure, no network)."""

from __future__ import annotations

from aptagent.enrich.detail import (
    amenities_from_resofacts,
    in_unit_laundry_from_reso,
    photo_urls,
)
from aptagent.enrich.funnel import _group, _representative, building_key
from aptagent.schemas import Listing


def _u(lid, **kw):
    return Listing(listing_id=lid, **kw)


def test_building_key_prefers_lot_id():
    ls = _u("zillow:1", raw={"building_lotId": "ABC"}, building_name="Foo")
    assert building_key(ls) == "bld:ABC"


def test_building_key_falls_back_to_name_then_id():
    assert building_key(_u("zillow:2", building_name="Luxe at Meridian")) == "name:luxe at meridian"
    assert building_key(_u("zillow:3")) == "id:zillow:3"


def test_group_collapses_units_of_same_building():
    units = [
        _u("zillow:10", raw={"building_lotId": "X"}, description="short"),
        _u("zillow:11", raw={"building_lotId": "X"}, description="a much longer description here"),
        _u("zillow:20", raw={"building_lotId": "Y"}),
    ]
    groups = _group(units)
    assert set(groups) == {"bld:X", "bld:Y"}
    assert len(groups["bld:X"]) == 2
    # representative is the unit with the most description text
    assert _representative(groups["bld:X"]).listing_id == "zillow:11"


def test_amenities_from_resofacts():
    reso = {
        "appliances": ["Dishwasher", "Washer"],
        "communityFeatures": ["Fitness Center", "Unknown"],
        "parkingFeatures": ["Garage"],
        "flooring": None,
    }
    out = amenities_from_resofacts(reso)
    assert "Fitness Center" in out and "Garage" in out and "Dishwasher" in out
    assert "Unknown" not in out  # sentinel dropped


def test_amenities_from_empty():
    assert amenities_from_resofacts(None) == []


def test_photo_urls_from_mixed_sources():
    item = {
        "responsivePhotos": [
            {"mixedSources": {"jpeg": [
                {"url": "https://photos.zillowstatic.com/a-192.jpg", "width": 192},
                {"url": "https://photos.zillowstatic.com/a-1536.jpg", "width": 1536},
            ]}},
            {"mixedSources": {"jpeg": [{"url": "https://photos.zillowstatic.com/b-1536.jpg"}]}},
        ]
    }
    urls = photo_urls(item, limit=4)
    assert urls == [
        "https://photos.zillowstatic.com/a-1536.jpg",  # largest variant chosen
        "https://photos.zillowstatic.com/b-1536.jpg",
    ]


def test_photo_urls_fallback_to_imgsrc():
    assert photo_urls({"imgSrc": "https://x/y.jpg"}) == ["https://x/y.jpg"]
    assert photo_urls({}) == []


def test_in_unit_laundry_detection():
    assert in_unit_laundry_from_reso({"laundryFeatures": ["Washer/Dryer In Unit"]}) is True
    assert in_unit_laundry_from_reso({"hasInUnitLaundry": True}) is True
    assert in_unit_laundry_from_reso({"laundryFeatures": ["Shared", "Common Area"]}) is False
    assert in_unit_laundry_from_reso({"laundryFeatures": []}) is None
    assert in_unit_laundry_from_reso(None) is None
