#
# Module: redis_store.py
# Description: Central Redis memory hub for AI comments, trade logs, and live signals.
#
# DTS Intraday AI Trading System - State Management
# Version: 2025-08-15
#
# This module provides a simple, robust interface for reading and writing
# data to a Redis instance, ensuring real-time state synchronization
# across all system modules.
#

import logging
import redis
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Placeholder for constants from your .env
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DB = int(os.getenv('REDIS_DB', 0))

log = logging.getLogger(__name__)

class RedisStore:
    """
    Manages all interactions with the Redis database.
    """
    def __init__(self):
        try:
            self.r = redis.StrictRedis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True # Decode responses to UTF-8
            )
            self.r.ping()
            log.info("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            log.error(f"Failed to connect to Redis: {e}")
            self.r = None # Set to None to prevent further operations

    def is_connected(self) -> bool:
        """Checks if the Redis connection is active."""
        return self.r is not None

    # --- Capital Management ---
    def get_capital(self) -> Optional[float]:
        """Retrieves the current capital from Redis."""
        try:
            capital = self.r.get('capital')
            return float(capital) if capital is not None else None
        except Exception as e:
            log.error(f"Error getting capital from Redis: {e}")
            return None

    def set_capital(self, value: float):
        """Sets the current capital in Redis."""
        self.r.set('capital', str(value))

    def update_capital(self, change: float):
        """Atomically updates the capital by a given amount."""
        try:
            self.r.incrbyfloat('capital', change)
        except Exception as e:
            log.error(f"Error updating capital in Redis: {e}")

    # --- Positions and Trade Logs ---
    def get_open_positions(self) -> Dict[str, Any]:
        """Retrieves all open positions."""
        positions = self.r.hgetall('open_positions')
        return {k: json.loads(v) for k, v in positions.items()}

    def get_open_position(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single open position by its ID."""
        position_data = self.r.hget('open_positions', trade_id)
        return json.loads(position_data) if position_data else None

    def add_open_position(self, trade_log: Dict[str, Any]):
        """Adds a new open position to Redis."""
        trade_id = trade_log.get('trade_id')
        if trade_id:
            self.r.hset('open_positions', trade_id, json.dumps(trade_log))

    def remove_open_position(self, trade_id: str):
        """Removes a closed position from the open_positions hash."""
        self.r.hdel('open_positions', trade_id)

    def get_active_positions_count(self) -> int:
        """Returns the number of active positions."""
        return self.r.hlen('open_positions')

    def add_closed_trade(self, trade_log: Dict[str, Any]):
        """Adds a closed trade to the closed_trades list."""
        self.r.lpush('closed_trades', json.dumps(trade_log))

    def get_all_closed_trades(self) -> List[Dict[str, Any]]:
        """Retrieves all closed trades."""
        trades = self.r.lrange('closed_trades', 0, -1)
        return [json.loads(t) for t in trades]
        
    # --- AI Signals and Comments ---
    def store_ai_signals(self, signals: Dict[str, float]):
        """Stores AI signals for consumption by the strategy module."""
        self.r.hmset('ai_signals', {k: str(v) for k, v in signals.items()})

    def get_top_signals(self, count: int = 10) -> Dict[str, float]:
        """Retrieves the top N signals based on score."""
        signals = self.r.hgetall('ai_signals')
        # Sort by score in descending order
        sorted_signals = sorted(signals.items(), key=lambda item: float(item[1]), reverse=True)
        return {k: float(v) for k, v in sorted_signals[:count]}

    def store_ai_comment(self, key: str, comment: str):
        """Stores a daily/weekly/monthly AI comment."""
        # Keys are 'ai_comment:daily', 'ai_comment:weekly', etc.
        self.r.set(f'ai_comment:{key}', comment)

    def get_ai_comment(self, key: str) -> Optional[str]:
        """Retrieves a stored AI comment."""
        return self.r.get(f'ai_comment:{key}')

    # --- Other State Management ---
    def add_to_cooldown(self, symbol: str, duration_seconds: int):
        """Adds a symbol to a cooldown period to prevent re-entry."""
        # Use a separate set or key for cooldown.
        cooldown_key = f'cooldown:{symbol}'
        self.r.setex(cooldown_key, duration_seconds, 'true')

    def is_on_cooldown(self, symbol: str) -> bool:
        """Checks if a symbol is currently in a cooldown period."""
        return self.r.exists(f'cooldown:{symbol}')

    def get_news_sentiment(self, symbol: str) -> Optional[float]:
        """Retrieves a news sentiment score for a symbol."""
        score = self.r.get(f'news_sentiment:{symbol}')
        return float(score) if score else None
        
    def get_trend_status(self, symbol: str) -> Optional[str]:
        """Retrieves the current trend status."""
        return self.r.get(f'trend:{symbol}')

