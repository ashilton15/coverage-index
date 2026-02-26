"""PDF Report Generation for Coverage Index using ReportLab."""

from __future__ import annotations

import os
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Circle, Rect


# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * inch

# Colors
BLACK = colors.HexColor("#000000")
WHITE = colors.HexColor("#FFFFFF")
LIGHT_GRAY = colors.HexColor("#F5F5F5")
MEDIUM_GRAY = colors.HexColor("#666666")
DARK_GRAY = colors.HexColor("#333333")

# Traffic light colors
GREEN = colors.HexColor("#10B981")
YELLOW = colors.HexColor("#F59E0B")
RED = colors.HexColor("#EF4444")


def get_traffic_light_color(grade: str) -> colors.Color:
    """Return traffic light color based on letter grade."""
    if not grade or grade == "N/A":
        return MEDIUM_GRAY
    grade_upper = grade.upper().replace("+", "").replace("-", "")
    if grade_upper in ["A", "B"]:
        return GREEN
    elif grade_upper == "C":
        return YELLOW
    else:  # D, F
        return RED


def hex_to_reportlab_color(hex_color: str) -> colors.Color:
    """Convert hex color string to ReportLab color."""
    if not hex_color:
        return BLACK
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        return colors.HexColor(f"#{hex_color}")
    return BLACK


