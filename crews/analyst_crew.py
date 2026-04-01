# crews/analyst_crew.py
from crewai import Crew, Process
from agents.analyst_agent import create_analyst_agent
from tasks.analyst_task import create_analyst_task

def run_analyst_crew(data_summary: str):
    analyst = create_analyst_agent()
    task = create_analyst_task(data_summary, analyst_agent=analyst)
    
    crew = Crew(
        agents=[analyst],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    result = crew.kickoff()
    return result