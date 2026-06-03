"""Scoring + geo tests (pure, no network/DB)."""

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
        "weights": {
            "affordability": 25, "transit_access": 30, "light_rail": 20,
            "central_seattle": 20, "gym": 15, "parks": 10, "bedroom_pref": 10,
            "move_in": 10,
        },
    }
)


def _capitol_hill_studio(**over) -> Listing:
    base = dict(
        listing_id="t:1", rent=1800, beds=0, baths=1, sqft=520,
        latitude=47.6190, longitude=-122.3206,  # Capitol Hill station
        transit_score=80, amenities=["Fitness center"],
    )
    base.update(over)
    return Listing(**base)


def test_hard_filter_rejects_over_cap():
    ok, reason = passes_hard_filters(_capitol_hill_studio(rent=2900, pet_rent=200, parking_fee=100), PREFS)
    assert not ok and "cap" in reason


def test_hard_filter_rejects_no_rent():
    ok, _ = passes_hard_filters(_capitol_hill_studio(rent=None), PREFS)
    assert not ok


def test_cheaper_scores_higher():
    cheap, _ = score_listing(_capitol_hill_studio(rent=1300), PREFS)
    pricey, _ = score_listing(_capitol_hill_studio(rent=2900), PREFS)
    assert cheap > pricey


def test_central_near_link_scores_well():
    s, reasons = score_listing(_capitol_hill_studio(), PREFS)
    assert s > 75
    assert "light_rail" in reasons and "transit_access" in reasons
    assert reasons["bedroom_pref"]["raw"] == 1.0


def test_remote_location_scores_lower():
    near, _ = score_listing(_capitol_hill_studio(), PREFS)
    # Far from downtown/Link, low transit.
    far, _ = score_listing(
        _capitol_hill_studio(latitude=47.30, longitude=-122.45, transit_score=20), PREFS
    )
    assert near > far


def test_sqft_floor_penalty():
    big, _ = score_listing(_capitol_hill_studio(sqft=600), PREFS)
    tiny, _ = score_listing(_capitol_hill_studio(sqft=300), PREFS)
    assert tiny < big  # 10% nudge for sub-floor sqft


def test_geo_nearest_station():
    name, d = geo.nearest_station(47.6190, -122.3206)
    assert name == "Capitol Hill"
    assert d < 0.2


def test_geo_handles_missing_coords():
    assert geo.nearest_station(None, None) == (None, None)
    assert geo.distance_to_downtown(None, None) is None
