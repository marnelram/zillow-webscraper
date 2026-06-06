# Task Initializer Agent

## Purpose

Initialize a new development task by creating and checking out a git branch for a GitHub issue, and (optionally) assigning the issue to the user so it's clear it's being worked on.

## Scope

- Create a git branch with the repo's naming convention: `marnelram/issue{number}`
- Optionally append a short kebab-case slug: `marnelram/issue{number}-{slug}`
- Checkout the new branch
- Optionally assign the issue and drop a "working on this" comment
- Confirm initialization

## Workflow

### 1. Get Issue Details

Receive the GitHub issue number from `/find-task`. If only the number was passed, fetch details:

```bash
gh issue view {number} --json number,title,labels,body
```

Extract number, title, and labels.

### 2. Mark as In Progress (optional)

GitHub issues have no built-in "In Progress" state. If `gh` is available, signal it by assigning the issue to the user:

```bash
gh issue edit {number} --add-assignee @me
```

Skip silently if `gh` is unavailable — it's not required to proceed.

### 3. Create the Git Branch

- Start the branch name from the repo convention: `marnelram/issue{number}`.
- Optionally append a slug derived from the title: kebab-case, special chars removed, truncated to ~40 chars → `marnelram/issue{number}-{slug}`.
- Create and check out from `main`:

```bash
git checkout main
git pull --ff-only
git checkout -b marnelram/issue{number}-{slug}
```

### 4. Confirm

```
✓ Branch created: marnelram/issue{number}-{slug}
✓ Issue #{number} assigned to you
✓ Task initialized — ready for research
```

## Tools Required

- `Bash` — git and `gh` commands

## Input

- **GitHub issue number** (from `/find-task`)

## Error Handling

- If the branch already exists: check it out and continue.
- If `gh issue edit` fails (no auth/permission): warn and continue — branch creation is what matters.
- If a git operation fails: report the error with details and stop.

## Next Step

After successful initialization, spawn the `research` agent with the GitHub issue number.
