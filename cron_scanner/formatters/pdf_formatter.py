import os
from typing import List, Dict, Any
from .base import BaseFormatter, get_all_fields, humanize_headers
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from xml.sax.saxutils import escape

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
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20,
        )
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        # Table cell style to enable wrapping within column widths
        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['BodyText'],
            fontSize=8,
            leading=10,
            spaceAfter=0,
            spaceBefore=0,
            wordWrap='CJK',
        )
        # Header cell style with wrapping enabled
        header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['BodyText'],
            fontSize=10,
            leading=12,
            spaceAfter=0,
            spaceBefore=0,
            wordWrap='CJK',
            textColor=colors.whitesmoke,
        )
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
            # Build a stable union of field names using shared helper
            all_fields = get_all_fields(entries)
            
            # Create table data
            # Build human-friendly headers and wrap them to avoid overflow into adjacent cells
            display_headers = humanize_headers(all_fields)
            header_row = [Paragraph(escape(h), header_style) for h in display_headers]
            table_data = [header_row]  # Header row
            for entry in entries:
                row = []
                for field in all_fields:
                    raw = entry.get(field, "")
                    text = "" if raw is None else str(raw)
                    row.append(Paragraph(escape(text), cell_style))
                table_data.append(row)
            
            # Calculate column widths to fit page width
            available_width = doc.width
            weight_map = {
                'schedule': 1.5,
                'description': 2.5,
                'command': 3.0,
                'user': 1.0,
                'next_run': 1.5,
                'line_number': 0.8,
                'line_content': 3.0,
            }
            weights = [weight_map.get(field, 1.0) for field in all_fields]
            total_weight = sum(weights) if sum(weights) > 0 else 1.0
            col_widths = [available_width * (w / total_weight) for w in weights]
            
            # Create the table with constrained width and repeated header
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Add style to the table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                # Center-align header labels only
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                # Slightly reduce padding to give text more room within narrow columns
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
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
