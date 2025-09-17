# Cron Scanner

A Python tool to scan and analyze crontab entries within a specified time range and export them to various formats.

## Features

- Parse system crontab or a custom crontab file
- Filter cron jobs that would run within a specified time range
- Export results to multiple formats: CSV, JSON, XLSX, Text, Markdown, or PDF
- Easy-to-use command-line interface
- No installation required (runs in a virtual environment)
- Understands system-style crontabs with a username column (e.g. `/etc/crontab`, `/etc/cron.d/*`) and user crontabs
- Supports multiple commands on one line separated by `;` (each command becomes its own entry)
- Ignores blank lines, comments, and environment variable assignments
- Adds a human-readable `description` column for each schedule (like crontab.guru), using 24-hour time format

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

## Installation

1. Clone this repository or download the source code
2. Make the `run.sh` script executable:
   ```bash
   chmod +x run.sh
   ```
3. (Optional) Run the installer to set up the virtual environment:
   ```bash
   ./run.sh --install
   ```

## Usage

### Basic Usage

```bash
# Show help
./run.sh --help

# Scan the default crontab for jobs in the next 24 hours (default)
./run.sh

# Specify a custom crontab file
./run.sh --args="--file /path/to/crontab"

# Specify a custom time range
./run.sh --args="--start-time 2023-01-01 --time-span 7d"

# Export to a specific format
./run.sh --args="--format json --output output.json"
```

### Command-line Arguments

```
usage: cron_scanner.py [-h] [-f FILE] [-s START_TIME] [-e END_TIME] [-t TIME_SPAN]
                      [-o OUTPUT] [-F {csv,json,xlsx,text,pdf,md,markdown}]

Cron Scanner - Scan crontab entries within a specified time range.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to a crontab file (default: read from current user's crontab)
  -s START_TIME, --start-time START_TIME
                        Start time in YYYY-MM-DD[THH:MM] format (default: now)
  -e END_TIME, --end-time END_TIME
                        End time in YYYY-MM-DD[THH:MM] format (mutually exclusive with --time-span)
  -t TIME_SPAN, --time-span TIME_SPAN
                        Time span from start time (e.g., 1d, 2h, 30m, 1h30m) (mutually exclusive with --end-time)
  -o OUTPUT, --output OUTPUT
                        Output file path (default: writes to a timestamped file in the current directory)
  -F {csv,json,xlsx,text,pdf,md,markdown}, --format {csv,json,xlsx,text,pdf,md,markdown}
                        Output format (default: csv)
```

### Time Format

- **Start/End Time**: Use `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM` format
  - Example: `2023-01-01` or `2023-01-01T14:30`

- **Time Span**: Use a combination of days (d), hours (h), and minutes (m)
  - Example: `1d` (1 day), `2h` (2 hours), `30m` (30 minutes), `1h30m` (1 hour and 30 minutes)

### Output Formats

- **CSV** (default): Comma-separated values
- **JSON**: JavaScript Object Notation
- **XLSX**: Microsoft Excel format
- **Text**: Formatted plain text
- **Markdown**: GitHub-flavored Markdown table (`.md`)
- **PDF**: Portable Document Format
  
All formats include a `description` field translating the cron expression into plain English, e.g. `*/15 * * * *` → "Every 15 minutes", `0 18 * * 1-5` → "At 18:00 on Monday through Friday".

## Examples

1. **Basic scan** (next 24 hours, CSV output to a file in the current directory):
   ```bash
   ./run.sh
   ```

2. **Custom time range** (specific date range):
   ```bash
   ./run.sh --args="--start-time 2023-01-01 --end-time 2023-01-08"
   ```

3. **Time span** (next 3 days):
   ```bash
   ./run.sh --args="--time-span 3d"
   ```

4. **Export to JSON**:
   ```bash
   ./run.sh --args="--format json --output cron_jobs.json"
   ```

5. **Export to Excel**:
   ```bash
   ./run.sh --args="--format xlsx --output cron_jobs.xlsx"
   ```

6. **Custom crontab file**:
   ```bash
   ./run.sh --args="--file /path/to/crontab --format text --output cron_jobs.txt"
   ```

7. **Export to Markdown**:
   ```bash
   ./run.sh --args="--format md --output cron_jobs.md"
   ```

## Windows usage (PowerShell)

Cron Scanner includes a PowerShell runner `run.ps1` with feature parity to `run.sh`.

Important:

- Windows does not have `crontab -l`. On Windows, always provide a crontab file via `-File`.
- Example crontab syntax is Unix-style. You can edit or create a file using that syntax and pass it with `-File`.

