import os
from typing import List, Dict, Any
from .base import BaseFormatter

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
            
        # Use stable column order from the first entry, and append any new fields encountered later
        all_fields: List[str] = list(entries[0].keys())
        for entry in entries[1:]:
            for k in entry.keys():
                if k not in all_fields:
                    all_fields.append(k)
        
        # Find the maximum width for each field for nice alignment
        field_widths = {}
        for field in all_fields:
            max_len = len(str(field))
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
        # Header
        output.append(format_str.format(*all_fields))
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
