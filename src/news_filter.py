#
# Module: news_filter.py
# Description: Applies news sentiment analysis to filter out trades.
#
# DTS Intraday AI Trading System - News & Sentiment Analysis
# Version: 2025-08-15
#
# This module provides functionality to fetch news for specific symbols,
# perform sentiment analysis using a placeholder NLP model, and store
# the results in Redis for the strategy to use as a filter.
#

import logging
import requests
import os
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import finnhub

from src.redis_store import RedisStore

log = logging.getLogger(__name__)

# Placeholder for a news API key
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = "https://example-news-api.com/v2/everything"

class NewsFilter:
    """
    Handles news fetching and sentiment analysis for trade filtering.
    """
    def __init__(self, redis_store: RedisStore):
        self.redis_store = redis_store
        self.finnhub_api_key = os.getenv('FINNHUB_API_KEY')
        if not self.finnhub_api_key:
            log.warning("FINNHUB_API_KEY not found. Finnhub news fetching will be disabled.")
            self.finnhub_client = None
        else:
            self.finnhub_client = finnhub.Client(api_key=self.finnhub_api_key)

    def get_and_analyze_sentiment(self, symbol: str):
        """
        Fetches news headlines for a symbol and performs sentiment analysis.
        Stores the resulting sentiment score in Redis.
        """
        log.info(f"Fetching news for {symbol}...")
        headlines = self._fetch_news_headlines(symbol)
        if not headlines:
            log.warning(f"No news found for {symbol}.")
            sentiment_score = 0.0 # Neutral if no news
        else:
            log.info(f"Analyzing sentiment for {len(headlines)} headlines...")
            sentiment_score = self._run_nlp_model(headlines)
            
        self.redis_store.r.set(f"news_sentiment:{symbol}", sentiment_score)
        log.info(f"Sentiment score for {symbol} is {sentiment_score:.2f}, stored in Redis.")
        return sentiment_score

    def _fetch_news_headlines(self, symbol: str) -> List[str]:
        """
        Fetches recent news headlines for a given symbol from Finnhub.
        """
        if not self.finnhub_client:
            log.warning("Finnhub client not initialized. Returning mock headlines.")
            # Fallback to mock headlines if API key is missing
            mock_headlines = [
                f"{symbol} announces massive new project.",
                f"Analysts are concerned about {symbol}'s recent earnings.",
                f"Positive market sentiment for the {symbol} sector."
            ]
            return random.sample(mock_headlines, random.randint(0, len(mock_headlines)))

        try:
            # Fetch company news for the symbol for the last 7 days
            # Finnhub expects symbol in uppercase
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            # Use company_news for specific symbol news
            news_items = self.finnhub_client.company_news(symbol.upper(), _from=from_date, to=to_date)
            
            headlines = [item['headline'] for item in news_items if 'headline' in item]
            log.info(f"Fetched {len(headlines)} news headlines for {symbol} from Finnhub.")
            return headlines
        except Exception as e:
            log.error(f"Error fetching news from Finnhub for {symbol}: {e}")
            return [] # Return empty list on error

    def _run_nlp_model(self, headlines: List[str]) -> float:
        """
        Placeholder for an NLP model that performs sentiment analysis.
        """
        # In a real system, this would use a library like NLTK, spaCy, or a custom model.
        # It would return a score, e.g., -1.0 to 1.0 (negative to positive).
        # For now, we simulate a random score based on some mock logic.
        positive_keywords = ["gains", "strong", "positive", "growth", "rally", "upbeat"]
        negative_keywords = ["concerns", "weak", "sell-off", "risk", "down", "crisis"]

        score = 0
        for headline in headlines:
            headline_lower = headline.lower()
            for keyword in positive_keywords:
                if keyword in headline_lower:
                    score += 0.5
            for keyword in negative_keywords:
                if keyword in headline_lower:
                    score -= 0.5
        
        # Ensure score is within the -1.0 to 1.0 range
        return max(-1.0, min(1.0, score))
