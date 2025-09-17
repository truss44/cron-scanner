import os
from typing import List, Dict, Any
from .base import BaseFormatter

class XLSXFormatter(BaseFormatter):
    """Formatter for Excel (XLSX) output."""
    
    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format cron entries as an Excel (XLSX) file.
        
        Args:
            entries: List of cron entries
            output_path: Path to save the XLSX file. If None, raises ValueError.
            
        Returns:
            str: Path to the XLSX file
            
        Raises:
            ValueError: If output_path is not provided
        """
        if not output_path:
            raise ValueError("output_path is required for XLSX formatter")
            
        output_path = self._ensure_extension(output_path, 'xlsx')
        
        import pandas as pd
        df = pd.DataFrame(entries)
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        return output_path
