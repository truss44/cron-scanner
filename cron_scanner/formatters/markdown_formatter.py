import os
from typing import List, Dict, Any
from .base import BaseFormatter


def _escape_md(text: str) -> str:
    """Escape Markdown table special chars and normalize newlines."""
    if text is None:
        return ""
    s = str(text)
    # Escape pipe and backslash
    s = s.replace("\\", "\\\\").replace("|", "\\|")
    # Normalize newlines to <br> so tables stay intact
    s = s.replace("\r\n", "<br>").replace("\n", "<br>")
    return s


class MarkdownFormatter(BaseFormatter):
    """Formatter for Markdown (.md) table output."""

    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format cron entries as a Markdown table.

        Args:
            entries: List of cron entries
            output_path: Path to save the .md file. If None, return as string.

        Returns:
            str: Markdown content or path to the .md file
        """
        # Build a stable union of field names, preferring canonical ordering
        canonical = ['schedule', 'description', 'command', 'user', 'next_run', 'line_number', 'line_content']
        all_fields = list(canonical)
        for entry in entries:
            for k in entry.keys():
                if k not in all_fields:
                    all_fields.append(k)

        if not entries and output_path is None:
            # Match CSV/Text behavior: return empty when no entries and no file is requested
            return ""

        # Header
        header = "| " + " | ".join(all_fields) + " |"
        separator = "| " + " | ".join(["---"] * len(all_fields)) + " |"

        # Rows
        rows: List[str] = []
        for entry in entries:
            row_vals = [_escape_md(entry.get(field, "")) for field in all_fields]
            rows.append("| " + " | ".join(row_vals) + " |")

        content = "\n".join([header, separator] + rows)

        if output_path:
            output_path = self._ensure_extension(output_path, 'md')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        else:
            return content
