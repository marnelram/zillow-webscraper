"""Enrichment funnel: group candidates by building, (optionally) fetch detail
pages, deep-dive once per building, and share building-level results across its
units. Shared by `aptagent enrich` and the weekly pipeline.
"""

from __future__ import annotations

from typing import Any, Callable

from aptagent import store
from aptagent.enrich import detail, llm


def building_key(listing: Any) -> str:
    """A stable grouping key so a building's units enrich once, not per-unit."""
    raw = getattr(listing, "raw", None) or {}
    bld = raw.get("building_lotId") or raw.get("lotId") or raw.get("buildingId")
    if bld:
        return f"bld:{bld}"
    name = (getattr(listing, "building_name", None) or "").strip().lower()
    if name:
        return f"name:{name}"
    return f"id:{listing.listing_id}"


def _group(listings: list[Any]) -> dict[str, list[Any]]:
    groups: dict[str, list[Any]] = {}
    for ls in listings:
        groups.setdefault(building_key(ls), []).append(ls)
    return groups


def _representative(group: list[Any]) -> Any:
    """Pick the unit with the most description text to deep-dive."""
    return max(group, key=lambda ls: len(getattr(ls, "description", None) or ""))


def run_enrichment(
    candidates: list[Any],
    *,
    triage_to: int = 0,
    fetch_detail: bool = False,
    web_search: bool = True,
    log: Callable[[str], None] = print,
) -> dict:
    """Enrich a set of candidate listings, deduped by building.

    For each building's representative we optionally fetch the detail page (full
    description, amenities, photos, deterministic laundry), then run the strong
    deep-dive with those photos attached and web search enabled, and share the
    building-level result across the building's units.

    Returns counts: {buildings, enriched, detail_fetched}.
    """
    groups = _group(candidates)
    reps = [(_representative(g), g) for g in groups.values()]
    log(f"{len(candidates)} listings -> {len(reps)} buildings")

    if triage_to and len(reps) > triage_to:
        scores = llm.triage_scores([r for r, _ in reps])
        reps.sort(key=lambda rg: scores.get(rg[0].listing_id, 0.0), reverse=True)
        reps = reps[:triage_to]

    model = llm.get_settings().aptagent_model_strong
    enriched = detail_fetched = 0

    for rep, group in reps:
        photos: list[str] = []
        reso_laundry: bool | None = None
        if fetch_detail and getattr(rep, "url", None):
            try:
                item = detail.fetch_detail(rep.url)
                if item:
                    fields = detail.detail_to_fields(item)
                    store.update_listing_detail(rep.listing_id, fields["description"], fields["amenities"])
                    if fields["description"]:
                        rep.description = fields["description"]
                    if fields["amenities"]:
                        rep.amenities = list({*(rep.amenities or []), *fields["amenities"]})
                    photos = fields.get("photos") or []
                    reso_laundry = fields.get("in_unit_laundry")
                    detail_fetched += 1
            except Exception as e:  # noqa: BLE001
                log(f"  detail skip {rep.listing_id}: {type(e).__name__}")

        # Fall back to the search card's own photo for vision when no detail photos
        # (e.g. detail fetch disabled or Apify budget exhausted).
        if not photos:
            img = (getattr(rep, "raw", None) or {}).get("imgSrc")
            if isinstance(img, str) and img.startswith("http"):
                photos = [img]

        try:
            dd = llm.deep_dive(rep, photos=photos, web_search=web_search)
        except Exception as e:  # noqa: BLE001
            log(f"  enrich skip {rep.listing_id}: {type(e).__name__}: {str(e)[:60]}")
            continue

        # Prefer the deterministic resoFacts laundry signal when the model is unsure.
        if dd.in_unit_laundry is None and reso_laundry is not None:
            dd.in_unit_laundry = reso_laundry

        # Representative gets unit-level fields; siblings share building-level only.
        store.save_enrichment(rep.listing_id, dd, model, apply_unit_fields=True, photos_used=len(photos))
        for sib in group:
            if sib.listing_id != rep.listing_id:
                store.save_enrichment(sib.listing_id, dd, model, apply_unit_fields=False)
        enriched += 1
        tag = []
        if dd.deals:
            tag.append(f"deals={dd.deals}")
        if dd.in_unit_laundry is True:
            tag.append("in-unit W/D")
        if dd.income_restricted:
            tag.append("income-restricted")
        if photos:
            tag.append(f"{len(photos)}img")
        log(f"  ok {(rep.building_name or rep.address or rep.listing_id)[:40]} "
            f"({len(group)} unit(s)) {' '.join(tag)}")

    return {"buildings": len(reps), "enriched": enriched, "detail_fetched": detail_fetched}
