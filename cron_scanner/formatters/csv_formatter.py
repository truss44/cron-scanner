import csv
import os
from typing import List, Dict, Any
from .base import BaseFormatter, get_all_fields, humanize_headers

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
        # Build a stable union of fieldnames across all entries using shared helper
        fieldnames = get_all_fields(entries)
        header_labels = humanize_headers(fieldnames)
        
        if output_path:
            output_path = self._ensure_extension(output_path, 'csv')
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Always write header row with human-readable labels
                writer.writerow(header_labels)
                # Write rows in field order
                for entry in entries:
                    writer.writerow([entry.get(field, "") for field in fieldnames])
            return output_path
        else:
            if not entries:
                return ""
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(header_labels)
            for entry in entries:
                writer.writerow([entry.get(field, "") for field in fieldnames])
            return output.getvalue()
