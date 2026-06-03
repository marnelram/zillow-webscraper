"""Load and validate ``preferences.yaml`` into typed objects."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

DEFAULT_PREFS_PATH = Path("preferences.yaml")


class HardFilters(BaseModel):
    total_cost_cap: int = 3000
    require_rent: bool = True


class SoftPrefs(BaseModel):
    rent_floor: int = 1200
    min_sqft: int = 450
    bedroom_pref: list[float] = Field(default_factory=lambda: [0, 1])


class MoveIn(BaseModel):
    earliest: date | None = None
    latest: date | None = None
    mode: str = "soft"


class Neighborhoods(BaseModel):
    preferred: list[str] = Field(default_factory=list)  # names in geo.NEIGHBORHOODS
    avoid: list[str] = Field(default_factory=list)
    preferred_radius_mi: float = 2.5   # full bonus within this radius of a preferred centroid
    avoid_radius_mi: float = 1.0       # penalty applies within this radius of an avoided centroid
    avoid_penalty: float = 0.6         # score multiplier when inside an avoided area (lower = harsher)


class Preferences(BaseModel):
    hard_filters: HardFilters = Field(default_factory=HardFilters)
    soft: SoftPrefs = Field(default_factory=SoftPrefs)
    move_in: MoveIn = Field(default_factory=MoveIn)
    neighborhoods: Neighborhoods = Field(default_factory=Neighborhoods)
    weights: dict[str, float] = Field(default_factory=dict)

    def weight(self, name: str) -> float:
        return float(self.weights.get(name, 0.0))


def load_preferences(path: str | Path = DEFAULT_PREFS_PATH) -> Preferences:
    path = Path(path)
    if not path.exists():
        return Preferences()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Preferences.model_validate(data)
