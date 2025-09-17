import json
import os
from typing import List, Dict, Any
from .base import BaseFormatter

class JSONFormatter(BaseFormatter):
    """Formatter for JSON output."""
    
    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format cron entries as JSON.
        
        Args:
            entries: List of cron entries
            output_path: Path to save the JSON file. If None, return as string.
            
        Returns:
            str: JSON content or path to the JSON file
        """
        if output_path:
            output_path = self._ensure_extension(output_path, 'json')
            with open(output_path, 'w') as f:
                json.dump(entries, f, indent=2)
            return output_path
        else:
            return json.dumps(entries, indent=2)
