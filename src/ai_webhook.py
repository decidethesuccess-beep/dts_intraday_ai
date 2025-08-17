#
# Module: ai_webhook.py
# Description: Sends/receives AI guidance via Gemini AI Studio.
#
# DTS Intraday AI Trading System - AI Webhook Integration
# Version: 2025-08-15
#
# This module is responsible for communicating with the Gemini AI Studio API
# to get daily, weekly, and monthly insights and commentary. It acts as an
# advisory system, storing the AI's output in Redis for the dashboard.
#

import logging
import requests
import json
import os
import time
from typing import Dict, Any, List

from src.redis_store import RedisStore

# Placeholder for API key from .env file
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

log = logging.getLogger(__name__)

class AIWebhook:
    """
    Handles all communication with the Gemini AI Studio API.
    """
    def __init__(self, redis_store: RedisStore):
        self.redis_store = redis_store
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            log.error("GEMINI_API_KEY not found in environment variables.")

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Internal method to make a request to the Gemini API with exponential backoff.
        """
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }

        retries = 0
        while retries < 5:
            try:
                response = requests.post(f"{API_URL}?key={self.api_key}", headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                if result.get('candidates') and result['candidates'][0].get('content'):
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    log.warning(f"AI API returned no content: {result}")
                    return "No insights available."
            except requests.exceptions.RequestException as e:
                log.error(f"Request failed: {e}. Retrying...")
                time.sleep(2 ** retries) # Exponential backoff
                retries += 1
        
        log.error("Failed to get response from Gemini API after multiple retries.")
        return "API connection error. Please check."

    def get_and_store_daily_commentary(self):
        """
        Fetches daily commentary from the AI and stores it in Redis.
        """
        log.info("Requesting daily commentary from Gemini AI...")
        
        # Get last 24 hours of closed trades from Redis
        closed_trades = self.redis_store.get_all_closed_trades()
        recent_trades = [
            trade for trade in closed_trades 
            if datetime.fromisoformat(trade['exit_time']) > datetime.now() - timedelta(hours=24)
        ]
        
        trade_summary = json.dumps(recent_trades)

        prompt = (
            f"As an AI Trading System advisor, provide a summary of the past day's trading activity. "
            f"Analyze the following closed trades and provide actionable suggestions for improvement. "
            f"If there were no trades, provide a general market outlook. "
            f"Trade data: {trade_summary}"
        )

        commentary = self._call_gemini_api(prompt)
        self.redis_store.store_ai_comment('daily', commentary)
        log.info("Daily commentary successfully stored.")

    def get_and_store_weekly_commentary(self):
        """
        Fetches weekly commentary from the AI and stores it in Redis.
        """
        log.info("Requesting weekly commentary from Gemini AI...")
        # Placeholder for weekly data aggregation
        prompt = "Provide a high-level summary of the past week's trading performance."
        commentary = self._call_gemini_api(prompt)
        self.redis_store.store_ai_comment('weekly', commentary)
        log.info("Weekly commentary successfully stored.")
        
    def get_and_store_monthly_commentary(self):
        """
        Fetches monthly commentary from the AI and stores it in Redis.
        """
        log.info("Requesting monthly commentary from Gemini AI...")
        # Placeholder for monthly data aggregation
        prompt = "Provide a detailed summary of the past month's trading performance."
        commentary = self._call_gemini_api(prompt)
        self.redis_store.store_ai_comment('monthly', commentary)
        log.info("Monthly commentary successfully stored.")
