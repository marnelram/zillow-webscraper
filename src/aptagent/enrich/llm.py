"""LLM enrichment funnel via OpenRouter (OpenAI-compatible API).

Two tiers, configured in settings:
- ``model_cheap`` — fast triage that re-ranks the rule-filtered shortlist by a
  quick "promising-ness" read of the available text.
- ``model_strong`` — a deep dive per surviving listing that extracts concessions
  / deals, community events, a vibe summary, and best-effort floor + orientation.

Output is cached in the ``enrichments`` table so weekly reruns don't re-pay.
Note: search-card data is thin; the deep dive is richest when a listing has a
description (e.g. fixture/building payloads). Fetching the detail page for more
text is a future enhancement.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from aptagent.settings import get_settings

_DEEP_DIVE_INSTRUCTIONS = (
    "You are helping someone screen apartment listings. From the listing data, "
    "extract ONLY facts you can support from the text. Return a JSON object with keys: "
    "deals (array of short strings for any rent specials/concessions like '1 month free'), "
    "concessions (string summary or null), community_events (array of strings, [] if none), "
    "vibe_summary (one-sentence neighborhood/building vibe or null), "
    "floor (integer floor number if determinable, else null), "
    "orientation (compass facing like 'south' if determinable, else null). "
    "Do not invent deals or events that aren't supported by the text."
)


class DeepDive(BaseModel):
    deals: list[str] = Field(default_factory=list)
    concessions: str | None = None
    community_events: list[str] = Field(default_factory=list)
    vibe_summary: str | None = None
    floor: int | None = None
    orientation: str | None = None


def _client():
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")
    from openai import OpenAI

    return OpenAI(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        default_headers={"X-Title": "aptagent"},
    )


def _listing_text(listing: Any) -> str:
    """Compact text blob describing a listing for the model."""
    parts = [
        f"Building: {getattr(listing, 'building_name', None)}",
        f"Address: {getattr(listing, 'address', None)}",
        f"Rent: ${getattr(listing, 'rent', None)}  Beds: {getattr(listing, 'beds', None)}  "
        f"Baths: {getattr(listing, 'baths', None)}  Sqft: {getattr(listing, 'sqft', None)}",
        f"Amenities: {', '.join(getattr(listing, 'amenities', []) or [])}",
        f"Description: {getattr(listing, 'description', None) or ''}",
    ]
    raw = getattr(listing, "raw", None) or {}
    for key in ("statusText", "marketingTreatments", "factsAndFeatures"):
        if raw.get(key):
            parts.append(f"{key}: {json.dumps(raw[key])[:800]}")
    return "\n".join(p for p in parts if p)


def parse_deep_dive(content: str) -> DeepDive:
    """Parse a model JSON response into a DeepDive (tolerant of fenced blocks)."""
    text = (content or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            return DeepDive()
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return DeepDive()
    if not isinstance(data, dict):
        return DeepDive()
    return DeepDive.model_validate(
        {k: data.get(k) for k in DeepDive.model_fields if data.get(k) is not None}
    )


def triage_scores(listings: list[Any], model: str | None = None) -> dict[str, float]:
    """Cheap-model pass: relevance 0..1 per listing_id (one batched call)."""
    if not listings:
        return {}
    model = model or get_settings().aptagent_model_cheap
    lines = [
        f"{i}. id={ls.listing_id} | {getattr(ls, 'building_name', None) or getattr(ls, 'address', None)} "
        f"| ${getattr(ls, 'rent', None)} | {getattr(ls, 'beds', None)}bd | "
        f"{(getattr(ls, 'description', None) or '')[:160]}"
        for i, ls in enumerate(listings)
    ]
    prompt = (
        "Rate how promising each apartment listing looks for a renter who wants a "
        "central/north-Seattle or Eastside studio/1BR near transit and groceries, "
        "cheaper is better. Return a JSON object mapping each id to a score 0.0-1.0.\n\n"
        + "\n".join(lines)
    )
    resp = _client().chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    try:
        data = json.loads(resp.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        return {}
    out: dict[str, float] = {}
    for k, v in (data.items() if isinstance(data, dict) else []):
        try:
            out[str(k)] = max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            continue
    return out


def deep_dive(listing: Any, model: str | None = None) -> DeepDive:
    """Strong-model extraction for a single listing."""
    model = model or get_settings().aptagent_model_strong
    resp = _client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _DEEP_DIVE_INSTRUCTIONS},
            {"role": "user", "content": _listing_text(listing)},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return parse_deep_dive(resp.choices[0].message.content)
