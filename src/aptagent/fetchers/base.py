"""The Fetcher interface.

Keeping the data source behind this ABC means the rest of the pipeline (store,
scoring, enrichment) never depends on Zillow specifics — a paid API (RentCast,
Apify) can be dropped in as another Fetcher without touching anything downstream.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from aptagent.schemas import Listing


class Fetcher(ABC):
    """Source of normalized rental listings for a metro area."""

    #: Human-readable source name, also stored on each Listing.
    source: str = "base"

    @abstractmethod
    def fetch(self, max_pages: int = 20) -> list[Listing]:
        """Return normalized listings for the configured search area."""
        raise NotImplementedError
