# Claude Code Configuration

Custom agents and skills for the **zillow-webscraper** project — a Python scraper (requests + BeautifulSoup4 + pandas) packaged under `src/`.

The workflow drives off **GitHub Issues** and **pytest**, and ships via the **GitHub CLI** (`gh`).

## Quick Start

```bash
# 1. Find an issue to work on (pulls open GitHub issues)
/find-task

# 2. Pick one → auto-initializes branch, researches, builds, tests

# 3. Answer any clarifying questions from the research agent

# 4. Work is committed and a PR is opened that closes the issue
```

## What's Included

### Skills (user commands)

- **`/find-task`** — list open GitHub issues and pick one (auto-spawns `task-initializer`)
- **`/ship`** — commit, push, and open a PR that closes the issue (auto-invoked by the builder)
- **`/prep`** — tidy the current diff and run pytest before committing
- **`/plan-feature`** — adversarial planning (plan mode): a planner + technical / data-quality / security critics
- **`/task-triage`** — recommend and autonomously work a ~30-minute batch of issues
- **`/security-audit`** — focused safety audit (secrets, unsafe parsing, SSRF/filesystem, CSV injection, dependencies)

### Agents (automated workers)

- **`task-initializer`** — create/checkout a git branch (`marnelram/issue{number}`), claim the issue
- **`research`** — read the issue, look up library docs (Context7), analyze `src/` patterns, ask questions
- **`builder`** — implement the change in `src/`, add pytest coverage, run tests, call `/ship`

## Workflow Diagram

```
/find-task → pick issue
   ↓
task-initializer  (git branch)
   ↓
research          (Context7 + codebase + clarifying questions)
   ↓
builder           (implement + pytest)
   ↓
/ship             (commit "Fixes #N" + push + PR)
   ↓
PR ready for review 🚀
```

## Requirements

- **GitHub CLI** (`gh`) installed and authenticated (`gh auth status`) — used to read issues and open PRs. If `gh` is unavailable, the skills fall back to fetching the issues page and printing a compare URL for manual PR creation.
- **Git** with `user.name`/`user.email` configured and push access.
- **Python 3.x** with the project installed (`pip install -e .` or `pip install requests beautifulsoup4 pandas`).
- Tests runnable: `python -m pytest src/tests`.
- **Context7 MCP** (optional) — library docs for requests / BeautifulSoup4 / pandas.

## Conventions

- **Branches**: `marnelram/issue{number}` (optionally `marnelram/issue{number}-{slug}`).
- **Commits / PRs**: concise imperative subject + a `Fixes #{number}` trailer to auto-close the issue on merge (matches existing repo history).
- **Tests**: pytest under `src/tests/`; prefer offline tests against the saved payloads in `data/raw/` over hitting the live site.

See [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) for the full walkthrough.
