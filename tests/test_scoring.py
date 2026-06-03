"""Scoring + geo tests (pure, no network/DB).

Note: grocery weight is intentionally omitted from PREFS so scoring never hits
the Overpass API during tests.
"""

from __future__ import annotations

from datetime import date

from aptagent.config import Preferences
from aptagent.enrich import geo
from aptagent.schemas import Listing
from aptagent.scoring import passes_hard_filters, score_listing

PREFS = Preferences.model_validate(
    {
        "hard_filters": {"total_cost_cap": 3000, "require_rent": True},
        "soft": {"rent_floor": 1200, "min_sqft": 450, "bedroom_pref": [0, 1]},
        "move_in": {"earliest": date(2026, 11, 1), "latest": date(2027, 2, 28), "mode": "soft"},
        "neighborhoods": {
            "preferred": ["Northgate", "Green Lake", "Lynnwood", "Bellevue"],
            "avoid": ["Capitol Hill"],
            "preferred_radius_mi": 2.5,
            "avoid_radius_mi": 1.0,
            "avoid_penalty": 0.55,
        },
        "weights": {
            "affordability": 18, "transit_access": 32, "light_rail": 25,
            "neighborhood_pref": 28, "gym": 15, "parks": 10, "bedroom_pref": 10,
            "in_unit_laundry": 18, "move_in": 8,
        },
    }
)


def _northgate_studio(**over) -> Listing:
    base = dict(
        listing_id="t:1", rent=1800, beds=0, baths=1, sqft=520,
        latitude=47.7060, longitude=-122.3260,  # Northgate (preferred + on Link)
        transit_score=75, amenities=["Fitness center"],
    )
    base.update(over)
    return Listing(**base)


def test_hard_filter_rejects_over_cap():
    ok, reason = passes_hard_filters(_northgate_studio(rent=2900, pet_rent=200, parking_fee=100), PREFS)
    assert not ok and "cap" in reason


def test_hard_filter_rejects_no_rent():
    ok, _ = passes_hard_filters(_northgate_studio(rent=None), PREFS)
    assert not ok


def test_cheaper_scores_higher():
    cheap, _ = score_listing(_northgate_studio(rent=1300), PREFS)
    pricey, _ = score_listing(_northgate_studio(rent=2900), PREFS)
    assert cheap > pricey


def test_preferred_neighborhood_scores_well():
    s, reasons = score_listing(_northgate_studio(), PREFS)
    assert s > 70
    assert "neighborhood_pref" in reasons
    assert "light_rail" in reasons and "transit_access" in reasons
    assert reasons["bedroom_pref"]["raw"] == 1.0


def test_avoid_area_penalizes():
    # Same quality unit, one at Capitol Hill (avoided) vs Northgate (preferred).
    cap_hill = score_listing(
        _northgate_studio(latitude=47.6190, longitude=-122.3120), PREFS
    )
    northgate = score_listing(_northgate_studio(), PREFS)
    assert cap_hill[0] < northgate[0]
    assert "avoid_area" in cap_hill[1]


def test_sqft_floor_penalty_scales():
    big, _ = score_listing(_northgate_studio(sqft=600), PREFS)       # above floor: no penalty
    near, _ = score_listing(_northgate_studio(sqft=440), PREFS)      # just below: small penalty
    micro, reasons = score_listing(_northgate_studio(sqft=225), PREFS)  # far below: ~x0.5
    assert big > near > micro
    assert "space" in reasons


def test_in_unit_laundry_bonus():
    with_wd, reasons = score_listing(_northgate_studio(in_unit_laundry=True), PREFS)
    without, _ = score_listing(_northgate_studio(in_unit_laundry=False), PREFS)
    unknown, _ = score_listing(_northgate_studio(), PREFS)  # None -> factor omitted
    assert with_wd > without
    assert reasons["in_unit_laundry"]["raw"] == 1.0


def test_geo_nearest_station_two_line():
    name, d = geo.nearest_station(47.6150, -122.1920)  # Bellevue Downtown
    assert name == "Bellevue Downtown"
    assert d < 0.2


def test_geo_nearest_named():
    name, d = geo.nearest_named(47.7060, -122.3260, ["Northgate", "Bellevue"])
    assert name == "Northgate" and d < 0.2


def test_geo_handles_missing_coords():
    assert geo.nearest_station(None, None) == (None, None)
    assert geo.nearest_named(None, None, ["Northgate"]) == (None, None)
