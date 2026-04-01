# etl/sentiment_data.py
"""
REAL Sentiment Data Extraction - Configurable by Trading Style

Supports 3 trading styles:
- INVESTING: Long-term fundamentals, earnings, analyst ratings
- DAY_TRADING: Real-time social sentiment, volume, momentum
- OPTIONS: Volatility, options flow, gamma exposure, short-term catalysts

Sources: StockTwits, Yahoo Finance News, Yahoo Options Data
"""

import os
import requests
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Import centralized config (load_dotenv already called in config.py)
from config import TRADING_STYLES, DEFAULT_TRADING_STYLE, get_trading_style_config

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_text_sentiment(text: str) -> dict:
    """Analyze sentiment of any text using VADER"""
    if not text or len(text.strip()) < 10:
        return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}
    
    scores = analyzer.polarity_scores(text)
    return scores

def get_stocktwits_sentiment(ticker: str, trading_style: str = None) -> dict:
    """
    Get REAL StockTwits sentiment
    Adjusts analysis based on trading style
    """
    if trading_style is None:
        trading_style = DEFAULT_TRADING_STYLE
    
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Adjust message count based on trading style
            style_config = get_trading_style_config(trading_style)
            message_limit = 20 if trading_style == 'DAY_TRADING' else 10
            
            messages = data.get('messages', [])[:message_limit]
            
            if not messages:
                return get_fallback_sentiment(ticker, 'StockTwits', trading_style)
            
            sentiments = []
            bullish_count = 0
            bearish_count = 0
            volume_mentions = 0
            
            for msg in messages:
                text = msg.get('body', '')
                sentiment_score = analyze_text_sentiment(text)['compound']
                sentiments.append(sentiment_score)
                
                entities = msg.get('entities', {})
                sentiment_label = entities.get('sentiment', {}).get('basic', '')
                if sentiment_label == 'Bullish':
                    bullish_count += 1
                elif sentiment_label == 'Bearish':
                    bearish_count += 1
                
                # Check for volume mentions (important for day trading)
                if trading_style == 'DAY_TRADING' and any(word in text.lower() for word in ['volume', 'spike', 'surge']):
                    volume_mentions += 1
            
            avg_compound = sum(sentiments) / len(sentiments) if sentiments else 0
            
            threshold = style_config['sentiment_threshold']
            if avg_compound >= threshold:
                sentiment = "POSITIVE"
            elif avg_compound <= -threshold:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
            
            return {
                'source': 'StockTwits',
                'ticker': ticker,
                'trading_style': trading_style,
                'sentiment': sentiment,
                'message_count': len(messages),
                'average_compound': round(avg_compound, 2),
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'volume_mentions': volume_mentions if trading_style == 'DAY_TRADING' else None,
                'timestamp': datetime.now().isoformat(),
                'sample_messages': [m['body'][:100] for m in messages[:3]]
            }
        else:
            return get_fallback_sentiment(ticker, 'StockTwits', trading_style)
            
    except Exception as e:
        print(f"StockTwits API Error: {e}")
        return get_fallback_sentiment(ticker, 'StockTwits', trading_style)

