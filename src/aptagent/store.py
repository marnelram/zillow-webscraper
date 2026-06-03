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
