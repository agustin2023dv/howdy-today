# main.py
import os
import platform
import shutil
import json
import re

def clear_python_cache():
    """Remove __pycache__ and .pyc files"""
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def clear_terminal():
    """Clear terminal screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def parse_agent_output(result_str):
    """Extract validation data from agent output"""
    try:
        # Try to find Status in plain text
        status_match = re.search(r'Status:\s*(PASS|FAIL|pass|fail)', result_str, re.IGNORECASE)
        issues_match = re.search(r'Issues:\s*(.+?)(?:\n|$)', result_str, re.IGNORECASE)
        
        if status_match:
            status = status_match.group(1).upper()
            issues = issues_match.group(1).strip() if issues_match else 'None'
        else:
            # Fallback: check for pass/fail keywords anywhere
            if 'pass' in result_str.lower():
                status = 'PASS'
                issues = 'None'
            elif 'fail' in result_str.lower():
                status = 'FAIL'
                issues = 'See details'
            else:
                status = 'UNKNOWN'
                issues = 'Could not parse'
        
        # Derive recommendation and confidence
        if status == 'PASS':
            recommendation = 'Approve for Load'
            confidence = 'High'
        elif status == 'FAIL':
            recommendation = 'Reject - Needs Review'
            confidence = 'Medium'
        else:
            recommendation = 'Manual Review'
            confidence = 'Low'
        
        return {
            'status': status,
            'issues': issues,
            'recommendation': recommendation,
            'confidence': confidence
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'issues': str(e),
            'recommendation': 'Manual Review',
            'confidence': 'Low'
        }

def run_steward_agent():
    """Run the Data Steward Agent"""
    from crews.steward_crew import run_steward_crew
    
    test_summary = """
    Ticker: AAPL
    Date Range: 2026-01-01 to 2026-04-01
    Records: 90
    Fields: Date, Open, High, Low, Close, Volume
    Min Close: 150.25
    Max Close: 185.50
    Avg Volume: 52,000,000
    Null Values: 0
    Negative Values: 0
    Max Daily Return: 3.2%
    Min Daily Return: -2.8%
    """
    
    print("=" * 60)
    print("🤖  DATA STEWARD AGENT - VALIDATION REPORT")
    print("=" * 60)
    print()
    
    result = run_steward_crew(test_summary)
    report = parse_agent_output(str(result))
    
    print("=" * 60)
    print("✅  VALIDATION COMPLETE")
    print("=" * 60)
    print()
    print("📋  FINAL REPORT:")
    print("-" * 60)
    print(f"  Status:        {report['status']} {'✅' if report['status'] == 'PASS' else '❌'}")
    print(f"  Issues:        {report['issues']}")
    print(f"  Recommendation: {report['recommendation']}")
    print(f"  Confidence:    {report['confidence']}")
    print("-" * 60)
    print()

def run_analyst_agent():
    """Run the Market Analyst Agent"""
    from crews.analyst_crew import run_analyst_crew
    
    test_summary = """
    Ticker: AAPL
    Date Range: 2026-01-01 to 2026-04-01
    Current Price: $185.50
    Price Change: +3.2%
    Volume: 52,000,000
    Volume vs Avg: +15%
    52-Week High: $195.00
    52-Week Low: $145.00
    S&P 500 Change: +1.5%
    Sector: Technology
    """
    
    print("=" * 60)
    print("📈  MARKET ANALYST AGENT - INSIGHT REPORT")
    print("=" * 60)
    print()
    
    result = run_analyst_crew(test_summary)
    result_str = str(result)
    
    # Clean up the output - extract only the final insight
    clean_output = result_str
    
    # Strategy 1: Look for text after "summary:" keyword
    if 'summary:' in result_str.lower():
        parts = result_str.lower().split('summary:')
        if len(parts) > 1:
            clean_output = parts[-1].strip()
    
    # Strategy 2: Look for quoted text that looks like a sentence (has periods)
    quotes = re.findall(r'"([^"]{50,})"', result_str)
    if quotes:
        # Find the quote with the most periods (likely a paragraph)
        best_quote = max(quotes, key=lambda x: x.count('.'))
        if best_quote.count('.') >= 2:  # At least 2 sentences
            clean_output = best_quote
    
    # Strategy 3: Look for text that starts with a ticker symbol
    ticker_match = re.search(r'(AAPL|MSFT|TSLA|SPY)[^\.]{50,}\.', result_str, re.IGNORECASE)
    if ticker_match:
        clean_output = ticker_match.group(0)
    
    # Clean up: Remove JSON brackets but keep text
    clean_output = clean_output.replace('{', '').replace('}', '')
    clean_output = clean_output.replace('"', '')
    clean_output = clean_output.strip()
    
    # Final fallback: if output is too short, show original
    if len(clean_output) < 20:
        clean_output = result_str
    
    print("=" * 60)
    print("✅  ANALYSIS COMPLETE")
    print("=" * 60)
    print()
    print("📋  MARKET INSIGHT:")
    print("-" * 60)
    print(clean_output)
    print("-" * 60)
    print()

def main():
    """Main menu"""
    clear_python_cache()
    clear_terminal()
    
    print("=" * 60)
    print("🇺🇸  US MARKET AI-AGENT BI PIPELINE")
    print("=" * 60)
    print()
    print("Select an agent to run:")
    print("  1. Data Steward Agent (Validation)")
    print("  2. Market Analyst Agent (Insights)")
    print("  3. Run Both Agents")
    print("  4. Exit")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        run_steward_agent()
    elif choice == '2':
        run_analyst_agent()
    elif choice == '3':
        print("\n" + "=" * 60)
        print("RUNNING BOTH AGENTS")
        print("=" * 60 + "\n")
        run_steward_agent()
        run_analyst_agent()
    elif choice == '4':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()