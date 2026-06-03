"""Format and send the weekly apartment digest to Telegram.

Uses the Bot API ``sendMessage`` with HTML parse mode. Long digests are split
into multiple messages (Telegram caps a message at 4096 chars).
"""

from __future__ import annotations

import html

import httpx

from aptagent import store
from aptagent.settings import get_settings

_TG_API = "https://api.telegram.org"
_MAX_LEN = 3800  # stay safely under Telegram's 4096 limit


def _fmt_listing(listing, enrichment, rank: int) -> str:
    new_tag = " 🆕" if store.is_new(listing) else ""
    beds = "studio" if listing.beds == 0 else (f"{listing.beds:g}BR" if listing.beds is not None else "?")
    name = html.escape(listing.building_name or listing.address or listing.listing_id)
    rent = f"${listing.rent:,}" if listing.rent else "$?"
    head = f"<b>{rank}. {name}</b>{new_tag}\n{rent} · {beds} · score {listing.score:g}"

    reasons = listing.score_reasons or {}
    why_bits = [r["note"] for r in reasons.values() if isinstance(r, dict) and r.get("note")]
    why = "; ".join(why_bits[:4])
    lines = [head]
    if why:
        lines.append(f"<i>{html.escape(why)}</i>")

    if enrichment:
        if enrichment.deals:
            lines.append("💸 " + html.escape(", ".join(enrichment.deals)))
        if enrichment.vibe_summary:
            lines.append("🏙 " + html.escape(enrichment.vibe_summary))
        if enrichment.community_events:
            lines.append("🎉 " + html.escape(", ".join(enrichment.community_events)))

    if listing.url:
        lines.append(f'<a href="{html.escape(listing.url)}">View on Zillow</a>')
    return "\n".join(lines)


def build_digest(limit: int = 12) -> list[str]:
    """Build the digest as a list of message-sized HTML chunks."""
    rows = store.top_with_enrichment(limit=limit)
    if not rows:
        return ["<b>🏠 Apartment digest</b>\nNo scored listings yet."]

    new_count = sum(1 for ls, _ in rows if store.is_new(ls))
    header = f"<b>🏠 Weekly apartment digest</b>\nTop {len(rows)} matches · {new_count} new this week\n"

    chunks: list[str] = []
    current = header
    for i, (listing, enrichment) in enumerate(rows, start=1):
        block = "\n" + _fmt_listing(listing, enrichment, i) + "\n"
        if len(current) + len(block) > _MAX_LEN:
            chunks.append(current)
            current = ""
        current += block
    if current.strip():
        chunks.append(current)
    return chunks


def send_digest(limit: int = 12) -> int:
    """Send the digest to the configured chat. Returns messages sent."""
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set.")
    url = f"{_TG_API}/bot{settings.telegram_bot_token}/sendMessage"
    chunks = build_digest(limit=limit)
    sent = 0
    with httpx.Client(timeout=30.0) as client:
        for chunk in chunks:
            resp = client.post(
                url,
                json={
                    "chat_id": settings.telegram_chat_id,
                    "text": chunk,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            resp.raise_for_status()
            sent += 1
    return sent
