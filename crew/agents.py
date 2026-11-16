import os
from typing import Optional
from dotenv import load_dotenv
from crewai import Agent, LLM
from crew.tools import calculate_financial_metrics, search_and_scrape_market_data

load_dotenv()


def ensure_env_key():
    """Ensures environment keys are present so CrewAI Agent models initialize properly."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    if not (gemini_key and gemini_key.strip()) and not (openai_key and openai_key.strip()):
        os.environ["OPENAI_API_KEY"] = "mock-openai-key-for-offline-eval"


def get_configured_llm(model_name: Optional[str] = None) -> LLM:
    """Returns configured LLM instance (Gemini, OpenAI, or local fallback)."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip():
        model = model_name or os.getenv("LLM_MODEL", "gemini/gemini-3.8-flash")
        if "gemini" in model and not model.startswith("gemini/"):
            model = f"gemini/{model}"
        return LLM(model=model, api_key=gemini_key.strip())

    ensure_env_key()
    api_key = os.getenv("OPENAI_API_KEY")
    model = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    return LLM(model=model, api_key=api_key)


def create_researcher_agent(llm: Optional[LLM] = None) -> Agent:
    """Lead Researcher Agent: Queries search networks, locates financial data, and scrapes company metrics."""
    agent_llm = llm or get_configured_llm()
    return Agent(
        role="Market Research Specialist",
        goal="Query search search networks, locate financial data, and scrape company metrics.",
        backstory=(
            "You are an elite market research specialist with extensive background in "
            "financial intelligence gathering, web scraping, and tracking macroeconomic trends "
            "across enterprise technology and semiconductor industries."
        ),
        tools=[search_and_scrape_market_data],
        llm=agent_llm,
        verbose=True,
        allow_delegation=False,
    )


def create_analyst_agent(llm: Optional[LLM] = None) -> Agent:
    """Data Analyst Agent: Parses data matrices using Pandas, computes averages, and verifies numeric consistency."""
    agent_llm = llm or get_configured_llm()
    return Agent(
        role="Financial Data Analyst",
        goal="Parse data matrices using Pandas, compute averages, and verify numeric consistency.",
        backstory=(
            "You are a quantitative financial analyst specialized in tabular data processing, "
            "statistical modeling with Pandas, outlier detection, and financial dispersion analysis."
        ),
        tools=[calculate_financial_metrics],
        llm=agent_llm,
        verbose=True,
        allow_delegation=False,
    )


def create_writer_agent(llm: Optional[LLM] = None) -> Agent:
    """Content Writer Agent: Synthesizes information, writes sections, and structures copy."""
    agent_llm = llm or get_configured_llm()
    return Agent(
        role="Technical Reports Writer",
        goal="Synthesize information, write sections, and structure copy.",
        backstory=(
            "You are an executive-level technical and financial reports author capable of turning "
            "disparate quantitative calculations and market research notes into comprehensive, "
            "well-structured C-suite intelligence reports."
        ),
        tools=[],
        llm=agent_llm,
        verbose=True,
        allow_delegation=False,
    )
