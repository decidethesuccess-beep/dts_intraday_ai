#
# Module: backtest_runner.py
# Description: Historical backtesting engine.
#
# DTS Intraday AI Trading System - Backtest Runner
# Version: 2025-08-18
#
# Fix: Updated __init__ to accept 'symbols' argument for backtesting on specific stocks.
#

import logging
from datetime import date, timedelta, datetime
import os
import sys

# Add the project root to the sys.path to ensure modules can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary dependencies.
from src.strategy import Strategy
from src.data_fetcher import DataFetcher
from src.order_manager import OrderManager
from src.redis_store import RedisStore
from src.constants import MAX_ACTIVE_POSITIONS, TSL_PERCENT, SL_PERCENT, TARGET_PERCENT

logger = logging.getLogger(__name__)

class BacktestRunner:
    """
    Simulates the intraday trading strategy using historical data.
    """
    # Fix: Added the 'symbols' argument to the constructor.
    def __init__(self, strategy, start_date: date, end_date: date, symbols: list):
        """
        Initializes the backtest runner.

        Args:
            strategy (Strategy): The trading strategy instance.
            start_date (date): The start date for the backtest.
            end_date (date): The end date for the backtest.
            symbols (list): A list of symbols to backtest.
        """
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.symbols = symbols
        self.data_fetcher = DataFetcher()

        logger.info(f"BacktestRunner initialized for dates {self.start_date} to {self.end_date}.")

    def run_backtest(self):
        """
        Executes the backtest simulation.
        """
        logger.info("Starting backtest simulation...")
        
        current_date = self.start_date
        while current_date <= self.end_date:
            logger.info(f"Simulating day: {current_date}")
            
            # Fetch historical data for the day
            historical_data = self.data_fetcher.fetch_historical_data(
                self.symbols,
                current_date
            )
            
            if not historical_data:
                logger.warning(f"No historical data found for {current_date}. Skipping day.")
                current_date += timedelta(days=1)
                continue

            # Simulate minute-by-minute
            # Note: This is a simplified loop, assuming 1-minute intervals.
            # A real implementation would handle market hours and intervals more robustly.
            for minute_data in historical_data.values():
                if not minute_data.empty:
                    for timestamp, row in minute_data.iterrows():
                        self.strategy.run_for_minute(timestamp, historical_data)

            # Close all positions at the end of the day
            self.strategy.close_all_positions_eod()

            current_date += timedelta(days=1)

        logger.info("Backtest simulation completed.")
