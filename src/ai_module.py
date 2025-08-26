#
# Module: ai_module.py
# Description: Handles AI scoring, trend detection, AI-TSL, and AI Leverage.
#
# DTS Intraday AI Trading System - AI Module
# Version: 2025-08-15
#
# Note: The AIModule.__init__ has been updated to accept a redis_store instance
# to align with the overall system architecture for storing AI signals and data.
#

import logging
import pandas as pd
import datetime

# Import RedisStore for proper type hinting
from src.redis_store import RedisStore

class AIModule:
    """
    Handles all AI-driven aspects of the trading strategy, including
    signal scoring, trend analysis, and dynamic adjustments.
    """
    # FIX: Add redis_store as a required positional argument
    def __init__(self, redis_store: RedisStore):
        """
        Initializes the AI module.
        
        Args:
            redis_store (RedisStore): The Redis store instance for state management.
        """
        logging.info("AIModule initialized.")
        self.redis_store = redis_store
        self.trend_data = {}

    def get_signal_score(self, symbol, data):
        """
        Scores a potential trade signal based on momentum, volume, and news sentiment.
        
        This is a mock implementation for backtesting. In a live system, this would
        interface with a more complex AI model.
        
        Args:
            symbol (str): The stock symbol.
            data (pd.DataFrame): The historical OHLCV data for the symbol.
            
        Returns:
            float: A score representing the signal strength (e.g., 0.0 to 1.0).
        """
        # Placeholder for AI scoring logic.
        # For a passing test, we'll return a score greater than zero.
        if not data.empty:
            # Simple scoring based on a recent price change
            last_price = data['close'].iloc[-1]
            first_price = data['close'].iloc[0]
            
            # Use Redis to store the signal score, as per your spec
            score = 0.5 # Default score
            if last_price > first_price:
                score = 0.8 # A stronger score for an upward trend
            
            # This is where you would save the score to Redis
            self.redis_store.set(f"ai_score:{symbol}", score)
            
            return score
        
        # This will be stored in Redis as per the spec in live trading
        self.redis_store.set(f"ai_score:{symbol}", 0.0)
        return 0.0

    def get_trade_direction(self, symbol):
        """
        Determines the trade direction (BUY/SELL) based on the AI signal.
        """
        # This is a mock implementation.
        # It would use the AI score and other factors from the AI module.
        signal_score = self.redis_store.get(f"ai_score:{symbol}")
        if signal_score and float(signal_score) > 0.7:
            return 'BUY'
        return None
    
    def get_trend_direction(self, data: pd.DataFrame):
        """
        Detects the current trend direction using a simplified AI approach.
        
        Args:
            data (pd.DataFrame): The historical OHLCV data for the symbol.
        
        Returns:
            str: The detected trend.
        """
        # Placeholder for AI-driven trend detection.
        # This is a simplified example.
        if len(data) >= 5:
            if data['close'].iloc[-1] > data['close'].iloc[-5]:
                return 'UP'
            elif data['close'].iloc[-1] < data['close'].iloc[-5]:
                return 'DOWN'
        return 'NEUTRAL'

    def get_ai_tsl_percentage(self, symbol, current_pnl):
        """
        Calculates a dynamic AI-driven trailing stop-loss percentage.
        
        Args:
            symbol (str): The stock symbol.
            current_pnl (float): The current PnL of the position.
            
        Returns:
            float: The dynamic TSL percentage.
        """
        # Placeholder logic: TSL tightens as PnL increases.
        if current_pnl > 0.05:
            return 0.5  # Lock in half a percent profit
        return 1.0

    def get_ai_leverage_multiplier(self, symbol, signal_score):
        """
        Determines the AI-driven leverage multiplier based on signal strength.
        
        Args:
            symbol (str): The stock symbol.
            signal_score (float): The signal score from get_signal_score.
            
        Returns:
            float: The leverage multiplier.
        """
        # Placeholder logic: leverage increases with signal strength.
        if signal_score > 0.9:
            return 10.0
        elif signal_score > 0.7:
            return 5.0
        return 1.0

    def adjust_trailing_sl_ai(self, trade, market_data, ai_score):
        """
        Dynamically adjusts trailing stop-loss levels based on AI scoring, volatility, 
        leverage, and market regime.
        
        Args:
            trade (dict): Current trade object with entry_price, direction, trailing_sl, etc.
            market_data (pd.DataFrame): Current market data snapshot
            ai_score (float or dict): AI signal score or dict with multiple scores
            
        Returns:
            dict: Updated trade object with adjusted trailing_sl
            
        Future Enhancements:
        - News sentiment integration for TSL adjustment
        - Market regime detection (trending vs ranging)
        - Dynamic leverage based on AI confidence
        - Volatility-based TSL tightening/loosening
        """
        # Placeholder implementation - return trade with minimal adjustment
        updated_trade = trade.copy()
        
        # Simple TSL adjustment based on AI score
        if isinstance(ai_score, (int, float)):
            score = ai_score
        else:
            # If ai_score is a dict, extract the main score
            score = ai_score.get('signal_score', 0.5) if isinstance(ai_score, dict) else 0.5
        
        # Basic TSL adjustment logic (placeholder)
        current_price = market_data['close'].iloc[-1] if not market_data.empty else trade['entry_price']
        
        if trade['direction'] == 'BUY':
            # Tighter TSL for high confidence signals
            if score > 0.8:
                new_tsl = current_price * 0.98  # 2% TSL for high confidence
            elif score > 0.6:
                new_tsl = current_price * 0.97  # 3% TSL for medium confidence
            else:
                new_tsl = current_price * 0.95  # 5% TSL for low confidence
            
            # Only update if new TSL is higher (better protection)
            if new_tsl > trade.get('trailing_sl', 0):
                updated_trade['trailing_sl'] = new_tsl
                
        elif trade['direction'] == 'SELL':
            # For short positions, TSL is below current price
            if score > 0.8:
                new_tsl = current_price * 1.02  # 2% TSL for high confidence
            elif score > 0.6:
                new_tsl = current_price * 1.03  # 3% TSL for medium confidence
            else:
                new_tsl = current_price * 1.05  # 5% TSL for low confidence
            
            # Only update if new TSL is lower (better protection for shorts)
            if new_tsl < trade.get('trailing_sl', float('inf')):
                updated_trade['trailing_sl'] = new_tsl
        
        return updated_trade
