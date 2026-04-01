# agents/analyst_agent.py
"""Market Analyst Agent Definition"""

from crewai import Agent, LLM

def create_analyst_agent():
    """Create and return the Market Analyst Agent"""
    
    llm = LLM(
        model="ollama/llama3.1",
        base_url="http://localhost:11434"
    )
    
    analyst = Agent(
        role="Senior Financial Market Analyst",
        goal="Generate concise natural language summaries of market performance for BI dashboard display",
        backstory="""You are an experienced market analyst who writes daily briefings for portfolio managers. 
        You have 15+ years of experience analyzing stock performance. You excel at translating complex 
        data into clear, actionable insights. Your writing is concise, professional, and focused.""",
        verbose=False,
        allow_delegation=False,
        llm=llm
        # NO TOOLS - agent writes directly
    )
    
    return analyst