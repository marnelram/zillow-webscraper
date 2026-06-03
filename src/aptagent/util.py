"""Small, dependency-free helpers shared across the package."""

from __future__ import annotations

from datetime import date, datetime, timezone

# Sentinel values Zillow uses for "no real data" in list fields.
_UNKNOWN = {"unknown", "none", "", "n/a"}


def epoch_ms_to_date(value) -> date | None:
    """Convert a Zillow epoch-milliseconds value (int or str) to a date."""
    if value is None:
        return None
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return None
    if ms <= 0:
        return None
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()
    except (OverflowError, OSError, ValueError):
        return None


def safe_int(value) -> int | None:
    """Best-effort int coercion; returns None on failure."""
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def clean_list(values) -> list[str]:
    """Drop Zillow 'Unknown'/empty sentinels from a list of strings."""
    if not values:
        return []
    out = []
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if s and s.lower() not in _UNKNOWN:
            out.append(s)
    return out


def split_custom_amenities(value) -> list[str]:
    """Zillow packs customAmenities as a '?'-delimited string."""
    if not value:
        return []
    return clean_list(str(value).split("?"))
