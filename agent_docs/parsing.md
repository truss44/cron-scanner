# Crontab Parsing Rules

Reference: `cron_scanner/parser.py`

## Line handling

- Blank lines and lines starting with `#` are ignored.
- Environment assignments (`NAME=value`) are skipped (see `_looks_like_env`).
- Inline `#` comments after a command are stripped unless inside single/double quotes
  (`_strip_inline_comment`).
- Multiple commands on one line separated by `;` become separate entries; quote and
  backslash escaping is respected (`_split_commands`).

## Username column detection

The parser distinguishes system-style crontabs (with a username column) from user
crontabs:

- `is_system_style` is set `True` when the file path is under `/etc/crontab`,
  `/etc/cron.d`, or `/etc/cron.*`. In that case any token matching
  `^[A-Za-z_][A-Za-z0-9_-]*$` after the 5 schedule fields is treated as the username.
- For user crontabs, the 6th token is only treated as a username if it resolves via
  `pwd.getpwnam` OR the following token looks like a command start
  (`_looks_like_command_start`: paths, common shells/interpreters, or alnum command
  names that are not `VAR=` assignments).
- `@macro` lines may also carry an optional username, detected the same way.

When no username is present, `user` defaults to `getpass.getuser()`.

## `@` macros

`_expand_special` maps:

| macro                  | expression    |
| ---------------------- | ------------- |
| `@yearly`/`@annually`  | `0 0 1 1 *`   |
| `@monthly`             | `0 0 1 * *`   |
| `@weekly`              | `0 0 * * 0`   |
| `@daily`/`@midnight`   | `0 0 * * *`   |
| `@hourly`              | `0 * * * *`   |
| `@reboot`              | `None` (skipped from time-range scans) |

## Time-range matching

`get_entries_in_range` iterates entries, expands `@` macros, and uses
`croniter(expr, start_time - 1min).get_next(datetime)`. Entries whose `next_run <= end_time`
are included and sorted ascending by `next_run`. `start_time`/`end_time` are swapped if
inverted. Either `end_time` or `time_span` must be supplied.

## Datetime / timespan parsing

- `parse_datetime` accepts `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM`, `YYYY-MM-DD HH:MM`.
- `parse_timespan` accepts combined `Nd`/`nh`/`nm` tokens (e.g. `1d2h30m`).
