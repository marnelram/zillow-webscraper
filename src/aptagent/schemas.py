"""Normalized, source-agnostic listing schema.

Every fetcher (Zillow today, RentCast/Apify later) must return ``Listing`` objects
in this shape so the store, scoring, and enrichment layers never see source quirks.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class Listing(BaseModel):
    """One rentable unit (a building's floor plan may expand into several)."""

    # Identity
    listing_id: str = Field(..., description="Stable unique id, e.g. 'zillow:<zpid>' or 'zillow:<bld>:<unit>'")
    source: str = "zillow"
    zpid: str | None = None
    url: str | None = Field(None, description="Absolute listing detail URL")

    # Location
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    # Core attributes
    rent: int | None = Field(None, description="Monthly rent in USD")
    beds: float | None = Field(None, description="0 == studio")
    baths: float | None = None
    sqft: int | None = None
    building_name: str | None = None
    unit_number: str | None = None
    available_from: date | None = None
    floor: int | None = Field(None, description="Best-effort; often unknown")
    orientation: str | None = Field(None, description="Best-effort facing direction, e.g. 'south'")

    # Costs beyond rent (for the total-cost cap)
    parking_fee: int | None = None
    pet_rent: int | None = None
    application_fee: int | None = None
    deposit: int | None = None
    utilities_included: bool | None = None

    # Walkability / transit (from source when present)
    walk_score: int | None = None
    transit_score: int | None = None
    bike_score: int | None = None

    # Free-form
    amenities: list[str] = Field(default_factory=list)
    description: str | None = None

    # Original payload for later re-processing / LLM enrichment
    raw: dict = Field(default_factory=dict)

    def total_monthly_cost(self) -> int | None:
        """Rough monthly cost: rent + parking + pet rent (fees amortized elsewhere)."""
        if self.rent is None:
            return None
        return self.rent + (self.parking_fee or 0) + (self.pet_rent or 0)
