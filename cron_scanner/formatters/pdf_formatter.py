import os
from typing import List, Dict, Any
from .base import BaseFormatter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFFormatter(BaseFormatter):
    """Formatter for PDF output."""
    
    def format(self, entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Format cron entries as a PDF file.
        
        Args:
            entries: List of cron entries
            output_path: Path to save the PDF file. If None, raises ValueError.
            
        Returns:
            str: Path to the PDF file
            
        Raises:
            ValueError: If output_path is not provided
        """
        if not output_path:
            raise ValueError("output_path is required for PDF formatter")
            
        output_path = self._ensure_extension(output_path, 'pdf')
        
        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=landscape(A4))
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20
        )
        title = Paragraph("Cron Job Report", title_style)
        elements.append(title)
        
        if not entries:
            elements.append(Paragraph("No cron entries found.", styles['Normal']))
            doc.build(elements)
            return output_path
            
        # Prepare data for table
        if entries:
            # Build a stable union of field names, preferring canonical ordering
            canonical = ['schedule', 'description', 'command', 'user', 'next_run', 'line_number', 'line_content']
            all_fields = list(canonical)
            for entry in entries:
                for k in entry.keys():
                    if k not in all_fields:
                        all_fields.append(k)
            
            # Create table data
            table_data = [all_fields]  # Header row
            for entry in entries:
                row = [str(entry.get(field, "")) for field in all_fields]
                table_data.append(row)
            
            # Create the table
            table = Table(table_data)
            
            # Add style to the table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ])
            
            # Alternate row colors
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    bg_color = colors.lightgrey
                else:
                    bg_color = colors.white
                style.add('BACKGROUND', (0, i), (-1, i), bg_color)
            
            table.setStyle(style)
            elements.append(table)
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
