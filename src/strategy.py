#
# Module: strategy.py
# Description: Orchestrates all modules and makes entry/exit decisions.
#
# DTS Intraday AI Trading System - Strategy Orchestrator
# Version: 2025-08-15
#
# Note: Updated to handle a new dependency: redis_store, and to correctly pass it to NewsFilter.
#

import logging
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher
from src.ai_module import AIModule
from src.news_filter import NewsFilter
from src.constants import TRADE_MODE, MAX_ACTIVE_POSITIONS

class Strategy:
    """
    Orchestrates the trading strategy, making entry and exit decisions.
    """
    def __init__(self, data_fetcher=None, ai_module=None, order_manager=None, news_filter=None, config=None, redis_store=None):
        """
        Initializes the strategy with all dependent modules.
        
        Args:
            data_fetcher (DataFetcher): The data fetching module.
            ai_module (AIModule): The AI module.
            order_manager (OrderManager): The order management module.
            news_filter (NewsFilter): The news filtering module.
            config (dict): The configuration dictionary for strategy parameters.
            redis_store (RedisStore): The Redis state management module.
        """
        self.data_fetcher = data_fetcher or DataFetcher()
        self.ai_module = ai_module or AIModule()
        self.order_manager = order_manager or OrderManager(mode=TRADE_MODE)
        self.redis_store = redis_store
        
        # This line is updated to pass the redis_store to NewsFilter if one isn't provided.
        self.news_filter = news_filter or NewsFilter(redis_store=self.redis_store)
        
        self.open_positions = {}
        
        # Store the config and extract key parameters with defaults
        self.config = config or {}
        self.top_n_symbols = self.config.get('TOP_N_SYMBOLS', 100)
        self.capital_per_trade_pct = self.config.get('CAPITAL_PER_TRADE_PCT', 10.0)

        logging.info("Strategy module initialized.")

    def run_for_minute(self, timestamp, historical_data):
        """
        This is the main loop function called for each minute of the backtest.
        It checks for new entries and manages open positions.
        
        Args:
            timestamp (datetime.datetime): The current timestamp.
            historical_data (dict): A dictionary of DataFrames with historical data for all symbols.
        """
        self.check_for_new_entry_signals(timestamp, historical_data)
        self.check_for_exit_signals(timestamp, historical_data)

    def check_for_new_entry_signals(self, timestamp, historical_data):
        """
        Checks for new trade entry signals based on AI scoring.
        
        Args:
            timestamp (datetime.datetime): The current timestamp.
            historical_data (dict): A dictionary of DataFrames with historical data.
        """
        # This is a simplified, mock implementation.
        # In the real strategy, this would use the AI module to score signals.
        for symbol, data in historical_data.items():
            if len(self.order_manager.get_open_positions()) >= MAX_ACTIVE_POSITIONS:
                # Log a message if the max position limit is reached
                continue

            # Check if there is a signal at the current timestamp
            if timestamp in data.index:
                # Example: If a condition is met, place a new trade
                # For demonstration, we'll place a dummy trade on the first minute.
                if timestamp.hour == 9 and timestamp.minute == 15 and not self.order_manager.get_open_positions():
                    entry_price = data.loc[timestamp, 'open']
                    self.order_manager.place_order(
                        symbol=symbol,
                        direction='BUY',
                        entry_price=entry_price,
                        timestamp=timestamp
                    )
                    break # Place only one trade for now

    def check_for_exit_signals(self, timestamp, historical_data):
        """
        Checks for exit conditions (SL, TSL, Target, Trend-Flip) for all open positions.
        
        Args:
            timestamp (datetime.datetime): The current timestamp.
            historical_data (dict): A dictionary of DataFrames with historical data.
        """
        # This is a simplified, mock implementation.
        # It should check if the current price crosses the SL/TGT/TSL levels.
        open_positions = self.order_manager.get_open_positions()
        
        for trade in open_positions:
            symbol = trade['symbol']
            
            if symbol in historical_data and timestamp in historical_data[symbol].index:
                current_price = historical_data[symbol].loc[timestamp, 'close']
                
                # Check for hard stop loss or target profit
                sl_price = trade['entry_price'] * (1 - trade['sl_percent'] / 100)
                tgt_price = trade['entry_price'] * (1 + trade['target_percent'] / 100)

                if (trade['direction'] == 'BUY' and current_price <= sl_price) or \
                   (trade['direction'] == 'SELL' and current_price >= tgt_price):
                    self.order_manager.close_order(trade['id'], current_price)
                elif (trade['direction'] == 'BUY' and current_price >= tgt_price) or \
                     (trade['direction'] == 'SELL' and current_price <= sl_price):
                    self.order_manager.close_order(trade['id'], current_price)
    
    def close_all_positions_eod(self):
        """
        Closes all open positions at the end of the day.
        """
        self.order_manager.close_all_positions_eod()
