"""The rule-based scorer.

Produces a 0-100 match score plus a per-factor reasons breakdown. Designed to be
transparent and tunable: each factor yields a 0..1 strength (or None to opt out
when there's no data), and the final score normalizes over whichever factors
applied. Best-effort signals (gym, high_floor, south_facing) are bonus-only —
they lift a listing when present but never penalize for missing data, which the
LLM enrichment pass later fills in.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from aptagent.config import Preferences
from aptagent.enrich import census, geo, groceries

# Gym keywords for best-effort amenity detection.
_GYM_WORDS = ("gym", "fitness", "exercise", "cardio", "peloton", "weight room", "health club")


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def total_monthly_cost(listing: Any) -> int | None:
    if getattr(listing, "rent", None) is None:
        return None
    return listing.rent + (getattr(listing, "parking_fee", 0) or 0) + (getattr(listing, "pet_rent", 0) or 0)


def passes_hard_filters(listing: Any, prefs: Preferences) -> tuple[bool, str | None]:
    """Return (passed, reject_reason)."""
    hf = prefs.hard_filters
    rent = getattr(listing, "rent", None)
    if hf.require_rent and rent is None:
        return False, "no rent listed"
    cost = total_monthly_cost(listing)
    if cost is not None and cost > hf.total_cost_cap:
        return False, f"total cost ${cost} > cap ${hf.total_cost_cap}"
    return True, None


# --- individual factors: each returns (raw_0_to_1 | None, note) ------------- #
def _f_affordability(listing, prefs):
    rent = getattr(listing, "rent", None)
    if rent is None:
        return None, ""
    floor, cap = prefs.soft.rent_floor, prefs.hard_filters.total_cost_cap
    raw = _clamp((cap - rent) / max(1, cap - floor))
    return raw, f"rent ${rent} (cheaper is better)"


def _f_transit(listing, prefs):
    ts = getattr(listing, "transit_score", None)
    if ts is None:
        return None, ""
    return _clamp(ts / 100), f"transit score {ts}"


def _f_light_rail(listing, prefs):
    name, d = geo.nearest_station(getattr(listing, "latitude", None), getattr(listing, "longitude", None))
    if d is None:
        return None, ""
    raw = _clamp(1 - max(0.0, d - 0.4) / 1.6)
    return raw, f"{d:.1f} mi to {name} Link"


def _f_neighborhood_pref(listing, prefs):
    lat, lon = getattr(listing, "latitude", None), getattr(listing, "longitude", None)
    name, d = geo.nearest_named(lat, lon, prefs.neighborhoods.preferred)
    if d is None:
        return None, ""
    radius = prefs.neighborhoods.preferred_radius_mi
    raw = _clamp(1 - max(0.0, d - 0.5) / max(0.1, radius))
    return raw, f"{d:.1f} mi to {name} (preferred)"


def _f_grocery(listing, prefs):
    name, d = groceries.nearest_grocery(getattr(listing, "latitude", None), getattr(listing, "longitude", None))
    if d is None:
        return None, ""
    raw = _clamp(1 - max(0.0, d - 0.2) / 1.3)
    return raw, f"{d:.1f} mi to grocery ({name})"


def _f_parks(listing, prefs):
    name, d = geo.nearest_park(getattr(listing, "latitude", None), getattr(listing, "longitude", None))
    if d is None:
        return None, ""
    return _clamp(1 - max(0.0, d - 0.2) / 1.8), f"{d:.1f} mi to {name}"


def _f_gym(listing, prefs):
    # Bonus-only: present -> 1.0, otherwise omit (sparse in structured data).
    blob = " ".join(getattr(listing, "amenities", []) or []).lower()
    desc = (getattr(listing, "description", None) or "").lower()
    if any(w in blob or w in desc for w in _GYM_WORDS):
        return 1.0, "gym/fitness amenity"
    return None, ""


def _f_neighborhood(listing, prefs):
    raw = census.neighborhood_feel_score(getattr(listing, "zipcode", None))
    if raw is None:
        return None, ""
    return raw, "lived-in neighborhood (Census)"


def _f_bedroom(listing, prefs):
    beds = getattr(listing, "beds", None)
    if beds is None:
        return None, ""
    pref = set(prefs.soft.bedroom_pref)
    if beds in pref:
        return 1.0, "studio" if beds == 0 else f"{int(beds)}BR (preferred)"
    if beds == 2:
        return 0.5, "2BR"
    return 0.2, f"{int(beds)}BR"


def _f_high_floor(listing, prefs):
    floor = getattr(listing, "floor", None)
    if floor is None:
        return None, ""  # bonus-only; usually filled by enrichment
    return (1.0, f"floor {floor} (3+)") if floor >= 3 else (0.3, f"floor {floor}")


def _f_south_facing(listing, prefs):
    o = (getattr(listing, "orientation", None) or "").lower()
    if not o:
        return None, ""  # bonus-only; usually filled by enrichment
    return (1.0, "south-facing") if "south" in o else (0.2, f"{o}-facing")


def _f_move_in(listing, prefs):
    af: date | None = getattr(listing, "available_from", None)
    e, l = prefs.move_in.earliest, prefs.move_in.latest
    if af is None or e is None or l is None:
        return None, ""
    if e <= af <= l:
        return 1.0, f"available {af} (in window)"
    if af < e:
        return 0.5, f"available {af} (before window; may re-list)"
    return 0.3, f"available {af} (after window)"


_FACTORS = {
    "affordability": _f_affordability,
    "transit_access": _f_transit,
    "light_rail": _f_light_rail,
    "neighborhood_pref": _f_neighborhood_pref,
    "grocery": _f_grocery,
    "parks": _f_parks,
    "gym": _f_gym,
    "neighborhood_feel": _f_neighborhood,
    "bedroom_pref": _f_bedroom,
    "high_floor": _f_high_floor,
    "south_facing": _f_south_facing,
    "move_in": _f_move_in,
}


def score_listing(listing: Any, prefs: Preferences) -> tuple[float, dict]:
    """Return (score 0-100, reasons). Score is normalized over applied factors."""
    reasons: dict[str, dict] = {}
    weighted_sum = 0.0
    weight_total = 0.0

    for name, fn in _FACTORS.items():
        w = prefs.weight(name)
        if w <= 0:
            continue
        raw, note = fn(listing, prefs)
        if raw is None:
            continue
        weighted_sum += raw * w
        weight_total += w
        reasons[name] = {"raw": round(raw, 3), "weight": w, "note": note}

    score = (100.0 * weighted_sum / weight_total) if weight_total else 0.0

    # Avoided-neighborhood penalty (e.g. Capitol Hill): multiply the score down.
    nb = prefs.neighborhoods
    if nb.avoid:
        name, d = geo.nearest_named(
            getattr(listing, "latitude", None), getattr(listing, "longitude", None), nb.avoid
        )
        if d is not None and d <= nb.avoid_radius_mi:
            score *= nb.avoid_penalty
            pct = int(round((1 - nb.avoid_penalty) * 100))
            reasons["avoid_area"] = {"raw": None, "weight": None, "note": f"in {name} (avoid, -{pct}%)"}

    # Soft sqft floor: gentle nudge down for sub-minimum units (space is low priority).
    sqft = getattr(listing, "sqft", None)
    if sqft is not None and sqft < prefs.soft.min_sqft:
        score *= 0.9
        reasons["space"] = {"raw": None, "weight": None, "note": f"{sqft} sqft below {prefs.soft.min_sqft} floor (-10%)"}

    return round(score, 1), reasons
