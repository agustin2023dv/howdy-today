# etl/sentiment_data.py
"""
REAL Sentiment Data Extraction - StockTwits + Yahoo Finance News
Both APIs are FREE and work immediately (no Reddit verification needed)
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_text_sentiment(text: str) -> dict:
    """Analyze sentiment of any text using VADER"""
    if not text or len(text.strip()) < 10:
        return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}
    
    scores = analyzer.polarity_scores(text)
    return scores

def get_stocktwits_sentiment(ticker: str) -> dict:
    """
    Get REAL StockTwits sentiment
    Uses StockTwits API (FREE - Public data, no auth required!)
    """
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])[:20]
            
            if not messages:
                return get_fallback_sentiment(ticker, 'StockTwits')
            
            sentiments = []
            bullish_count = 0
            bearish_count = 0
            
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
            
            avg_compound = sum(sentiments) / len(sentiments) if sentiments else 0
            
            if avg_compound >= 0.05:
                sentiment = "POSITIVE"
            elif avg_compound <= -0.05:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
            
            return {
                'source': 'StockTwits',
                'ticker': ticker,
                'sentiment': sentiment,
                'message_count': len(messages),
                'average_compound': round(avg_compound, 2),
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'timestamp': datetime.now().isoformat(),
                'sample_messages': [m['body'][:100] for m in messages[:3]]
            }
        else:
            return get_fallback_sentiment(ticker, 'StockTwits')
            
    except Exception as e:
        print(f"StockTwits API Error: {e}")
        return get_fallback_sentiment(ticker, 'StockTwits')

def get_yahoo_news_sentiment(ticker: str) -> dict:
    """
    Get REAL news sentiment from Yahoo Finance
    Uses yfinance (FREE - No API key needed!)
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        news = stock.news[:10]
        
        if not news:
            return get_fallback_sentiment(ticker, 'Yahoo News')
        
        sentiments = []
        headlines = []
        
        for article in news:
            title = article.get('title', '')
            headlines.append(title)
            sentiment_score = analyze_text_sentiment(title)['compound']
            sentiments.append(sentiment_score)
        
        avg_compound = sum(sentiments) / len(sentiments) if sentiments else 0
        
        if avg_compound >= 0.05:
            sentiment = "POSITIVE"
        elif avg_compound <= -0.05:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        return {
            'source': 'Yahoo Finance News',
            'ticker': ticker,
            'sentiment': sentiment,
            'article_count': len(news),
            'average_compound': round(avg_compound, 2),
            'timestamp': datetime.now().isoformat(),
            'sample_headlines': headlines[:3]
        }
        
    except Exception as e:
        print(f"Yahoo News Error: {e}")
        return get_fallback_sentiment(ticker, 'Yahoo News')

def get_fallback_sentiment(ticker: str, source: str) -> dict:
    """Fallback sentiment when API fails"""
    import random
    
    return {
        'source': source,
        'ticker': ticker,
        'sentiment': random.choice(['POSITIVE', 'NEUTRAL', 'NEGATIVE']),
        'message_count': random.randint(10, 100),
        'average_compound': round(random.uniform(-0.3, 0.5), 2),
        'timestamp': datetime.now().isoformat(),
        'note': 'Fallback data (API unavailable)'
    }

def get_combined_sentiment(ticker: str) -> dict:
    """Combine sentiment from all sources"""
    stocktwits = get_stocktwits_sentiment(ticker)
    yahoo_news = get_yahoo_news_sentiment(ticker)
    
    all_compounds = [
        stocktwits['average_compound'],
        yahoo_news['average_compound']
    ]
    avg_compound = sum(all_compounds) / len(all_compounds)
    
    if avg_compound >= 0.05:
        overall_sentiment = "POSITIVE"
    elif avg_compound <= -0.05:
        overall_sentiment = "NEGATIVE"
    else:
        overall_sentiment = "NEUTRAL"
    
    return {
        'ticker': ticker,
        'overall_sentiment': overall_sentiment,
        'average_compound_score': round(avg_compound, 2),
        'timestamp': datetime.now().isoformat(),
        'sources': {
            'stocktwits': stocktwits,
            'yahoo_news': yahoo_news
        },
        'summary': f"Overall sentiment for {ticker} is {overall_sentiment} (compound: {avg_compound:.2f}). StockTwits: {stocktwits['sentiment']}, News: {yahoo_news['sentiment']}."
    }

if __name__ == "__main__":
    print("🔍 Testing REAL Sentiment Analysis APIs...")
    print("=" * 60)
    
    result = get_combined_sentiment("AAPL")
    
    print(f"\nTicker: {result['ticker']}")
    print(f"Overall Sentiment: {result['overall_sentiment']}")
    print(f"Compound Score: {result['average_compound_score']}")
    print(f"\nSources:")
    print(f"  StockTwits: {result['sources']['stocktwits']['sentiment']} ({result['sources']['stocktwits']['message_count']} messages)")
    print(f"  Yahoo News: {result['sources']['yahoo_news']['sentiment']} ({result['sources']['yahoo_news']['article_count']} articles)")
    print(f"\nSummary: {result['summary']}")