"""Normalization tests — run against the real saved Zillow payloads, no network."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from aptagent.fetchers.zillow import load_fixture_buildings, normalize_building, normalize_buildings
from aptagent.schemas import Listing

FIXTURE = Path(__file__).parent.parent / "data" / "raw" / "raw_listings_2.json"


@pytest.fixture(scope="module")
def buildings() -> list[dict]:
    return load_fixture_buildings(FIXTURE)


def test_fixture_loads(buildings):
    assert len(buildings) == 31


def test_normalizes_to_units(buildings):
    listings = normalize_buildings(buildings)
    # 337 units + floor plans without units (priced via minPrice).
    assert len(listings) >= 337
    assert all(isinstance(x, Listing) for x in listings)


def test_unit_fields_populated(buildings):
    # Angeline Apartments is the first building in the fixture.
    angeline = next(b for b in buildings if b.get("buildingName") == "Angeline Apartments")
    listings = normalize_building(angeline)
    assert listings, "expected at least one unit"
    first = listings[0]
    assert first.city == "Seattle"
    assert first.state == "WA"
    assert first.zipcode == "98118"
    assert first.walk_score == 94
    assert first.transit_score == 62
    assert first.rent and first.rent > 0
    assert first.beds is not None  # 0 == studio is valid
    assert first.listing_id.startswith("zillow:")


def test_available_from_parsed(buildings):
    listings = normalize_buildings(buildings)
    dated = [ls for ls in listings if ls.available_from is not None]
    assert dated, "expected some units with a parsed available_from date"
    assert all(isinstance(ls.available_from, date) for ls in dated)


def test_listing_ids_mostly_unique(buildings):
    listings = normalize_buildings(buildings)
    ids = [ls.listing_id for ls in listings]
    # zpid-keyed ids should be unique; allow a tiny tolerance for floorplan-only rows.
    assert len(set(ids)) >= len(ids) - 5


def test_amenities_have_no_unknown_sentinels(buildings):
    listings = normalize_buildings(buildings)
    for ls in listings:
        assert "Unknown" not in ls.amenities
