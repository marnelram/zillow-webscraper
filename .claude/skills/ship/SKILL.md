# Ship Skill

## Purpose

Finalize completed work: commit changes, push the feature branch, and open a pull request that closes the associated GitHub issue. Final step of the development workflow.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated. If unavailable, push the branch and give the user the compare URL (`https://github.com/marnelram/zillow-webscraper/compare/main...{branch}`) to open the PR manually.

## Workflow

### 1. Validate Preconditions

- Changes exist (`git status --porcelain` is non-empty).
- On a feature branch, not `main`.
- Tests pass (implied when invoked by the builder; otherwise run `python -m pytest` first).

If no changes: `No changes to commit. Ensure the work is complete before shipping.`

### 2. Determine the Issue Number

Get the issue number from the invocation (`/ship 21`), the builder's context, or the branch name (e.g. `marnelram/issue21` → `21`). If none can be found, ask the user.

### 3. Create the Commit Message

Match the repo's existing style (see `git log`) — a concise imperative subject, with the issue closed via a `Fixes #N` trailer:

```
{concise summary of what changed}

Fixes #{number}
```

Guidelines:
- Subject under 72 chars, imperative mood ("add" not "added").
- Optional body for context when the change is non-trivial.

### 4. Stage and Commit

```bash
git add -A
git commit -m "{subject}" -m "Fixes #{number}"
git log -1 --oneline
```

### 5. Push the Branch

```bash
git push -u origin {current_branch}
```

### 6. Create the Pull Request

```bash
gh pr create \
  --base main \
  --title "{issue title or commit subject}" \
  --body "$(cat <<'EOF'
## Summary
{brief description of the change}

## Changes
{key changes}

## Testing
- [x] `python -m pytest` passes

Fixes #{number}
EOF
)"
```

`Fixes #{number}` in the PR body auto-closes the issue on merge.

### 7. Success Message

```
✓ Committed: {subject}
✓ Pushed to origin/{branch}
✓ PR opened: {PR URL}  (closes #{number})

🚀 Ready for review.
```

## Error Handling

- **No changes**: stop with a message; don't create an empty commit.
- **On `main`**: `Cannot ship from main. Create a feature branch first.`
- **Push fails**: report the error; if the remote moved ahead, ask the user to pull/rebase — never force-push.
- **`gh` missing/PR fails**: print the manual command and the compare URL.
- **Existing PR for the branch**: update it with `gh pr edit` instead of creating a new one.

## Notes

**DO**: use `Fixes #N` to link/close the issue · push before opening the PR · keep the subject concise and imperative.
**DON'T**: force-push · push to `main` · commit failing tests.

## Usage

Auto-invoked by the builder when tests pass. Manual: `/ship 21` (where `21` is the issue number).
