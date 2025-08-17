#
# Module: test_strategy.py
# Description: Unit tests for the TradingStrategy class.
#
# DTS Intraday AI Trading System - Strategy Unit Tests
# Version: 2025-08-15
#

import unittest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime, time, timedelta
import os

# Set up the path to import from the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the class to be tested
from src.strategy import TradingStrategy

class TestTradingStrategy(unittest.TestCase):
    """
    Test suite for the TradingStrategy class, focusing on unit-testing
    its core logic by mocking all external dependencies.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the environment for all tests in this class.
        This is a good place for shared setup.
        """
        # Patch the configuration to use a consistent mock config for all tests.
        cls.patcher = patch('src.strategy.get_config')
        cls.mock_get_config = cls.patcher.start()
        cls.mock_get_config.return_value = {
            'TRADE_MODE': 'paper',
            'INITIAL_CAPITAL': 100000.0,
            'MAX_ACTIVE_POSITIONS': 10,
            'TOP_N_SYMBOLS': 100,
            'CAPITAL_PER_TRADE_PCT': 10,
            'SL_PERCENT': 2,
            'TARGET_PERCENT': 10,
            'COOLDOWN_PERIOD_SECONDS': 300,
            'MARKET_OPEN_TIME': '09:15',
            'MARKET_CLOSE_TIME': '15:30',
            'AUTO_EXIT_TIME': '15:20',
        }
    
    @classmethod
    def tearDownClass(cls):
        """
        Tears down the environment after all tests in this class are done.
        """
        cls.patcher.stop()

    def setUp(self):
        """
        Sets up mocks and a new instance of TradingStrategy for each test.
        """
        # Patch all external dependencies' classes so their constructors are never called.
        # It's crucial to patch where the class is *used* (in src.strategy), not where it's defined.
        self.patcher_redis = patch('src.strategy.RedisStore')
        self.patcher_data_fetcher = patch('src.strategy.DataFetcher')
        self.patcher_order_manager = patch('src.strategy.OrderManager')
        self.patcher_news_filter = patch('src.strategy.NewsFilter')
        
        self.mock_redis_store_class = self.patcher_redis.start()
        self.mock_data_fetcher_class = self.patcher_data_fetcher.start()
        self.mock_order_manager_class = self.patcher_order_manager.start()
        self.mock_news_filter_class = self.patcher_news_filter.start()
        
        # Create and configure MagicMock objects for each dependency
        self.mock_redis_store = MagicMock()
        self.mock_data_fetcher = MagicMock()
        self.mock_order_manager = MagicMock()
        self.mock_news_filter = MagicMock()
        
        self.mock_redis_store_class.return_value = self.mock_redis_store
        self.mock_data_fetcher_class.return_value = self.mock_data_fetcher
        self.mock_order_manager_class.return_value = self.mock_order_manager
        self.mock_news_filter_class.return_value = self.mock_news_filter

        # Based on ai_module.py, the AI logic is in a class named 'AIMethods'.
        # We need to patch this class and its instance methods for the test.
        # Again, the patch target must be the module where it's used: src.strategy
        self.patcher_ai_module = patch('src.strategy.AIMethods')
        self.mock_ai_module_class = self.patcher_ai_module.start()
        self.mock_ai_instance = MagicMock()
        self.mock_ai_module_class.return_value = self.mock_ai_instance
        
        # Set the mock instance on the strategy object's attribute
        self.strategy = TradingStrategy()
        self.strategy.ai_module = self.mock_ai_instance
        
    def tearDown(self):
        """
        Stops all patches after each test.
        """
        self.patcher_redis.stop()
        self.patcher_data_fetcher.stop()
        self.patcher_order_manager.stop()
        self.patcher_news_filter.stop()
        self.patcher_ai_module.stop()
        
    def test_entry_signal_triggers_trade(self):
        """
        Verifies that a strong AI signal triggers a new trade entry.
        """
        # Set up mock return values to simulate a scenario where a trade should occur.
        self.mock_redis_store.get_active_positions_count.return_value = 0
        self.mock_data_fetcher.get_tradable_symbols.return_value = ["SYMBOL1"]
        self.mock_redis_store.is_symbol_on_cooldown.return_value = False
        
        # Mocking the AIMethods instance's behavior. We mock the `evaluate_entry`
        # and `calculate_ai_leverage` methods as they are used in the strategy.
        self.mock_ai_instance.evaluate_entry.return_value = True
        self.mock_ai_instance.calculate_ai_leverage.return_value = 2.0
        self.mock_ai_instance.get_entry_threshold.return_value = 0.7 # Mock a value for completeness

        self.mock_news_filter.is_trade_allowed.return_value = True
        self.mock_data_fetcher.get_ltp_for_symbol.return_value = 100.0

        # Execute the method to be tested
        self.strategy.check_for_new_entry_signals()

        # Assert that the correct methods were called.
        self.mock_order_manager.enter_position.assert_called_once()
        self.mock_redis_store.set_symbol_cooldown.assert_called_once_with("SYMBOL1")

    def test_sl_exit_logic(self):
        """
        Simulates a price drop that should trigger a hard stop loss.
        """
        # Set up a mock open position
        mock_position = {
            'symbol': 'SYMBOL1',
            'entry_price': 100.0,
            'direction': 'BUY',
            'quantity': 10,
            'entry_time': datetime.now().isoformat()
        }
        self.mock_redis_store.get_all_open_positions.return_value = {'trade_123': mock_position}
        
        # Set up mock LTP to be below the stop loss price (2% of 100 is 98.0)
        ltp_below_sl = 97.5
        self.mock_data_fetcher.get_ltp_for_symbol.return_value = ltp_below_sl
        
        # --- FIX: Patch datetime.now() to control the time of the test ---
        with patch('src.strategy.datetime') as mock_datetime:
            # Set the time to be before the auto-exit time (15:20)
            mock_datetime.now.return_value = datetime.now().replace(hour=14, minute=0, second=0)
            mock_datetime.now.side_effect = lambda: datetime.now().replace(hour=14, minute=0, second=0)
            mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

            # We need to provide a datetime object to the function
            mock_current_time = mock_datetime.now().time()
            self.strategy.check_exit_conditions(mock_current_time)
        
        # Assert that the exit method was called with the correct reason.
        self.mock_order_manager.exit_position.assert_called_once_with('trade_123', 'hard_stop_loss')
        
    def test_auto_exit_at_end_of_day(self):
        """
        Verifies that all open positions are closed at the auto-exit time.
        """
        # Set up a mock open position
        mock_position = {
            'symbol': 'SYMBOL1',
            'entry_price': 100.0,
            'direction': 'BUY',
            'quantity': 10,
            'entry_time': datetime.now().isoformat()
        }
        self.mock_redis_store.get_all_open_positions.return_value = {'trade_123': mock_position}

        # Create a mock time at or after the auto-exit time (15:20)
        auto_exit_time = time(15, 20)
        
        # We now pass the mock time as a positional argument, as intended.
        self.strategy.check_exit_conditions(auto_exit_time)
        
        # Assert that the exit method was called with the correct reason.
        self.mock_order_manager.exit_position.assert_called_once_with('trade_123', 'auto_exit')

if __name__ == '__main__':
    unittest.main()
