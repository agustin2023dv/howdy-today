# main.py
"""
US Market AI-Agent BI Pipeline - Main Entry Point

This module provides the main menu and orchestration for:
- Data Steward Agent (Data Quality Validation)
- Market Analyst Agent (Market Insights with Sentiment)
- ISO Financial MCP Integration Testing

Usage:
    python main.py

Author: Agu Fernandez
GitHub: https://github.com/agustin2023dv/howdy-today
"""

import os
import platform
import shutil
import json
import re

# Import centralized config FIRST (load_dotenv called here once)
from config import DEFAULT_TRADING_STYLE, get_trading_style_config, LLM_MODEL, LLM_BASE_URL


def clear_python_cache():
    """Remove __pycache__ and .pyc files"""
    cache_count = 0
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
                cache_count += 1
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
                cache_count += 1
    return cache_count


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


def run_analyst_agent(trading_style: str = None):
    """Run the Market Analyst Agent"""
    from crews.analyst_crew import run_analyst_crew
    from etl.sentiment_data import get_combined_sentiment
    
    if trading_style is None:
        trading_style = DEFAULT_TRADING_STYLE
    
    # Get sentiment data with trading style
    sentiment = get_combined_sentiment("AAPL", trading_style=trading_style)
    
    # Build sentiment context for agent
    sentiment_text = f"""
    Trading Style: {trading_style}
    Overall Sentiment: {sentiment['overall_sentiment']}
    Compound Score: {sentiment['average_compound_score']}
    Focus: {sentiment['config']['focus']}
    """
    
    # Add source-specific details
    if 'stocktwits' in sentiment['sources']:
        st = sentiment['sources']['stocktwits']
        sentiment_text += f"\nStockTwits: {st['sentiment']} ({st['bullish_count']} bullish vs {st['bearish_count']} bearish)"
    
    if 'yahoo_news' in sentiment['sources']:
        yn = sentiment['sources']['yahoo_news']
        sentiment_text += f"\nYahoo News: {yn['sentiment']} ({yn['article_count']} articles)"
    
    if 'options_flow' in sentiment['sources']:
        of = sentiment['sources']['options_flow']
        sentiment_text += f"\nOptions Flow: {of['sentiment']} (Put/Call: {of['put_call_ratio']})"
    
    test_summary = """
    Ticker: AAPL
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
    print(f"📈  MARKET ANALYST AGENT - {trading_style} INSIGHT REPORT")
    print("=" * 60)
    print()
    
    result = run_analyst_crew(test_summary, sentiment_text)
    result_str = str(result)
    
    # Clean up output - extract meaningful text
    clean_output = result_str
    
    # Strategy 1: Look for text after key phrases
    if 'summary:' in result_str.lower():
        parts = result_str.lower().split('summary:')
        if len(parts) > 1:
            clean_output = parts[-1].strip()
    
    # Strategy 2: Look for quoted text that looks like sentences
    quotes = re.findall(r'"([^"]{50,})"', result_str)
    if quotes:
        best_quote = max(quotes, key=lambda x: x.count('.'))
        if best_quote.count('.') >= 2:
            clean_output = best_quote
    
    # Strategy 3: Look for ticker-based sentences
    ticker_match = re.search(r'(AAPL|MSFT|TSLA|SPY)[^\.]{50,}\.', result_str, re.IGNORECASE)
    if ticker_match:
        clean_output = ticker_match.group(0)
    
    # Clean up artifacts
    clean_output = clean_output.replace('{', '').replace('}', '')
    clean_output = clean_output.replace('"', '')
    clean_output = clean_output.strip()
    
    # Fallback: if too short, show original
    if len(clean_output) < 20:
        clean_output = result_str
    
    print("=" * 60)
    print("✅  ANALYSIS COMPLETE")
    print("=" * 60)
    print()
    print(f"📋  MARKET INSIGHT ({trading_style}):")
    print("-" * 60)
    print(clean_output)
    print("-" * 60)
    print()


def test_iso_mcp():
    """Test ISO Financial MCP integration"""
    from etl.market_data import MarketDataExtractor, ISO_MCP_AVAILABLE
    
    print("=" * 60)
    print("🔍 ISO FINANCIAL MCP INTEGRATION TEST")
    print("=" * 60)
    print()
    
    if not ISO_MCP_AVAILABLE:
        print("❌ iso-financial-mcp not installed!")
        print("   Run: pip install iso-financial-mcp")
        print()
        return
    
    ticker = input("Enter ticker symbol (default: AAPL): ").strip().upper() or "AAPL"
    
    print(f"\n📊 Fetching comprehensive data for {ticker}...")
    print()
    
    extractor = MarketDataExtractor(ticker)
    report = extractor.get_comprehensive_report()
    
    print(f"Ticker: {report['ticker']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Data Sources: {', '.join(report['data_sources'])}")
    print()
    
    # Handle company_info - could be dict or string
    if 'company_info' in report:
        print(f"🏢 Company:")
        company_data = report['company_info']
        if isinstance(company_data, dict):
            print(f"   Name: {company_data.get('longName', 'N/A')}")
            print(f"   Sector: {company_data.get('sector', 'N/A')}")
            print(f"   Industry: {company_data.get('industry', 'N/A')}")
        elif isinstance(company_data, str):
            # If it's a string, print it directly
            print(f"   {company_data[:200]}...")
        else:
            print(f"   Data available (type: {type(company_data).__name__})")
        print()
    
    # Handle earnings
    if 'earnings' in report:
        print(f"💰 Earnings:")
        earnings_data = report['earnings']
        if isinstance(earnings_data, dict):
            print(f"   Data available: Yes")
        elif isinstance(earnings_data, list):
            print(f"   Records: {len(earnings_data)}")
        else:
            print(f"   Data available (type: {type(earnings_data).__name__})")
        print()
    
    # Handle news
    if 'news' in report:
        print(f"📰 News:")
        news_data = report['news']
        if isinstance(news_data, list) and len(news_data) > 0:
            print(f"   Headlines: {len(news_data)} articles")
            for i, article in enumerate(news_data[:3], 1):
                if isinstance(article, dict):
                    title = article.get('title', 'N/A')[:60]
                else:
                    title = str(article)[:60]
                print(f"   {i}. {title}...")
        else:
            print(f"   Data available (type: {type(news_data).__name__})")
        print()
    
    # Handle SEC filings
    if 'sec_filings' in report:
        print(f"📋 SEC Filings:")
        filings_data = report['sec_filings']
        if isinstance(filings_data, list):
            print(f"   Recent filings: {len(filings_data)}")
        else:
            print(f"   Data available (type: {type(filings_data).__name__})")
        print()
    
    # Handle short volume
    if 'short_volume' in report:
        print(f"📉 Short Volume:")
        short_data = report['short_volume']
        if isinstance(short_data, dict):
            print(f"   Data available: Yes")
        else:
            print(f"   Data available (type: {type(short_data).__name__})")
        print()
    
    # Handle trends
    if 'trends' in report:
        print(f"📈 Google Trends:")
        trends_data = report['trends']
        if isinstance(trends_data, dict):
            print(f"   Data available: Yes")
        else:
            print(f"   Data available (type: {type(trends_data).__name__})")
        print()
    
    print("=" * 60)
    print("✅ ISO Financial MCP Test Complete!")
    print("=" * 60)
    print()
    """Test ISO Financial MCP integration"""
    from etl.market_data import MarketDataExtractor, ISO_MCP_AVAILABLE
    
    print("=" * 60)
    print("🔍 ISO FINANCIAL MCP INTEGRATION TEST")
    print("=" * 60)
    print()
    
    if not ISO_MCP_AVAILABLE:
        print("❌ iso-financial-mcp not installed!")
        print("   Run: pip install iso-financial-mcp")
        print()
        return
    
    ticker = input("Enter ticker symbol (default: AAPL): ").strip().upper() or "AAPL"
    
    print(f"\n📊 Fetching comprehensive data for {ticker}...")
    print()
    
    extractor = MarketDataExtractor(ticker)
    report = extractor.get_comprehensive_report()
    
    print(f"Ticker: {report['ticker']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Data Sources: {', '.join(report['data_sources'])}")
    print()
    
    if 'company_info' in report:
        print(f"🏢 Company:")
        print(f"   Name: {report['company_info'].get('longName', 'N/A')}")
        print(f"   Sector: {report['company_info'].get('sector', 'N/A')}")
        print(f"   Industry: {report['company_info'].get('industry', 'N/A')}")
        print()
    
    if 'earnings' in report:
        print(f"💰 Earnings:")
        earnings_data = report['earnings']
        if isinstance(earnings_data, dict):
            print(f"   Data available: Yes")
        print()
    
    if 'news' in report:
        print(f"📰 News:")
        news_data = report['news']
        if isinstance(news_data, list) and len(news_data) > 0:
            print(f"   Headlines: {len(news_data)} articles")
            for i, article in enumerate(news_data[:3], 1):
                if isinstance(article, dict):
                    title = article.get('title', 'N/A')[:60]
                else:
                    title = str(article)[:60]
                print(f"   {i}. {title}...")
        print()
    
    if 'sec_filings' in report:
        print(f"📋 SEC Filings:")
        filings_data = report['sec_filings']
        if isinstance(filings_data, list):
            print(f"   Recent filings: {len(filings_data)}")
        print()
    
    if 'short_volume' in report:
        print(f"📉 Short Volume:")
        print(f"   Data available: Yes")
        print()
    
    if 'trends' in report:
        print(f"📈 Google Trends:")
        print(f"   Data available: Yes")
        print()
    
    print("=" * 60)
    print("✅ ISO Financial MCP Test Complete!")
    print("=" * 60)
    print()


def show_project_info():
    """Display project information and status"""
    print("=" * 60)
    print("🇺  US MARKET AI-AGENT BI PIPELINE")
    print("=" * 60)
    print()
    print("Project Information:")
    print("-" * 60)
    print(f"  LLM Model:      {LLM_MODEL}")
    print(f"  LLM Base URL:   {LLM_BASE_URL}")
    print(f"  Default Style:  {DEFAULT_TRADING_STYLE}")
    print()
    print("Trading Styles Available:")
    print("  - INVESTING    (Long-term fundamentals)")
    print("  - DAY_TRADING  (Short-term momentum)")
    print("  - OPTIONS      (Derivatives & volatility)")
    print()
    print("Data Sources:")
    print("  - StockTwits (Social sentiment)")
    print("  - Yahoo Finance News")
    print("  - SEC EDGAR (Filings)")
    print("  - FINRA (Short volume)")
    print("  - Google Trends")
    print()
    print("GitHub: https://github.com/agustin2023dv/howdy-today")
    print("=" * 60)
    print()


def main():
    """Main menu"""
    cache_cleared = clear_python_cache()
    clear_terminal()
    
    if cache_cleared > 0:
        print(f"🧹 Cleared {cache_cleared} cache files")
        print()
    
    while True:
        print("=" * 60)
        print("🇺  US MARKET AI-AGENT BI PIPELINE")
        print("=" * 60)
        print()
        print("Select an option:")
        print("  1. Data Steward Agent (Validation)")
        print("  2. Market Analyst Agent (Insights)")
        print("  3. Run Both Agents")
        print("  4. Test ISO Financial MCP")
        print("  5. Project Info")
        print("  6. Exit")
        print()
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            run_steward_agent()
            input("\nPress Enter to continue...")
            clear_terminal()
        
        elif choice == '2':
            # Ask for trading style
            print("\nSelect Trading Style:")
            print("  1. INVESTING (Long-term)")
            print("  2. DAY_TRADING (Short-term)")
            print("  3. OPTIONS (Derivatives)")
            style_choice = input("Enter choice (1-3): ").strip()
            
            style_map = {'1': 'INVESTING', '2': 'DAY_TRADING', '3': 'OPTIONS'}
            trading_style = style_map.get(style_choice, 'DAY_TRADING')
            
            run_analyst_agent(trading_style)
            input("\nPress Enter to continue...")
            clear_terminal()
        
        elif choice == '3':
            print("\n" + "=" * 60)
            print("RUNNING BOTH AGENTS")
            print("=" * 60 + "\n")
            
            run_steward_agent()
            
            # Ask for trading style
            print("\nSelect Trading Style:")
            print("  1. INVESTING (Long-term)")
            print("  2. DAY_TRADING (Short-term)")
            print("  3. OPTIONS (Derivatives)")
            style_choice = input("Enter choice (1-3): ").strip()
            
            style_map = {'1': 'INVESTING', '2': 'DAY_TRADING', '3': 'OPTIONS'}
            trading_style = style_map.get(style_choice, 'DAY_TRADING')
            
            run_analyst_agent(trading_style)
            input("\nPress Enter to continue...")
            clear_terminal()
        
        elif choice == '4':
            test_iso_mcp()
            input("\nPress Enter to continue...")
            clear_terminal()
        
        elif choice == '5':
            show_project_info()
            input("\nPress Enter to continue...")
            clear_terminal()
        
        elif choice == '6':
            print("\nExiting... Goodbye! 👋")
            print()
            return
        
        else:
            print("\nInvalid choice. Please enter a number between 1-6.")
            print()


if __name__ == "__main__":
    main()