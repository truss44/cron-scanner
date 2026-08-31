# Architecture Overview

Cron Scanner is a small Python 3.9+ CLI with three layers:

1. **Parser** (`cron_scanner/parser.py`) — `CronParser`
   - Reads a crontab from a file, raw string, or `crontab -l`.
   - Tokenizes each line into `schedule + [user] + command`, splits `;`-separated
     commands, strips inline comments (quote-aware), and produces entry dicts.
   - Expands `@` macros and computes next-run times with `croniter`.
   - Generates a human-readable `description` via `cron-descriptor` (24-hour format).

2. **Scanner** (`cron_scanner/scanner.py`) — `CronScanner`
   - Owns a `CronParser` and a registry of formatter instances.
   - `scan(start_time, end_time|time_span)` returns entries whose next run falls in range,
     sorted by `next_run`.
   - `export(entries, output_format, output_file)` dispatches to the matching formatter.
   - `main()` / `parse_args()` / `parse_datetime()` / `parse_timespan()` form the CLI.

3. **Formatters** (`cron_scanner/formatters/`) — one module per output format, all
   subclassing `BaseFormatter`. See formatters.md.

## Entry shape

Every entry produced by the parser is a dict with these keys (canonical order defined in
`cron_scanner/formatters/base.py:CANONICAL_FIELDS`):

| key           | meaning                                              |
| ------------- | ---------------------------------------------------- |
| `schedule`    | Raw 5-field expression or `@macro`                   |
| `description` | Human-readable schedule (cron-descriptor, 24h)       |
| `command`     | A single command (one per `;`-split segment)         |
| `user`        | Username column if system-style, else current user   |
| `next_run`    | ISO datetime of the next firing within range (scan)  |
| `line_number` | 1-based source line                                  |
| `line_content`| Original (stripped) source line                      |

## Runners

- `run.sh` (POSIX) and `run.ps1` (Windows PowerShell) wrap venv setup and forward args
  to `cron_scanner.scanner:main` via `--args="..."` / `-Args`.
- Windows has no `crontab -l`; users must pass `--file` / `-File`.
