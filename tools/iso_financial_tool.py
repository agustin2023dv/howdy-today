# tools/iso_financial_tool.py
"""ISO Financial MCP Tool for AI Agents"""

from crewai.tools.base_tool import BaseTool
from etl.market_data import MarketDataExtractor

class ISOFINANCIALTool(BaseTool):
    name: str = "ISO Financial Data Tool"
    description: str = """
    Provides comprehensive financial market data through ISO Financial MCP.
    
    Available data sources:
    - Company profile and basic information
    - Historical prices (OHLCV)
    - Financial statements (Balance Sheet, Income, Cash Flow)
    - SEC Filings (10-K, 10-Q, 8-K)
    - FINRA Short Volume
    - Earnings Calendar with estimates
    - News Headlines
    - Google Trends social momentum
    - Options chain with Greeks
    
    Input: Ticker symbol and data type request
    Output: Structured financial data for analysis
    """

    def _run(self, ticker: str, data_type: str = "comprehensive") -> str:
        """
        Get financial data for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            data_type: Type of data requested (comprehensive, company, earnings, news, sec, short, trends)
        
        Returns:
            Formatted financial data summary
        """
        try:
            extractor = MarketDataExtractor(ticker)
            
            if data_type == "comprehensive":
                result = extractor.get_comprehensive_report()
                
                # Format for agent consumption
                summary = f"""
COMPREHENSIVE MARKET REPORT: {ticker}
{'='*50}
Data Sources: {', '.join(result.get('data_sources', []))}

COMPANY: {result.get('company_info', {}).get('longName', 'N/A')}
SECTOR: {result.get('company_info', {}).get('sector', 'N/A')}

EARNINGS: Data available - {len(result.get('earnings', {}).get('earningsChart', {}).get('quarterly', []))} quarters

NEWS: {len(result.get('news', []))} recent articles

SEC FILINGS: {len(result.get('sec_filings', []))} recent filings

SHORT VOLUME: Data available

GOOGLE TRENDS: Data available

{'='*50}
"""
                return summary
            
            elif data_type == "company":
                result = extractor.get_company_info()
                return f"Company: {result['data'].get('longName', 'N/A')}, Sector: {result['data'].get('sector', 'N/A')}"
            
            elif data_type == "earnings":
                result = extractor.get_earnings_data()
                return f"Earnings data available for {ticker}"
            
            elif data_type == "news":
                result = extractor.get_news(limit=5)
                headlines = result['data'][:3] if isinstance(result['data'], list) else []
                return f"Recent news: {len(headlines)} headlines available"
            
            elif data_type == "sec":
                result = extractor.get_sec_filings()
                return f"SEC filings: {len(result['data'])} recent filings"
            
            elif data_type == "short":
                result = extractor.get_short_volume()
                return f"Short volume data available for {ticker}"
            
            elif data_type == "trends":
                result = extractor.get_trends_data()
                return f"Google trends data available for {ticker}"
            
            else:
                return f"Unknown data type: {data_type}. Use: comprehensive, company, earnings, news, sec, short, trends"
                
        except Exception as e:
            return f"Error fetching data for {ticker}: {str(e)}"