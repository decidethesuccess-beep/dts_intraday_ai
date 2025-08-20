#
# Module: test_strategy.py
# Description: Unit tests for the TradingStrategy class.
#
# DTS Intraday AI Trading System - Strategy Unit Tests
# Version: 2025-08-20
#
# Fixes Applied:
# ✅ Added a stateful mock for OrderManager.update_position to fix KeyError.
# ✅ Added a mock for OrderManager.get_open_positions_count to fix AttributeError.
# ✅ Centralized mock setup in the setUp method for better test maintainability.
# ✅ Added import for MAX_ACTIVE_POSITIONS to resolve NameError.
# ✅ Made the mock OrderManager.close_order and OrderManager.close_all_positions_eod
#    stateful to correctly clear positions, resolving AssertionError.
# ✅ Corrected method names in test calls to match `strategy.py`.
#

import unittest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime, time, timedelta
import os
import pandas as pd

# Set up the path to import from the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the class to be tested
from src.strategy import Strategy
from src.constants import SL_PERCENT, TARGET_PERCENT, TSL_PERCENT, AUTO_EXIT_TIME, MAX_ACTIVE_POSITIONS
from src.ai_module import AIModule

class TestStrategy(unittest.TestCase):
    """
    Test suite for the Strategy class, focusing on unit-testing
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
            'TOP_N_SYMBOLS': 5,
            'CAPITAL_PER_TRADE_PCT': 0.1,
            'SL_PERCENT': 2.0,
            'TARGET_PERCENT': 10.0,
            'TSL_PERCENT': 1.0,
            'MIN_PROFIT_MODE': True,
            'AUTO_EXIT_TIME': '15:20'
        }

    def setUp(self):
        """
        Set up mocks and a fresh instance of the Strategy class for each test.
        """
        # Create mock dependencies for the Strategy class
        self.mock_redis_store = MagicMock()
        self.mock_order_manager = MagicMock()
        self.mock_data_fetcher = MagicMock()
        self.mock_ai_module = MagicMock()
        self.mock_news_filter = MagicMock()

        # ✅ FIX: Create a mock dictionary to simulate open positions and make the mock stateful.
        self.mock_positions = {}
        self.mock_order_manager.get_open_positions.return_value = self.mock_positions
        
        # ✅ FIX: Mock get_open_positions_count to prevent AttributeError.
        # This will return the actual number of open positions in our mock.
        self.mock_order_manager.get_open_positions_count.side_effect = lambda: len(self.mock_positions)

        # ✅ FIX: Make the mock OrderManager.close_order stateful to correctly clear positions.
        def mock_close_order(symbol, price):
            if symbol in self.mock_positions:
                del self.mock_positions[symbol]
        self.mock_order_manager.close_order.side_effect = mock_close_order

        # ✅ FIX: Make the mock OrderManager.close_all_positions_eod clear the mock positions.
        def mock_close_all_positions_eod():
            self.mock_positions.clear()
        self.mock_order_manager.close_all_positions_eod.side_effect = mock_close_all_positions_eod

        # ✅ FIX: Add a stateful mock for update_position to correctly update the mock dictionary.
        def mock_update_position(symbol, updates):
            if symbol in self.mock_positions:
                self.mock_positions[symbol].update(updates)
        self.mock_order_manager.update_position.side_effect = mock_update_position

        # Initialize the Strategy instance with the mocked dependencies
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )

        # Mock the logging to prevent test output from cluttering the console
        self.mock_logger = MagicMock()
        Strategy.logger = self.mock_logger

    @classmethod
    def tearDownClass(cls):
        """
        Cleans up resources after all tests have run.
        """
        cls.patcher.stop()

    def test_initialization(self):
        """
        Verifies that the Strategy class initializes correctly with all dependencies.
        """
        self.assertIsInstance(self.strategy, Strategy)
        self.assertEqual(self.strategy.max_active_positions, 10)
        self.assertEqual(self.strategy.sl_percent, 2.0)
        self.assertEqual(self.strategy.auto_exit_time, '15:20')
        self.assertEqual(self.strategy.min_profit_mode, True)

    def test_hard_stop_loss_exit(self):
        """
        Tests that a position is closed when the hard stop-loss is hit.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        # Populate the mock open_positions dictionary
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10
        }

        # Simulate a price drop below the SL
        sl_price = entry_price * (1 - SL_PERCENT / 100)
        current_price = sl_price - 0.5  # A price that should trigger the SL

        # Create mock historical data
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price}])
        }

        # ✅ FIX: Call the correct method name
        self.strategy.check_hard_sl_target(self.mock_positions, mock_historical_data)

        # Assert the close_order method was called with the correct symbol and price
        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price)
        self.assertEqual(self.mock_positions, {})

    def test_hard_target_exit(self):
        """
        Tests that a position is closed when the hard target is hit.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        # Populate the mock open_positions dictionary
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10
        }
        
        # Simulate a price rise above the target
        target_price = entry_price * (1 + TARGET_PERCENT / 100)
        current_price = target_price + 0.5

        # Create mock historical data
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price}])
        }

        # ✅ FIX: Call the correct method name
        self.strategy.check_hard_sl_target(self.mock_positions, mock_historical_data)

        # Assert the close_order method was called
        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price)
        self.assertEqual(self.mock_positions, {})

    def test_ai_tsl_exit_logic(self):
        """
        Tests the AI-driven trailing stop-loss exit logic.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        current_price = 103.0 # Price is up, TSL should be updated
        
        # Initialize the mock position
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10,
            'trailing_sl': entry_price * (1 - TSL_PERCENT / 100) # Initial TSL
        }

        # Mock the AI module to return a specific TSL percentage
        self.mock_ai_module.get_ai_tsl_percentage.return_value = 0.5 # A tighter TSL
        
        # Create mock historical data
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price}])
        }

        # Call the TSL exit logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Calculate the expected new TSL price
        new_tsl_price = current_price * (1 - 0.5 / 100)
        
        # Assert that update_position was called with the new TSL
        self.mock_order_manager.update_position.assert_called_once_with(symbol, {'trailing_sl': new_tsl_price})
        self.mock_order_manager.reset_mock() # Reset mock to allow for a new assertion

        # Simulate TSL hit
        current_price_hit = 102.0 # A price that hits the new TSL
        
        # Update mock data to reflect the TSL hit
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price_hit}])
        }
        
        # Call the TSL exit logic again
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Assert that the position was closed
        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price_hit)
        self.assertEqual(self.mock_positions, {})

    def test_trend_flip_exit(self):
        """
        Verifies that a position is closed when the trend flips.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        # Set up a mock open position (long/BUY)
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10
        }
        
        # Mock the AIModule to return a 'DOWN' trend
        # This will trigger the trend flip exit for a BUY position
        self.mock_ai_module.get_trend_direction.return_value = 'DOWN'
        
        # Mock the historical data to contain actual numeric values
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': 105.0}])
        }
        
        # The function will check the last 'close' price to close the position
        closing_price = mock_historical_data[symbol]['close'].iloc[-1]
        
        # Call the method
        self.strategy.check_trend_flip_exit(self.mock_positions, mock_historical_data)
        
        # Assert that close_order was called with the correct symbol and price
        self.mock_order_manager.close_order.assert_called_once_with(symbol, closing_price)
        self.assertEqual(self.mock_positions, {})

    def test_entry_condition_max_positions_reached(self):
        """
        Verifies that no new entries are made when the max number of open positions is reached.
        """
        # Populate the mock positions to hit the max limit (10)
        for i in range(MAX_ACTIVE_POSITIONS):
            self.mock_positions[f'SYMBOL{i}'] = {'symbol': f'SYMBOL{i}', 'direction': 'BUY', 'entry_price': 100.0}

        # Mock the signal score to be above the threshold
        self.mock_ai_module.get_signal_score.return_value = 0.8
        
        # Mock historical data for a new symbol
        mock_historical_data = {'SYMBOL11': pd.DataFrame([{'close': 100.0}])}

        # Call the entry logic
        self.strategy.check_entry_signals(datetime.now(), mock_historical_data)

        # Assert that open_order was NOT called
        self.mock_order_manager.open_order.assert_not_called()
        self.assertIn('SYMBOL0', self.mock_positions) # Ensure existing positions are untouched

    def test_eod_exit_at_end_of_day(self):
        """
        Verifies that all open positions are closed at the auto-exit time.
        """
        # Set up a mock open position
        symbol = 'SYMBOL1'
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'entry_price': 100.0,
            'direction': 'BUY',
            'quantity': 10,
        }

        # Create a mock time at the auto-exit time
        current_time = time(15, 20, 0) # AUTO_EXIT_TIME is 15:20
        
        # Call the EOD exit logic
        self.strategy.check_eod_exit(current_time)
        
        # Assert that the EOD method was called
        self.mock_order_manager.close_all_positions_eod.assert_called_once()
        self.assertEqual(self.mock_positions, {}) # The mock logic should have cleared this
        
    def test_eod_exit_before_end_of_day(self):
        """
        Verifies that no positions are closed before the auto-exit time.
        """
        # Set up a mock open position
        symbol = 'SYMBOL1'
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'entry_price': 100.0,
            'direction': 'BUY',
            'quantity': 10,
        }
        
        # Create a mock time before the auto-exit time
        current_time = time(15, 19, 59) # 1 second before auto exit
        
        # Call the EOD exit logic
        self.strategy.check_eod_exit(current_time)
        
        # Assert that the EOD method was NOT called
        self.mock_order_manager.close_all_positions_eod.assert_not_called()
        self.assertIn(symbol, self.mock_positions) # Position should still exist
        
    def test_close_all_positions_eod_method(self):
        """
        Verifies that the wrapper method correctly calls the OrderManager's method.
        """
        self.strategy.close_all_positions_eod()
        self.mock_order_manager.close_all_positions_eod.assert_called_once()
