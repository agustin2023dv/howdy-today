# etl/market_data.py
"""
Market Data Extraction using ISO Financial MCP

Provides comprehensive financial data through Model Context Protocol:
- Core market data (Yahoo Finance)
- Financial statements (Balance Sheet, Income, Cash Flow)
- SEC Filings (EDGAR)
- FINRA Short Volume
- Earnings Calendar
- News Headlines
- Google Trends

Documentation: https://pypi.org/project/iso-financial-mcp/
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    from iso_financial_mcp.server import (
        get_info,
        get_historical_prices,
        get_financials,
        get_balance_sheet,
        get_cash_flow,
        get_earnings_calendar,
        get_news_headlines,
        get_sec_filings,
        get_finra_short_volume,
        get_google_trends,
        get_options_expirations,
        get_option_chain,
    )
    ISO_MCP_AVAILABLE = True
except ImportError:
    ISO_MCP_AVAILABLE = False
    print("⚠️  Warning: iso-financial-mcp not installed. Run: pip install iso-financial-mcp")

from config import ISO_MCP_CACHE_TTL, ISO_MCP_TIMEOUT


class MarketDataExtractor:
    """
    Unified market data extractor using ISO Financial MCP.
    All methods return consistent dictionary format for easy integration.
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get company profile and basic information"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('company_info')
        
        try:
            result = asyncio.run(get_info(self.ticker))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (Yahoo Finance)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('company_info'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_historical_data(self, period: str = '1mo', interval: str = '1d') -> Dict[str, Any]:
        """Get historical price data with OHLCV"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('historical')
        
        try:
            result = asyncio.run(get_historical_prices(self.ticker, period, interval))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (Yahoo Finance)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('historical'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_financial_statements(self, freq: str = 'quarterly') -> Dict[str, Any]:
        """Get income statement, balance sheet, and cash flow"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('financials')
        
        try:
            financials = asyncio.run(get_financials(self.ticker, freq))
            balance_sheet = asyncio.run(get_balance_sheet(self.ticker, freq))
            cash_flow = asyncio.run(get_cash_flow(self.ticker, freq))
            
            return {
                'success': True,
                'data': {
                    'income_statement': financials,
                    'balance_sheet': balance_sheet,
                    'cash_flow': cash_flow
                },
                'source': 'ISO Financial MCP',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('financials'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_earnings_data(self) -> Dict[str, Any]:
        """Get earnings calendar with estimates and surprises"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('earnings')
        
        try:
            result = asyncio.run(get_earnings_calendar(self.ticker))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (Yahoo/Nasdaq)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('earnings'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_sec_filings(self, form_types: str = "8-K,10-Q,10-K", lookback_days: int = 30) -> Dict[str, Any]:
        """Get SEC filings from EDGAR"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('sec_filings')
        
        try:
            result = asyncio.run(get_sec_filings(self.ticker, form_types, lookback_days))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (SEC EDGAR)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('sec_filings'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_short_volume(self, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        """Get FINRA short volume data"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('short_volume')
        
        try:
            result = asyncio.run(get_finra_short_volume(self.ticker, start_date, end_date))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (FINRA)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('short_volume'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_news(self, limit: int = 10, lookback_days: int = 3) -> Dict[str, Any]:
        """Get news headlines with sentiment"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('news')
        
        try:
            result = asyncio.run(get_news_headlines(self.ticker, limit, lookback_days))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (Yahoo Finance RSS)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('news'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_trends_data(self, window_days: int = 30) -> Dict[str, Any]:
        """Get Google Trends social momentum data"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('trends')
        
        try:
            result = asyncio.run(get_google_trends(self.ticker, window_days))
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (Google Trends)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('trends'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_options_data(self, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Get options chain with Greeks"""
        if not ISO_MCP_AVAILABLE:
            return self._fallback_data('options')
        
        try:
            if expiration_date:
                result = asyncio.run(get_option_chain(self.ticker, expiration_date))
            else:
                expirations = asyncio.run(get_options_expirations(self.ticker))
                result = {'expirations': expirations, 'note': 'Use expiration_date for full chain'}
            
            return {
                'success': True,
                'data': result,
                'source': 'ISO Financial MCP (Yahoo Options)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': self._fallback_data('options'),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """
        Get comprehensive market data report for AI agent consumption.
        Combines all data sources into a single structured report.
        """
        report = {
            'ticker': self.ticker,
            'timestamp': datetime.now().isoformat(),
            'data_sources': []
        }
        
        # Get all data
        company_info = self.get_company_info()
        if company_info['success']:
            report['company_info'] = company_info['data']
            report['data_sources'].append('Company Info')
        
        earnings = self.get_earnings_data()
        if earnings['success']:
            report['earnings'] = earnings['data']
            report['data_sources'].append('Earnings')
        
        news = self.get_news(limit=5, lookback_days=3)
        if news['success']:
            report['news'] = news['data']
            report['data_sources'].append('News')
        
        sec_filings = self.get_sec_filings(lookback_days=7)
        if sec_filings['success']:
            report['sec_filings'] = sec_filings['data']
            report['data_sources'].append('SEC Filings')
        
        short_volume = self.get_short_volume()
        if short_volume['success']:
            report['short_volume'] = short_volume['data']
            report['data_sources'].append('Short Volume')
        
        trends = self.get_trends_data(window_days=7)
        if trends['success']:
            report['trends'] = trends['data']
            report['data_sources'].append('Google Trends')
        
        return report
    
    def _fallback_data(self, data_type: str) -> Dict[str, Any]:
        """Fallback data when ISO MCP is unavailable"""
        return {
            'note': 'Fallback data - ISO Financial MCP not available',
            'ticker': self.ticker,
            'type': data_type
        }


# Test function
if __name__ == "__main__":
    print("🔍 Testing ISO Financial MCP Integration...")
    print("=" * 80)
    
    if not ISO_MCP_AVAILABLE:
        print("❌ iso-financial-mcp not installed!")
        print("   Run: pip install iso-financial-mcp")
    else:
        extractor = MarketDataExtractor("AAPL")
        
        print("\n📊 Getting Comprehensive Market Report...")
        report = extractor.get_comprehensive_report()
        
        print(f"\nTicker: {report['ticker']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Data Sources: {', '.join(report['data_sources'])}")
        
        if 'company_info' in report:
            print(f"\n📈 Company Info:")
            print(f"   Long Name: {report['company_info'].get('longName', 'N/A')}")
            print(f"   Sector: {report['company_info'].get('sector', 'N/A')}")
            print(f"   Industry: {report['company_info'].get('industry', 'N/A')}")
        
        if 'earnings' in report:
            print(f"\n💰 Earnings:")
            earnings_data = report['earnings']
            if isinstance(earnings_data, dict):
                print(f"   Data available: Yes")
        
        if 'news' in report:
            print(f"\n📰 News:")
            news_data = report['news']
            if isinstance(news_data, list) and len(news_data) > 0:
                print(f"   Headlines: {len(news_data)} articles")
                for i, article in enumerate(news_data[:3], 1):
                    title = article.get('title', 'N/A')[:60] if isinstance(article, dict) else str(article)[:60]
                    print(f"   {i}. {title}...")
        
        if 'sec_filings' in report:
            print(f"\n📋 SEC Filings:")
            filings_data = report['sec_filings']
            if isinstance(filings_data, list) and len(filings_data) > 0:
                print(f"   Recent filings: {len(filings_data)}")
        
        if 'short_volume' in report:
            print(f"\n📉 Short Volume:")
            short_data = report['short_volume']
            if isinstance(short_data, dict):
                print(f"   Data available: Yes")
        
        if 'trends' in report:
            print(f"\n📈 Google Trends:")
            trends_data = report['trends']
            if isinstance(trends_data, dict):
                print(f"   Data available: Yes")
        
        print(f"\n{'='*80}")
        print("✅ ISO Financial MCP Integration Test Complete!")
        print(f"{'='*80}")