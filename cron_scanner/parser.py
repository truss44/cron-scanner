import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from croniter import croniter
from cron_descriptor import get_description as cron_get_description, Options as CronOptions
import getpass
import subprocess
import shutil

try:
    import pwd  # type: ignore
except Exception:  # pragma: no cover - not available on non-Unix platforms
    pwd = None

class CronParser:
    """Parser for crontab entries."""
    
    def __init__(self, crontab_content: str = None, filename: str = None):
        """
        Initialize the CronParser.
        
        Args:
            crontab_content: Raw crontab content as a string
            filename: Path to a crontab file
        """
        self.crontab_content = crontab_content
        self.filename = filename
        self.entries = []
        self.is_system_style = False  # Heuristic: cron files that include a username column
        
        if self.filename and os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.crontab_content = f.read()
            # Heuristic: files under /etc typically require a username column
            path = os.path.abspath(self.filename)
            if path.startswith('/etc/cron.') or '/etc/cron.d' in path or path == '/etc/crontab':
                self.is_system_style = True
        
        if not self.crontab_content and not self.filename:
            # Try to read the current user's crontab via the system crontab utility
            if shutil.which('crontab') is None:
                raise ValueError("No crontab content or filename provided and 'crontab' command not found")
            try:
                out = subprocess.check_output(['crontab', '-l'], stderr=subprocess.STDOUT, text=True)
                self.crontab_content = out
            except subprocess.CalledProcessError as e:
                raise ValueError("Failed to read user's crontab via 'crontab -l'")
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the crontab content into a list of cron entries.
        
        Returns:
            List[Dict[str, Any]]: List of parsed cron entries
        """
        if not self.crontab_content:
            return []
            
        self.entries = []
        
        # Parse each line in the crontab
        for line_num, line in enumerate(self.crontab_content.split('\n'), 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Try to parse the line as a cron job
            try:
                # Handle special cases like @reboot, @hourly, etc.
                if line.startswith('@'):
                    schedule, full_command = self._parse_special(line)
                    user = None
                    # @macro lines may include a username
                    if full_command:
                        # Split into first two tokens to test for username + command
                        parts_after = re.split(r'\s+', full_command, maxsplit=2)
                        if parts_after:
                            candidate_user = parts_after[0]
                            next_token = parts_after[1] if len(parts_after) > 1 else ''
                            if self._seems_username_column(candidate_user, next_token):
                                user = candidate_user
                                full_command = parts_after[2] if len(parts_after) > 2 else ''
                else:
                    # Parse standard cron line (min hour dom month dow [username] command)
                    tokens = re.split(r'\s+', line.strip())
                    if len(tokens) < 6:
                        # Might be an env var line like PATH=/usr/bin
                        if self._looks_like_env(line):
                            continue
                        else:
                            continue  # Not a valid cron line
                    minute, hour, dom, month, dow = tokens[0:5]
                    schedule = f"{minute} {hour} {dom} {month} {dow}"

                    user = None
                    # Determine if there's a username column
                    if len(tokens) >= 7:
                        candidate_user = tokens[5]
                        next_token = tokens[6]
                        if self._seems_username_column(candidate_user, next_token):
                            user = candidate_user
                            # Reconstruct command as the remainder of the line after the 6th token
                            full_command = self._remainder_after_tokens(line, 6)
                        else:
                            # No username; command starts after 5 schedule tokens
                            full_command = self._remainder_after_tokens(line, 5)
                    else:
                        # No username column expected; command starts after 5 schedule tokens
                        full_command = self._remainder_after_tokens(line, 5)

                # Strip inline comments not within quotes
                full_command = self._strip_inline_comment(full_command).strip()

                # Split by semicolons into separate commands, respecting quotes
                commands = self._split_commands(full_command)

                for cmd in commands:
                    cmd_clean = cmd.strip()
                    if not cmd_clean:
                        continue
                    # Create a cron entry
                    entry = {
                        'schedule': schedule,
                        'description': self._describe_schedule(schedule),
                        'command': cmd_clean,
                        'user': user if user else self._current_user(),
                        'line_number': line_num,
                        'line_content': line,
                    }
                    self.entries.append(entry)
                
            except Exception as e:
                # Skip lines that can't be parsed
                continue
                
        return self.entries
    
    def _parse_special(self, line: str) -> Tuple[str, str]:
        """
        Parse a special cron line (e.g., @reboot, @hourly).
        
        Args:
            line: The special cron line
            
        Returns:
            Tuple[str, str]: (schedule, command)
        """
        parts = line.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError("Invalid special cron line")
            
        special, command = parts
        return special, command
    
    def _looks_like_env(self, line: str) -> bool:
        """Return True if the line appears to be an environment variable assignment."""
        return re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*=\s*.*$', line) is not None

    def _is_valid_username(self, token: str) -> bool:
        """Check if a token is a valid system username (best-effort)."""
        # If we heuristically know it's a system-style file and there are enough tokens, assume username
        if self.is_system_style:
            try:
                if pwd is not None:
                    pwd.getpwnam(token)  # type: ignore
                # If pwd is None (non-Unix), accept alnum/underscore/hyphen pattern
                else:
                    if not re.match(r'^[A-Za-z_][A-Za-z0-9_-]*$', token):
                        return False
                return True
            except Exception:
                # Fall back to pattern check
                return re.match(r'^[A-Za-z_][A-Za-z0-9_-]*$', token) is not None
        # For user crontabs, only treat as username if it actually exists (avoids misclassification)
        try:
            if pwd is not None:
                pwd.getpwnam(token)  # type: ignore
                return True
        except Exception:
            pass
        return False

    def _looks_like_command_start(self, token: str) -> bool:
        """Heuristic to determine if a token looks like the start of a command/binary/path."""
        if not token:
            return False
        if token.startswith('/') or token.startswith('./') or token.startswith('~/'):
            return True
        # Common shells/commands
        if token in {'sh', 'bash', 'zsh', 'python', 'python3', 'ruby', 'node', 'perl'}:
            return True
        # Looks like an assignment? Then not a command start
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', token):
            return False
        # Alphanumeric with typical command chars
        return re.match(r'^[A-Za-z0-9_.\-]+$', token) is not None

    def _seems_username_column(self, user_token: str, next_token: str) -> bool:
        """Decide if user_token is a username column by combining validity and next token check."""
        pattern_ok = re.match(r'^[A-Za-z_][A-Za-z0-9_-]*$', user_token) is not None
        if not pattern_ok:
            return False
        # If it's a system-style file, be liberal: accept username-looking token
        if self.is_system_style:
            return True
        # Otherwise, accept if it's a real user OR the next token looks like a command
        if self._is_valid_username(user_token):
            return True
        return self._looks_like_command_start(next_token)

    def _remainder_after_tokens(self, line: str, token_count: int) -> str:
        """Return the remainder of the line after the first token_count whitespace-separated tokens."""
        # Use regex to capture the remainder to preserve original spacing/args
        pattern = r'^\s*(?:\S+\s+){' + str(token_count) + r'}(.*)$'
        m = re.match(pattern, line)
        return m.group(1) if m else ''

    def _strip_inline_comment(self, s: str) -> str:
        """Strip inline comments starting with #, respecting quotes."""
        out = []
        in_single = False
        in_double = False
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == "'" and not in_double:
                in_single = not in_single
                out.append(ch)
            elif ch == '"' and not in_single:
                in_double = not in_double
                out.append(ch)
            elif ch == '#' and not in_single and not in_double:
                break  # comment starts here
            else:
                out.append(ch)
            i += 1
        return ''.join(out)

    def _split_commands(self, s: str) -> List[str]:
        """Split a command string by semicolons not inside quotes (and not escaped)."""
        parts: List[str] = []
        buf: List[str] = []
        in_single = False
        in_double = False
        escape = False
        for ch in s:
            if escape:
                buf.append(ch)
                escape = False
                continue
            if ch == '\\':
                buf.append(ch)
                escape = True
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
                buf.append(ch)
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                buf.append(ch)
                continue
            if ch == ';' and not in_single and not in_double:
                parts.append(''.join(buf).strip())
                buf = []
                continue
            buf.append(ch)
        if buf:
            parts.append(''.join(buf).strip())
        return parts

    def _current_user(self) -> Optional[str]:
        try:
            return getpass.getuser()
        except Exception:
            return None
    
    def get_entries_in_range(self, 
                           start_time: datetime, 
                           end_time: Optional[datetime] = None,
                           time_span: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """
        Get cron entries that would run within a specified time range.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range (optional if time_span is provided)
            time_span: Time span from start_time (optional if end_time is provided)
            
        Returns:
            List[Dict[str, Any]]: List of cron entries that would run in the specified range
        """
        if not self.entries:
            self.parse()
            
        if end_time is None and time_span is not None:
            end_time = start_time + time_span
        elif end_time is None:
            raise ValueError("Either end_time or time_span must be provided")
            
        if start_time > end_time:
            start_time, end_time = end_time, start_time
            
        result = []
        
        for entry in self.entries:
            schedule = entry['schedule']

            # Expand special schedules; skip @reboot which has no time schedule
            if schedule.startswith('@'):
                expanded = self._expand_special(schedule)
                if expanded is None:
                    # e.g., @reboot
                    continue
                expr = expanded
            else:
                expr = schedule

            try:
                # Compute the next run time inclusively from start_time
                base = start_time - timedelta(minutes=1)
                it = croniter(expr, base)
                next_time = it.get_next(datetime)

                # Check if the next scheduled time is within our range
                if next_time <= end_time:
                    # Add the next scheduled time to the entry
                    entry_with_time = entry.copy()
                    entry_with_time['next_run'] = next_time.isoformat()
                    result.append(entry_with_time)
            except Exception:
                # Skip entries that can't be parsed
                continue
                
        # Sort by next run time
        result.sort(key=lambda x: x.get('next_run', ''))
        
        return result

    def _expand_special(self, special: str) -> Optional[str]:
        """Expand @ macros to standard 5-field expressions. Return None for non-time-based macros."""
        mapping = {
            '@yearly': '0 0 1 1 *',
            '@annually': '0 0 1 1 *',
            '@monthly': '0 0 1 * *',
            '@weekly': '0 0 * * 0',
            '@daily': '0 0 * * *',
            '@midnight': '0 0 * * *',
            '@hourly': '0 * * * *',
        }
        if special == '@reboot':
            return None
        return mapping.get(special, special)

    def _describe_schedule(self, schedule: str) -> str:
        """Return a human-readable description of a cron schedule.

        Uses cron-descriptor with 24-hour time format. Supports @macros; returns a
        friendly phrase for @reboot. Falls back to the raw schedule on error.
        """
        try:
            # Expand @macros except @reboot
            if schedule.startswith('@'):
                expanded = self._expand_special(schedule)
                if expanded is None:
                    return 'At reboot'
                expr = expanded
            else:
                expr = schedule

            options = CronOptions()
            options.use_24hour_time_format = True
            return cron_get_description(expr, options)
        except Exception:
            # Fallback to the schedule string if description cannot be generated
            return schedule
