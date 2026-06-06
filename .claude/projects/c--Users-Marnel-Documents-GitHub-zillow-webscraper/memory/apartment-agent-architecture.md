---
name: apartment-agent-architecture
description: Agreed architecture for revamping the Zillow scraper into a personal apartment-hunting agent
metadata:
  type: project
---

Revamp of the Zillow scraper into a personal apartment-hunting **web dashboard** for one user (Seattle). Decided direction:

**Four layers:**
1. **Fetchers** — pluggable behind an interface so the data source can be swapped. Start with the existing Zillow mobile-JSON scrape (free, already solves the 800-result cap); upgrade to a headless browser (Playwright) for robustness; optionally add RentCast later for fair-price enrichment. There is **no good free official rental API** in 2026 (Zillow API closed for this use; RentCast free tier is 2 req/mo, paid from $29/mo).
2. **Store** — SQLite, tracks seen listings so "new since last run" and price-drop detection work.
3. **Scoring engine** — config-driven (a `preferences.yaml`), produces a 0–100 match score per listing **with reasons**. See [[apartment-hunt-preferences]].
4. **Web app** — FastAPI + light frontend (filterable/sortable table, map, favorites), plus a scheduled weekly job.

**Key design pattern — cheap bulk + expensive shortlist:** bulk-fetch all listings under budget (cheap), rule-based score and keep top ~25, then run an **LLM enrichment pass only on the shortlist** to extract concessions/deals ("1st month free"), community events, and vibe from each property's own site — data no API provides. New/changed matches surface as a **"New this week" view in the dashboard** (no email — decided against it).

Config-driven preferences chosen over hard-coding so the user can tune weights live in the dashboard and watch ranking re-sort.
