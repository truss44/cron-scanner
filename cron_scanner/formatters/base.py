from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os

class BaseFormatter(ABC):
    """Base class for all formatters."""
    
    @abstractmethod
    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format the cron entries.
        
        Args:
            entries: List of cron entries to format
            output_path: Path to save the formatted output. If None, return as string.
            
        Returns:
            str: Formatted output or path to the output file
        """
        pass
    
    def _ensure_extension(self, path: str, extension: str) -> str:
        """Ensure the output path has the correct extension."""
        if not path.endswith(f".{extension}"):
            if not path.endswith('.'):
                path += '.'
            path += extension
        return path
