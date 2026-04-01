# tasks/steward_task.py
from crewai import Task
from agents.steward_agent import create_steward_agent

def create_steward_task(data_summary: str, steward_agent=None) -> Task:
    if steward_agent is None:
        steward_agent = create_steward_agent()
    
    return Task(
        description=f"""
        You are reviewing market data for quality before it loads to the database.
        
        DATA TO VALIDATE:
        {data_summary}
        
        INSTRUCTIONS:
        1. Use the Data Validation Tool to analyze this data summary
        2. Review the tool's output for any issues
        3. Produce a final validation report with ONLY these 4 fields:
           - Status: PASS or FAIL
           - Issues: List any problems found (or 'None')
           - Recommendation: Approve/Reject/Needs Review
           - Confidence: High/Medium/Low
        
        IMPORTANT: 
        - Call the Data Validation Tool first
        - Output ONLY the 4 fields above, no JSON, no explanations
        """,
        expected_output="""
        Status: PASS or FAIL
        Issues: None or list of problems
        Recommendation: Approve/Reject/Needs Review
        Confidence: High/Medium/Low
        """,
        agent=steward_agent
    )