# Security Audit Skill

## Purpose

Run a focused security/safety audit of this Python scraper by launching a handful of specialized agents in parallel — one per category that actually applies to a `requests`/BeautifulSoup/pandas script. Each produces severity-ranked findings; results are merged into one report sorted by severity with suggested fixes.

## Input

```
/security-audit            # Full audit of src/ (default)
/security-audit src/web_scraping/   # Audit a specific directory
```

Optional scope argument. Defaults to the `src/` package.

## Workflow Overview

```
1. Determine audit scope
2. Launch the category agents in parallel
3. Collect, deduplicate, and merge findings
4. Present a severity-ranked report with suggested fixes
```

## Step 1: Determine Scope

- **No args**: audit `src/` (and `setup.py`).
- **With args**: audit only the specified paths.

Announce:

```
Starting security audit...
Scope: {src/ | specified paths}
Categories: Secrets & Config · Unsafe Parsing & Deserialization · SSRF & Filesystem · Output Injection · Dependencies
```

## Step 2: Launch Category Agents in Parallel

Spawn all agents in a single message (one `Agent` call each, `subagent_type: "general-purpose"`).

Shared preamble for every agent:

```
You are a security auditor for a small Python web scraper.

**Project**: zillow-webscraper — fetches Zillow listings with `requests`, parses with BeautifulSoup4 (data is often embedded as JSON in the page), and writes a CSV with pandas. Package rooted at `src/` (web_scraping / processing / utils / zillow_scraper.py).

**Audit scope**: {scope}

**Instructions**:
1. Skim the README and `src/zillow_scraper.py` for context (HEADERS, config, output).
2. Systematically read files in scope relevant to your category.
3. Only report real issues you can point to in the code — no hypotheticals.
4. This is a local scraping script, not a web server: do NOT report web-app concerns (auth, XSS, CSRF, IDOR) that don't apply.

**Output format** — for each finding:
### {FINDING_TITLE}
- **Severity**: Critical / High / Medium / Low
- **Category**: {your category}
- **File(s)**: {paths with line numbers}
- **Description**: {what it is and why it matters}
- **Proof**: {the code that demonstrates it}
- **Suggested Fix**: {concrete change}

If you find nothing, report: "No {category} issues found." and list files reviewed.
```

### Agent 1: Secrets & Configuration

```
{preamble, CATEGORY = "Secrets & Configuration"}

**Focus areas**:
- Hardcoded cookies, auth tokens, or API keys in `HEADERS` or anywhere in source
- Credentials or session values that would be committed to git
- `.gitignore` coverage for any local secrets, output files, or caches
- Sensitive values that should be read from the environment instead of hardcoded

**Where to look**: `src/zillow_scraper.py` (HEADERS/config), `src/web_scraping/`, `.gitignore`
```

### Agent 2: Unsafe Parsing & Deserialization

```
{preamble, CATEGORY = "Unsafe Parsing & Deserialization"}

**Focus areas**:
- `eval()`, `exec()`, or `pickle` applied to scraped/remote content
- Unsafe construction of objects from untrusted JSON/HTML
- Regexes on attacker-influenced input that could catastrophically backtrack (ReDoS)
- Trusting scraped numeric/text fields without validation before use

**Where to look**: `src/processing/`, `src/utils/parse_json_encoded_url.py`, `src/utils/dict_utils.py`
```

### Agent 3: SSRF & Filesystem

```
{preamble, CATEGORY = "SSRF & Filesystem"}

**Focus areas**:
- If a URL, search query, or base host becomes user/config-controlled, can requests be aimed at internal hosts, `file://`, or arbitrary domains?
- Missing timeouts on `requests` calls (hang / resource exhaustion)
- Output/file paths built from scraped fields → path traversal or writing outside the intended output directory
- Following redirects to unexpected hosts

**Where to look**: `src/web_scraping/`, `src/utils/path.py`, any `requests.get/post` call, any file write
```

### Agent 4: Output Injection (CSV)

```
{preamble, CATEGORY = "Output Injection"}

**Focus areas**:
- CSV formula injection: scraped fields beginning with `=`, `+`, `-`, or `@` written to the CSV unescaped (executes when opened in a spreadsheet)
- Untrusted content breaking CSV structure (unescaped delimiters/newlines) — though pandas usually handles quoting, verify
- Misleading/garbage rows silently written when parsing fails

**Where to look**: wherever the DataFrame is built and `to_csv` is called
```

### Agent 5: Dependencies

```
{preamble, CATEGORY = "Dependencies"}

**Focus areas**:
- Known vulnerabilities in `requests`, `beautifulsoup4`, `pandas` (and any others) — run `python -m pip list` / `pip-audit` if available
- Unpinned or outdated dependencies in `setup.py`
- Unnecessary or risky transitive dependencies

**Where to look**: `setup.py`, `requirements.txt` (if present), installed package versions
```

## Step 3: Collect and Merge

After all agents return:

1. **Deduplicate** overlapping findings (note which categories they span).
2. **Sort** by severity: Critical → High → Medium → Low.
3. **Count** per severity and per category; note hotspot files.

## Step 4: Present the Report

```markdown
# Security Audit Report

**Scope**: {src/ | specified paths}
**Files Reviewed**: {approx count}

## Summary
| Severity | Count |
|----------|-------|
| Critical | {n} |
| High     | {n} |
| Medium   | {n} |
| Low      | {n} |

## Findings by Category
| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Secrets & Config | | | | |
| Unsafe Parsing | | | | |
| SSRF & Filesystem | | | | |
| Output Injection | | | | |
| Dependencies | | | | |

## Critical Findings
{...}
## High Findings
{...}
## Medium / Low Findings
{...}

## Recommendations
1. {top priority action}
2. {...}
```

## Tools Required

- `Agent` (subagent_type: `general-purpose`) — category agents
- `Read`, `Grep`, `Glob` — code analysis
- `Bash` — `pip list` / `pip-audit` for the dependency agent

## Error Handling

- **Agent failure**: report which category was missed; continue with the rest.
- **No findings**: state it, list files reviewed, and note this isn't a guarantee — suggest `pip-audit` and manual review.

## Notes

**DO**: launch all agents in one parallel batch · ground every finding in real code (path + line + snippet) · deduplicate · prioritize actionable findings.
**DON'T**: report web-app vulns (auth/XSS/CSRF/IDOR) that don't apply to a local script · flag theoretical risks without code evidence · modify code (this skill only audits) · report issues in installed packages' source or generated files.
