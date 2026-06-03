"""Building-grouping and detail-extraction tests (pure, no network)."""

from __future__ import annotations

from aptagent.enrich.detail import amenities_from_resofacts
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
