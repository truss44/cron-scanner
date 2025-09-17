import os
from typing import List, Dict, Any
from .base import BaseFormatter, get_all_fields, humanize_headers


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
        # Build a stable union of field names using shared helper
        all_fields = get_all_fields(entries)

        if not entries and output_path is None:
            # Match CSV/Text behavior: return empty when no entries and no file is requested
            return ""

        # Header (human-readable labels for non-JSON formats)
        header_labels = humanize_headers(all_fields)
        header_labels_esc = [_escape_md(h) for h in header_labels]
        header = "| " + " | ".join(header_labels_esc) + " |"
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