First-time setup:

```powershell
# Allow running scripts for your user (if needed)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Unblock-File .\run.ps1

# Install dependencies (creates venv if possible; else uses user site-packages)
./run.ps1 -Install
```

Basic run (next 24 hours, default CSV output to a timestamped file):

```powershell
./run.ps1 -File .\sample_crontab_windows.txt
```

Custom time range and formats:

```powershell
# Time span window
./run.ps1 -File .\sample_crontab_windows.txt -TimeSpan 3d -Format text

# Explicit start/end window
./run.ps1 -File .\sample_crontab_windows.txt -StartTime 2025-01-01 -EndTime 2025-01-07 -Format json -Output .\cron_jobs.json

# Excel and PDF outputs
./run.ps1 -File .\sample_crontab_windows.txt -TimeSpan 2d -Format xlsx -Output .\cron_jobs.xlsx
./run.ps1 -File .\sample_crontab_windows.txt -TimeSpan 1d -Format pdf -Output .\cron_jobs.pdf

# Markdown output
./run.ps1 -File .\sample_crontab_windows.txt -TimeSpan 1d -Format md -Output .\cron_jobs.md
```

Maintenance:

```powershell
# Remove the virtual environment
./run.ps1 -Uninstall
```

## Converting Windows Task Scheduler to a crontab-style file

Cron Scanner expects crontab-style timing syntax. On Windows, you can export your Task Scheduler tasks and manually map them to crontab lines. Here’s a practical workflow:

1. Export tasks for reference
   ```powershell
   schtasks /Query /V /FO CSV > tasks.csv
   # or for a single task's detailed XML (shows triggers clearly):
   schtasks /Query /TN "MyTaskName" /XML > MyTask.xml
   ```

2. Determine the schedule
   - Daily at 02:30 → `30 2 * * *`
   - Every 15 minutes → `*/15 * * * *`
   - Weekly on Mon, Wed, Fri at 18:00 → `0 18 * * 1,3,5`
   - Monthly on day 1 at 01:00 → `0 1 1 * *`
   - Hourly → `0 * * * *`

3. Determine the command to run
   - Use the “Task To Run” (older systems) or the action’s “Program/script” + “Add arguments” fields.
   - Example:
     ```
     C:\\Windows\\System32\\cmd.exe /c "C:\\scripts\\report.bat --daily"
     ```

4. Build crontab lines (username is optional; you can omit it):
   - Without username:
     ```
     30 2 * * * C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -File C:\\scripts\\nightly.ps1
     */15 * * * * C:\\Python39\\python.exe C:\\scripts\\telemetry.py --push
     0 18 * * 1,3,5 C:\\Windows\\System32\\cmd.exe /c "C:\\scripts\\report.bat --daily"; C:\\Windows\\System32\\cmd.exe /c "C:\\scripts\\cleanup.bat"
     ```
   - With a username column (system-style format):
     ```
     0 * * * * someuser C:\\Windows\\System32\\cmd.exe /c "C:\\scripts\\hourly.bat"
     ```

5. Save as a text file and pass it with `--file` (Linux/macOS) or `-File` (Windows PowerShell):
   - Windows PowerShell:
     ```powershell
     ./run.ps1 -File .\my_tasks_as_crontab.txt -TimeSpan 7d -Format json -Output .\cron_hits.json
     ```
   - Linux/macOS:
     ```bash
     ./run.sh --args="--file ./my_tasks_as_crontab.txt --time-span 7d --format json --output ./cron_hits.json"
     ```

Tips:
 - Quote paths with spaces in `"double quotes"`.
 - Use `;` between commands on the same line to represent multiple actions at the same scheduled time.
 - Inline comments starting with `#` are supported (ignored) unless inside quotes.
 - If you include a username column, ensure it appears immediately after the 5 time fields.

## Parsing behavior

- Lines beginning with `#` and blank lines are ignored.
- Environment variable assignments like `PATH=/usr/bin` are ignored.
- For system-style files (e.g., `/etc/crontab`, `/etc/cron.d/*`), a username column after the schedule is supported:
  ```
  1 1 * * * username /path/to/your/script.sh
  ```
- Multiple commands on a single line separated by `;` are each treated as separate entries and retain the full command with arguments:
  ```
  1 1 * * * username /path/to/your/script.sh --arg1 foo; /path/to/your/script2.sh -v
  ```
- Inline comments after commands are stripped unless inside quotes.
   ```

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
