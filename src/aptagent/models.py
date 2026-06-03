"""ORM models for the listing store.

Three tables:
- ``listings``    one row per unit, with first_seen/last_seen for "new this week".
- ``price_history`` append-only rent observations, for price-drop detection.
- ``enrichments`` cached LLM deep-dive output, keyed 1:1 to a listing.
"""

from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aptagent.db import Base


class Listing(Base):
    __tablename__ = "listings"

    listing_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    source: Mapped[str] = mapped_column(String(32), default="zillow", index=True)
    zpid: Mapped[str | None] = mapped_column(String(32), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    state: Mapped[str | None] = mapped_column(String(16), nullable=True)
    zipcode: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    rent: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    beds: Mapped[float | None] = mapped_column(Float, nullable=True)
    baths: Mapped[float | None] = mapped_column(Float, nullable=True)
    sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    building_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    orientation: Mapped[str | None] = mapped_column(String(16), nullable=True)
    in_unit_laundry: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    parking_fee: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pet_rent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    application_fee: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deposit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    utilities_included: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    walk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bike_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    amenities: Mapped[list] = mapped_column(JSONB, default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Latest computed score (set by the scoring engine)
    score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    score_reasons: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    prices: Mapped[list["PriceHistory"]] = relationship(
        back_populates="listing", cascade="all, delete-orphan"
    )
    enrichment: Mapped["Enrichment | None"] = relationship(
        back_populates="listing", cascade="all, delete-orphan", uselist=False
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[str] = mapped_column(
        ForeignKey("listings.listing_id", ondelete="CASCADE"), index=True
    )
    rent: Mapped[int] = mapped_column(Integer)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    listing: Mapped[Listing] = relationship(back_populates="prices")


class Enrichment(Base):
    __tablename__ = "enrichments"

    listing_id: Mapped[str] = mapped_column(
        ForeignKey("listings.listing_id", ondelete="CASCADE"), primary_key=True
    )
    deals: Mapped[list] = mapped_column(JSONB, default=list)
    concessions: Mapped[str | None] = mapped_column(Text, nullable=True)
    community_events: Mapped[list] = mapped_column(JSONB, default=list)
    vibe_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    inferred_floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    inferred_orientation: Mapped[str | None] = mapped_column(String(16), nullable=True)
    in_unit_laundry: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    income_restricted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    income_restriction_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    photos_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(80), nullable=True)
    raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    listing: Mapped[Listing] = relationship(back_populates="enrichment")
