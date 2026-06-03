"""End-to-end weekly pipeline: fetch -> store -> score -> enrich -> notify.

This is what the Railway cron runs once a week (`aptagent run`).
"""

from __future__ import annotations

from dataclasses import dataclass

from aptagent import store
from aptagent.config import Preferences, load_preferences
from aptagent.scoring import passes_hard_filters, score_listing


@dataclass
class ScoreSummary:
    scored: int = 0
    rejected: int = 0


def score_all(prefs: Preferences | None = None) -> ScoreSummary:
    """Score every active listing and persist scores + reasons."""
    prefs = prefs or load_preferences()
    summary = ScoreSummary()
    scored: list[tuple[str, float, dict]] = []
    for ls in store.all_active_listings():
        ok, _ = passes_hard_filters(ls, prefs)
        if not ok:
            summary.rejected += 1
            continue
        s, reasons = score_listing(ls, prefs)
        scored.append((ls.listing_id, s, reasons))
    store.save_scores(scored)
    summary.scored = len(scored)
    return summary


def run(
    *,
    do_fetch: bool = True,
    max_items: int | None = None,
    enrich_top: int = 15,
    triage_to: int = 0,
    do_send: bool = True,
    digest_limit: int = 12,
    log=print,
) -> dict:
    """Run the full weekly pipeline. Returns a small result dict."""
    result: dict = {}

    if do_fetch:
        from aptagent.fetchers.apify import ApifyFetcher

        log("Fetching live listings via Apify...")
        listings = ApifyFetcher().fetch(max_items=max_items)
        up = store.upsert_listings(listings)
        result["fetched"] = len(listings)
        result["new"] = up.new
        result["price_changes"] = len(up.price_changes)
        log(f"  fetched {len(listings)}, {up.new} new, {len(up.price_changes)} price changes")

    summary = score_all()
    result["scored"] = summary.scored
    log(f"Scored {summary.scored} (rejected {summary.rejected}).")

    if enrich_top:
        from aptagent.enrich import llm

        candidates = [c for c in store.top_scored(limit=enrich_top) if c.listing_id not in store.enriched_ids()]
        if triage_to and len(candidates) > triage_to:
            scores = llm.triage_scores(candidates)
            candidates.sort(key=lambda c: scores.get(c.listing_id, 0.0), reverse=True)
            candidates = candidates[:triage_to]
        enriched = 0
        for c in candidates:
            try:
                store.save_enrichment(c.listing_id, llm.deep_dive(c), llm.get_settings().aptagent_model_strong)
                enriched += 1
            except Exception as e:  # noqa: BLE001
                log(f"  enrich skip {c.listing_id}: {type(e).__name__}")
        result["enriched"] = enriched
        if enriched:
            score_all()  # fold inferred floor/orientation into scores
        log(f"Enriched {enriched} listings.")

    if do_send:
        from aptagent.notify.telegram import send_digest

        result["messages_sent"] = send_digest(limit=digest_limit)
        log(f"Sent digest ({result['messages_sent']} message(s)).")

    return result
