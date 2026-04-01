# agents/steward_agent.py
"""Data Steward Agent Definition"""

from crewai import Agent, LLM
from config import LLM_MODEL, LLM_BASE_URL
from tools.validation_tool import DataValidationTool

def create_steward_agent():
    """Create and return the Data Steward Agent"""
    
    llm = LLM(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL
    )
    
    steward = Agent(
        role="Senior Data Quality Engineer",
        goal="Validate extracted market data for anomalies and ensure integrity before loading",
        backstory="""You are a meticulous data engineer responsible for maintaining the integrity 
        of financial market data. You have 10+ years of experience spotting outliers, missing values, 
        and formatting errors. You are thorough, detail-oriented, and never approve data without 
        proper validation.""",
        verbose=False,
        allow_delegation=False,
        llm=llm,
        tools=[DataValidationTool()]
    )
    
    return steward