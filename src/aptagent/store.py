"""Persistence helpers over the ORM models.

Upserts normalized :class:`~aptagent.schemas.Listing` records into Postgres,
appends a price-history row whenever rent changes, and maintains
first_seen / last_seen so the weekly digest can highlight "new this week".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from aptagent.db import session_scope
from aptagent.models import Enrichment
from aptagent.models import Listing as ListingRow
from aptagent.models import PriceHistory
from aptagent.schemas import Listing

# Listing fields that map 1:1 onto columns we refresh on every upsert.
_SCALAR_FIELDS = (
    "source", "zpid", "url", "address", "city", "state", "zipcode",
    "latitude", "longitude", "rent", "beds", "baths", "sqft",
    "building_name", "unit_number", "available_from", "floor", "orientation",
    "parking_fee", "pet_rent", "application_fee", "deposit", "utilities_included",
    "walk_score", "transit_score", "bike_score", "amenities", "description", "raw",
)


@dataclass
class UpsertResult:
    new: int = 0
    updated: int = 0
    price_changes: list[tuple[str, int, int]] = field(default_factory=list)  # (id, old, new)

    @property
    def total(self) -> int:
        return self.new + self.updated


def upsert_listings(listings: list[Listing]) -> UpsertResult:
    """Insert or update listings; record rent changes in price_history."""
    result = UpsertResult()
    with session_scope() as session:
        for listing in listings:
            _upsert_one(session, listing, result)
    return result


def _upsert_one(session: Session, listing: Listing, result: UpsertResult) -> None:
    row = session.get(ListingRow, listing.listing_id)
    if row is None:
        row = ListingRow(listing_id=listing.listing_id)
        for fname in _SCALAR_FIELDS:
            setattr(row, fname, getattr(listing, fname))
        row.is_active = True
        session.add(row)
        if listing.rent is not None:
            session.add(PriceHistory(listing_id=listing.listing_id, rent=listing.rent))
        result.new += 1
        return

    old_rent = row.rent
    for fname in _SCALAR_FIELDS:
        setattr(row, fname, getattr(listing, fname))
    row.is_active = True
    if listing.rent is not None and listing.rent != old_rent:
        session.add(PriceHistory(listing_id=listing.listing_id, rent=listing.rent))
        if old_rent is not None:
            result.price_changes.append((listing.listing_id, old_rent, listing.rent))
    result.updated += 1


def deactivate_missing(keep_ids: set[str]) -> int:
    """Mark active listings whose id isn't in keep_ids as inactive.

    Used after a *full* weekly fetch so listings that have left the market drop
    out of scoring/digests. Only call when the fetch wasn't capped/partial.
    """
    if not keep_ids:
        return 0
    with session_scope() as session:
        rows = session.scalars(select(ListingRow).where(ListingRow.is_active.is_(True))).all()
        n = 0
        for row in rows:
            if row.listing_id not in keep_ids:
                row.is_active = False
                n += 1
        return n


def count_listings() -> int:
    with session_scope() as session:
        return session.scalar(select(func.count()).select_from(ListingRow)) or 0


def all_active_listings() -> list[ListingRow]:
    """Return active listing rows (detached) for scoring."""
    with session_scope() as session:
        rows = session.scalars(select(ListingRow).where(ListingRow.is_active.is_(True))).all()
        session.expunge_all()
        return list(rows)


def save_scores(scored: list[tuple[str, float, dict]]) -> int:
    """Persist (listing_id, score, reasons) tuples back onto listing rows."""
    n = 0
    with session_scope() as session:
        for listing_id, score, reasons in scored:
            row = session.get(ListingRow, listing_id)
            if row is None:
                continue
            row.score = score
            row.score_reasons = reasons
            n += 1
    return n


def enriched_ids() -> set[str]:
    """listing_ids that already have a cached enrichment."""
    with session_scope() as session:
        return set(session.scalars(select(Enrichment.listing_id)).all())


def save_enrichment(listing_id: str, dd, model: str, apply_unit_fields: bool = True) -> None:
    """Upsert a DeepDive result for a listing.

    Building-level fields (deals/concessions/events/vibe) are always stored.
    Unit-level inferred floor/orientation are only propagated onto the listing
    when ``apply_unit_fields`` is True — set False for sibling units sharing a
    building-level enrichment, since those are unit-specific.
    """
    with session_scope() as session:
        row = session.get(Enrichment, listing_id)
        if row is None:
            row = Enrichment(listing_id=listing_id)
            session.add(row)
        row.deals = dd.deals
        row.concessions = dd.concessions
        row.community_events = dd.community_events
        row.vibe_summary = dd.vibe_summary
        row.inferred_floor = dd.floor if apply_unit_fields else None
        row.inferred_orientation = dd.orientation if apply_unit_fields else None
        row.model_used = model
        if apply_unit_fields:
            listing = session.get(ListingRow, listing_id)
            if listing is not None:
                if dd.floor is not None and listing.floor is None:
                    listing.floor = dd.floor
                if dd.orientation is not None and listing.orientation is None:
                    listing.orientation = dd.orientation


def update_listing_detail(listing_id: str, description: str | None, amenities: list[str] | None) -> None:
    """Persist richer description/amenities fetched from a listing's detail page."""
    with session_scope() as session:
        row = session.get(ListingRow, listing_id)
        if row is None:
            return
        if description:
            row.description = description
        if amenities:
            existing = {a.lower() for a in (row.amenities or [])}
            merged = list(row.amenities or [])
            for a in amenities:
                if a.lower() not in existing:
                    merged.append(a)
            row.amenities = merged


def top_scored(limit: int = 25, min_score: float = 0.0) -> list[ListingRow]:
    """Return the highest-scoring active listings (detached)."""
    with session_scope() as session:
        stmt = (
            select(ListingRow)
            .where(ListingRow.is_active.is_(True), ListingRow.score.isnot(None))
            .where(ListingRow.score >= min_score)
            .order_by(ListingRow.score.desc())
            .limit(limit)
        )
        rows = session.scalars(stmt).all()
        session.expunge_all()
        return list(rows)


def top_with_enrichment(limit: int = 15, min_score: float = 0.0):
    """Return [(listing, enrichment|None)] for the top listings, detached.

    Used by the digest so it can show deals/vibe alongside the score.
    """
    with session_scope() as session:
        stmt = (
            select(ListingRow)
            .where(ListingRow.is_active.is_(True), ListingRow.score.isnot(None))
            .where(ListingRow.score >= min_score)
            .order_by(ListingRow.score.desc())
            .limit(limit)
        )
        rows = session.scalars(stmt).all()
        result = [(r, session.get(Enrichment, r.listing_id)) for r in rows]
        session.expunge_all()
        return result


def is_new(listing: ListingRow, days: int = 7) -> bool:
    """True if first seen within the last `days` (best-effort, tz-aware)."""
    from datetime import datetime, timedelta, timezone

    fs = listing.first_seen
    if fs is None:
        return False
    if fs.tzinfo is None:
        fs = fs.replace(tzinfo=timezone.utc)
    return fs >= datetime.now(timezone.utc) - timedelta(days=days)
