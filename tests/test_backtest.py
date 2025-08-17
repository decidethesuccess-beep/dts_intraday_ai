import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, time, timedelta
import os
import sys
import pandas as pd

# Add the project root to the sys.path to ensure module imports work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the necessary modules from your project
from src.backtest_runner import BacktestRunner
from src.strategy import Strategy
from src.order_manager import OrderManager
from src.redis_store import RedisStore


class TestBacktestRunner(unittest.TestCase):
    """
    Unit tests for the BacktestRunner class, focusing on its core logic
    and interactions with other modules.
    """

    def setUp(self):
        """
        Set up the necessary mock objects and an instance of BacktestRunner
        before each test case.
        """
        # Mock the dependencies that the BacktestRunner needs directly
        self.mock_order_manager = MagicMock(spec=OrderManager)
        self.mock_data_fetcher = MagicMock()
        
        # Explicitly mock the close_all_positions_eod method on the mock_order_manager
        self.mock_order_manager.close_all_positions_eod = MagicMock()

        # Mock the strategy and attach the other mocks to it
        # This mirrors how BacktestRunner will access them (e.g., self.strategy.data_fetcher)
        self.mock_strategy = MagicMock(spec=Strategy)
        self.mock_strategy.data_fetcher = self.mock_data_fetcher
        self.mock_strategy.order_manager = self.mock_order_manager
        self.mock_strategy.run_for_minute = MagicMock()

        # Create a real pandas DataFrame for the mock data
        dummy_data = {
            datetime(2025, 8, 15, 9, 15): {'open': 100, 'high': 105, 'low': 99, 'close': 102, 'volume': 1000},
            datetime(2025, 8, 15, 9, 16): {'open': 102, 'high': 106, 'low': 101, 'close': 104, 'volume': 1200},
            datetime(2025, 8, 15, 15, 29): {'open': 104, 'high': 105, 'low': 103, 'close': 104, 'volume': 800},
            datetime(2025, 8, 15, 15, 30): {'open': 104, 'high': 105, 'low': 103, 'close': 104, 'volume': 900},
        }

        # Ensure the mock data fetcher returns a dict of real DataFrames
        self.mock_data_fetcher.get_historical_data.return_value = {
            'SYMBOL1': pd.DataFrame.from_dict(dummy_data, orient='index')
        }

        # FIX: Pass the dates as strings to match the BacktestRunner's constructor
        self.runner = BacktestRunner(
            strategy=self.mock_strategy,
            start_date="2025-08-15",
            end_date="2025-08-15"
        )

    def test_run_orchestration_flow(self):
        """
        Tests if the BacktestRunner correctly orchestrates the main loop.
        - Verifies that `run_for_minute` is called for each data point.
        - Verifies that the EOD cleanup (`close_all_positions_eod`) is called.
        """
        # Run the backtest
        self.runner.run()

        # Assertions to verify the flow.
        # Check that the strategy's core logic was called
        expected_calls = len(self.mock_data_fetcher.get_historical_data.return_value['SYMBOL1'].index)
        self.assertEqual(self.mock_strategy.run_for_minute.call_count, expected_calls)

        # Check that the EOD cleanup method on the order_manager was called exactly once
        # This confirms the runner correctly orchestrates the final step.
        self.mock_order_manager.close_all_positions_eod.assert_called_once()
