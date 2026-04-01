# config.py
"""
Centralized Configuration for US Market AI-Agent BI Pipeline

All environment variables and configuration settings are loaded here
at program startup. Import this module wherever config is needed.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables ONCE at startup
# This finds .env file in project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# =============================================================================
# LLM Configuration
# =============================================================================
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")

# =============================================================================
# API Credentials
# =============================================================================
# StockTwits API (Optional - public data works without auth)
STOCKTWITS_CLIENT_ID = os.getenv("STOCKTWITS_CLIENT_ID", "")
STOCKTWITS_CLIENT_SECRET = os.getenv("STOCKTWITS_CLIENT_SECRET", "")

# Reddit API (Optional - not currently used)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

# NewsAPI (Optional backup)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# SerpAPI for Google Trends (Optional)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# =============================================================================
# Trading Style Configuration
# =============================================================================
TRADING_STYLES = {
    'INVESTING': {
        'sources': ['yahoo_news', 'stocktwits'],
        'weights': {'yahoo_news': 0.7, 'stocktwits': 0.3},
        'timeframe_days': 30,
        'focus': 'fundamentals, earnings, analyst ratings',
        'sentiment_threshold': 0.05
    },
    'DAY_TRADING': {
        'sources': ['stocktwits', 'yahoo_news'],
        'weights': {'stocktwits': 0.6, 'yahoo_news': 0.4},
        'timeframe_days': 1,
        'focus': 'social momentum, volume spikes, intraday catalysts',
        'sentiment_threshold': 0.10
    },
    'OPTIONS': {
        'sources': ['stocktwits', 'yahoo_news', 'options_flow'],
        'weights': {'stocktwits': 0.3, 'yahoo_news': 0.2, 'options_flow': 0.5},
        'timeframe_days': 7,
        'focus': 'volatility, options flow, gamma exposure, short-term catalysts',
        'sentiment_threshold': 0.15
    }
}

# Default trading style
DEFAULT_TRADING_STYLE = os.getenv("DEFAULT_TRADING_STYLE", "DAY_TRADING")

# =============================================================================
# Database Configuration
# =============================================================================
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/market_data.db")

# =============================================================================
# Agent Configuration
# =============================================================================
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "False").lower() == "true"
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))

# =============================================================================
# ISO Financial MCP Configuration
# =============================================================================
ISO_MCP_CACHE_TTL = int(os.getenv("ISO_MCP_CACHE_TTL", "3600"))
ISO_MCP_TIMEOUT = int(os.getenv("ISO_MCP_TIMEOUT", "30"))

# =============================================================================
# Utility Functions
# =============================================================================

def get_trading_style_config(trading_style: str) -> dict:
    """Get configuration for a specific trading style"""
    return TRADING_STYLES.get(trading_style, TRADING_STYLES[DEFAULT_TRADING_STYLE])

def get_llm_config() -> dict:
    """Get LLM configuration dictionary"""
    return {
        'model': LLM_MODEL,
        'base_url': LLM_BASE_URL
    }

def validate_config() -> bool:
    """Validate that required configuration is present"""
    required = ['LLM_MODEL', 'LLM_BASE_URL']
    for key in required:
        if not globals().get(key):
            print(f"⚠️  Warning: {key} not set in .env file")
    return True

# Validate config on import
validate_config()