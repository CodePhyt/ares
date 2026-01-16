"""
Professional PDF export with ARES watermark and audit reports.
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from PIL import Image as PILImage
import io
from loguru import logger


class ARESPDFExporter:
    """Export audit reports and query results as professional PDFs."""

    def __init__(self):
        """Initialize PDF exporter."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="ARESTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1a2332"),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # Subtitle style
        self.styles.add(
            ParagraphStyle(
                name="ARESSubtitle",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#475569"),
                spaceAfter=20,
                fontName="Helvetica-Bold",
            )
        )

        # Body style
        self.styles.add(
            ParagraphStyle(
                name="ARESBody",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#334155"),
                leading=14,
                fontName="Helvetica",
            )
        )

        # Citation style
        self.styles.add(
            ParagraphStyle(
                name="ARESCitation",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#64748b"),
                leftIndent=20,
                fontName="Helvetica-Oblique",
            )
        )

    def _draw_watermark(self, canvas_obj, doc):
        """Draw ARES watermark on every page."""
        canvas_obj.saveState()
        
        # Set watermark properties
        canvas_obj.setFillColor(colors.HexColor("#e2e8f0"), alpha=0.1)
        canvas_obj.setFont("Helvetica-Bold", 60)
        canvas_obj.rotate(45)
        
        # Draw watermark text
        canvas_obj.drawCentredString(
            A4[0] / 2,
            A4[1] / 2,
            "ARES"
        )
        
        canvas_obj.restoreState()

    def export_audit_report(
        self,
        output_path: str,
        query: str,
        answer: str,
        citations: List[Dict[str, Any]],
        confidence: float,
        pii_count: int,
        metadata: Dict[str, Any],
    ) -> str:
        """
        Export audit report as PDF.

        Args:
            output_path: Path to save PDF
            query: Original query
            answer: Generated answer
            citations: Source citations
            confidence: Confidence score
            pii_count: Number of PII entities masked
            metadata: Additional metadata

        Returns:
            Path to saved PDF
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            story = []

            # Title
            story.append(Paragraph("ARES Audit Report", self.styles["ARESTitle"]))
            story.append(Spacer(1, 0.2 * inch))

            # Report metadata
            report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"<b>Report Date:</b> {report_date}", self.styles["ARESBody"]))
            story.append(Paragraph(f"<b>Version:</b> ARES v1.0.0", self.styles["ARESBody"]))
            story.append(Spacer(1, 0.3 * inch))

            # Query section
            story.append(Paragraph("Query", self.styles["ARESSubtitle"]))
            story.append(Paragraph(query, self.styles["ARESBody"]))
            story.append(Spacer(1, 0.2 * inch))

            # Answer section
            story.append(Paragraph("Generated Answer", self.styles["ARESSubtitle"]))
            story.append(Paragraph(answer, self.styles["ARESBody"]))
            story.append(Spacer(1, 0.2 * inch))

            # Metrics table
            metrics_data = [
                ["Metric", "Value"],
                ["Confidence Score", f"{confidence:.2%}"],
                ["PII Entities Masked", str(pii_count)],
                ["Number of Sources", str(len(citations))],
                ["Iterations", str(metadata.get("iterations", 0))],
            ]

            metrics_table = Table(metrics_data, colWidths=[3 * inch, 2 * inch])
            metrics_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2332")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ]
                )
            )
            story.append(metrics_table)
            story.append(Spacer(1, 0.3 * inch))

            # Citations section
            if citations:
                story.append(Paragraph("Source Citations", self.styles["ARESSubtitle"]))
                for i, citation in enumerate(citations, 1):
                    filename = citation.get("filename", "Unknown")
                    page = citation.get("page", "N/A")
                    score = citation.get("score", 0.0)
                    
                    citation_text = f"[{i}] {filename} (Page: {page}, Relevance: {score:.2f})"
                    story.append(Paragraph(citation_text, self.styles["ARESCitation"]))
                    story.append(Spacer(1, 0.1 * inch))

            # Footer
            story.append(PageBreak())
            story.append(Spacer(1, 0.5 * inch))
            story.append(
                Paragraph(
                    "<i>This report was generated by ARES - Autonomous Resilient Enterprise Suite</i>",
                    self.styles["ARESBody"],
                )
            )
            story.append(
                Paragraph(
                    "<i>GDPR-Compliant | 100% Offline | Privacy-First</i>",
                    self.styles["ARESBody"],
                )
            )

            # Build PDF with watermark
            doc.build(story, onFirstPage=self._draw_watermark, onLaterPages=self._draw_watermark)

            logger.info("PDF audit report exported: {}", output_path)
            return output_path

        except Exception as e:
            logger.error("Error exporting PDF: {}", e)
            raise
