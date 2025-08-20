#
# File: test_backtest.py
# Description: Unit and integration tests for the BacktestRunner.
#
# ✅ FIX: The test now correctly initializes the BacktestRunner with
# start and end dates.
#
# ✅ FIX: The test now correctly calls the `run_backtest` method instead
# of the non-existent `run` method.
#
# ✅ FIX: The test now properly mocks the internal loops, preventing the
# hang and turning it into a fast, reliable unit test.
#
# Note: MockOrderManager updated to correctly accept 'quantity' to fix TypeError.
#
# ✅ FIX: The `test_stop_loss_exit` has been updated to correctly call
# the `check_for_exit_signals` method with the correct parameters.
#
# ❌ REMOVED: The patching of `src.backtest_runner.get_config` has been
# removed as it was causing an AttributeError. The BacktestRunner test
# now focuses on the runner's logic and does not mock its dependencies'
# internal config calls.
#

import sys
import os
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import date, datetime, time, timedelta

# Add the project root to the Python path to find the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backtest_runner import BacktestRunner
from src.strategy import Strategy # Note: Import the real class for type hinting/reference
from src.constants import SL_PERCENT # Import constants


# Mock classes to isolate the BacktestRunner logic
class MockStrategy(MagicMock):
    """A mock version of the Strategy class for testing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We need to set up the attributes that are accessed by BacktestRunner
        self.order_manager = MagicMock()
        self.check_entry_signals = MagicMock()
        self.check_for_exit_signals = MagicMock()
        self.close_all_positions_eod = MagicMock()

class MockDataFetcher(MagicMock):
    """A mock version of the DataFetcher for testing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This mock returns a simple, one-minute DataFrame for testing
        self.fetch_historical_data.return_value = {
            'SYMBOL1': pd.DataFrame(
                {'close': [100.0]},
                index=pd.to_datetime(['2025-08-15 09:15:00'])
            )
        }

class MockRedisStore(MagicMock):
    """A mock version of the RedisStore for testing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MockOrderManager(MagicMock):
    """A mock version of the OrderManager for testing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.open_positions = {}
        self.closed_trades = []
        self.close_all_positions_eod = MagicMock()

class TestBacktestRunner(unittest.TestCase):
    """Test suite for the BacktestRunner."""
    
    def setUp(self):
        """
        Set up mock objects and the BacktestRunner instance before each test.
        The runner is now correctly initialized with dates and symbols.
        """
        self.strategy_mock = MockStrategy()
        self.data_fetcher_mock = MockDataFetcher()
        self.redis_mock = MockRedisStore()
        self.order_manager_mock = MockOrderManager()
        
        # Set up a fixed date range for the tests
        start_date = date(2025, 8, 15)
        end_date = date(2025, 8, 16)
        symbols = ['SYMBOL1']
        
        self.runner = BacktestRunner(
            strategy=self.strategy_mock,
            start_date=start_date,
            end_date=end_date,
            symbols=symbols
        )
        self.runner.data_fetcher = self.data_fetcher_mock

    def test_run_backtest_loop(self):
        """
        Tests the core loop logic of the BacktestRunner without running a
        full simulation by mocking the internal `run_for_minute` and
        `close_all_positions_eod` calls. This ensures the test is fast
        and doesn't hang.
        """
        # Patch the actual methods to verify they are called
        with patch.object(self.strategy_mock, 'run_for_minute') as mock_run_for_minute, \
             patch.object(self.strategy_mock, 'close_all_positions_eod') as mock_close_all:
            
            # Run the backtest. The mock data fetcher will return data for each day.
            self.runner.run_backtest()
            
            # The backtest should run for 2 days (Aug 15 and Aug 16)
            # The mock data has 1 minute, so `run_for_minute` should be called 2 times.
            self.assertEqual(mock_run_for_minute.call_count, 2)
            
            # The `close_all_positions_eod` should be called once for each day.
            self.assertEqual(mock_close_all.call_count, 2)
            
            # Verify that data fetching was called once for each day.
            self.assertEqual(self.runner.data_fetcher.fetch_historical_data.call_count, 2)


    def test_sl_exit_logic(self):
        """
        Verifies that the strategy correctly triggers a stop-loss exit.
        This is an integration test between BacktestRunner and Strategy.
        """
        symbol = 'TCS'
        entry_price = 100.0
        
        # Mock a get_config call for the Strategy class
        with patch('src.strategy.get_config') as mock_get_config:
            mock_get_config.return_value = {
                'TRADE_MODE': 'paper',
                'INITIAL_CAPITAL': 100000.0,
                'MAX_ACTIVE_POSITIONS': 10,
                'TOP_N_SYMBOLS': 100,
                'SL_PERCENT': 2,
                'TARGET_PERCENT': 10,
                'TSL_PERCENT': 1,
            }

            # Create a mock Strategy instance and an OrderManager instance
            strategy = Strategy(
                redis_store=self.redis_mock,
                order_manager=self.order_manager_mock,
            )
        
            # 1. Simulate an open position in the order manager
            strategy.order_manager.open_positions = {
                symbol: {
                    'symbol': symbol,
                    'direction': 'BUY',
                    'entry_price': entry_price,
                    'quantity': 10
                }
            }
        
            # 2. Simulate a price drop below the SL
            # SL price = 100 * (1 - 2/100) = 98
            current_price = 97.5 # A price that should trigger the SL
        
            # Create a mock historical data structure to pass to the function
            mock_historical_data = {
                symbol: pd.DataFrame([
                    {'close': current_price}
                ], index=pd.to_datetime(['2025-01-01 09:15:00']))
            }
        
            # Set the mock order manager's close_order method to return a known value
            self.order_manager_mock.close_order.return_value = True

            # 3. Call the check_for_exit_signals method with the new price
            strategy.check_for_exit_signals(
                timestamp=pd.to_datetime('2025-01-01 09:15:00'),
                historical_data=mock_historical_data
            )
        
            # 4. Assert that the close_order method was called
            # The mock order manager should have been called once with the symbol and the current price
            self.order_manager_mock.close_order.assert_called_once_with(symbol, current_price)


# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()
