# Task Triage Skill

## Purpose

Pull open issues from GitHub, recommend a small prioritized batch targeting ~30 minutes of work, then autonomously execute the approved issues sequentially — planning each one, implementing it, running tests, and opening PRs.

## Workflow

### Phase 1: Gather Context

#### 1.1 Fetch GitHub Issues

```bash
gh issue list --state open --limit 50 \
  --json number,title,labels,assignees,body,updatedAt
```

For each issue, extract: number, title, labels, body, assignee, updated date. (If `gh` is unavailable, fetch the issues page via WebFetch and ask the user to confirm the list.)

#### 1.2 Flag Sensitive Issues

Mark issues that should be handled manually (shown but excluded from autonomous execution):

- **Dependencies / packaging**: changes to `setup.py`, adding new third-party libraries
- **Anything that increases request volume** against Zillow (rate limits, parallelism) — needs a human judgment call on ToS/abuse
- **Secrets / headers**: changes touching cookies, auth headers, or credentials

### Phase 2: Prioritize and Recommend

#### 2.1 Score Issues

Composite score per issue:

1. **Severity** (weight 40%) — `bug` labeled = highest; broken-output bugs above cosmetic ones.
2. **Impact on data quality** (weight 40%) — does it fix wrong/missing scraped data, or just polish? Rate 1–4.
3. **Quick win** (weight 20%) — estimate effort: Small ~5min=4, Medium ~10–15min=3, Large ~20–30min=2, XL 30min+=1.

#### 2.2 Select Batch

- Sort by composite score (desc).
- Pick issues totaling ~30 minutes.
- Group related issues that can share a branch/PR.
- Cap at 5 per session.

#### 2.3 Present Recommendations

Show ALL open issues, recommended batch highlighted:

```
Recommended (~30 min):
  1. #21 Prices missing for some listings (bug) ~10 min
     Why: data-correctness bug — directly affects output quality
  2. #18 Add sqft column to CSV (enhancement) ~10 min
     Why: small, isolated parsing+output change

  Flagged (manual):
  3. #14 Add concurrent page fetching ~20 min
     Reason: increases request volume against Zillow — needs human sign-off

  Other open issues:
  4. #9 Refactor dict_utils ~15 min
  ...
```

Ask: **"Which issues should I work on? (e.g. 1,2)"** — or **"type 'recommended' to accept the batch."**

### Phase 3: Execute Approved Issues

#### 3.1 Group and Branch

- Group related issues into one branch; unrelated issues get separate branches.
- Branch naming (repo convention): `marnelram/issue{number}` (or `marnelram/issue{n1}-{n2}` for a group), optionally with a short slug.

#### 3.2 Sequential Loop

For each issue (or group):

**A — Claim it.** `gh issue edit {number} --add-assignee @me` (skip if `gh` unavailable).

**B — Plan.** Read the issue fully, search `src/` for affected code (web_scraping / processing / utils), list the specific changes and risks. Show the plan briefly; proceed without waiting for approval.

**C — Implement.** Create the branch from `main` if not already on one. Make the change following the `src/` layout. Reuse existing helpers.

**D — Test.** Run `python -m pytest src/tests -q`. Fix real failures; flag live-site flakiness rather than masking it.

**E — Commit.** Stage the specific files (not `git add .` blindly — though `git add -A` is fine if the diff is clean). Commit with a concise subject plus `Fixes #{number}`.

**F — Next.** If the next issue is unrelated, branch fresh from `main`.

#### 3.3 Create PR(s)

```bash
git push -u origin {branch}
gh pr create --base main --title "{title}" --body "{summary}\n\nFixes #{number}"
```

### Phase 4: Summary

```
Session complete.

Completed:
  #21 Prices missing for some listings — PR #N
  #18 Add sqft column — PR #N

Skipped:
  #14 Concurrent fetching — flagged (request volume, manual)

Remaining open issues: {count}
```

## Tools Required

- `gh` via `Bash` — list/view/edit issues, create PRs
- `Read`, `Edit`, `Write`, `Glob`, `Grep` — codebase work
- `Bash` — git, pytest
- `AskUserQuestion` — present the list and get the selection

## Error Handling

- **No open issues**: `No open issues in marnelram/zillow-webscraper.`
- **`gh` error**: fall back to WebFetch on the issues page; if PRs can't be created, push and give the compare URL.
- **Test failure during implementation**: try to fix; if unfixable, revert that issue's changes, unassign, note it in the summary, and continue.
- **Issue too large (>~30 min)**: note it; if it runs long, commit partial progress and flag it.

## Notes

**DO**: show reasoning for each recommendation · commit after each issue · keep the user posted between issues · batch related issues.
**DON'T**: auto-execute flagged issues (request-volume / packaging / secrets) without explicit approval · force-push or push to `main` · add new dependencies without asking · "fix" flaky network tests.
