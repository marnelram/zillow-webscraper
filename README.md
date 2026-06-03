# aptagent — personal apartment-hunting agent (Seattle)

Fetches rental listings, scores them against your personal preferences, enriches
the shortlist with an LLM, and pushes a weekly ranked digest to Telegram.
Designed to run unattended on a weekly cron (Railway).

> Revamp of an earlier Zillow scraper. The legacy `src/web_scraping`,
> `src/processing`, and `src/zillow_scraper.py` modules are superseded by the
> `src/aptagent` package and slated for removal.

## How it works

A cost-tiered funnel:

1. **Fetch** — listings via a pluggable `Fetcher` (Apify Zillow actor by default;
   direct/ScraperAPI and fixtures also supported). Normalized into a common shape.
2. **Store** — Neon Postgres (SQLAlchemy + Alembic), tracking first/last seen and
   price history so "new this week" and price drops work.
3. **Score** — a transparent 0–100 rule-based score with a per-factor reasons
   breakdown: affordability, transit, light rail, preferred/avoided neighborhoods,
   grocery proximity (OpenStreetMap), parks, gym, Census neighborhood feel,
   bedroom fit, move-in window. Tuned in `preferences.yaml`.
4. **Enrich** — OpenRouter funnel over the top listings: a cheap-model triage then
   a strong-model deep dive for deals/concessions, community events, vibe, and
   best-effort floor/orientation. Cached so reruns don't re-pay.
5. **Notify** — a weekly Telegram digest of the top matches, flagged "new" when new.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
cp .env.example .env   # then fill in the values below
uv run alembic upgrade head
```

### Environment (`.env`)

| Var | Purpose |
| --- | --- |
| `NEON_DATABASE_URL` | Neon Postgres connection string |
| `APIFY_TOKEN` | Apify API token (runs the Zillow scraper actor) |
| `APIFY_ZILLOW_ACTOR` | actor id (default `maxcopell~zillow-scraper`) |
| `OPENROUTER_API_KEY` | OpenRouter key for LLM enrichment |
| `APTAGENT_MODEL_CHEAP` / `APTAGENT_MODEL_STRONG` | triage / deep-dive models |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | digest delivery |
| `CENSUS_API_KEY` | (optional) unlocks the neighborhood-feel factor |
| `SCRAPERAPI_KEY` | (optional) alternative unblocker for the direct Zillow fetcher |

## Usage

```bash
uv run aptagent fetch --source apify --max-items 60   # pull live listings
uv run aptagent fetch --fixtures data/raw/raw_listings_2.json  # or from saved payloads
uv run aptagent score --top 15                        # rank + explain
uv run aptagent enrich --top 15 --triage-to 8         # LLM deep-dive the shortlist
uv run aptagent digest --limit 12                     # send digest to Telegram
uv run aptagent run                                   # full weekly pipeline (cron entrypoint)
uv run pytest                                         # tests (no network/DB needed)
```

## Deploy (Railway, weekly cron)

1. Create a Railway project from this repo (it builds via the `Dockerfile`).
2. Add the env vars above in the service's **Variables**.
3. Set the service **Cron Schedule** (e.g. `0 16 * * 1` = Mondays 09:00 PT) — the
   container runs `aptagent run` once and exits; the cron re-invokes weekly.

Neon + OpenRouter + Apify + Telegram all work from Railway's datacenter IP
(unlike direct scraping, which Zillow blocks).
