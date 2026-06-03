"""aptagent command-line interface.

Commands (built out phase by phase):
- ``fetch``  pull listings (live Zillow or from saved fixtures) into the store.
- ``stats``  quick DB summary.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from aptagent import store
from aptagent.config import load_preferences
from aptagent.fetchers.zillow import (
    ZillowFetcher,
    load_fixture_buildings,
    normalize_buildings,
)

app = typer.Typer(add_completion=False, help="Personal Seattle apartment-hunting agent.")
console = Console()


@app.command()
def fetch(
    fixtures: list[Path] = typer.Option(
        None, "--fixtures", "-f", help="Load building payloads from JSON file(s) instead of the network."
    ),
    source: str = typer.Option("apify", "--source", "-s", help="Live source: 'apify' or 'zillow' (direct/ScraperAPI)."),
    max_pages: int = typer.Option(20, help="Max search pages per rent band (zillow source)."),
    max_buildings: int = typer.Option(None, help="Cap building-detail fetches (zillow source; protects credits)."),
    max_items: int = typer.Option(None, help="Cap results (apify source; protects credits)."),
    dry_run: bool = typer.Option(False, help="Normalize only; do not write to the database."),
):
    """Fetch listings and upsert them into Postgres."""
    if fixtures:
        buildings = []
        for path in fixtures:
            buildings.extend(load_fixture_buildings(path))
        console.print(f"Loaded [bold]{len(buildings)}[/] building payloads from fixtures.")
        listings = normalize_buildings(buildings)
    elif source == "apify":
        from aptagent.fetchers.apify import ApifyFetcher
        console.print("Fetching live via Apify Zillow actor...")
        listings = ApifyFetcher().fetch(max_items=max_items)
    else:
        fetcher = ZillowFetcher()
        via = "ScraperAPI" if fetcher.scraperapi_key else "direct (likely blocked)"
        console.print(f"Fetching live from Zillow via {via} (slow, ToS-sensitive)...")
        listings = fetcher.fetch(max_pages=max_pages, max_buildings=max_buildings)

    console.print(f"Normalized [bold]{len(listings)}[/] units.")
    if dry_run:
        for ls in listings[:5]:
            console.print(f"  {ls.listing_id}  ${ls.rent}  {ls.beds}bd/{ls.baths}ba  {ls.sqft}sqft  {ls.building_name}")
        console.print("[yellow]dry-run: nothing written.[/]")
        return

    result = store.upsert_listings(listings)
    console.print(
        f"[green]Stored[/] {result.total} ({result.new} new, {result.updated} updated); "
        f"{len(result.price_changes)} price changes."
    )


@app.command()
def score(
    prefs_path: Path = typer.Option("preferences.yaml", "--prefs", help="Preferences YAML file."),
    top: int = typer.Option(15, help="How many top listings to print."),
):
    """Score all active listings against preferences and print the ranked shortlist."""
    from aptagent import pipeline

    prefs = load_preferences(prefs_path)
    console.print("Scoring active listings...")
    summary = pipeline.score_all(prefs)
    console.print(f"[green]Scored[/] {summary.scored}; rejected {summary.rejected} on hard filters.")

    table = Table(title=f"Top {top} matches")
    table.add_column("Score", justify="right", style="bold cyan")
    table.add_column("Rent", justify="right")
    table.add_column("Bd/Ba")
    table.add_column("Building / Address")
    table.add_column("Why", overflow="fold")
    for row in store.top_scored(limit=top):
        reasons = row.score_reasons or {}
        why = "; ".join(
            r["note"] for r in reasons.values() if isinstance(r, dict) and r.get("note")
        )
        beds = "studio" if row.beds == 0 else (f"{row.beds:g}" if row.beds is not None else "?")
        table.add_row(
            f"{row.score:g}",
            f"${row.rent}" if row.rent else "?",
            f"{beds}/{row.baths:g}" if row.baths is not None else beds,
            (row.building_name or row.address or row.listing_id)[:40],
            why[:90],
        )
    console.print(table)


@app.command()
def enrich(
    top: int = typer.Option(20, help="Rule-scored listings to consider for enrichment."),
    triage_to: int = typer.Option(0, help="If >0, cheap-model triage cuts to this many before deep-dive."),
    force: bool = typer.Option(False, help="Re-enrich even if a cached enrichment exists."),
):
    """LLM funnel: (optional) cheap triage of the top listings, then strong-model deep-dive."""
    from aptagent.enrich import llm

    candidates = store.top_scored(limit=top)
    if not force:
        done = store.enriched_ids()
        candidates = [c for c in candidates if c.listing_id not in done]
    if not candidates:
        console.print("Nothing to enrich (all cached; use --force to redo).")
        return

    if triage_to and len(candidates) > triage_to:
        console.print(f"Triaging {len(candidates)} via {llm.get_settings().aptagent_model_cheap}...")
        scores = llm.triage_scores(candidates)
        candidates.sort(key=lambda c: scores.get(c.listing_id, 0.0), reverse=True)
        candidates = candidates[:triage_to]

    model = llm.get_settings().aptagent_model_strong
    console.print(f"Deep-diving [bold]{len(candidates)}[/] listings via {model}...")
    for c in candidates:
        try:
            dd = llm.deep_dive(c)
        except Exception as e:  # noqa: BLE001 — keep going on a single failure
            console.print(f"  [red]skip[/] {c.listing_id}: {type(e).__name__}: {str(e)[:80]}")
            continue
        store.save_enrichment(c.listing_id, dd, model)
        bits = []
        if dd.deals:
            bits.append(f"deals={dd.deals}")
        if dd.floor is not None:
            bits.append(f"floor={dd.floor}")
        if dd.orientation:
            bits.append(f"facing={dd.orientation}")
        console.print(f"  [green]ok[/] {(c.building_name or c.address or c.listing_id)[:40]} {' '.join(bits)}")
    console.print("[green]Enrichment complete.[/] Re-run `aptagent score` to fold in floor/orientation.")


@app.command()
def digest(limit: int = typer.Option(12, help="How many listings to include.")):
    """Send the current ranked digest to Telegram now."""
    from aptagent.notify.telegram import send_digest

    sent = send_digest(limit=limit)
    console.print(f"[green]Sent[/] {sent} Telegram message(s).")


@app.command()
def run(
    no_fetch: bool = typer.Option(False, help="Skip the live fetch (use what's already stored)."),
    max_items: int = typer.Option(None, help="Cap Apify results (protects credits)."),
    enrich_top: int = typer.Option(15, help="Deep-dive this many top listings."),
    triage_to: int = typer.Option(0, help="If >0, cheap-triage to this many before deep-dive."),
    no_send: bool = typer.Option(False, help="Skip sending the Telegram digest."),
    digest_limit: int = typer.Option(12, help="Listings in the digest."),
):
    """Full weekly pipeline: fetch -> score -> enrich -> Telegram digest. (Railway cron entrypoint.)"""
    from aptagent import pipeline

    result = pipeline.run(
        do_fetch=not no_fetch,
        max_items=max_items,
        enrich_top=enrich_top,
        triage_to=triage_to,
        do_send=not no_send,
        digest_limit=digest_limit,
        log=lambda m: console.print(m),
    )
    console.print(f"[bold green]Pipeline done.[/] {result}")


@app.command()
def stats():
    """Print a quick summary of what's in the store."""
    console.print(f"listings in store: [bold]{store.count_listings()}[/]")


if __name__ == "__main__":
    app()
