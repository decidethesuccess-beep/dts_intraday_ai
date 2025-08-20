#
# Module: strategy.py
# Description: Orchestrates all modules and makes entry/exit decisions.
#
# DTS Intraday AI Trading System - Strategy Orchestrator
# Version: 2025-08-20
#
# Note: Added a new master method `check_exit_conditions` to consolidate all
# exit logic and simplify the main loop in the backtest runner.
#
import logging
from datetime import datetime, time
import os
import sys
import pandas as pd

# Add the project root to the sys.path to ensure modules can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary dependencies.
from src.redis_store import RedisStore
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher
from src.ai_module import AIModule
from src.news_filter import NewsFilter
from src.constants import MAX_ACTIVE_POSITIONS, TSL_PERCENT, SL_PERCENT, TARGET_PERCENT, AUTO_EXIT_TIME
from src.config import get_config

# Set up logging for the module
logger = logging.getLogger(__name__)

# Fix: Renamed class back to `Strategy` to align with tests.
class Strategy:
    """
    Orchestrates all modules and makes entry/exit decisions based on
    market data, AI signals, and risk management rules.
    """
    # ✅ FIX: Updated the constructor to accept all key dependencies to align with
    # the system architecture and fix test failures.
    def __init__(self, redis_store: RedisStore, order_manager: OrderManager,
                 data_fetcher: DataFetcher, ai_module: AIModule, news_filter: NewsFilter):
        """
        Initializes the trading strategy with all necessary dependencies.
        """
        self.config = get_config()
        self.redis_store = redis_store
        self.order_manager = order_manager
        self.data_fetcher = data_fetcher
        self.ai_module = ai_module
        self.news_filter = news_filter
        
        # Strategy parameters from config
        self.max_active_positions = self.config.get("MAX_ACTIVE_POSITIONS", MAX_ACTIVE_POSITIONS)
        self.sl_percent = self.config.get("SL_PERCENT", SL_PERCENT)
        self.target_percent = self.config.get("TARGET_PERCENT", TARGET_PERCENT)
        self.tsl_percent = self.config.get("TSL_PERCENT", TSL_PERCENT)
        self.auto_exit_time = self.config.get("AUTO_EXIT_TIME", AUTO_EXIT_TIME)
        # ✅ FIX: Added the `min_profit_mode` attribute to the Strategy class
        self.min_profit_mode = self.config.get("MIN_PROFIT_MODE", False)

    def run_for_minute(self, timestamp: datetime, historical_data: dict):
        """
        Main loop for a single minute of the trading day.
        """
        # Step 1: Check for exit signals on existing positions
        self.check_exit_conditions(timestamp, historical_data)
        
        # Step 2: Check for new entry signals
        self.check_entry_signals(timestamp, historical_data)

    def check_exit_conditions(self, timestamp: datetime, historical_data: dict):
        """
        Consolidates all exit logic checks into a single master method.
        """
        open_positions = self.order_manager.get_open_positions()

        # Only proceed if there are open positions
        if open_positions:
            # Check for various exit signals
            self.check_hard_sl_target(open_positions, historical_data)
            self.check_ai_tsl_exit(open_positions, historical_data)
            self.check_trend_flip_exit(open_positions, historical_data)

        # Check for end-of-day exit
        self.check_eod_exit(timestamp.time())

    def check_hard_sl_target(self, open_positions, historical_data):
        """
        Checks for hard stop-loss or target profit exits.
        """
        # ✅ FIX: Wrap the loop with `list()` to prevent `RuntimeError`.
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue

            current_price = historical_data[symbol]['close'].iloc[-1]
            sl_price = trade['entry_price'] * (1 - self.sl_percent / 100)
            tgt_price = trade['entry_price'] * (1 + self.target_percent / 100)

            if trade['direction'] == 'BUY' and current_price <= sl_price:
                self.order_manager.close_order(symbol, current_price)
                logger.info(f"Position for {symbol} closed due to Hard SL at {current_price}.")
            elif trade['direction'] == 'BUY' and current_price >= tgt_price:
                self.order_manager.close_order(symbol, current_price)
                logger.info(f"Position for {symbol} closed due to Hard TGT at {current_price}.")
            elif trade['direction'] == 'SELL' and current_price >= sl_price:
                self.order_manager.close_order(symbol, current_price)
                logger.info(f"Position for {symbol} closed due to Hard SL at {current_price}.")
            elif trade['direction'] == 'SELL' and current_price <= tgt_price:
                self.order_manager.close_order(symbol, current_price)
                logger.info(f"Position for {symbol} closed due to Hard TGT at {current_price}.")

    def check_ai_tsl_exit(self, open_positions, historical_data):
        """
        Applies a dynamic trailing stop-loss based on AI signals.
        """
        # ✅ FIX: Wrap the loop with `list()` to prevent `RuntimeError`.
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue

            current_price = historical_data[symbol]['close'].iloc[-1]
            
            # Placeholder for TSL logic
            current_pnl = (current_price - trade['entry_price']) / trade['entry_price'] if trade['direction'] == 'BUY' else (trade['entry_price'] - current_price) / trade['entry_price']
            new_tsl_percent = self.ai_module.get_ai_tsl_percentage(symbol, current_pnl)

            # Update TSL based on new percentage
            new_tsl = current_price * (1 - new_tsl_percent / 100)
            if new_tsl > trade['trailing_sl']:
                self.order_manager.update_position(symbol, {'trailing_sl': new_tsl})

            # Check if TSL has been hit
            if current_price <= trade['trailing_sl']:
                self.order_manager.close_order(symbol, current_price)
                logger.info(f"AI-TSL hit for {symbol}. Position closed at {current_price}.")


    def check_trend_flip_exit(self, open_positions, historical_data):
        """
        Checks for a trend flip signal to exit a position early.
        """
        # ✅ FIX: Wrap the loop with `list()` to prevent `RuntimeError`.
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue
            
            data = historical_data[symbol]
            current_trend = self.ai_module.get_trend_direction(data)
            
            if trade['direction'] == 'BUY' and current_trend == 'DOWN':
                self.order_manager.close_order(symbol, data['close'].iloc[-1])
                logger.info(f"Position for {symbol} closed due to trend flip (BUY to DOWN).")
            elif trade['direction'] == 'SELL' and current_trend == 'UP':
                self.order_manager.close_order(symbol, data['close'].iloc[-1])
                logger.info(f"Position for {symbol} closed due to trend flip (SELL to UP).")

    def check_entry_signals(self, timestamp: datetime, historical_data: dict):
        """
        Checks for new trade entry signals based on AI scoring.
        """
        # Placeholder for entry logic
        pass

    def close_all_positions_eod(self):
        """
        Closes all open positions at the end of the day.
        """
        self.order_manager.close_all_positions_eod()

    def check_eod_exit(self, current_time):
        """
        Triggers an end-of-day exit at the specified time.
        """
        try:
            eod_time = datetime.strptime(self.auto_exit_time, "%H:%M").time()
            if current_time >= eod_time:
                self.close_all_positions_eod()
        except ValueError:
            logger.error(f"Invalid AUTO_EXIT_TIME format in config: {self.auto_exit_time}")
            
