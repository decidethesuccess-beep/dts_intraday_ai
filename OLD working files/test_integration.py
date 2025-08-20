#
# Module: test_integration.py
# Description: Integration tests for the full trading system pipeline.
#
# DTS Intraday AI Trading System - Integration Tests
# Version: 2025-08-16
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
from src.redis_store import RedisStore
from src.data_fetcher import DataFetcher

# Constants for test data
TEST_START_DATE = date(2025, 8, 15)
TEST_END_DATE = date(2025, 8, 15)
TEST_SYMBOL = 'NIFTY'

# Mock data in the correct pandas DataFrame format
MOCK_OHLCV_DATA = pd.DataFrame.from_dict({
    datetime(2025, 8, 15, 9, 15): {'open': 100, 'high': 105, 'low': 98, 'close': 102, 'volume': 1000},
    datetime(2025, 8, 15, 9, 16): {'open': 102, 'high': 108, 'low': 101, 'close': 107, 'volume': 1100},
    datetime(2025, 8, 15, 9, 17): {'open': 107, 'high': 109, 'low': 105, 'close': 108, 'volume': 1200},
    datetime(2025, 8, 15, 9, 18): {'open': 108, 'high': 110, 'low': 107, 'close': 109, 'volume': 1300},
}, orient='index')

class TestFullBacktest(unittest.TestCase):
    """
    Integration tests for the entire backtesting pipeline.
    """
    def setUp(self):
        """
        Sets up the test environment with mock dependencies for integration testing.
        """
        self.mock_redis = MagicMock(spec=RedisStore)
        self.mock_order_manager = MagicMock(spec=OrderManager, handle_auto_exit=MagicMock())
        
        # FIX: Ensure the mock data fetcher returns a pandas DataFrame.
        self.mock_data_fetcher = MagicMock()
        self.mock_data_fetcher.get_historical_data.return_value = {TEST_SYMBOL: MOCK_OHLCV_DATA}
        
        self.strategy = Strategy(
            data_fetcher=self.mock_data_fetcher,
            order_manager=self.mock_order_manager
        )
        self.runner = BacktestRunner(
            strategy=self.strategy,
            start_date=TEST_START_DATE,
            end_date=TEST_END_DATE,
            symbols=[TEST_SYMBOL]
        )

    def test_full_backtest_pipeline(self):
        """
        Tests the entire backtest pipeline from run() to EOD cleanup.
        """
        print("\n--- Running Integration Test: test_full_backtest_pipeline ---")

        # Mock the run_for_minute method to avoid complex logic within the test.
        with patch.object(self.strategy, 'run_for_minute'):
            self.runner.run()

            # Assertions to verify the flow.
            # 1. The historical data should be fetched once for the test day.
            self.mock_data_fetcher.get_historical_data.assert_called_once()
            
            # 2. The strategy's run_for_minute should be called for each minute of data.
            # Assuming 4 data points in our mock data.
            expected_calls = len(MOCK_OHLCV_DATA.index)
            self.assertEqual(self.strategy.run_for_minute.call_count, expected_calls)

            # 3. The end-of-day cleanup function should be called at the end.
            self.mock_order_manager.handle_auto_exit.assert_called_once()
            
            print("Integration test passed successfully! ✅")
