---
name: apartment-hunt-preferences
description: The user's personal apartment-hunting criteria driving the scoring engine (budget, commute, lifestyle, lease, alerts)
metadata:
  type: project
---

The user (27yo M) is revamping this Zillow scraper into a personal apartment-hunting agent for **Seattle** that ranks/explains matches, monitors weekly, and surfaces deals. His criteria, to drive the scoring engine:

- **Budget:** **cheaper-is-better** — lower rent scores higher (NOT a target band). Total cost (rent + parking + pet rent + utilities + amortized fees) hard cap ~$3,000/mo.
- **Size/type:** prefers **studio or 1BR**; "enough space" protected by a **soft minimum sqft (~400–450)**, not heavily weighted beyond that.
- **Commute:** proximity to Link light rail is a major bonus (he named Northgate, Lynnwood, Tukwila as examples — score the whole line by distance to nearest station).
- **Lifestyle priorities (high→low):** quick transit access > near light rail > close to the heart of Seattle > nearby gym > nearby parks > "higher density of working class" neighborhood feel. **Quiet living and space are explicitly low priority.**
- **Building:** bonus for **3rd+ floor** units, and **south-facing** units (wants to start an in-house garden). Both are rarely in structured listing data → delivered best-effort via the LLM deep-dive pass; expect them to populate on a minority of listings.
- **Move-in:** ~4–6 months out, roughly **Nov 2026–Feb 2027**. Lease length 1–2 years. No furnished/unfurnished preference.
- **Alerts:** weekly cadence, surfaced as a "New this week" view **in the dashboard** — no email for now (decided against Gmail send/draft).

"Working-class density" has no listing field — **confirmed** proxy is US Census ACS (median income + renter share by zip/tract), interpreted as "lived-in, not sterile-luxury."

See [[apartment-agent-architecture]] for the system design these prefs plug into.
