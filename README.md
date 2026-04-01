# 🇺🇸 US Market AI-Agent Business Intelligence Pipeline

> An autonomous multi-agent AI system that extracts, validates, analyzes, and generates insights from US stock market data with **social media & news sentiment analysis** for BI decision support.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🎯 Project Goal

Build an end-to-end Business Intelligence pipeline augmented by AI Agents that:
- ✅ Extract market data from Yahoo Finance
- ✅ **Scrape sentiment from social media (Twitter, Reddit) & news sources**
- ✅ Validate data quality autonomously (Data Steward Agent)
- ✅ Generate natural language insights with sentiment context (Market Analyst Agent)
- ✅ Visualize in Power BI Dashboard

**Why This Matters:** Anyone can see stock prices on Google. This system provides **AI-driven sentiment intelligence** from alternative data sources that institutional investors use.

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| **Language** | Python 3.10+ | Core development |
| **Agent Framework** | CrewAI | Multi-agent orchestration |
| **LLM Engine** | Ollama (Llama 3.1) | Local inference, $0 API costs |
| **Market Data** | yfinance | Stock prices, volumes, indexes |
| **Sentiment Data** | Tweepy, PRAW, NewsAPI | Social media & news scraping |
| **Sentiment Analysis** | VADER / TextBlob | NLP sentiment scoring |
| **Database** | SQLite | Structured data storage |
| **BI Tool** | Power BI Desktop | Enterprise visualization |
| **Version Control** | Git + GitHub | Portfolio showcase |

---

## 📁 Project Structure
howdy-today/
├── agents/ # AI Agent definitions
│ ├── steward_agent.py # Data quality validation
│ └── analyst_agent.py # Market insights + sentiment
├── tools/ # Custom agent tools
│ ├── validation_tool.py # Data quality checks
│ └── sentiment_tool.py # Social media & news sentiment
├── tasks/ # Agent task definitions
│ ├── steward_task.py
│ └── analyst_task.py
├── crews/ # Agent crew orchestration
│ ├── steward_crew.py
│ └── analyst_crew.py
├── etl/ # Data extraction pipelines
│ ├── market_data.py # Yahoo Finance extraction
│ └── sentiment_data.py # Social media & news scraping
├── database/ # SQLite database
│ └── schema.sql
├── reports/ # Power BI outputs
│ └── screenshots/
├── docs/ # Documentation
├── main.py # Entry point
├── requirements.txt # Python dependencies
├── README.md # This file
└── .gitignore


---

## 🤖 AI Agents

### 1. Data Steward Agent
| Attribute | Description |
|-----------|-------------|
| **Role** | Senior Data Quality Engineer |
| **Goal** | Validate market data for anomalies before loading |
| **Input** | Raw price/volume data |
| **Output** | Validation report (PASS/FAIL + recommendations) |
| **Tools** | Data Validation Tool |

### 2. Market Analyst Agent
| Attribute | Description |
|-----------|-------------|
| **Role** | Senior Financial Market Analyst |
| **Goal** | Generate insights combining price data + sentiment analysis |
| **Input** | Market data + social media sentiment + news sentiment |
| **Output** | Natural language commentary for BI dashboard |
| **Tools** | Sentiment Analysis Tool |

---

##  Sentiment Analysis Sources

| Source | Type | Data Collected |
|--------|------|----------------|
| **Twitter/X** | Social Media | Mentions, sentiment, volume |
| **Reddit (r/wallstreetbets, r/stocks)** | Social Media | Discussion sentiment, hype indicators |
| **News APIs** | News Articles | Headline sentiment, article tone |
| **Financial Blogs** | News | Analyst opinions, market commentary |

**Sentiment Scoring:**
- 🟢 Positive (>0.05)
- 🟡 Neutral (-0.05 to 0.05)
- 🔴 Negative (<-0.05)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOURUSERNAME/howdy-today.git
cd howdy-today

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure Ollama is running
ollama serve

# 5. Pull Llama model (one-time)
ollama pull llama3.1

# 6. Run the pipeline
python main.py

📈 Sample Output
Data Steward Report

Status:        PASS ✅
Issues:        None
Recommendation: Approve for Load
Confidence:    High

Market Analyst Insight (with Sentiment)

AAPL gained 3.2% today on volume 15% above average. The stock 
outperformed the S&P 500 which rose 1.5%. Social media sentiment 
is strongly positive (0.72) with increased mention volume on 
Twitter and Reddit. News coverage highlights optimistic analyst 
upgrades. Technology sector showing bullish momentum.