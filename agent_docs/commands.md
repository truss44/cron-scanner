# Development Commands

## Environment

```bash
# First-time setup (creates ./venv and installs requirements)
./run.sh --install

# Windows PowerShell equivalent
./run.ps1 -Install
```

## Running the scanner

```bash
# Default: scan current user's crontab for next 24h, CSV to timestamped file
./run.sh

# Pass arguments through to cron_scanner
./run.sh --args="--file ./sample_crontab.txt --time-span 7d --format json --output out.json"

# Run the module directly (inside venv)
python -m cron_scanner.scanner --file ./sample_crontab.txt --format md --output out.md

# Installed console script
cron-scanner --help
```

## Testing

No formal test suite is present. To smoke-test changes:

```bash
# Parse + scan the sample crontab and dump JSON
./run.sh --args="--file ./sample_crontab.txt --time-span 1d --format json --output /tmp/out.json"
# Then inspect /tmp/out.json for expected entries and descriptions.
```

When adding behavior, add a focused script under a scratch path (do not commit ad-hoc
test files) or add a proper `tests/` package with `pytest` before introducing regressions.

## Building / packaging

```bash
python -m pip install --upgrade pip build
python -m build --sdist --wheel .
```

Releases are automated via semantic-release (see release.md); do not bump version numbers
manually in `cron_scanner/__init__.py` or `setup.py`.
