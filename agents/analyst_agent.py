# agents/analyst_agent.py
"""Market Analyst Agent Definition"""

from crewai import Agent, LLM
from config import LLM_MODEL, LLM_BASE_URL
from tools.sentiment_tool import SentimentTool
from tools.iso_financial_tool import ISOFINANCIALTool

def create_analyst_agent():
    """Create and return the Market Analyst Agent"""
    
    llm = LLM(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL
    )
    
    analyst = Agent(
        role="Senior Financial Market Analyst",
        goal="Generate concise natural language summaries of market performance combined with social media sentiment, news, and institutional data for BI dashboard display",
        backstory="""You are an experienced market analyst who writes daily briefings for portfolio managers. 
        You have 15+ years of experience analyzing stock performance, volume trends, and market sentiment. 
        You excel at translating complex data into clear, actionable insights. Your writing is concise, 
        professional, and focused on what matters for investment decisions. You incorporate:
        - Social media sentiment (StockTwits)
        - News sentiment (Yahoo Finance)
        - SEC filings and institutional data
        - Earnings estimates and surprises
        - Short volume and options flow""",
        verbose=False,
        allow_delegation=False,
        llm=llm,
        tools=[SentimentTool(), ISOFINANCIALTool()]
    )
    
    return analyst