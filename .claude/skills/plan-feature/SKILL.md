# Plan Feature Skill

## Purpose

Adversarial planning skill for use in **plan mode only**. Launches a planner agent that drafts an implementation plan, then three adversarial agents (technical, data-quality/reliability, security) that critique it in parallel. The planner incorporates their feedback, and the cycle repeats for a number of rounds proportional to task complexity. The final plan is written to TodoWrite for execution.

## Input

Must be invoked from plan mode with a description of the feature or bug:

```
/plan-feature Add retry-with-backoff to listing requests
/plan-feature Fix missing prices for some listings
```

## Preconditions

- **Must be in plan mode.** If not in plan mode, instruct the user to enter plan mode first (`/plan`) and stop.

## Workflow Overview

```
1. Assess complexity → determine round count (1-3)
2. Planner agent drafts initial plan
3. Three adversarial agents critique in parallel:
   - Technical Adversary (architecture, performance, edge cases, correctness)
   - Data Quality & Reliability Adversary (data correctness, completeness, anti-scraping robustness)
   - Security Adversary (auth, injection, data exposure, OWASP top 10)
4. Planner reviews all critiques and revises plan
5. Repeat steps 3-4 for remaining rounds
6. Present final plan to user for approval (plan mode handles this)
7. On approval, write plan to TodoWrite
```

---

## Step 1: Assess Complexity

Analyze the feature/bug description and codebase to determine complexity:

| Complexity | Rounds | Criteria |
|-----------|--------|----------|
| **Low** (bug fix, small tweak) | 1 | Single file or narrow scope, clear fix, no structural changes |
| **Medium** (feature, moderate refactor) | 2 | Multiple modules (e.g. new fetch + parse paths), some design decisions |
| **High** (large feature, cross-cutting) | 3 | New subsystem, change to the scraping/parsing pipeline, output schema changes, multiple integration points |

Present the assessment to the user:

```
Complexity: {Low/Medium/High} → {1/2/3} adversarial rounds

Reasoning: {brief justification}
```

The user can override the round count if they disagree.

## Step 2: Planner Drafts Initial Plan

The planner agent analyzes the codebase and creates a detailed implementation plan.

**Spawn the planner agent** (`Agent` tool with `subagent_type: "general-purpose"`):

Prompt the planner with:

```
You are a senior software architect planning an implementation for the zillow-webscraper codebase — a Python scraper (requests + BeautifulSoup4 + pandas) packaged under `src/` (package `zillow_scraper`), with fetching in `src/web_scraping/`, parsing in `src/processing/`, helpers in `src/utils/`, and CSV output.

**Task**: {feature/bug description from user}

**Instructions**:
1. Read the README and skim `src/zillow_scraper.py` for project context and config
2. Search the codebase for relevant existing code, patterns, and similar implementations
3. Research any unfamiliar library APIs via Context7 if needed
4. Create a detailed implementation plan with:

   a. **Summary**: One paragraph describing what will be built and why
   b. **Files to modify**: List each file with what changes are needed
   c. **Files to create**: Any new files with their purpose
   d. **Data/output changes**: Changes to the scraped record shape or CSV columns, if any
   e. **Scraping concerns**: Rate limiting/delay, headers, blocked/non-200 responses, pagination
   f. **Key implementation details**: Important parsing logic, helpers to reuse
   g. **Testing approach**: What to test (prefer offline tests against saved payloads in `data/raw/`)
   h. **Notes**: Any special steps needed

Return the full plan as markdown.
```

## Step 3: Adversarial Review (Parallel)

Spawn **three adversarial agents in parallel** using the `Agent` tool. Each receives the planner's draft and critiques it from their perspective.

### Technical Adversary

Spawn with `subagent_type: "general-purpose"`:

