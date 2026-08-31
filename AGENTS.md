# Cron Scanner

Python 3.9+ CLI that scans crontab entries within a time range and exports them to
CSV, JSON, XLSX, Text, Markdown, or PDF. Runs via `run.sh` (POSIX) or `run.ps1`
(Windows); the package entry point is `cron-scanner` → `cron_scanner.scanner:main`.

## Tech stack

- Python 3.9+ (CI uses 3.12). Packaging: `setuptools` + `pyproject.toml`.
- Core deps: `croniter` (next-run math), `cron-descriptor` (human-readable schedule),
  `pandas` + `openpyxl` (XLSX), `reportlab` (PDF), `python-dateutil`.
- Releases: `python-semantic-release` via GitHub Actions on push to `main`.

## Critical rules

- Use **Conventional Commits** (`feat:`, `fix:`, `chore:`, `deps:`, etc.). semantic-release
  derives versions and the changelog from commit messages.
- Never manually bump `__version__` in `cron_scanner/__init__.py` or `version` in
  `setup.py` — semantic-release owns both.
- Keep the entry dict shape and column order in sync with
  `cron_scanner/formatters/base.py:CANONICAL_FIELDS` when touching parser or formatters.
- Preserve quote-aware handling of `;`-separated commands and inline `#` comments in the
  parser (see agent_docs/parsing.md).
- Windows has no `crontab -l`; any change to default input behavior must keep `--file`
  as the supported Windows path.
- No linter/formatter is configured; follow the style of neighboring code and keep
  changes minimal and idiomatic.

## Progressive disclosure

Read the relevant file before working in that area:

- `agent_docs/commands.md` — setup, running, building, smoke-testing
- `agent_docs/architecture.md` — parser/scanner/formatter layers and entry shape
- `agent_docs/parsing.md` — crontab parsing, username detection, `@` macros, time-range
- `agent_docs/formatters.md` — formatter registry, shared helpers, adding a new format
- `agent_docs/release.md` — semantic-release workflow and Dependabot config