class CoverageReportPDF:
    """Generate PDF coverage report."""

    def __init__(
        self,
        client_name: str,
        campaign_name: str,
        results: list,
        accent_color: str = "#000000",
        logo_path: str = None,
    ):
        self.client_name = client_name
        self.campaign_name = campaign_name
        self.results = results
        self.accent_color = hex_to_reportlab_color(accent_color)
        self.logo_path = logo_path

        # Calculate metrics
        self._calculate_metrics()

        # Setup styles
        self._setup_styles()

    def _calculate_metrics(self):
        """Calculate aggregate metrics from results."""
        successful_results = [r for r in self.results if r.get("scores", {}).get("success")]

        self.article_count = len(successful_results)

        # Average score
        if successful_results:
            total = sum(r["scores"].get("total_score", 0) for r in successful_results)
            self.avg_score = round(total / len(successful_results), 1)
        else:
            self.avg_score = 0

        # Score distribution by grade band
        self.score_distribution = {
            "A": 0,  # 90-100
            "B": 0,  # 80-89
            "C": 0,  # 70-79
            "D": 0,  # 60-69
            "F": 0,  # below 60
        }

        for r in successful_results:
            score = r["scores"].get("total_score", 0)
            if score >= 90:
                self.score_distribution["A"] += 1
            elif score >= 80:
                self.score_distribution["B"] += 1
            elif score >= 70:
                self.score_distribution["C"] += 1
            elif score >= 60:
                self.score_distribution["D"] += 1
            else:
                self.score_distribution["F"] += 1

    def _setup_styles(self):
        """Setup paragraph styles."""
        self.styles = getSampleStyleSheet()

        # Title page styles
        self.styles.add(ParagraphStyle(
            name='ClientName',
            fontName='Helvetica-Bold',
            fontSize=42,
            leading=50,
            textColor=BLACK,
            alignment=TA_LEFT,
        ))

        self.styles.add(ParagraphStyle(
            name='CampaignName',
            fontName='Helvetica',
            fontSize=24,
            leading=30,
            textColor=DARK_GRAY,
            alignment=TA_LEFT,
        ))

        self.styles.add(ParagraphStyle(
            name='DateRange',
            fontName='Helvetica',
            fontSize=14,
            leading=18,
            textColor=MEDIUM_GRAY,
            alignment=TA_LEFT,
        ))

        # Overview page styles
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=28,
            leading=34,
            textColor=BLACK,
            alignment=TA_LEFT,
            spaceAfter=20,
        ))

        self.styles.add(ParagraphStyle(
            name='BigScore',
            fontName='Helvetica-Bold',
            fontSize=72,
            leading=80,
            textColor=BLACK,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name='ScoreLabel',
            fontName='Helvetica',
            fontSize=14,
            leading=18,
            textColor=MEDIUM_GRAY,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name='StatNumber',
            fontName='Helvetica-Bold',
            fontSize=36,
            leading=42,
            textColor=BLACK,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name='StatLabel',
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=MEDIUM_GRAY,
            alignment=TA_CENTER,
        ))

        # Article listing styles
        self.styles.add(ParagraphStyle(
            name='ArticleHeadline',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=BLACK,
            alignment=TA_LEFT,
        ))

        self.styles.add(ParagraphStyle(
            name='ArticleOutlet',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=MEDIUM_GRAY,
            alignment=TA_LEFT,
        ))

        self.styles.add(ParagraphStyle(
            name='ArticleScore',
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=BLACK,
            alignment=TA_RIGHT,
        ))

        self.styles.add(ParagraphStyle(
            name='ArticleSummary',
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=MEDIUM_GRAY,
            alignment=TA_LEFT,
        ))

        self.styles.add(ParagraphStyle(
            name='PageNumber',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=MEDIUM_GRAY,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name='Footer',
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=MEDIUM_GRAY,
            alignment=TA_LEFT,
        ))

    def _add_header_footer(self, canvas_obj, doc):
        """Add header/footer to each page."""
        canvas_obj.saveState()

        # Footer with logo
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                canvas_obj.drawImage(
                    self.logo_path,
                    MARGIN,
                    0.4 * inch,
                    width=1.2 * inch,
                    height=0.4 * inch,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception:
                pass

        # Page number (right side)
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(MEDIUM_GRAY)
        canvas_obj.drawRightString(
            PAGE_WIDTH - MARGIN,
            0.5 * inch,
            f"Page {page_num}"
        )

        canvas_obj.restoreState()

    def _build_title_page(self) -> list:
        """Build title page elements."""
        elements = []

        # Spacer to push content down
        elements.append(Spacer(1, 2.5 * inch))

        # Client name (large, bold)
        elements.append(Paragraph(self.client_name.upper(), self.styles['ClientName']))
        elements.append(Spacer(1, 0.3 * inch))

        # Campaign name
        elements.append(Paragraph(self.campaign_name, self.styles['CampaignName']))
        elements.append(Spacer(1, 0.5 * inch))

        # Accent line
        line_table = Table([[""]], colWidths=[2 * inch], rowHeights=[3])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.accent_color),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Date
        date_str = datetime.now().strftime("%B %Y")
        elements.append(Paragraph(f"Coverage Report  •  {date_str}", self.styles['DateRange']))

        # Push logo to bottom
        elements.append(Spacer(1, 3 * inch))

        # CoverageIndex branding at bottom
        elements.append(Paragraph("Powered by CoverageIndex", self.styles['Footer']))

        elements.append(PageBreak())
        return elements

    def _build_overview_page(self) -> list:
        """Build campaign overview page."""
        elements = []

        # Section header
        elements.append(Paragraph("Campaign Overview", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.3 * inch))

        # Overall score - big and prominent
        score_data = [
            [Paragraph(f"{self.avg_score:.0f}", self.styles['BigScore'])],
            [Paragraph("AVERAGE SCORE", self.styles['ScoreLabel'])],
        ]
        score_table = Table(score_data, colWidths=[3 * inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        # Wrap score in a bordered box
        score_wrapper = Table([[score_table]], colWidths=[3.5 * inch])
        score_wrapper.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 2, self.accent_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))

        elements.append(score_wrapper)
        elements.append(Spacer(1, 0.5 * inch))

        # Score Distribution section
        elements.append(Paragraph("Score Distribution", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2 * inch))

        # Grade bands with visual bars
        grade_bands = [
            ("A", "90-100", self.score_distribution["A"], GREEN),
            ("B", "80-89", self.score_distribution["B"], GREEN),
            ("C", "70-79", self.score_distribution["C"], YELLOW),
            ("D", "60-69", self.score_distribution["D"], RED),
            ("F", "Below 60", self.score_distribution["F"], RED),
        ]

        # Calculate max for bar scaling
        max_count = max(self.score_distribution.values()) if self.score_distribution.values() else 1
        max_count = max(max_count, 1)  # Avoid division by zero

        dist_data = []
        for grade, range_text, count, color in grade_bands:
            # Create visual bar
            bar_width = max((count / max_count) * 3, 0.1) if count > 0 else 0.1
            bar = Table([[""]], colWidths=[bar_width * inch], rowHeights=[16])
            bar.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), color if count > 0 else LIGHT_GRAY),
            ]))

            # Article count text
            count_text = f"{count} article{'s' if count != 1 else ''}"

            dist_data.append([
                Paragraph(f"<b>{grade}</b>", self.styles['ArticleHeadline']),
                Paragraph(range_text, self.styles['ArticleOutlet']),
                bar,
                Paragraph(count_text, self.styles['ArticleOutlet']),
            ])

        dist_table = Table(
            dist_data,
            colWidths=[0.4 * inch, 1 * inch, 3.5 * inch, 1.2 * inch]
        )
        dist_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(dist_table)
        elements.append(PageBreak())

        return elements

    def _build_article_listing(self) -> list:
        """Build article listing pages."""
        elements = []

        elements.append(Paragraph("Coverage Details", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.3 * inch))

        # Filter successful results
        successful_results = [r for r in self.results if r.get("scores", {}).get("success")]

        if not successful_results:
            elements.append(Paragraph("No articles analyzed.", self.styles['ArticleOutlet']))
            return elements

        # Sort by score descending
        successful_results.sort(key=lambda x: x["scores"].get("total_score", 0), reverse=True)

        # Build article entries (fewer per page since we have summaries now)
        articles_per_page = 12

        for i, result in enumerate(successful_results):
            article = result.get("article", {})
            outlet = result.get("outlet", {})
            scores = result.get("scores", {})

            headline = article.get("headline", "Untitled")[:80]
            if len(article.get("headline", "")) > 80:
                headline += "..."

            outlet_name = outlet.get("name", "Unknown Outlet")
            tier = outlet.get("tier", 3)
            score = scores.get("total_score", 0)
            grade = scores.get("grade", "N/A")

            # Get summary from AI scores
            summary = scores.get("summary", "")
            # Truncate long summaries to one sentence
            if summary:
                # Take first sentence or truncate at 150 chars
                if ". " in summary:
                    summary = summary.split(". ")[0] + "."
                if len(summary) > 150:
                    summary = summary[:147] + "..."

            # Traffic light indicator
            indicator_color = get_traffic_light_color(grade)

            # Create row with headline, outlet, and score
            row_data = [
                [
                    # Indicator dot
                    self._create_indicator_dot(indicator_color),
                    # Headline and outlet
                    [
                        Paragraph(headline, self.styles['ArticleHeadline']),
                        Paragraph(f"{outlet_name}  •  Tier {tier}", self.styles['ArticleOutlet']),
                    ],
                    # Score
                    Paragraph(f"{score:.0f} ({grade})", self.styles['ArticleScore']),
                ]
            ]

            row_table = Table(
                row_data,
                colWidths=[0.4 * inch, 5.3 * inch, 1.3 * inch]
            )
            row_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

            elements.append(row_table)

            # Add summary row below
            if summary:
                summary_row = Table(
                    [["", Paragraph(summary, self.styles['ArticleSummary']), ""]],
                    colWidths=[0.4 * inch, 5.3 * inch, 1.3 * inch]
                )
                summary_row.setStyle(TableStyle([
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LINEBELOW', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
                ]))
                elements.append(summary_row)
            else:
                # Just add the bottom line
                line_row = Table(
                    [["", "", ""]],
                    colWidths=[0.4 * inch, 5.3 * inch, 1.3 * inch]
                )
                line_row.setStyle(TableStyle([
                    ('LINEBELOW', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(line_row)

            # Page break after every N articles
            if (i + 1) % articles_per_page == 0 and i < len(successful_results) - 1:
                elements.append(PageBreak())
                elements.append(Paragraph("Coverage Details (continued)", self.styles['SectionHeader']))
                elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_indicator_dot(self, color: colors.Color) -> Table:
        """Create a small colored circle indicator."""
        # Use a small table with background color to simulate a dot
        dot = Table([[""]], colWidths=[12], rowHeights=[12])
        dot.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), color),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))
        return dot

    def generate(self) -> BytesIO:
        """Generate the PDF report and return as BytesIO buffer."""
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )

        # Build all elements
        elements = []
        elements.extend(self._build_title_page())
        elements.extend(self._build_overview_page())
        elements.extend(self._build_article_listing())

        # Build PDF
        doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)

        buffer.seek(0)
        return buffer


def generate_coverage_report(
    client_name: str,
    campaign_name: str,
    results: list,
    accent_color: str = "#000000",
    logo_path: str = None,
) -> BytesIO:
    """
    Generate a PDF coverage report.

    Args:
        client_name: Name of the client
        campaign_name: Name of the campaign
        results: List of article results from scoring
        accent_color: Hex color for accent details (e.g., "#C8102E")
        logo_path: Path to CoverageIndex logo PNG

    Returns:
        BytesIO buffer containing the PDF
    """
    report = CoverageReportPDF(
        client_name=client_name,
        campaign_name=campaign_name,
        results=results,
        accent_color=accent_color,
        logo_path=logo_path,
    )
    return report.generate()