```
You are a senior technical reviewer adversarially critiquing an implementation plan for the zillow-webscraper codebase (Python, requests + BeautifulSoup4 + pandas).

**Your job**: Find everything that could go wrong technically. Be thorough and skeptical.

**Plan to review**:
{planner's draft plan}

**Review these areas**:
1. **Structure**: Does this follow the existing `src/` layering (web_scraping / processing / utils)? Will it create tech debt or duplicate existing helpers?
2. **Correctness**: Parsing logic errors? Wrong assumptions about the response shape? Off-by-one in pagination? Mishandled missing/optional fields?
3. **Robustness**: Network failures, timeouts, non-200 responses, empty result sets, malformed JSON — are they handled?
4. **Performance**: Unbounded loops over pages? Re-fetching the same URL? Building large pandas frames inefficiently?
5. **Brittleness to site changes**: How tightly does the parsing couple to Zillow's current HTML/JSON? Will a small markup change silently break it?
6. **Dependencies**: Are proposed libraries necessary, or can existing ones (requests/bs4/pandas) do it? Version conflicts?

**Read the relevant codebase files** to verify your critiques are grounded in reality (not hypothetical).

**Output format**:
For each issue found:
- **Issue**: {description}
- **Severity**: Critical / High / Medium / Low
- **Location**: {which part of the plan}
- **Suggestion**: {how to fix it}

If something in the plan is solid, say so briefly. Don't nitpick for the sake of it — focus on issues that would actually cause problems.
```

### Data Quality & Reliability Adversary

Spawn with `subagent_type: "general-purpose"`:

```
You are a data engineer adversarially critiquing an implementation plan for zillow-webscraper — a script that scrapes real-estate listings into a CSV.

**Your job**: Find everything that could make the scraped data wrong, incomplete, or unreliable. The output is only as good as the data it produces.

**Plan to review**:
{planner's draft plan}

**Review these areas**:
1. **Data correctness**: Will the right fields be extracted? Are types/units (price, beds, sqft) parsed correctly? Currency/locale issues?
2. **Completeness**: Could listings be silently dropped (e.g. the existing "prices missing for some listings" class of bug)? Does pagination capture everything?
3. **Missing-data handling**: What lands in the CSV when a field is absent — blank, null, crash? Is it consistent?
4. **Deduplication**: Could the same listing appear twice across pages?
5. **Output schema**: Does the CSV stay stable for downstream analysis? Are new columns added without breaking existing ones?
6. **Anti-scraping reality**: Captchas, rate limits, IP blocks — does the plan acknowledge the DELAY/HEADERS config and degrade gracefully instead of producing partial garbage?
7. **Observability**: If a run scrapes 0 results or far fewer than expected, will anyone notice?

**Read relevant scraping/processing code and the sample payloads in `data/raw/`** to ground your concerns.

**Output format**:
For each issue found:
- **Issue**: {description}
- **Severity**: Critical / High / Medium / Low
- **Location**: {which part of the plan}
- **Suggestion**: {how to fix it}

Focus on real data-quality and reliability problems, not style preferences.
```

### Security Adversary

Spawn with `subagent_type: "general-purpose"`:

```
You are a security engineer adversarially critiquing an implementation plan for zillow-webscraper — a Python script that fetches pages from Zillow and writes a CSV.

**Your job**: Find every safety, security, and compliance risk this plan could introduce. Be paranoid but grounded in what a scraper actually does.

**Plan to review**:
{planner's draft plan}

**Review these areas**:
1. **Secrets**: Hardcoded cookies, API keys, or auth tokens in `HEADERS` or source? Anything that would leak into git?
2. **Unsafe parsing**: `eval()`/`exec()` on scraped content? Untrusted JSON/HTML handled unsafely? Deserialization of remote data?
3. **SSRF / URL handling**: If a URL or search query becomes user/config-controlled, can it be pointed at internal hosts or `file://`?
4. **Filesystem**: Path traversal when naming output files from scraped fields? Overwriting arbitrary paths? Writing outside the intended output dir?
5. **Injection into output**: CSV injection (formula injection) from scraped fields starting with `=`,`+`,`-`,`@`?
6. **Compliance / ToS / legal**: Does the change increase request volume or ignore robots/rate limits in a way that's abusive? Does it collect PII (agent names, contact info) that needs care?
7. **Dependencies**: Known vulnerabilities in any proposed package?

