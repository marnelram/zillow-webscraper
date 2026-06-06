# Prep Skill

## Purpose

Prepare working changes for a clean commit. Reviews every file in the current git diff, tidies the Python code, runs related tests, and drafts a commit message. The step between "done coding" and "ready to ship."

## Workflow

### 1. Identify Changed Files

```bash
git diff --name-only HEAD
git diff --name-only --cached
git ls-files --others --exclude-standard
```

Combine into a deduplicated list. If nothing changed: `No changes detected. Nothing to prep.`

### 2. Review Each Changed File

For every changed `.py` file, read it and check for:

**Tidiness**
- Remove leftover debug `print()` statements (keep intentional CLI output and logging).
- Remove commented-out / dead code.
- Remove unused imports.
- Trim over-explaining comments — this codebase uses minimal comments; keep only non-obvious ones.
- Remove `TODO`/`FIXME` notes that the current change resolves.
- Strip trailing whitespace.

**File size**
- If a changed file exceeds ~300 lines, consider splitting it into a module under `src/` following the existing layout (`src/web_scraping/`, `src/processing/`, `src/utils/`). Just do it; don't ask.

**Quality**
- Look for obvious bugs introduced by the change.
- Match existing patterns (package layout under `src/`, relative imports, function style).
- Verify no secrets, API keys, or cookies are hardcoded — scrapers often leak these in `HEADERS`.

### 3. Run Formatting / Linting (if available)

These tools aren't configured in the repo, so use them only if present on the system; skip silently if not:

```bash
python -m black src 2>/dev/null      # format, if black is installed
python -m ruff check --fix src 2>/dev/null   # lint, if ruff is installed
```

Don't add new dev dependencies or config files as part of prep.

### 4. Run Related Tests

Tests live in `src/tests/` and run with pytest:

```bash
python -m pytest src/tests -q
```

If a changed module has a matching test (e.g. `zillow_scraper.py` → `test_zillow_scraper.py`), make sure it still runs. If tests fail because of the change, fix the change. Note that some existing tests hit the live Zillow site and may be flaky — flag network failures rather than "fixing" them.

### 5. Final Review

```bash
git diff --stat
```

Review the full set of changes (including cleanup) for coherence.

### 6. Draft a Commit Message

Match existing `git log` style — concise imperative subject; add `Fixes #N` if a GitHub issue is associated (check the branch name, e.g. `marnelram/issue21`):

```
{concise summary of what changed}

Fixes #{number}
```

Present it:

```
Prep complete. Here's what was done:

Files reviewed: {N}
- {cleanup performed}
- {any refactoring}
- {test results}

Suggested commit message:
---
{commit message}
---

Ready to commit? Use /ship or commit manually.
```

## Input

None. Optional path argument to scope the prep:

```
/prep                  # prep all changed files
/prep src/web_scraping # prep only changes there
```

## Notes

**DO**: focus cleanup on files in the diff · fix test failures caused by the change · preserve intentional logging/CLI output · present the commit message as a suggestion.
**DON'T**: auto-commit (that's `/ship`) · make functional changes beyond cleanup (flag bugs, don't fix unrelated ones) · add config/tooling the repo doesn't already use · "fix" flaky network-dependent tests.
