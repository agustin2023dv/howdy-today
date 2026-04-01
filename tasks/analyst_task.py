# tasks/analyst_task.py
from crewai import Task
from agents.analyst_agent import create_analyst_agent

def create_analyst_task(data_summary: str, analyst_agent=None) -> Task:
    if analyst_agent is None:
        analyst_agent = create_analyst_agent()
    
    return Task(
        description=f"""
        Write a market commentary paragraph for a BI dashboard.
        
        DATA:
        {data_summary}
        
        INSTRUCTIONS:
        - Write 2-4 sentences about the stock performance
        - Start with the ticker symbol (AAPL)
        - Mention price change and volume
        - Write in professional financial analyst tone
        - Output ONLY the paragraph text
        - NO JSON, NO brackets, NO bullet points
        - NO introductions like "Here is my analysis"
        
        EXAMPLE OUTPUT:
        AAPL gained 3.2% today on volume 15% above average. The stock 
        outperformed the S&P 500 which rose 1.5%. Trading remains active 
        near the 52-week high of $195.
        """,
        expected_output="A 2-4 sentence paragraph starting with AAPL, mentioning price and volume, no JSON or formatting.",
        agent=analyst_agent
    )