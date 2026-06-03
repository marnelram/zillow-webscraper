"""Small, dependency-free helpers shared across the package."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

# Sentinel values Zillow uses for "no real data" in list fields.
_UNKNOWN = {"unknown", "none", "", "n/a"}


def parse_price(value) -> int | None:
    """Parse a price string like '$1,462+/mo' or '$1,454/mo' into an int."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    m = re.search(r"[\d,]+", str(value))
    if not m:
        return None
    try:
        return int(m.group().replace(",", ""))
    except ValueError:
        return None


def parse_address(address: str | None) -> tuple[str | None, str | None, str | None]:
    """Parse 'street, City, ST 98115' -> (city, state, zipcode). Best-effort."""
    if not address:
        return None, None, None
    parts = [p.strip() for p in address.split(",") if p.strip()]
    if len(parts) < 2:
        return None, None, None
    city = parts[-2]
    state, zipcode = None, None
    tail = parts[-1].split()
    if tail:
        state = tail[0]
        if len(tail) > 1 and re.fullmatch(r"\d{5}(-\d{4})?", tail[1]):
            zipcode = tail[1]
    return city, state, zipcode


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
