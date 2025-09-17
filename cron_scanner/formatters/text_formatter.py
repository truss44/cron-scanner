import os
from typing import List, Dict, Any
from .base import BaseFormatter, get_all_fields, humanize_headers

class TextFormatter(BaseFormatter):
    """Formatter for plain text output."""
    
    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format cron entries as plain text.
        
        Args:
            entries: List of cron entries
            output_path: Path to save the text file. If None, return as string.
            
        Returns:
            str: Formatted text or path to the text file
        """
        if not entries:
            return ""
            
        # Use shared canonical union for consistent ordering
        all_fields = get_all_fields(entries)
        header_labels = humanize_headers(all_fields)
        
        # Find the maximum width for each column considering header labels and values
        field_widths: Dict[str, int] = {}
        for idx, field in enumerate(all_fields):
            max_len = len(str(header_labels[idx]))
            for entry in entries:
                if field in entry:
                    max_len = max(max_len, len(str(entry[field])))
            field_widths[field] = max_len + 2  # Add some padding
            
        # Build the format string
        format_str = "".join(
            f"{{:<{field_widths[field]}.{field_widths[field]-2}}}" for field in all_fields
        )
        
        # Build the output
        output = []
        # Header (human-readable labels)
        output.append(format_str.format(*header_labels))
        # Separator
        output.append("-" * sum(field_widths.values()))
        
        # Rows
        for entry in entries:
            row = []
            for field in all_fields:
                row.append(str(entry.get(field, "")))
            output.append(format_str.format(*row))
        
        result = "\n".join(output)
        
        if output_path:
            output_path = self._ensure_extension(output_path, 'txt')
            with open(output_path, 'w') as f:
                f.write(result)
            return output_path
        else:
            return result