**Read relevant fetching/output code** in the codebase to verify concerns.

**Output format**:
For each issue found:
- **Issue**: {description}
- **Severity**: Critical / High / Medium / Low
- **Location**: {which part of the plan}
- **Suggestion**: {how to fix it}

Focus on real risks, not theoretical concerns that don't apply to a local scraping script.
```

## Step 4: Planner Revises Plan

After all three adversarial agents return, **spawn the planner agent again** with all critiques:

```
You are the same senior software architect. You previously drafted this implementation plan:

{previous plan}

Three adversarial reviewers have critiqued your plan:

**Technical Review**:
{technical adversary output}

**Data Quality & Reliability Review**:
{data-quality adversary output}

**Security Review**:
{security adversary output}

**Instructions**:
1. Review each critique carefully
2. For each issue raised:
   - If valid: incorporate the fix into your revised plan
   - If invalid or already handled: briefly explain why (1 sentence)
3. Produce a **revised plan** with the same structure as the original
4. Add a **Changes Made** section at the end summarizing what was changed and why

{If this is NOT the final round}: Focus on addressing Critical and High severity issues. Medium/Low can be noted for next round.
{If this IS the final round}: Address all remaining issues. The plan should be comprehensive and ready for implementation.

Return the full revised plan as markdown.
```

## Step 5: Repeat (if rounds remain)

If more rounds remain, go back to Step 3 with the revised plan. Each subsequent round should surface fewer issues as the plan improves.

## Step 6: Present Final Plan

Present the final plan to the user in plan mode. Plan mode already handles user review and approval. Include:

```
## Adversarial Planning Complete

**Rounds**: {N} | **Issues found**: {total} | **Addressed**: {count} | **Dismissed**: {count}

### Final Plan
{revised plan from last round}

### Adversarial Summary
| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Technical | {n} | {n} | {n} | {n} |
| Data Quality | {n} | {n} | {n} | {n} |
| Security | {n} | {n} | {n} | {n} |

### Dismissed Issues (with reasoning)
{list of issues the planner dismissed and why}
```

The user reviews and can request changes. Plan mode handles this iteration.

## Step 7: Write to TodoWrite

Once the user approves the plan, convert it into a structured TodoWrite task list:

- Break the plan into discrete, actionable steps
- Order tasks by dependency (what must be done first)
- Group related changes (e.g., "Create API route + update types" as one task)
- Include testing as explicit tasks

## Tools Required

### Agent Spawning

- `Agent` (subagent_type: `general-purpose`) — Planner agent, three adversarial agents

### Task Management

- `TodoWrite` — Write final approved plan as tasks

### Code Analysis (used by spawned agents)

- `Read`, `Grep`, `Glob` — Codebase analysis
- `mcp__context7__resolve-library-id`, `mcp__context7__query-docs` — API documentation lookup

## Output

- Adversarially-reviewed implementation plan
- Severity-ranked summary of issues found and addressed
- TodoWrite task list ready for execution

## Error Handling

**Not in Plan Mode**:

```
/plan-feature must be used in plan mode. Enter plan mode first with /plan, then run /plan-feature.
```

**Agent Timeout/Failure**:

If an adversarial agent fails, continue with the remaining agents' feedback. Note the missing perspective:

```
Note: {Technical/Product/Security} review failed. Proceeding with available feedback.
Consider manually reviewing {area} before approving the plan.
```

**No Issues Found**:

If all adversaries find zero issues (unlikely for complex features), note this and proceed directly to presenting the plan. The plan is likely either very simple or the agents need more context — flag this to the user.

## Important Notes

**DO:**

- Always run all three adversarial agents in parallel for speed
- Ground all critiques in actual codebase reading (not hypothetical)
- Track issue counts across rounds to show convergence
- Respect the user's round count override
- Present dismissed issues transparently

**DON'T:**

- Run outside of plan mode
- Skip the adversarial step for "simple" tasks (even 1 round has value)
- Let adversaries be overly pedantic — focus on real issues
- Auto-approve the plan — the user must review in plan mode
- Modify any code — this skill only plans