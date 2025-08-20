#
# Module: backtest_runner.py
# Description: Orchestrates the backtesting simulation.
#
# DTS Intraday AI Trading System - Backtest Engine
# Version: 2025-08-16
#
# This file simulates the live trading environment but uses historical data.
#

import logging
from datetime import datetime, date, timedelta
import os
import sys
import pandas as pd

# Set up logging for the module
logging.basicConfig(level=logging.INFO, format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the sys.path to ensure modules can be imported
# when this script is run directly.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the Strategy and its dependencies
from src.strategy import Strategy
from src.data_fetcher import DataFetcher
from src.order_manager import OrderManager
from src.redis_store import RedisStore
from unittest.mock import MagicMock

# Constants for market hours (from your strategy_spec.md and .env)
MARKET_OPEN_TIME = datetime.strptime("09:15", "%H:%M").time()
MARKET_CLOSE_TIME = datetime.strptime("15:30", "%H:%M").time()


class BacktestRunner:
    """
    Orchestrates the backtesting simulation by iterating through historical data
    and applying the trading strategy minute by minute.

    This class simulates the live trading environment but uses historical data
    instead of real-time feeds.
    """

    def __init__(self, strategy: Strategy, start_date: date, end_date: date, symbols: list = ['NIFTY']):
        """
        Initializes the backtest runner with a strategy and date range.

        Args:
            strategy (Strategy): An instance of the trading strategy to backtest.
            start_date (date): The start date for the backtest.
            end_date (date): The end date for the backtest.
            symbols (list): A list of symbols to backtest.
        """
        self.strategy = strategy
        # The data_fetcher is now taken from the strategy instance, which is crucial for testing.
        self.data_fetcher = self.strategy.data_fetcher
        self.start_date = start_date
        self.end_date = end_date
        self.symbols = symbols
        logger.info("BacktestRunner initialized.")

    def run(self):
        """
        Main method to start the backtest simulation.
        """
        logger.info(f"Starting backtest from {self.start_date} to {self.end_date}.")
        current_date = self.start_date
        while current_date <= self.end_date:
            logger.info(f"Simulating market for date: {current_date}")
            self._simulate_day(current_date)
            current_date += timedelta(days=1)
        logger.info("Backtest simulation completed successfully. ✅")

    def _simulate_day(self, current_date: date):
        """
        Simulates one full trading day minute by minute.
        """
        # Fetch all historical data for the day at once
        historical_data = self.data_fetcher.get_historical_data(
            symbols=self.symbols,
            start_date=current_date,
            end_date=current_date,
            interval='1min'
        )

        for symbol, data in historical_data.items():
            if not data.empty and isinstance(data, pd.DataFrame):
                print(f"Simulating candles for {symbol}:", len(data))
                # Loop through each minute's data (candle) and run the strategy
                for timestamp, candle in data.iterrows():
                    current_time = timestamp.time()
                    if MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME:
                        print("Calling strategy.run_for_minute for", timestamp)
                        # The `run_for_minute` method now expects a timestamp and a candle (row of data)
                        self.strategy.run_for_minute(timestamp, candle)

        # At the end of the day, close all open positions
        self.strategy.order_manager.handle_auto_exit()


# Main execution block for running the script directly
if __name__ == "__main__":
    # --- Example Usage ---
    # This block is for direct execution and shows how to set up the runner.
    # We use mocks here for a self-contained example.
    
    # 1. Initialize dependencies with mocks
    redis_store = MagicMock(spec=RedisStore)
    data_fetcher = MagicMock(spec=DataFetcher)
    order_manager = MagicMock(spec=OrderManager, handle_auto_exit=MagicMock())
    
    # Mock get_historical_data to return a small, dummy DataFrame
    dummy_data = pd.DataFrame.from_dict({
        datetime(2025, 1, 1, 9, 15): {'open': 100, 'high': 105, 'low': 99, 'close': 102, 'volume': 1000},
        datetime(2025, 1, 1, 9, 16): {'open': 102, 'high': 106, 'low': 101, 'close': 105, 'volume': 1100},
        datetime(2025, 1, 1, 9, 17): {'open': 105, 'high': 107, 'low': 104, 'close': 106, 'volume': 1200},
        datetime(2025, 1, 1, 9, 18): {'open': 106, 'high': 108, 'low': 105, 'close': 107, 'volume': 1300},
    }, orient='index')
    data_fetcher.get_historical_data.return_value = {'SYMBOL1': dummy_data}
    
    # 2. Initialize the Strategy with its dependencies
    test_strategy = Strategy(
        data_fetcher=data_fetcher,
        ai_module=MagicMock(),
        order_manager=order_manager,
        news_filter=MagicMock(),
    )
    
    # 3. Create and run the BacktestRunner instance
    test_runner = BacktestRunner(
        strategy=test_strategy,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 1)
    )

    test_runner.run()
