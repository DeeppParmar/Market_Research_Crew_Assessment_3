import os
import json
import tempfile
import pytest
from crew.agents import (
    create_researcher_agent,
    create_analyst_agent,
    create_writer_agent,
)
from crew.crew import MarketResearchCrew
from crew.benchmarks import BenchmarkTracker
from crewai import Process


def test_agent_roles_and_goals():
    """Verifies that all three specialized agents adhere strictly to requirements."""
    researcher = create_researcher_agent()
    analyst = create_analyst_agent()
    writer = create_writer_agent()

    # Exact roles from requirements
    assert researcher.role == "Market Research Specialist"
    assert "Query search" in researcher.goal
    assert len(researcher.tools) >= 1

    assert analyst.role == "Financial Data Analyst"
    assert "Parse data matrices using Pandas" in analyst.goal
    assert len(analyst.tools) >= 1

    assert writer.role == "Technical Reports Writer"
    assert "Synthesize information" in writer.goal


def test_crew_hierarchical_configuration():
    """Verifies the Crew is configured with Process.hierarchical and supervisor manager."""
    crew_coordinator = MarketResearchCrew(
        query="Tech Sector Q3 Analysis",
        csv_path="data/mock_financials.csv",
    )
    assert crew_coordinator.crew.process == Process.hierarchical
    assert len(crew_coordinator.crew.agents) == 3
    assert len(crew_coordinator.crew.tasks) == 3


def test_benchmarking_tracker():
    """Verifies task execution measurement and routing history serialization."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        bench_file = f.name

    try:
        tracker = BenchmarkTracker(output_file=bench_file)
        with tracker.track("Test Task", "Market Research Specialist", "Testing benchmark"):
            pass

        summary = tracker.finalize()
        assert os.path.exists(bench_file)
        assert summary["task_count"] == 1
        assert summary["routing_history"][0]["assigned_agent"] == "Market Research Specialist"
        assert summary["tasks"][0]["status"] == "completed"

        with open(bench_file, "r") as bf:
            loaded_json = json.load(bf)
            assert loaded_json["total_duration_seconds"] >= 0
    finally:
        if os.path.exists(bench_file):
            os.remove(bench_file)


def test_end_to_end_crew_run(monkeypatch):
    """Verifies full execution pipeline run, generating markdown, benchmarks, and PDF."""
    monkeypatch.setenv("MOCK_EXECUTION", "true")
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_out = os.path.join(temp_dir, "test_market_report.pdf")
        bench_out = os.path.join(temp_dir, "test_benchmarks.json")

        coordinator = MarketResearchCrew(
            query="Automated Test Query",
            csv_path="data/mock_financials.csv",
            benchmarks_path=bench_out,
            output_pdf_path=pdf_out,
        )

        report, benchmarks, pdf_path = coordinator.run()

        assert len(report) > 100
        assert os.path.exists(bench_out)
        assert os.path.exists(pdf_out)
        assert benchmarks["task_count"] == 3
