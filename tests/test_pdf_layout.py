import os
import tempfile
import pytest
from crew.pdf_generator import PDFReportGenerator


@pytest.fixture
def temp_pdf_path():
    temp_dir = tempfile.mkdtemp()
    target_path = os.path.join(temp_dir, "test_output.pdf")
    yield target_path
    if os.path.exists(target_path):
        os.remove(target_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def test_pdf_report_generation(temp_pdf_path):
    """Verifies that PDFReportGenerator produces a valid A4 PDF without styling exceptions."""
    generator = PDFReportGenerator(output_path=temp_pdf_path)
    markdown_content = """# Executive Summary
Technology sector operating margins expanded during Q3.

## Core Financial Observations
- Revenue momentum driven by hyperscale cloud consumption.
- CapEx allocation expanded across semiconductor portfolios.

### Valuation Commentary
Trading multiples remain elevated relative to historical median levels.
"""
    output_file = generator.compile(
        query="Tech Sector Q3 Analysis",
        report_markdown=markdown_content,
        csv_path="data/mock_financials.csv",
    )

    assert os.path.exists(output_file), "PDF file should be created"
    assert os.path.getsize(output_file) > 1000, "PDF file must not be empty"

    # Verify PDF magic bytes
    with open(output_file, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-", "Generated file must have standard PDF header"


def test_pdf_report_with_special_characters(temp_pdf_path):
    """Verifies that markdown with special XML characters does not raise formatting errors."""
    generator = PDFReportGenerator(output_path=temp_pdf_path)
    tricky_markdown = """# Tech & Media Valuation Analysis <Q3 2026>
Growth rate was > 25% & margins were < 40%.
- Item with ampersand & brackets: [Tech Sector]
- Price: $100 & Multiples: 25.5x
"""
    output_file = generator.compile(
        query="Special & Characters <Test>",
        report_markdown=tricky_markdown,
        csv_path="data/mock_financials.csv",
    )
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000
