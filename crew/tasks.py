from crewai import Agent, Task


def create_research_task(agent: Agent, query: str) -> Task:
    """Lead Researcher task to gather real-time market data and industry metrics."""
    return Task(
        description=(
            f"Conduct exhaustive market intelligence gathering for query: '{query}'. "
            "Use the search_and_scrape_market_data tool to query search networks, scrape "
            "relevant enterprise tech news, revenue trajectories, hyperscaler cloud trends, "
            "and locate audited corporate financial data. Output structured research notes."
        ),
        expected_output=(
            "A structured research dossier summarizing macro sector trends, revenue growth dynamics, "
            "margins, and references to target financial metrics."
        ),
        agent=agent,
    )


def create_analysis_task(agent: Agent, csv_path: str = "data/mock_financials.csv") -> Task:
    """Data Analyst task to calculate statistical summaries with Pandas."""
    return Task(
        description=(
            f"Process the corporate financials dataset at '{csv_path}' using the "
            "calculate_financial_metrics tool. Compute statistical summaries (mean, min, max, "
            "standard deviations, quartiles) across key metrics (Revenue, Net Income, Operating Margins, "
            "P/E Ratios, Free Cash Flows). Verify numeric consistency across companies and summarize "
            "key outliers."
        ),
        expected_output=(
            "A quantitative analysis report with clean Markdown tables displaying summary statistics, "
            "ratio comparisons, and commentary on numeric dispersion."
        ),
        agent=agent,
    )


def create_writing_task(agent: Agent, query: str) -> Task:
    """Content Writer task to synthesize research and financial metrics into executive report copy."""
    return Task(
        description=(
            f"Synthesize all intelligence gathered from the research and data analysis tasks into a "
            f"polished executive market research report on '{query}'. Structure the copy with clear "
            "markdown sections: # Executive Summary, ## Macro Market Trends & Cloud Dynamics, "
            "## Quantitative Financial Highlights, ## Key Outliers & Valuation Multiples, and "
            "## Strategic Recommendations. Ensure findings from the Pandas summary table are seamlessly "
            "integrated into the narrative."
        ),
        expected_output=(
            "A comprehensive, executive-ready technical market research report written in clean Markdown, "
            "structured into formal sections with deep analytical insights."
        ),
        agent=agent,
    )
