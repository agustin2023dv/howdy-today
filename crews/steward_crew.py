# crews/steward_crew.py
from crewai import Crew, Process
from agents.steward_agent import create_steward_agent
from tasks.steward_task import create_steward_task

def run_steward_crew(data_summary: str):
    steward = create_steward_agent()
    task = create_steward_task(data_summary, steward_agent=steward)
    
    crew = Crew(
        agents=[steward],
        tasks=[task],
        process=Process.sequential,
        verbose=False  
    )
    
    result = crew.kickoff()
    return result