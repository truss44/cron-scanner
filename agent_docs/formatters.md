# Output Formatters

Reference: `cron_scanner/formatters/`

All formatters subclass `BaseFormatter` (`base.py`) and implement
`format(entries, output_path=None) -> str` (returns the output path when writing a file).

## Registry

`cron_scanner/scanner.py:FORMATTERS` maps CLI `--format` values to classes:

| `--format` | class               | file ext |
| ---------- | ------------------- | -------- |
| `csv`      | `CSVFormatter`      | `.csv`   |
| `json`     | `JSONFormatter`     | `.json`  |
| `xlsx`     | `XLSXFormatter`     | `.xlsx`  |
| `text`     | `TextFormatter`     | `.txt`   |
| `pdf`      | `PDFFormatter`      | `.pdf`   |
| `md`       | `MarkdownFormatter` | `.md`    |
| `markdown` | `MarkdownFormatter` | `.md`    |

`md` and `markdown` are aliases for the same class.

## Shared helpers (`base.py`)

- `CANONICAL_FIELDS` — stable column order: `schedule, description, command, user,
  next_run, line_number, line_content`.
- `get_all_fields(entries)` — canonical fields first, then any extra keys discovered.
- `humanize_headers(fields)` — maps data keys to display labels via `HEADER_TITLE_MAP`,
  falling back to `Title Case` of the key.
- `BaseFormatter._ensure_extension(path, ext)` — appends the expected extension if missing.

## Adding a new format

1. Create `cron_scanner/formatters/<name>_formatter.py` with a class subclassing
   `BaseFormatter` and implementing `format`.
2. Export it from `cron_scanner/formatters/__init__.py` (`__all__` included).
3. Register the name(s) in `FORMATTERS` in `cron_scanner/scanner.py`.
4. Add the extension to `ext_map` in `scanner.main()` for default output filenames.
5. Add the choice to the README usage section.

Reuse `get_all_fields` / `humanize_headers` so column ordering and labels stay consistent
across formats.
