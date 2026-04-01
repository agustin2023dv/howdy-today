# agents/steward_agent.py
"""Data Steward Agent Definition"""

from crewai import Agent, LLM
from tools.validation_tool import DataValidationTool

def create_steward_agent():
    """Create and return the Data Steward Agent"""
    
    llm = LLM(
        model="ollama/llama3.1",
        base_url="http://localhost:11434"
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