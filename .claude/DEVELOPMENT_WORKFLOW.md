# Development Workflow

Automated feature/bugfix workflow for **zillow-webscraper** using GitHub Issues, Context7 (optional), and pytest.

## Overview

1. Find and select an issue from GitHub
2. Initialize the task (create a git branch, claim the issue)
3. Research requirements and gather library docs
4. Build the change with tests
5. Ship it (commit, push, open a PR that closes the issue)

## Workflow Steps

```
/find-task
  ↓
  Shows top 5 open GitHub issues
  ↓
  User selects an issue
  ↓
task-initializer agent (auto-spawned)
  ├─ git branch: marnelram/issue{number}[-{slug}] from main
  └─ assign issue to @me (if gh available)
  ↓
research agent (auto-spawned)
  ├─ Read the issue (gh issue view) + comments
  ├─ Look up docs via Context7 (requests / bs4 / pandas)
  ├─ Analyze src/ patterns and data/raw/ payloads
  └─ Ask clarifying questions
  ↓
  User answers questions
  ↓
builder agent (auto-spawned with context)
  ├─ Implement in src/ (web_scraping / processing / utils)
  ├─ Add pytest coverage (offline, against saved payloads)
  ├─ Run python -m pytest src/tests & fix failures
  └─ Call /ship
  ↓
/ship skill (auto-invoked)
  ├─ Commit with "Fixes #{number}" trailer
  ├─ Push branch
  └─ Open PR (gh pr create)
  ↓
Done 🚀
```

## Commands

### `/find-task`
List open GitHub issues (unassigned first, bugs prioritized), pick one, auto-spawn `task-initializer`.

### `/ship [number]`
Commit, push, and open a PR that closes the issue. Auto-invoked by the builder; can be run manually (`/ship 21`).

### `/prep [path]`
Tidy the current diff (remove debug prints/dead code/unused imports), run related pytest tests, and draft a commit message. The step between "done coding" and `/ship`.

### `/plan-feature <description>` (plan mode)
Adversarial planning: a planner drafts a plan, then technical / data-quality / security critics review it in parallel over 1–3 rounds. Produces a TodoWrite task list.

### `/task-triage`
Recommend a ~30-minute batch of open issues and autonomously work the approved set, opening a PR per issue/group.

### `/security-audit [path]`
Focused safety audit of the scraper: secrets/config, unsafe parsing, SSRF/filesystem, CSV injection, dependencies.

## Agents

### task-initializer
Create and checkout a git branch (`marnelram/issue{number}`) from `main`; claim the issue. Then spawn `research`.

### research
Read the issue, look up library docs (Context7), study `src/` patterns and the sample payloads in `data/raw/`/`data/interim/`, ask focused clarifying questions, and hand the builder a context document. Then spawn `builder`.

### builder
Implement in the `src/` package following the fetch → parse → output layering, reuse existing helpers, add offline pytest coverage where warranted, run tests, then invoke `/ship`.

## Conventions

**Branch naming**: `marnelram/issue{number}` (optionally `marnelram/issue{number}-{slug}`).

**Commit / PR closing**: concise imperative subject + a `Fixes #{number}` trailer (matches existing repo history; auto-closes the issue on merge).

```
Fix missing prices for some listings

Fixes #21
```

**PR template**:

```markdown
## Summary
{one-liner}

## Changes
{key changes}

## Testing
- [x] `python -m pytest` passes

Fixes #{number}
```

## Required Setup

- **GitHub CLI**: `gh` installed and authenticated (`gh auth status`); push access to `marnelram/zillow-webscraper`. Skills degrade gracefully without `gh` (WebFetch the issues page; print a compare URL for manual PRs).
- **Git**: `user.name` / `user.email` configured.
- **Python**: 3.x with `requests`, `beautifulsoup4`, `pandas` installed; `python -m pytest src/tests` runs.
- **Context7 MCP** (optional): docs for requests / BeautifulSoup4 / pandas.

## Manual Checkpoints

1. **Issue selection** (`/find-task`)
2. **Requirement clarification** (research agent questions)
3. **Final review** (review the PR before merging)

Everything else is automated.

## Error Handling

- **No open issues**: reported; nothing to do.
- **Tests fail during build**: the builder fixes and re-runs until green; live-site flakiness is flagged, not masked.
- **Git/`gh` failures**: clear errors and manual commands; never force-pushes, never pushes to `main`.

## Best Practices

- One issue at a time.
- Prefer offline tests against `data/raw/` payloads over hitting the live Zillow site.
- Be a polite scraper: keep the `DELAY`/`HEADERS` config, don't increase request volume without a human decision.
- Don't add dependencies beyond requests / beautifulsoup4 / pandas without updating `setup.py` and asking.

## File Structure

```
.claude/
├── agents/
│   ├── task-initializer.md   # git branch + claim issue
│   ├── research.md           # gather context & ask questions
│   └── builder.md            # implement & test
├── skills/
│   ├── find-task/SKILL.md    # list GitHub issues
│   ├── ship/SKILL.md         # commit + push + PR
│   ├── prep/SKILL.md         # tidy diff + pytest
│   ├── plan-feature/SKILL.md # adversarial planning
│   ├── task-triage/SKILL.md  # batch autonomous work
│   └── security-audit/SKILL.md
└── DEVELOPMENT_WORKFLOW.md    # this file
```
