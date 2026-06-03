"""Deep-dive JSON parsing tests (pure, no network)."""

from __future__ import annotations

from aptagent.enrich.llm import DeepDive, parse_deep_dive


def test_parses_clean_json():
    dd = parse_deep_dive(
        '{"deals": ["1 month free"], "concessions": "look-and-lease", '
        '"community_events": ["resident happy hour"], "vibe_summary": "lively", '
        '"floor": 5, "orientation": "south"}'
    )
    assert dd.deals == ["1 month free"]
    assert dd.floor == 5 and dd.orientation == "south"
    assert dd.community_events == ["resident happy hour"]


def test_parses_fenced_json():
    dd = parse_deep_dive('```json\n{"deals": [], "floor": 3}\n```')
    assert dd.floor == 3 and dd.deals == []


def test_parses_json_with_prose_around_it():
    dd = parse_deep_dive('Sure! Here is the data: {"concessions": "none", "floor": null} Hope that helps.')
    assert dd.concessions == "none" and dd.floor is None


def test_garbage_returns_empty_deepdive():
    dd = parse_deep_dive("I could not find anything useful.")
    assert isinstance(dd, DeepDive)
    assert dd.deals == [] and dd.floor is None