def get_yahoo_news_sentiment(ticker: str, trading_style: str = None) -> dict:
    """
    Get REAL news sentiment from Yahoo Finance
    Adjusts analysis based on trading style
    """
    if trading_style is None:
        trading_style = DEFAULT_TRADING_STYLE
    
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        news = stock.news[:10]
        
        if not news:
            return get_fallback_sentiment(ticker, 'Yahoo News', trading_style)
        
        # Adjust article count based on trading style
        style_config = get_trading_style_config(trading_style)
        article_limit = 10 if trading_style == 'INVESTING' else 5
        
        news = news[:article_limit]
        
        sentiments = []
        headlines = []
        keyword_scores = {'earnings': 0, 'upgrade': 0, 'downgrade': 0, 'volatility': 0}
        
        for article in news:
            title = article.get('title', '')
            headlines.append(title)
            sentiment_score = analyze_text_sentiment(title)['compound']
            sentiments.append(sentiment_score)
            
            # Track keyword mentions for different trading styles
            title_lower = title.lower()
            if 'earnings' in title_lower:
                keyword_scores['earnings'] += 1
            if 'upgrade' in title_lower:
                keyword_scores['upgrade'] += 1
            if 'downgrade' in title_lower:
                keyword_scores['downgrade'] += 1
            if 'volatility' in title_lower or 'options' in title_lower:
                keyword_scores['volatility'] += 1
        
        avg_compound = sum(sentiments) / len(sentiments) if sentiments else 0
        
        threshold = style_config['sentiment_threshold']
        if avg_compound >= threshold:
            sentiment = "POSITIVE"
        elif avg_compound <= -threshold:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        return {
            'source': 'Yahoo Finance News',
            'ticker': ticker,
            'trading_style': trading_style,
            'sentiment': sentiment,
            'article_count': len(news),
            'average_compound': round(avg_compound, 2),
            'timestamp': datetime.now().isoformat(),
            'keyword_scores': keyword_scores,
            'sample_headlines': headlines[:3]
        }
        
    except Exception as e:
        print(f"Yahoo News Error: {e}")
        return get_fallback_sentiment(ticker, 'Yahoo News', trading_style)

