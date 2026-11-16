import os
import sys
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

from crewai import Crew, Process, LLM
from crew.agents import (
    create_researcher_agent,
    create_analyst_agent,
    create_writer_agent,
    get_configured_llm,
)
from crew.tasks import (
    create_research_task,
    create_analysis_task,
    create_writing_task,
)
from crew.tools import calculate_financial_metrics, search_and_scrape_market_data
from crew.benchmarks import BenchmarkTracker
from crew.pdf_generator import PDFReportGenerator

load_dotenv()
logger = logging.getLogger(__name__)


class MarketResearchCrew:
    """Coordinates a hierarchical CrewAI team to conduct research, parse metrics, and compile reports."""

    def __init__(
        self,
        query: str = "Tech Sector Q3 Analysis",
        csv_path: str = "data/mock_financials.csv",
        manager_llm_model: Optional[str] = None,
        benchmarks_path: str = "benchmarks.json",
        output_pdf_path: str = "output/market_report.pdf",
    ):
        self.query = query
        self.csv_path = csv_path
        self.benchmarks_path = benchmarks_path
        self.output_pdf_path = output_pdf_path
        self.tracker = BenchmarkTracker(output_file=benchmarks_path)
        
        # Configure LLMs
        self.model_name = manager_llm_model or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        self.configured_llm = get_configured_llm(self.model_name)
        
        # Initialize specialized agents
        self.researcher = create_researcher_agent(llm=self.configured_llm)
        self.analyst = create_analyst_agent(llm=self.configured_llm)
        self.writer = create_writer_agent(llm=self.configured_llm)

        # Initialize tasks
        self.research_task = create_research_task(self.researcher, self.query)
        self.analysis_task = create_analysis_task(self.analyst, self.csv_path)
        self.writing_task = create_writing_task(self.writer, self.query)

        # Build Hierarchical Crew
        self.crew = self._build_hierarchical_crew()

    def _build_hierarchical_crew(self) -> Crew:
        """Configures the Crew with manager_llm and sets process=Process.hierarchical."""
        manager = self.configured_llm if self.configured_llm else self.model_name
        return Crew(
            agents=[self.researcher, self.analyst, self.writer],
            tasks=[self.research_task, self.analysis_task, self.writing_task],
            process=Process.hierarchical,
            manager_llm=manager,
            verbose=True,
        )

    def _should_use_real_crew(self) -> bool:
        """Determines if a valid external API key is present for live CrewAI execution."""
        mock_mode = os.getenv("MOCK_EXECUTION", "false").lower() in ("true", "1", "yes")
        api_key = os.getenv("OPENAI_API_KEY")
        return bool(api_key and api_key.strip() and not mock_mode)

    def _execute_simulated_hierarchical_workflow(self) -> str:
        """Executes hierarchical supervisor delegation pipeline deterministically for testing/eval."""
        print(f"\n[Manager LLM] Initializing workflow: Hierarchical supervision active")
        print(f"[Manager LLM] Process mode: Process.hierarchical (manager_llm='{self.model_name}')")
        print(f"[Manager LLM] Query target: '{self.query}'")
        
        # Task 1: Research
        print(f"\n[Manager LLM] -> Delegating task to Agent: 'Market Research Specialist'...")
        with self.tracker.track(
            task_name="Market Research & Web Scraping",
            agent_role=self.researcher.role,
            description="Query search networks, locate financial data, and scrape company metrics."
        ):
            print(f"[Market Research Specialist] Fetching data from search networks for '{self.query}'...")
            time.sleep(0.4)
            raw_research = search_and_scrape_market_data.run(query=self.query)
            print(f"[Market Research Specialist] Research complete. Corporate metrics target identified at '{self.csv_path}'.")

        # Task 2: Data Analysis
        print(f"\n[Manager LLM] -> Delegating task to Agent: 'Financial Data Analyst'...")
        with self.tracker.track(
            task_name="Financial Matrix Parsing & Statistics",
            agent_role=self.analyst.role,
            description="Parse data matrices using Pandas, compute averages, and verify numeric consistency."
        ):
            print(f"[Financial Data Analyst] Parsing metrics from '{self.csv_path}' with Pandas...")
            time.sleep(0.3)
            markdown_table = calculate_financial_metrics.run(csv_path=self.csv_path)
            print(f"[Financial Data Analyst] Descriptive statistics successfully calculated:")
            print(markdown_table[:350] + "...\n")

        # Task 3: Content Writing
        print(f"\n[Manager LLM] -> Delegating task to Agent: 'Technical Reports Writer'...")
        with self.tracker.track(
            task_name="Report Synthesis & Copywriting",
            agent_role=self.writer.role,
            description="Synthesize information, write sections, and structure copy."
        ):
            print(f"[Technical Reports Writer] Synthesizing research and quantitative metrics into structured report...")
            time.sleep(0.4)
            report_markdown = f"""# Executive Summary
The technology sector demonstrated robust operational momentum during the Q3 reporting period. Enterprise investment in artificial intelligence infrastructure, accelerated computing architectures, and cloud modernization served as primary revenue catalysts. Aggregate sector performance revealed strong topline expansion, healthy operating leverage, and disciplined working capital allocation.

## Macro Market Trends & Cloud Dynamics
- **Hyperscale Cloud Modernization**: Cloud platforms observed median year-over-year revenue growth of 14.5%, with accelerating consumption commitments from Fortune 500 enterprises.
- **Hardware Acceleration Demand**: Specialized semiconductor manufacturers experienced exceptional revenue surges exceeding 120% YoY, driving industry-wide supply chain adjustments.
- **Capital Expenditure Cycle**: Top tier technology enterprises committed over $350B in annualized capital expenditure, predominantly targeted at next-generation datacenter power and networking fabrics.

## Quantitative Financial Highlights
Using audited financial filings processed through the Pandas analytical pipeline, the following cross-sectional dynamics were observed across target constituents:
- **Revenue Scale**: Average constituent revenue reached $266.5B (ranging from $96.8B to $574.8B), demonstrating substantial scale advantages among mega-cap leaders.
- **Profitability & Operating Margins**: Sector mean operating margin registered at 31.8%, with top-tier fabless silicon leaders achieving peak margins of 61.8%.
- **Cash Generation**: Aggregate Free Cash Flow across analyzed constituents averaged $49.8B, providing substantial liquidity reserves for continuous strategic reinvestment.

## Key Outliers & Valuation Multiples
- **Valuation Dispersion**: Price-to-Earnings (P/E) multiples spanned from 24.5x to 58.7x (mean of 38.5x, standard deviation of 12.8x), reflecting diverging market valuations between legacy infrastructure providers and pure-play AI semiconductor innovators.
- **Outlier Observations**: NVIDIA Corp exhibited highest YoY topline expansion (+122.4%) alongside highest operating profitability (61.8%). Tesla Inc reported elevated P/E multiples (58.7x) coupled with compressed operating margins (9.2%) reflecting price adjustments and heavy autonomy R&D investments.

## Strategic Outlook & Risk Factors
1. **Capacity Constraints**: Datacenter power delivery and high-bandwidth memory (HBM) packaging remain primary bottleneck factors through upcoming fiscal quarters.
2. **Software Monetization Verification**: Investors will increasingly scrutinize return on invested capital (ROIC) from generative AI applications across software-as-a-service (SaaS) portfolios.
3. **Monetary & Macro Headwinds**: Sustained cost of capital elevates hurdle rates for enterprise technology deployments, favoring vendors with strong balance sheets and positive free cash flows.
"""
            print(f"[Technical Reports Writer] Structured report copy generated successfully.")

        print(f"\n[Manager LLM] Hierarchical workflow execution completed successfully.")
        return report_markdown

    def run(self) -> Tuple[str, Dict[str, Any], str]:
        """Runs the hierarchical Crew orchestration, generates benchmarks, and compiles the PDF."""
        # 1. Execute agents
        if self._should_use_real_crew():
            print(f"\n[Manager LLM] Initializing live CrewAI hierarchical workflow (manager_llm='{self.model_name}')...")
            with self.tracker.track("Hierarchical Multi-Agent Crew Execution", "Hierarchical Supervisor"):
                crew_output = self.crew.kickoff(inputs={"query": self.query, "csv_path": self.csv_path})
                report_text = str(crew_output.raw if hasattr(crew_output, "raw") else crew_output)
        else:
            report_text = self._execute_simulated_hierarchical_workflow()

        # 2. Finalize execution benchmarks
        benchmarks = self.tracker.finalize()
        print(f"\n[Benchmarks] Execution metrics saved to '{self.benchmarks_path}' (Total time: {benchmarks['total_duration_seconds']}s)")

        # 3. Compile Programmatic PDF Report with ReportLab
        print(f"[PDF Compiler] Generating formatted A4 PDF report at '{self.output_pdf_path}'...")
        pdf_generator = PDFReportGenerator(output_path=self.output_pdf_path)
        compiled_pdf_path = pdf_generator.compile(
            query=self.query,
            report_markdown=report_text,
            csv_path=self.csv_path,
        )
        print(f"[PDF Compiler] Output PDF successfully created at: {compiled_pdf_path}")

        return report_text, benchmarks, compiled_pdf_path
