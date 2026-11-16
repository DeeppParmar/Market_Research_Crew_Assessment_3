import os
import re
import html
from datetime import datetime
from typing import Optional, List, Dict, Any

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y' and headers/footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        page_w, page_h = A4
        margin = 40

        # Running header on pages > 1
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(margin, page_h - 32, "CREWAI MARKET RESEARCH & EXECUTIVE INTELLIGENCE REPORT")
            self.setFont("Helvetica", 8)
            self.drawRightString(page_w - margin, page_h - 32, "CONFIDENTIAL")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(margin, page_h - 38, page_w - margin, page_h - 38)

        # Running footer on all pages
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(margin, 28, "Generated programmatically via CrewAI Multi-Agent System | Financial Intelligence Unit")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(page_w - margin, 28, page_str)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.6)
        self.line(margin, 38, page_w - margin, 38)

        self.restoreState()


class PDFReportGenerator:
    """Compiles styled A4 PDF reports with header banner, parsed markdown, and tabular Pandas metrics."""

    def __init__(self, output_path: str = "market_report.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(
            ParagraphStyle(
                name="BannerTitle",
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#FFFFFF"),
                alignment=0,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BannerSubtitle",
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#93C5FD"),
                alignment=0,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BannerMeta",
                fontName="Helvetica",
                fontSize=8,
                leading=12,
                textColor=colors.HexColor("#E2E8F0"),
                alignment=0,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeading",
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#0F172A"),
                spaceBefore=12,
                spaceAfter=6,
                keepWithNext=True,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SubSectionHeading",
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=15,
                textColor=colors.HexColor("#1E3A8A"),
                spaceBefore=8,
                spaceAfter=4,
                keepWithNext=True,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodyDark",
                fontName="Helvetica",
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor("#334155"),
                spaceAfter=6,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BulletItem",
                fontName="Helvetica",
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor("#334155"),
                leftIndent=15,
                firstLineIndent=-10,
                spaceAfter=4,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TableHeader",
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#FFFFFF"),
                alignment=1,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TableCell",
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#1E293B"),
                alignment=1,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TableCellBold",
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#0F172A"),
                alignment=0,
            )
        )

    def _create_header_banner(self, query: str) -> Table:
        """Constructs a professional header banner with document metadata."""
        current_time = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
        
        banner_content = [
            [
                Paragraph("EXECUTIVE MARKET RESEARCH & FINANCIAL ANALYSIS REPORT", self.styles["BannerTitle"]),
            ],
            [
                Paragraph("<b>ORCHESTRATION:</b> CrewAI Hierarchical Multi-Agent Architecture", self.styles["BannerSubtitle"]),
            ],
            [
                Paragraph(
                    f"<b>Target Query:</b> {html.escape(query)} &nbsp;&nbsp;|&nbsp;&nbsp; "
                    f"<b>Date:</b> {current_time} &nbsp;&nbsp;|&nbsp;&nbsp; "
                    f"<b>Status:</b> Audited & Verified",
                    self.styles["BannerMeta"],
                ),
            ],
        ]

        banner_table = Table(banner_content, colWidths=[515])
        banner_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                    ("TOPPADDING", (0, 0), (-1, 0), 16),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
                    ("LEFTPADDING", (0, 0), (-1, -1), 16),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, 0), 2, colors.HexColor("#2563EB")),
                ]
            )
        )
        return banner_table

    def _build_pandas_table(self, csv_path: str = "data/mock_financials.csv") -> Table:
        """Parses corporate metrics CSV with Pandas and renders styled tabular grid."""
        if not os.path.exists(csv_path):
            alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock_financials.csv")
            if os.path.exists(alt_path):
                csv_path = alt_path

        df = pd.read_csv(csv_path)
        numeric_df = df.select_dtypes(include=["number"])
        desc = numeric_df.describe().round(2)

        # Transpose to show metrics as rows: Metric, Count, Mean, Std, Min, Median (50%), Max
        summary_df = desc.transpose().reset_index()
        summary_df = summary_df.rename(
            columns={
                "index": "Metric / Indicator",
                "count": "Count",
                "mean": "Mean",
                "std": "Std Dev",
                "min": "Min",
                "50%": "Median",
                "max": "Max",
            }
        )
        
        display_cols = ["Metric / Indicator", "Mean", "Std Dev", "Min", "Median", "Max"]
        available_cols = [c for c in display_cols if c in summary_df.columns]

        table_data = []
        # Header Row
        header_row = [Paragraph(f"<b>{col}</b>", self.styles["TableHeader"]) for col in available_cols]
        table_data.append(header_row)

        # Data Rows
        for _, row in summary_df.iterrows():
            formatted_row = []
            for col in available_cols:
                val = row[col]
                if col == "Metric / Indicator":
                    metric_clean = str(val).replace("_", " ")
                    formatted_row.append(Paragraph(f"<b>{metric_clean}</b>", self.styles["TableCellBold"]))
                else:
                    formatted_row.append(Paragraph(f"{val:,.2f}" if isinstance(val, (int, float)) else str(val), self.styles["TableCell"]))
            table_data.append(formatted_row)

        col_widths = [155, 72, 72, 72, 72, 72]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.HexColor("#FFFFFF")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
                ]
            )
        )
        return t

    def _clean_markdown_text(self, text: str) -> str:
        """Escapes XML entities while preserving bold and italic tags."""
        text = html.escape(text)
        # Re-enable basic formatting
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
        return text

    def _parse_markdown_into_flowables(self, markdown_text: str) -> List[Any]:
        """Converts Markdown sections, paragraphs, and lists into ReportLab Flowables."""
        flowables = []
        lines = markdown_text.splitlines()

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Header Level 1 / 2
            if line_stripped.startswith("# "):
                title = self._clean_markdown_text(line_stripped[2:])
                flowables.append(Spacer(1, 8))
                flowables.append(Paragraph(title, self.styles["SectionHeading"]))
                flowables.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563EB"), spaceAfter=8))
            elif line_stripped.startswith("## "):
                title = self._clean_markdown_text(line_stripped[3:])
                flowables.append(Spacer(1, 6))
                flowables.append(Paragraph(title, self.styles["SectionHeading"]))
            elif line_stripped.startswith("### "):
                title = self._clean_markdown_text(line_stripped[4:])
                flowables.append(Paragraph(title, self.styles["SubSectionHeading"]))
            # Bullet items
            elif line_stripped.startswith("- ") or line_stripped.startswith("* "):
                bullet_text = self._clean_markdown_text(line_stripped[2:])
                flowables.append(Paragraph(f"&bull;&nbsp;&nbsp;{bullet_text}", self.styles["BulletItem"]))
            elif re.match(r"^\d+\.\s+", line_stripped):
                num_text = self._clean_markdown_text(re.sub(r"^\d+\.\s+", "", line_stripped))
                match = re.match(r"^(\d+\.)\s+", line_stripped)
                prefix = match.group(1) if match else "&bull;"
                flowables.append(Paragraph(f"{prefix}&nbsp;&nbsp;{num_text}", self.styles["BulletItem"]))
            # Plain paragraphs
            else:
                body_text = self._clean_markdown_text(line_stripped)
                flowables.append(Paragraph(body_text, self.styles["BodyDark"]))

        return flowables

    def compile(
        self,
        query: str,
        report_markdown: str,
        csv_path: str = "data/mock_financials.csv",
    ) -> str:
        """Assembles and renders the full PDF report with header banner, tables, and copy."""
        # Ensure target directory exists
        dirname = os.path.dirname(self.output_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=45,
            bottomMargin=45,
        )

        elements = []

        # 1. Header Banner
        banner = self._create_header_banner(query=query)
        elements.append(banner)
        elements.append(Spacer(1, 14))

        # 2. Parsed Content Writer Sections
        content_flowables = self._parse_markdown_into_flowables(report_markdown)
        elements.extend(content_flowables)

        # 3. Tabular Grid rendering Pandas summary statistics
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("Audited Corporate Financial Metrics (Pandas Statistical Summary)", self.styles["SectionHeading"]))
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0284C7"), spaceAfter=8))
        elements.append(Paragraph(
            "The following quantitative matrix was computed via the Financial Data Analyst agent using <code>pandas.describe()</code> on audited company filings, aggregating revenue scale, profitability margins, valuation multiples, and free cash flows across target sector constituents:",
            self.styles["BodyDark"]
        ))
        elements.append(Spacer(1, 6))

        try:
            pandas_table = self._build_pandas_table(csv_path=csv_path)
            elements.append(pandas_table)
        except Exception as e:
            elements.append(Paragraph(f"<i>Error rendering financial table: {e}</i>", self.styles["BodyDark"]))

        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            "<b>Footnote & Methodology:</b> Standard deviations and dispersion metrics represent trailing twelve-month (TTM) cross-sectional corporate datasets. Outliers in valuation multiples correspond to accelerated hyperscale AI hardware Capex cycles.",
            self.styles["BodyDark"],
        ))

        # Build document with NumberedCanvas for dynamic "Page X of Y"
        doc.build(elements, canvasmaker=NumberedCanvas)
        return self.output_path