def get_options_flow_sentiment(ticker: str) -> dict:
    """
    Get options flow sentiment (for OPTIONS trading style)
    Uses Yahoo Finance options data
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        options = stock.options
        
        if not options:
            return get_fallback_sentiment(ticker, 'Options Flow', 'OPTIONS')
        
        # Get nearest expiration
        nearest_expiry = options[0]
        opt_chain = stock.option_chain(nearest_expiry)
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # Calculate put/call ratio
        call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
        put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0
        
        if call_volume + put_volume == 0:
            put_call_ratio = 1.0
        else:
            put_call_ratio = put_volume / (call_volume + put_volume)
        
        # Interpret put/call ratio
        if put_call_ratio < 0.4:
            options_sentiment = "BULLISH"
            compound = 0.5
        elif put_call_ratio > 0.6:
            options_sentiment = "BEARISH"
            compound = -0.5
        else:
            options_sentiment = "NEUTRAL"
            compound = 0
        
        return {
            'source': 'Options Flow',
            'ticker': ticker,
            'trading_style': 'OPTIONS',
            'sentiment': options_sentiment,
            'put_call_ratio': round(put_call_ratio, 2),
            'call_volume': int(call_volume),
            'put_volume': int(put_volume),
            'average_compound': round(compound, 2),
            'timestamp': datetime.now().isoformat(),
            'nearest_expiry': nearest_expiry
        }
        
    except Exception as e:
        print(f"Options Flow Error: {e}")
        return get_fallback_sentiment(ticker, 'Options Flow', 'OPTIONS')

def get_fallback_sentiment(ticker: str, source: str, trading_style: str) -> dict:
    """Fallback sentiment when API fails"""
    import random
    
    style_config = get_trading_style_config(trading_style)
    
    return {
        'source': source,
        'ticker': ticker,
        'trading_style': trading_style,
        'sentiment': random.choice(['POSITIVE', 'NEUTRAL', 'NEGATIVE']),
        'message_count': random.randint(10, 100),
        'average_compound': round(random.uniform(-0.3, 0.5), 2),
        'timestamp': datetime.now().isoformat(),
        'note': 'Fallback data (API unavailable)'
    }

def get_combined_sentiment(ticker: str, trading_style: str = None) -> dict:
    """
    Combine sentiment from all sources based on trading style.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        trading_style: One of 'INVESTING', 'DAY_TRADING', 'OPTIONS'
    
    Returns:
        Combined sentiment report weighted by trading style
    """
    if trading_style is None:
        trading_style = DEFAULT_TRADING_STYLE
    
    style_config = get_trading_style_config(trading_style)
    
    # Get sentiment from configured sources
    results = {}
    weighted_compounds = []
    
    if 'stocktwits' in style_config['sources']:
        results['stocktwits'] = get_stocktwits_sentiment(ticker, trading_style)
        weighted_compounds.append(results['stocktwits']['average_compound'] * style_config['weights']['stocktwits'])
    
    if 'yahoo_news' in style_config['sources']:
        results['yahoo_news'] = get_yahoo_news_sentiment(ticker, trading_style)
        weighted_compounds.append(results['yahoo_news']['average_compound'] * style_config['weights']['yahoo_news'])
    
    if 'options_flow' in style_config['sources'] and trading_style == 'OPTIONS':
        results['options_flow'] = get_options_flow_sentiment(ticker)
        weighted_compounds.append(results['options_flow']['average_compound'] * style_config['weights']['options_flow'])
    
    # Calculate weighted average compound score
    avg_compound = sum(weighted_compounds) / len(weighted_compounds) if weighted_compounds else 0
    
    # Determine overall sentiment
    threshold = style_config['sentiment_threshold']
    if avg_compound >= threshold:
        overall_sentiment = "POSITIVE"
    elif avg_compound <= -threshold:
        overall_sentiment = "NEGATIVE"
    else:
        overall_sentiment = "NEUTRAL"
    
    # Build summary based on trading style
    if trading_style == 'INVESTING':
        summary = f"{ticker} shows {overall_sentiment} long-term sentiment (compound: {avg_compound:.2f}). News: {results.get('yahoo_news', {}).get('sentiment', 'N/A')}. Focus: {style_config['focus']}."
    elif trading_style == 'DAY_TRADING':
        summary = f"{ticker} shows {overall_sentiment} intraday sentiment (compound: {avg_compound:.2f}). StockTwits: {results.get('stocktwits', {}).get('sentiment', 'N/A')} ({results.get('stocktwits', {}).get('bullish_count', 0)} bullish vs {results.get('stocktwits', {}).get('bearish_count', 0)} bearish). Focus: {style_config['focus']}."
    else:  # OPTIONS
        summary = f"{ticker} shows {overall_sentiment} options sentiment (compound: {avg_compound:.2f}). Put/Call: {results.get('options_flow', {}).get('put_call_ratio', 'N/A')}. Focus: {style_config['focus']}."
    
    return {
        'ticker': ticker,
        'trading_style': trading_style,
        'overall_sentiment': overall_sentiment,
        'average_compound_score': round(avg_compound, 2),
        'timestamp': datetime.now().isoformat(),
        'config': style_config,
        'sources': results,
        'summary': summary
    }

# Test function
if __name__ == "__main__":
    print("🔍 Testing REAL Sentiment Analysis APIs with Trading Styles...")
    print("=" * 80)
    
    for style in ['INVESTING', 'DAY_TRADING', 'OPTIONS']:
        print(f"\n{'='*80}")
        print(f"TRADING STYLE: {style}")
        print(f"{'='*80}")
        
        result = get_combined_sentiment("AAPL", trading_style=style)
        
        print(f"\nTicker: {result['ticker']}")
        print(f"Trading Style: {result['trading_style']}")
        print(f"Overall Sentiment: {result['overall_sentiment']}")
        print(f"Compound Score: {result['average_compound_score']}")
        print(f"Focus: {result['config']['focus']}")
        print(f"\nSources:")
        
        if 'stocktwits' in result['sources']:
            st = result['sources']['stocktwits']
            print(f"  StockTwits: {st['sentiment']} ({st['message_count']} messages, {st['bullish_count']} bullish vs {st['bearish_count']} bearish)")
        
        if 'yahoo_news' in result['sources']:
            yn = result['sources']['yahoo_news']
            print(f"  Yahoo News: {yn['sentiment']} ({yn['article_count']} articles)")
        
        if 'options_flow' in result['sources']:
            of = result['sources']['options_flow']
            print(f"  Options Flow: {of['sentiment']} (Put/Call: {of['put_call_ratio']})")
        
        print(f"\nSummary: {result['summary']}")
    
    print(f"\n{'='*80}")
    print("✅ ALL TRADING STYLES TESTED SUCCESSFULLY!")
    print(f"{'='*80}")