#
# Module: test_integration.py
# Description: Integration tests for the DTS Intraday AI Trading System.
# Version: 2025-08-16
#
# This file tests the end-to-end pipeline of the backtest runner.
#

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, timedelta
import pandas as pd
import os
import sys

# Add the project root to the sys.path to ensure modules can be imported.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import core modules
from src.strategy import Strategy
from src.backtest_runner import BacktestRunner
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher
from src.redis_store import RedisStore

# Constants for test data
TEST_START_DATE = date(2025, 8, 15)
TEST_END_DATE = date(2025, 8, 15)
TEST_SYMBOL = 'NIFTY'

# Mock data in the correct pandas DataFrame format
MOCK_OHLCV_DATA = pd.DataFrame.from_dict({
    datetime(2025, 8, 15, 9, 15): {'open': 100, 'high': 105, 'low': 98, 'close': 102, 'volume': 1000},
    datetime(2025, 8, 15, 9, 16): {'open': 102, 'high': 108, 'low': 101, 'close': 107, 'volume': 1500}
}, orient='index')


class TestIntegration(unittest.TestCase):
    """
    Tests the full backtest pipeline by mocking external dependencies
    and verifying the flow of execution.
    """

    def setUp(self):
        """
        Set up the necessary mocks and BacktestRunner instance for testing.
        """
        # Mock dependencies
        self.mock_data_fetcher = MagicMock(spec=DataFetcher)
        self.mock_data_fetcher.get_historical_data.return_value = {TEST_SYMBOL: MOCK_OHLCV_DATA}
        
        self.mock_order_manager = MagicMock(spec=OrderManager)
        self.mock_order_manager.get_open_positions.return_value = []
        self.mock_order_manager.close_all_positions_eod = MagicMock()
        
        self.mock_ai_module = MagicMock()
        self.mock_news_filter = MagicMock()

        # Configure a mock strategy instance with its dependencies
        self.strategy = Strategy(
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            order_manager=self.mock_order_manager,
            news_filter=self.mock_news_filter,
        )

        # Create the BacktestRunner instance
        self.runner = BacktestRunner(
            strategy=self.strategy,
            start_date=TEST_START_DATE.strftime('%Y-%m-%d'),
            end_date=TEST_END_DATE.strftime('%Y-%m-%d')
        )
        
        # Ensure the runner has the correct data_fetcher
        self.runner.data_fetcher = self.mock_data_fetcher


    def test_full_backtest_pipeline(self):
        """
        Tests the entire backtest pipeline from run() to EOD cleanup.
        """
        print("\n--- Running Integration Test: test_full_backtest_pipeline ---")

        # Patch the method we want to test for its call count
        # CORRECT: Capture the mock object in a variable
        with patch.object(self.runner.strategy, 'run_for_minute') as mock_run_for_minute:
            self.runner.run()

            # Assertions to verify the flow.
            # 1. The historical data should be fetched once for the test day.
            self.mock_data_fetcher.get_historical_data.assert_called_once()
            
            # 2. The strategy's run_for_minute should be called for each minute of data.
            expected_calls = len(MOCK_OHLCV_DATA.index)
            self.assertEqual(mock_run_for_minute.call_count, expected_calls)

            # 3. The end-of-day cleanup function should be called at the end.
            self.mock_order_manager.close_all_positions_eod.assert_called_once()
            
            # Optional: Print success message
            print("Integration test passed successfully. 👍")


