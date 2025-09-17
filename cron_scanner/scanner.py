#!/usr/bin/env python3
"""
Cron Scanner - A tool to scan and analyze crontab entries within a specified time range.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Type
from .parser import CronParser
from .formatters import (
    CSVFormatter, JSONFormatter, XLSXFormatter, TextFormatter, PDFFormatter, MarkdownFormatter
)
from . import __version__ as APP_VERSION

# Map of format names to formatter classes
FORMATTERS = {
    'csv': CSVFormatter,
    'json': JSONFormatter,
    'xlsx': XLSXFormatter,
    'text': TextFormatter,
    'pdf': PDFFormatter,
    'md': MarkdownFormatter,
    'markdown': MarkdownFormatter
}

class CronScanner:
    """Main class for the Cron Scanner application."""
    
    def __init__(self, crontab_content: str = None, filename: str = None):
        """
        Initialize the CronScanner.
        
        Args:
            crontab_content: Raw crontab content as a string
            filename: Path to a crontab file
        """
        self.parser = CronParser(crontab_content, filename)
        self.formatters = {name: formatter() for name, formatter in FORMATTERS.items()}
    
    def scan(self, 
            start_time: datetime,
            end_time: Optional[datetime] = None,
            time_span: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """
        Scan the crontab for entries that would run within the specified time range.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range (optional if time_span is provided)
            time_span: Time span from start_time (optional if end_time is provided)
            
        Returns:
            List[Dict[str, Any]]: List of cron entries that would run in the specified range
        """
        return self.parser.get_entries_in_range(start_time, end_time, time_span)
    
    def export(self, 
              entries: List[Dict[str, Any]], 
              output_format: str = 'csv',
              output_file: Optional[str] = None) -> str:
        """
        Export the cron entries in the specified format.
        
        Args:
            entries: List of cron entries to export
            output_format: Output format (csv, json, xlsx, text, pdf, md, markdown)
            output_file: Path to the output file (optional)
            
        Returns:
            str: The exported content or path to the output file
            
        Raises:
            ValueError: If the output format is not supported
        """
        if output_format not in self.formatters:
            raise ValueError(f"Unsupported output format: {output_format}. "
                           f"Available formats: {', '.join(self.formatters.keys())}")
        
        formatter = self.formatters[output_format]
        return formatter.format(entries, output_file)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Cron Scanner - Scan crontab entries within a specified time range.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input options
    input_group = parser.add_argument_group('Input Options')
    input_group.add_argument(
        '-f', '--file',
        help='Path to a crontab file (default: read from current user\'s crontab)'
    )
    
    # Time range options
    time_group = parser.add_argument_group('Time Range Options')
    time_group.add_argument(
        '-s', '--start-time',
        help='Start time in YYYY-MM-DD[THH:MM] format (default: now)'
    )
    time_group.add_argument(
        '-e', '--end-time',
        help='End time in YYYY-MM-DD[THH:MM] format (mutually exclusive with --time-span)'
    )
    time_group.add_argument(
        '-t', '--time-span',
        help='Time span from start time (e.g., 1d, 2h, 30m, 1h30m) (mutually exclusive with --end-time)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '-o', '--output',
        help='Output file path (default: writes to a timestamped file in the current directory)'
    )
    output_group.add_argument(
        '-F', '--format',
        choices=FORMATTERS.keys(),
        default='csv',
        help='Output format'
    )
    
    # Other options
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {APP_VERSION}'
    )
    
    return parser.parse_args()

def parse_datetime(dt_str: str) -> datetime:
    """Parse a datetime string in YYYY-MM-DD[THH:MM] format."""
    formats = [
        '%Y-%m-%dT%H:%M',  # YYYY-MM-DDTHH:MM
        '%Y-%m-%d %H:%M',  # YYYY-MM-DD HH:MM
        '%Y-%m-%d',        # YYYY-MM-DD
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Invalid datetime format: {dt_str}")

def parse_timespan(span_str: str) -> timedelta:
    """Parse a time span string (e.g., 1d, 2h, 30m, 1h30m)."""
    if not span_str:
        raise ValueError("Empty time span")
    
    # Match all numbers followed by their units
    import re
    pattern = r'(\d+)([dhm])'
    matches = re.findall(pattern, span_str)
    
    if not matches:
        raise ValueError(f"Invalid time span format: {span_str}")
    
    delta = timedelta()
    
    for value, unit in matches:
        value = int(value)
        if unit == 'd':
            delta += timedelta(days=value)
        elif unit == 'h':
            delta += timedelta(hours=value)
        elif unit == 'm':
            delta += timedelta(minutes=value)
    
    return delta

def main():
    """Main entry point for the Cron Scanner."""
    try:
        args = parse_args()
        
        # Set up time range
        start_time = datetime.now()
        if args.start_time:
            start_time = parse_datetime(args.start_time)
        
        end_time = None
        time_span = None
        
        if args.end_time and args.time_span:
            print("Error: Cannot specify both --end-time and --time-span", file=sys.stderr)
            return 1
        elif args.end_time:
            end_time = parse_datetime(args.end_time)
        elif args.time_span:
            time_span = parse_timespan(args.time_span)
        else:
            # Default to 24 hours if no end time or time span is provided
            time_span = timedelta(days=1)
        
        # Initialize the scanner
        scanner = CronScanner(filename=args.file)
        
        # Scan for entries in the specified time range
        entries = scanner.scan(start_time, end_time, time_span)
        
        # Determine output path
        output_path = args.output
        if output_path is None:
            # Default to writing a file in the current working directory
            ext_map = {'csv': 'csv', 'json': 'json', 'xlsx': 'xlsx', 'text': 'txt', 'pdf': 'pdf', 'md': 'md', 'markdown': 'md'}
            ext = ext_map.get(args.format, args.format)
            # Create a descriptive filename based on the time window
            end_time_effective = end_time if end_time is not None else (start_time + time_span)
            start_str = start_time.strftime('%Y%m%d_%H%M')
            end_str = end_time_effective.strftime('%Y%m%d_%H%M')
            output_path = os.path.join(os.getcwd(), f'cron_scan_{start_str}_to_{end_str}.{ext}')

        # Export the results (always to a file by default)
        exported = scanner.export(
            entries=entries,
            output_format=args.format,
            output_file=output_path
        )

        # If export returned content (for formats that allow stdout), and user explicitly
        # asked for no output file, print it. Otherwise, inform where we wrote the file.
        if args.output is None or args.output:
            print(f'Output written to: {exported}')
            
        print(f"Found {len(entries)} cron jobs scheduled in the specified time range.", file=sys.stderr)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if '--help' not in sys.argv and '-h' not in sys.argv:
            print("\nUse --help for usage information.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    from . import __version__
    sys.exit(main())
