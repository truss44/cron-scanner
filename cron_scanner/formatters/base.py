from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os

# Canonical column order used across output formats
CANONICAL_FIELDS: List[str] = [
    'schedule',
    'description',
    'command',
    'user',
    'next_run',
    'line_number',
    'line_content',
]

# Shared mapping from data keys to human-readable column labels (for non-JSON outputs)
HEADER_TITLE_MAP: Dict[str, str] = {
    'schedule': 'Schedule',
    'description': 'Description',
    'command': 'Command',
    'user': 'User',
    'next_run': 'Next Run',
    'line_number': 'Line #',
    'line_content': 'Line Content',
}

def get_all_fields(entries: List[Dict[str, Any]]) -> List[str]:
    """
    Build a stable union of field names encountered in entries,
    preferring the canonical ordering.
    """
    all_fields = list(CANONICAL_FIELDS)
    for entry in entries:
        for k in entry.keys():
            if k not in all_fields:
                all_fields.append(k)
    return all_fields

def humanize_headers(fields: List[str]) -> List[str]:
    """Convert data field names into human-readable column labels."""
    return [HEADER_TITLE_MAP.get(f, f.replace('_', ' ').title()) for f in fields]


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
