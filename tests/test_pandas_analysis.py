import os
import tempfile
import pandas as pd
import pytest
from crew.tools import calculate_financial_metrics


@pytest.fixture
def sample_csv():
    """Generates a temporary CSV with known numerical values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Company,Revenue,Net_Income,PE_Ratio\n")
        f.write("Alpha,100.0,20.0,15.0\n")
        f.write("Beta,200.0,40.0,25.0\n")
        f.write("Gamma,300.0,60.0,35.0\n")
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_calculate_financial_metrics_output_type(sample_csv):
    """Verifies that the financial parser returns markdown table string."""
    result = calculate_financial_metrics.run(csv_path=sample_csv)
    assert isinstance(result, str)
    assert "|" in result, "Result must contain markdown table delimiters"


def test_calculate_financial_metrics_math(sample_csv):
    """Verifies that summary statistics match pandas mathematical calculations."""
    result = calculate_financial_metrics.run(csv_path=sample_csv)
    
    # Expected mean for Revenue: (100 + 200 + 300) / 3 = 200.0
    # Expected min: 100.0, max: 300.0
    assert "mean" in result.lower()
    assert "200" in result
    assert "100" in result
    assert "300" in result


def test_calculate_financial_metrics_default_dataset():
    """Verifies parsing on the baseline mock_financials dataset."""
    result = calculate_financial_metrics.run(csv_path="data/mock_financials.csv")
    assert isinstance(result, str)
    assert "Revenue_Billion_USD" in result
    assert "Operating_Margin_Pct" in result
    assert "std" in result.lower()
