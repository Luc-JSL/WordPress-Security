# Skills for Secure WP Care: review sheet

11 skills from two trusted sources: **Anthropic** (official) and **Trail of Bits** (a security
research firm). Copies of every file are in `skills/` so you can read them before installing.

## What each one is for

| Skill | Source | Why we need it | Runs scripts? | License |
|---|---|---|---|---|
| **skill-creator** | Anthropic | Build your own "Secure WP Care" skill (your checklist, report style, rules) | Yes: runs the `claude` CLI to test skills | Apache 2.0 |
| **webapp-testing** | Anthropic | Load sites in a real browser, screenshots for reports, catch JavaScript-loaded plugins | Yes: starts local test servers you name | Apache 2.0 |
| **pdf** | Anthropic | Turn health check reports and client reports into PDFs | Yes: PDF tools only, no network | Anthropic (use allowed, not open source) |
| **xlsx** | Anthropic | Prospect tracker, money tracker, client list spreadsheets | Yes: runs LibreOffice to recalculate formulas | Anthropic (use allowed, not open source) |
| **semgrep** | Trail of Bits | Scan the checker's code, and suspicious plugin code during cleanups (supports PHP) | Yes: runs Semgrep, deletes only its own temp files | CC BY-SA 4.0 (repo) |
| **differential-review** | Trail of Bits | Security review of every change we make to the checker | No (instructions only) | CC BY-SA 4.0 (repo) |
| **supply-chain-risk-auditor** | Trail of Bits | Check new libraries (webappanalyzer, checkdmarc) for known risks before adding them | Yes: read-only lookups to OSV, deps.dev, Scorecard, PyPI, npm, GitHub | CC BY-SA 4.0 (repo) |
| **fp-check** | Trail of Bits | Verify a finding is real before you tell a client (no false alarms) | No (instructions only) | CC BY-SA 4.0 (repo) |
| **yara-rule-authoring** | Trail of Bits | Write malware detection rules for hacked-site cleanups | Yes: rule review script, deletes only its own temp folder | CC BY-SA 4.0 (repo) |
| **vulnerability-triage-brocards** | Trail of Bits | Decide which plugin vulnerabilities actually matter for a client | No (instructions only) | CC BY-SA 4.0 (repo) |
| **modern-python** | Trail of Bits | Clean, modern setup for the checker project (uv, ruff) | No (instructions only) | CC BY-SA 4.0 (repo) |

## What I checked

- Searched every script for downloads, shell commands, file deletion and code evaluation.
- **Nothing suspicious.** Every hit was expected: deleting its own temporary folders, starting
  servers or tools you ask for, or read-only lookups to public security databases.
- No skill sends your files or data anywhere except those public lookups
  (supply-chain-risk-auditor) and the `claude` CLI you already use (skill-creator).

## Things to know

- **semgrep** needs `pip install semgrep`. **yara-rule-authoring** needs `pip install yara-x`.
  **xlsx** formula recalculation needs LibreOffice (free).
- **skill-creator** tests use your Claude usage when you run evals.
- Trail of Bits skills are CC BY-SA 4.0: free to use; if you share modified versions, share them
  under the same license.

## Skipped on purpose

Anthropic: docx, pptx, mcp-builder (add later when we connect tools), design and Slack skills.
Trail of Bits: blockchain scanners, fuzzing, C/C++/Rust/Lean tools, CodeQL (heavy), and the rest
that don't fit this business.
