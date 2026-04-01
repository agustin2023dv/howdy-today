# tools/validation_tool.py
"""Data Validation Tool for Data Steward Agent"""

from crewai.tools.base_tool import BaseTool

class DataValidationTool(BaseTool):
    name: str = "Data Validation Tool"
    description: str = """
    Validates market data for quality issues including:
    - Missing/null values in critical fields
    - Negative prices or volumes
    - Unusual price movements (>20% daily change)
    - Data completeness checks
    
    Input: Data summary string with ticker, records, null values, etc.
    Output: Validation report with status, issues, recommendation
    """

    def _run(self, data_summary: str) -> str:
        """
        Perform validation on data summary string.
        Returns a formatted validation report.
        """
        issues = []
        
        # Parse the summary for key indicators
        summary_lower = data_summary.lower()
        
        # Check for null values mentioned
        if "null values: 0" not in summary_lower and "null values: none" not in summary_lower:
            if "null values:" in summary_lower:
                issues.append("Missing values detected in data.")
        
        # Check for negative values mentioned
        if "negative values: 0" not in summary_lower and "negative values: none" not in summary_lower:
            if "negative values:" in summary_lower:
                issues.append("Negative values detected in prices or volumes.")
        
        # Check for unusual returns (>20%)
        if "max daily return:" in summary_lower:
            try:
                for line in data_summary.split('\n'):
                    if 'max daily return:' in line.lower():
                        value = float(line.split(':')[1].strip().replace('%', ''))
                        if value > 20:
                            issues.append(f"Unusual price movement detected: {value}%")
                        break
            except:
                pass
        
        # Check for unusual negative returns (<-20%)
        if "min daily return:" in summary_lower:
            try:
                for line in data_summary.split('\n'):
                    if 'min daily return:' in line.lower():
                        value = float(line.split(':')[1].strip().replace('%', ''))
                        if value < -20:
                            issues.append(f"Unusual price drop detected: {value}%")
                        break
            except:
                pass
        
        # Generate report
        status = "PASS" if not issues else "FAIL"
        recommendation = "Approve for load" if status == "PASS" else "Reject - Needs Review"
        confidence = "High" if status == "PASS" else "Medium"
        
        report = f"""
Status: {status}
Issues: {', '.join(issues) if issues else 'None'}
Recommendation: {recommendation}
Confidence: {confidence}
"""
        return report