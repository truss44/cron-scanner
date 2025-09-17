import csv
import os
from typing import List, Dict, Any
from .base import BaseFormatter

class CSVFormatter(BaseFormatter):
    """Formatter for CSV output."""
    
    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format cron entries as CSV.
        
        Args:
            entries: List of cron entries
            output_path: Path to save the CSV file. If None, return as string.
            
        Returns:
            str: CSV content or path to the CSV file
        """
        # Build a stable union of fieldnames across all entries
        default_fields = ['schedule', 'command', 'user', 'next_run', 'line_number', 'line_content']
        fieldnames = list(default_fields)
        for entry in entries:
            for k in entry.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        
        if output_path:
            output_path = self._ensure_extension(output_path, 'csv')
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                if entries:
                    writer.writerows(entries)
            return output_path
        else:
            if not entries:
                return ""
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)
            return output.getvalue()
