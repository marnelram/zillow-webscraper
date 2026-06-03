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
    log: Callable[[str], None] = print,
) -> dict:
    """Enrich a set of candidate listings, deduped by building.

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
        if fetch_detail and getattr(rep, "url", None):
            try:
                item = detail.fetch_detail(rep.url)
                if item:
                    fields = detail.detail_to_fields(item)
                    store.update_listing_detail(rep.listing_id, fields["description"], fields["amenities"])
                    # reflect on the in-memory object so deep_dive sees richer text
                    if fields["description"]:
                        rep.description = fields["description"]
                    if fields["amenities"]:
                        rep.amenities = list({*(rep.amenities or []), *fields["amenities"]})
                    detail_fetched += 1
            except Exception as e:  # noqa: BLE001
                log(f"  detail skip {rep.listing_id}: {type(e).__name__}")

        try:
            dd = llm.deep_dive(rep)
        except Exception as e:  # noqa: BLE001
            log(f"  enrich skip {rep.listing_id}: {type(e).__name__}: {str(e)[:60]}")
            continue

        # Representative gets unit-level fields; siblings share building-level only.
        store.save_enrichment(rep.listing_id, dd, model, apply_unit_fields=True)
        for sib in group:
            if sib.listing_id != rep.listing_id:
                store.save_enrichment(sib.listing_id, dd, model, apply_unit_fields=False)
        enriched += 1
        tag = []
        if dd.deals:
            tag.append(f"deals={dd.deals}")
        if dd.vibe_summary:
            tag.append("vibe")
        log(f"  ok {(rep.building_name or rep.address or rep.listing_id)[:40]} "
            f"({len(group)} unit(s)) {' '.join(tag)}")

    return {"buildings": len(reps), "enriched": enriched, "detail_fetched": detail_fetched}
