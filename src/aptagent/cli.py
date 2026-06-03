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
from aptagent.scoring import passes_hard_filters, score_listing

app = typer.Typer(add_completion=False, help="Personal Seattle apartment-hunting agent.")
console = Console()


@app.command()
def fetch(
    fixtures: list[Path] = typer.Option(
        None, "--fixtures", "-f", help="Load building payloads from JSON file(s) instead of the network."
    ),
    max_pages: int = typer.Option(20, help="Max search pages per rent band (live mode)."),
    dry_run: bool = typer.Option(False, help="Normalize only; do not write to the database."),
):
    """Fetch listings and upsert them into Postgres."""
    if fixtures:
        buildings = []
        for path in fixtures:
            buildings.extend(load_fixture_buildings(path))
        console.print(f"Loaded [bold]{len(buildings)}[/] building payloads from fixtures.")
        listings = normalize_buildings(buildings)
    else:
        console.print("Fetching live from Zillow (this is slow and ToS-sensitive)...")
        listings = ZillowFetcher().fetch(max_pages=max_pages)

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
    prefs = load_preferences(prefs_path)
    listings = store.all_active_listings()
    console.print(f"Scoring [bold]{len(listings)}[/] active listings...")

    scored: list[tuple[str, float, dict]] = []
    rejected = 0
    for ls in listings:
        ok, reason = passes_hard_filters(ls, prefs)
        if not ok:
            rejected += 1
            continue
        s, reasons = score_listing(ls, prefs)
        scored.append((ls.listing_id, s, reasons))

    store.save_scores(scored)
    console.print(f"[green]Scored[/] {len(scored)}; rejected {rejected} on hard filters.")

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
def stats():
    """Print a quick summary of what's in the store."""
    console.print(f"listings in store: [bold]{store.count_listings()}[/]")


if __name__ == "__main__":
    app()
