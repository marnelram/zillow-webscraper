# Find Task Skill

## Purpose

Query GitHub Issues for open, unassigned tasks in `marnelram/zillow-webscraper`, display the top 5, and let the user pick one to work on. After selection, spawn the `task-initializer` agent.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated (`gh auth status`).
- If `gh` is not available, fall back to fetching `https://github.com/marnelram/zillow-webscraper/issues` with WebFetch and ask the user which issue to work on.

## Workflow

### 1. Query GitHub for Open Issues

```bash
gh issue list --state open --limit 50 \
  --json number,title,labels,assignees,updatedAt,body
```

### 2. Filter and Sort

- Drop issues already assigned (`assignees` non-empty), unless the user asks to include them.
- Sort: issues labeled `bug` first, then most recently updated (`updatedAt`).
- Take the top 5.
- For each, extract: number, title, labels, first ~100 chars of body.

### 3. Present Tasks to User

Use `AskUserQuestion` (single select), one option per issue:

- **Label**: `#{number}: {title} ({labels})` — truncate to ~80 chars
- **Description**: first ~100 chars of the issue body

Show `no label` when an issue has none.

### 4. Spawn Task Initializer Agent

After selection, parse the issue number and spawn:

```
Agent({
  subagent_type: "task-initializer",
  description: "Initialize issue #{number}",
  prompt: "Initialize work for GitHub issue #{number}.\n\nTitle: {title}\nLabels: {labels}\nBody:\n{body}"
})
```

## Output

- Top 5 open issues displayed
- User selection
- `task-initializer` spawned with the GitHub issue number

## Error Handling

- **No open issues**: `No open issues in marnelram/zillow-webscraper. 🎉`
- **`gh` not found / not authenticated**: tell the user to install/auth `gh` (https://cli.github.com/), or fall back to WebFetch on the issues page.
- **Fewer than 5 issues**: show all; don't fail.

## Next Steps

1. `task-initializer` — create the git branch
2. `research` — gather context, ask clarifying questions
3. `builder` — implement + add pytest coverage
4. `/ship` — commit and open a PR that closes the issue
