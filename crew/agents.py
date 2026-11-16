import os
from typing import Optional
from dotenv import load_dotenv
from crewai import Agent, LLM
from crew.tools import calculate_financial_metrics, search_and_scrape_market_data

load_dotenv()


def get_configured_llm(model_name: Optional[str] = None) -> Optional[LLM]:
    """Returns configured LLM instance or None if API key is not present."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        return None
    model = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    return LLM(model=model, api_key=api_key.strip())


def create_researcher_agent(llm: Optional[LLM] = None) -> Agent:
    """Lead Researcher Agent: Queries search networks, locates financial data, and scrapes company metrics."""
    return Agent(
        role="Market Research Specialist",
        goal="Query search search networks, locate financial data, and scrape company metrics.",
        backstory=(
            "You are an elite market research specialist with extensive background in "
            "financial intelligence gathering, web scraping, and tracking macroeconomic trends "
            "across enterprise technology and semiconductor industries."
        ),
        tools=[search_and_scrape_market_data],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_analyst_agent(llm: Optional[LLM] = None) -> Agent:
    """Data Analyst Agent: Parses data matrices using Pandas, computes averages, and verifies numeric consistency."""
    return Agent(
        role="Financial Data Analyst",
        goal="Parse data matrices using Pandas, compute averages, and verify numeric consistency.",
        backstory=(
            "You are a quantitative financial analyst specialized in tabular data processing, "
            "statistical modeling with Pandas, outlier detection, and financial dispersion analysis."
        ),
        tools=[calculate_financial_metrics],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_writer_agent(llm: Optional[LLM] = None) -> Agent:
    """Content Writer Agent: Synthesizes information, writes sections, and structures copy."""
    return Agent(
        role="Technical Reports Writer",
        goal="Synthesize information, write sections, and structure copy.",
        backstory=(
            "You are an executive-level technical and financial reports author capable of turning "
            "disparate quantitative calculations and market research notes into comprehensive, "
            "well-structured C-suite intelligence reports."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
