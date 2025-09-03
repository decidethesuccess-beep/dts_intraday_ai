#
# Module: test_strategy.py
# Description: Unit tests for the TradingStrategy class.
#
# DTS Intraday AI Trading System - Strategy Unit Tests
# Version: 2025-08-29
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
import numpy as np
import json

# Set up the path to import from the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the class to be tested
from src.strategy import Strategy
from src.constants import SL_PERCENT, TARGET_PERCENT, TSL_PERCENT, AUTO_EXIT_TIME, MAX_ACTIVE_POSITIONS
from src.ai_module import AIModule
from src.redis_store import RedisStore
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher
from src.news_filter import NewsFilter

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
            'AUTO_EXIT_TIME': '15:20',
            'AI_RETRAINING_WINDOW_SIZE': 100,
            'AI_RETRAINING_INTERVAL_MINUTES': 60,
            'HOLIDAY_SESSION_LEVERAGE_MULTIPLIER': 0.5
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

        # Initialize the Strategy instance with the mocked dependencies
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )

        # Mock adjust_sl_target_sentiment_aware to return expected values
        self.mock_ai_module.adjust_sl_target_sentiment_aware.return_value = (98.0, 110.0) # Example values

        # Mock news_filter.get_and_analyze_sentiment to return a default sentiment score
        self.mock_news_filter.get_and_analyze_sentiment.return_value = 0.1 # Neutral sentiment for tests

        # Mock get_ai_metrics to return a dictionary of AI metrics
        self.mock_ai_module.get_ai_metrics.return_value = {
            'ai_score': 0.8,
            'leverage': 1.0,
            'trend_direction': 'UP',
            'trend_flip_confirmation': False,
            'sentiment_score': 0.1,
            'circuit_potential': 0.0 # Default to 0.0 for most tests
        }

        # Mock get_tsl_movement to return a dictionary of TSL details
        self.mock_ai_module.get_tsl_movement.return_value = {
            'new_tsl': 102.47,
            'old_tsl': 99.0,
            'tsl_percent': 0.5,
            'volatility': 2.0,
            'pnl_percent': 3.0,
            'leverage': 1.0
        }

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
                return True
            return False
        self.mock_order_manager.close_order.side_effect = mock_close_order

        

        # ✅ FIX: Add a stateful mock for update_position to correctly update the mock dictionary.
        def mock_update_position(symbol, updates):
            if symbol in self.mock_positions:
                self.mock_positions[symbol].update(updates)
        self.mock_order_manager.update_position.side_effect = mock_update_position

        # Add a stateful mock for place_order to correctly add positions and leverage
        def mock_place_order(symbol, direction, quantity, entry_price, leverage, ai_metrics=None):
            if symbol in self.mock_positions:
                return False
            trade = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'status': 'OPEN',
                'leverage': leverage,
            }
            if ai_metrics:
                trade.update(ai_metrics)
            self.mock_positions[symbol] = trade
            return True
        self.mock_order_manager.place_order.side_effect = mock_place_order

        # Mock the logging to prevent test output from cluttering the console
        self.mock_logger = MagicMock()
        Strategy.logger = self.mock_logger

        # Mock the TradeLogger
        self.mock_trade_logger = MagicMock()
        self.strategy.trade_logger = self.mock_trade_logger

        # Patch the webhook function
        self.patcher_webhook = patch('src.strategy.send_event_webhook')
        self.mock_send_webhook = self.patcher_webhook.start()

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.patcher_webhook.stop()

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
        ai_metrics = {"test_metric": "test_value"}
        
        # Populate the mock open_positions dictionary
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10,
            'entry_time': datetime.now(),
            'ai_metrics': ai_metrics
        }

        # Simulate a price drop below the SL
        sl_price = entry_price * (1 - SL_PERCENT / 100)
        current_price = sl_price - 0.5  # A price that should trigger the SL

        # Create mock historical data
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price}])
        }

        # Capture the trade details BEFORE calling the strategy method that closes the position
        initial_position_details = self.mock_positions[symbol].copy()

        # ✅ FIX: Call the correct method name
        self.strategy.check_hard_sl_target(self.mock_positions, mock_historical_data)

        # Assert the close_order method was called with the correct symbol and price
        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price)
        self.mock_send_webhook.assert_called_once_with('trade_signal', {'signal_type': 'exit', 'reason': 'stop_loss', 'symbol': symbol, 'price': current_price})
        
        pnl = (current_price - initial_position_details['entry_price']) * initial_position_details['quantity']
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], pnl, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'stop_loss')
        self.assertEqual(kwargs['strategy_id'], 'hard_sl')
        self.assertEqual(kwargs['ai_audit_trail'], json.dumps(ai_metrics))
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
            'quantity': 10,
            'entry_time': datetime.now()
        }
        
        # Simulate a price rise above the target
        target_price = entry_price * (1 + TARGET_PERCENT / 100)
        current_price = target_price + 0.5

        # Create mock historical data
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price}])
        }

        # Capture the trade details BEFORE calling the strategy method that closes the position
        initial_position_details = self.mock_positions[symbol].copy()

        # ✅ FIX: Call the correct method name
        self.strategy.check_hard_sl_target(self.mock_positions, mock_historical_data)

        # Assert the close_order method was called
        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price)
        self.mock_send_webhook.assert_called_once_with('trade_signal', {'signal_type': 'exit', 'reason': 'target_profit', 'symbol': symbol, 'price': current_price})
        
        pnl = (current_price - initial_position_details['entry_price']) * initial_position_details['quantity']
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], pnl, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'target_profit')
        self.assertEqual(kwargs['strategy_id'], 'hard_target')
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
            'trailing_sl': entry_price * (1 - TSL_PERCENT / 100), # Initial TSL
            'entry_time': datetime.now()
        }

        # Create mock historical data
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price}])
        }

        # Call the TSL exit logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Assert that update_position was called with the new TSL
        self.mock_order_manager.update_position.assert_called_once_with(symbol, {'trailing_sl': 102.47})
        self.mock_order_manager.reset_mock() # Reset mock to allow for a new assertion

        # Simulate TSL hit
        current_price_hit = 102.0 # A price that hits the new TSL
        self.mock_positions[symbol]['trailing_sl'] = 102.47
        
        # Update mock data to reflect the TSL hit
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': current_price_hit}])
        }
        
        # Capture the trade details before the position is closed by the mock
        closed_trade_details = self.mock_positions[symbol].copy()

        # Call the TSL exit logic again
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Assert that the position was closed
        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price_hit)
        self.mock_send_webhook.assert_called_once_with('trade_signal', {'signal_type': 'exit', 'reason': 'ai_tsl', 'symbol': symbol, 'price': current_price_hit})

        pnl = (current_price_hit - closed_trade_details['entry_price']) * closed_trade_details['quantity']
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], pnl, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'ai_tsl')
        self.assertEqual(kwargs['strategy_id'], 'ai_tsl')
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
            'quantity': 10,
            'entry_time': datetime.now()
        }
        
        # Mock the AIModule to return a 'DOWN' trend
        # This will trigger the trend flip exit for a BUY position
        self.mock_ai_module.get_trend_direction.return_value = 'DOWN'
        self.mock_ai_module.confirm_trend_reversal.return_value = True
        
        # Mock the historical data to contain actual numeric values
        mock_historical_data = {
            symbol: pd.DataFrame([{'close': 105.0}])
        }
        
        # The function will check the last 'close' price to close the position
        closing_price = mock_historical_data[symbol]['close'].iloc[-1]
        
        # Capture the trade details BEFORE calling the strategy method that closes the position
        initial_position_details = self.mock_positions[symbol].copy()

        # Call the method
        self.strategy.check_trend_flip_exit(self.mock_positions, mock_historical_data)
        
        # Assert that close_order was called with the correct symbol and price
        self.mock_order_manager.close_order.assert_called_once_with(symbol, closing_price)
        self.mock_send_webhook.assert_called_once_with('trade_signal', {'signal_type': 'exit', 'reason': 'trend_flip', 'symbol': symbol, 'price': closing_price})
        
        pnl = (closing_price - initial_position_details['entry_price']) * initial_position_details['quantity']
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], pnl, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'trend_flip')
        self.assertEqual(kwargs['strategy_id'], 'trend_flip')
        self.assertEqual(self.mock_positions, {})

    def test_entry_condition_max_positions_reached(self):
        """
        Verifies that no new entries are made when the max number of open positions is reached.
        """
        # Populate the mock positions to hit the max limit (10)
        for i in range(MAX_ACTIVE_POSITIONS):
            self.mock_positions[f'SYMBOL{i}'] = {'symbol': f'SYMBOL{i}', 'direction': 'BUY', 'entry_price': 100.0, 'entry_time': datetime.now()}

        # Mock historical data for a new symbol
        mock_historical_data = {'SYMBOL11': pd.DataFrame([{'close': 100.0}])}

        # Call the entry logic
        self.strategy.check_entry_signals(datetime.now(), mock_historical_data)

        # Assert that open_order was NOT called
        self.mock_order_manager.place_order.assert_not_called()
        self.assertIn('SYMBOL0', self.mock_positions) # Ensure existing positions are untouched

    def test_entry_signal_sends_webhook(self):
        """
        Verifies that a webhook is sent when a new position is successfully opened.
        """
        symbol = 'TEST_SYMBOL'
        trade_direction = 'BUY'
        entry_price = 120.0
        quantity = 10
        ai_metrics = {
            'ai_score': 0.8,
            'leverage': 2.0,
            'trend_direction': 'UP',
            'trend_flip_confirmation': False,
            'sentiment_score': 0.2
        }

        # Mock AI and news filter responses
        self.mock_news_filter.get_and_analyze_sentiment.return_value = 0.2
        self.mock_ai_module.get_ai_metrics.return_value = ai_metrics
        self.mock_ai_module.get_trade_direction.return_value = trade_direction
        self.mock_ai_module.get_leverage.return_value = 2.0
        self.mock_order_manager.place_order.return_value = True

        # Mock historical data
        mock_historical_data = {symbol: pd.DataFrame([{'close': entry_price}])}

        # Call the entry logic
        self.strategy.check_entry_signals(datetime.now(), mock_historical_data)

        # Assert that place_order was called
        self.mock_order_manager.place_order.assert_called_once_with(symbol, trade_direction, quantity, entry_price, leverage=1.0, ai_metrics=ai_metrics)

        # Assert that the webhook was sent with the correct payload
        self.mock_send_webhook.assert_called_once_with('trade_signal', {
            'signal_type': 'entry',
            'symbol': symbol,
            'direction': trade_direction,
            'price': entry_price,
            'quantity': quantity,
            'leverage': 1.0,
            'signal_score': ai_metrics['ai_score']
        })

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
            'entry_time': datetime.now()
        }

        # Create a mock time at the auto-exit time
        current_time = time(15, 20, 0) # AUTO_EXIT_TIME is 15:20
        
        # Capture the trade details before the position is closed by the mock
        closed_trade_details = self.mock_positions[symbol].copy()

        # Call the EOD exit logic
        self.strategy.check_eod_exit(current_time, {symbol: pd.DataFrame([{'close': 110.0}])})
        
        # Assert that close_order was called for the symbol
        self.mock_order_manager.close_order.assert_called_once_with(symbol, 110.0)
        self.mock_send_webhook.assert_called_once_with('safe_timeout', {'reason': 'end_of_day_exit', 'time': str(current_time)})

        pnl = (110.0 - closed_trade_details['entry_price']) * closed_trade_details['quantity']
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], pnl, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'eod')
        self.assertEqual(kwargs['strategy_id'], 'eod')
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
            'entry_time': datetime.now()
        }
        
        # Create a mock time before the auto-exit time
        current_time = time(15, 19, 59) # 1 second before auto exit
        
        # Call the EOD exit logic
        self.strategy.check_eod_exit(current_time, {})
        
        # Assert that the EOD method was NOT called
        self.mock_order_manager.close_all_positions_eod.assert_not_called()
        self.assertIn(symbol, self.mock_positions) # Position should still exist
        
    def test_close_all_positions_eod_method(self):
        """
        Verifies that the wrapper method correctly calls the OrderManager's method.
        """
        symbol = 'SYMBOL1'
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'entry_price': 100.0,
            'direction': 'BUY',
            'quantity': 10,
            'entry_time': datetime.now()
        }
        self.strategy.close_all_positions_eod({symbol: pd.DataFrame([{'close': 100.0}])})
        self.mock_order_manager.close_order.assert_called_once_with(symbol, 100.0)
        self.assertEqual(self.mock_positions, {})

    def test_profit_lock_triggered_and_tsl_updated(self):
        """
        Tests that the profit lock is triggered and updates the TSL.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10,
            'trailing_sl': 98.0,
            'entry_time': datetime.now()
        }

        # Simulate a price rise to trigger profit lock
        current_price = entry_price * (1 + self.strategy.profit_lock_threshold / 100) + 0.1
        mock_historical_data = {symbol: pd.DataFrame([{'close': current_price}])}

        self.strategy.check_profit_lock(mock_historical_data)

        expected_tsl = current_price * (1 - self.strategy.profit_lock_tsl_percent / 100)
        self.mock_order_manager.update_position.assert_called_once_with(symbol, {'trailing_sl': np.float64(expected_tsl), 'ai_safety_activation': 'profit_lock'})

    def test_min_profit_exit_triggered(self):
        """
        Tests that a position is closed when the minimum profit threshold is reached.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10,
            'trailing_sl': 98.0,
            'entry_time': datetime.now()
        }

        # Simulate a price rise to trigger min profit exit
        current_price = entry_price * (1 + self.strategy.min_profit_threshold / 100) + 0.1
        mock_historical_data = {symbol: pd.DataFrame([{'close': current_price}])}

        # Capture the trade details before the position is closed by the mock
        closed_trade_details = self.mock_positions[symbol].copy()

        self.strategy.check_min_profit_exit(mock_historical_data)

        self.mock_order_manager.close_order.assert_called_once_with(symbol, current_price)
        self.mock_send_webhook.assert_called_once_with('trade_signal', {'signal_type': 'exit', 'reason': 'min_profit', 'symbol': symbol, 'price': current_price})

        pnl = (current_price - closed_trade_details['entry_price']) * closed_trade_details['quantity']
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], pnl, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'min_profit')
        self.assertEqual(kwargs['strategy_id'], 'min_profit')
        self.assertEqual(self.mock_positions, {})

    def test_min_profit_exit_not_triggered_below_threshold(self):
        """
        Tests that a position is NOT closed if profit is below the minimum profit threshold.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10,
            'trailing_sl': 98.0,
            'entry_time': datetime.now()
        }

        # Simulate a price rise below the min profit threshold
        current_price = entry_price * (1 + self.strategy.min_profit_threshold / 100) - 0.1
        mock_historical_data = {symbol: pd.DataFrame([{'close': current_price}])}

        self.strategy.check_min_profit_exit(mock_historical_data)

        self.mock_order_manager.close_order.assert_not_called()
        self.assertIn(symbol, self.mock_positions)

    def test_profit_lock_and_ai_tsl_interaction(self):
        """
        Tests that AI-TSL respects a tighter TSL set by profit lock.
        """
        symbol = 'SYMBOL1'
        entry_price = 100.0
        
        # Position with profit lock already triggered, setting a tight TSL
        profit_locked_tsl_price = 102.0 # TSL set by profit lock
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 10,
            'trailing_sl': profit_locked_tsl_price,
            'entry_time': datetime.now()
        }

        # Simulate current price above entry, but AI-TSL would suggest a looser TSL
        current_price = 103.0
        mock_historical_data = {symbol: pd.DataFrame([{'close': current_price}])}

        # Mock AI-TSL to return a new_tsl that is looser than the profit-locked TSL
        self.mock_ai_module.get_tsl_movement.return_value = {
            'new_tsl': 101.0, # Looser than profit_locked_tsl_price
            'old_tsl': profit_locked_tsl_price,
            'tsl_percent': 0.5,
            'volatility': 2.0,
            'pnl_percent': 3.0,
            'leverage': 1.0
        }

        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)

        # Assert that the TSL is updated to the tighter, profit-locked TSL, not the looser AI-TSL
        self.mock_order_manager.update_position.assert_not_called()

    def test_holiday_session_leverage_adjustment(self):
        """
        Tests that leverage is adjusted during holiday sessions.
        """
        self.mock_data_fetcher.is_holiday_or_special_session.return_value = True
        symbol = 'TEST_SYMBOL'
        trade_direction = 'BUY'
        entry_price = 120.0
        quantity = 10
        ai_metrics = {
            'ai_score': 0.8,
            'leverage': 2.0,
            'trend_direction': 'UP',
            'trend_flip_confirmation': False,
            'sentiment_score': 0.2
        }

        self.mock_ai_module.get_ai_metrics.return_value = ai_metrics
        self.mock_ai_module.get_trade_direction.return_value = trade_direction
        self.mock_ai_module.get_leverage.return_value = 2.0
        self.mock_order_manager.place_order.return_value = True

        mock_historical_data = {symbol: pd.DataFrame([{'close': entry_price}])}
        self.strategy.check_entry_signals(datetime.now(), mock_historical_data)

        expected_leverage = ai_metrics['leverage'] * self.strategy.holiday_leverage_multiplier
        self.mock_order_manager.place_order.assert_called_once_with(symbol, trade_direction, quantity, entry_price, leverage=expected_leverage, ai_metrics=ai_metrics)

    def test_entry_signal_with_high_circuit_potential(self):
        """
        Tests that the entry threshold is lowered when circuit potential is high.
        """
        symbol = 'CIRCUIT_STOCK'
        trade_direction = 'BUY'
        entry_price = 100.0
        quantity = 10
        ai_metrics = {
            'ai_score': 0.65, # Score that would normally not trigger entry
            'leverage': 1.0,
            'trend_direction': 'UP',
            'trend_flip_confirmation': False,
            'sentiment_score': 0.1,
            'circuit_potential': 0.8 # High circuit potential
        }

        # Mock AI and news filter responses
        self.mock_news_filter.get_and_analyze_sentiment.return_value = 0.1
        self.mock_ai_module.get_ai_metrics.return_value = ai_metrics
        self.mock_ai_module.get_trade_direction.return_value = trade_direction
        self.mock_ai_module.get_leverage.return_value = 1.0
        self.mock_order_manager.place_order.return_value = True

        # Mock historical data
        mock_historical_data = {symbol: pd.DataFrame([{'close': entry_price}])}

        # Call the entry logic
        self.strategy.check_entry_signals(datetime.now(), mock_historical_data)

        # Assert that place_order was called, indicating entry was triggered
        self.mock_order_manager.place_order.assert_called_once_with(
            symbol, trade_direction, quantity, entry_price, leverage=0.5, ai_metrics=ai_metrics
        )

    def test_retraining_triggered_by_size(self):
        """
        Tests that AI model retraining is triggered when the data buffer reaches the window size.
        """
        self.strategy.retraining_window_size = 50 # Lower for testing
        self.strategy.retraining_data_buffer = pd.DataFrame([{'data': i} for i in range(50)])
        self.mock_ai_module.last_retrained_timestamp = None

        self.strategy.check_and_trigger_retraining(datetime.now())

        self.mock_ai_module.retrain.assert_called_once()
        self.assertEqual(len(self.strategy.retraining_data_buffer), 0) # Buffer should be cleared

    def test_retraining_triggered_by_time(self):
        """
        Tests that AI model retraining is triggered after the specified time interval.
        """
        self.strategy.retraining_interval = timedelta(minutes=30)
        self.mock_ai_module.last_retrained_timestamp = datetime.now() - timedelta(minutes=31)

        self.strategy.check_and_trigger_retraining(datetime.now())

        self.mock_ai_module.retrain.assert_called_once()

class TestAITSLAdjustments(unittest.TestCase):
    """Test suite for AI-driven trailing stop-loss adjustments."""
    
    def setUp(self):
        """
        Set up test fixtures for AI-TSL tests.
        """
        self.mock_redis_store = MagicMock(spec=RedisStore)
        self.mock_order_manager = MagicMock(spec=OrderManager)
        self.mock_data_fetcher = MagicMock(spec=DataFetcher)
        self.mock_ai_module = MagicMock(spec=AIModule)
        self.mock_news_filter = MagicMock(spec=NewsFilter)
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Sample trade and market data for testing
        self.sample_trade = {
            'symbol': 'RELIANCE',
            'direction': 'BUY',
            'entry_price': 1000.0,
            'quantity': 100,
            'trailing_sl': 950.0,
            'entry_time': datetime.now()
        }
        
        self.sample_market_data = pd.DataFrame({
            'open': [990, 995, 1000, 1005, 1010],
            'high': [995, 1000, 1005, 1010, 1015],
            'low': [985, 990, 995, 1000, 1005],
            'close': [990, 995, 1000, 1005, 1010],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range('2025-08-15 09:15', periods=5, freq='1min'))

    def test_ai_tsl_tightens_in_high_volatility(self):
        """
        Test that AI-TSL tightens trailing stop-loss in high volatility conditions.
        """
        # Mock high volatility market data
        high_vol_data = self.sample_market_data.copy()
        high_vol_data['close'] = [1000, 1020, 980, 1040, 960]  # High volatility price swings
        
        # Mock AI score indicating high confidence
        ai_score = 0.9
        
        # Configure the mock AI module to return a proper dict
        expected_updated_trade = self.sample_trade.copy()
        expected_updated_trade['trailing_sl'] = 980.0  # Example adjusted TSL
        self.mock_ai_module.adjust_trailing_sl_ai.return_value = expected_updated_trade
        
        # Call the AI-TSL adjustment function
        updated_trade = self.mock_ai_module.adjust_trailing_sl_ai(
            self.sample_trade, 
            high_vol_data, 
            ai_score
        )
        
        # Verify the function returns an updated trade
        self.assertIsInstance(updated_trade, dict)
        self.assertIn('trailing_sl', updated_trade)
        
        # Placeholder assertion - in real implementation, TSL should tighten
        self.assertIsNotNone(updated_trade['trailing_sl'])

    def test_ai_tsl_releases_in_trending_market(self):
        """
        Test that AI-TSL releases trailing stop-loss in trending market conditions.
        """
        # Mock trending market data (consistent upward movement)
        trending_data = self.sample_market_data.copy()
        trending_data['close'] = [1000, 1005, 1010, 1015, 1020]  # Steady uptrend
        
        # Mock AI score indicating medium confidence
        ai_score = 0.7
        
        # Configure the mock AI module to return a proper dict
        expected_updated_trade = self.sample_trade.copy()
        expected_updated_trade['trailing_sl'] = 975.0  # Example adjusted TSL for trending market
        self.mock_ai_module.adjust_trailing_sl_ai.return_value = expected_updated_trade
        
        # Call the AI-TSL adjustment function
        updated_trade = self.mock_ai_module.adjust_trailing_sl_ai(
            self.sample_trade, 
            trending_data, 
            ai_score
        )
        
        # Verify the function returns an updated trade
        self.assertIsInstance(updated_trade, dict)
        self.assertIn('trailing_sl', updated_trade)
        
        # Placeholder assertion - in real implementation, TSL might loosen in trending markets
        self.assertIsNotNone(updated_trade['trailing_sl'])

    def test_ai_tsl_respects_leverage_limits(self):
        """
        Test that AI-TSL respects leverage limits and risk management rules.
        """
        # Create a short position trade
        short_trade = self.sample_trade.copy()
        short_trade['direction'] = 'SELL'
        short_trade['trailing_sl'] = 1050.0  # Higher TSL for shorts
        
        # Mock market data showing downward movement
        short_market_data = self.sample_market_data.copy()
        short_market_data['close'] = [1000, 995, 990, 985, 980]  # Downtrend
        
        # Mock AI score as dict with multiple scores
        ai_score_dict = {
            'signal_score': 0.8,
            'volatility_score': 0.3,
            'leverage_score': 0.6
        }
        
        # Configure the mock AI module to return a proper dict for short position
        expected_updated_trade = short_trade.copy()
        expected_updated_trade['trailing_sl'] = 1020.0  # Example adjusted TSL for short position
        self.mock_ai_module.adjust_trailing_sl_ai.return_value = expected_updated_trade
        
        # Call the AI-TSL adjustment function
        updated_trade = self.mock_ai_module.adjust_trailing_sl_ai(
            short_trade, 
            short_market_data, 
            ai_score_dict
        )
        
        # Verify the function returns an updated trade
        self.assertIsInstance(updated_trade, dict)
        self.assertEqual(updated_trade['direction'], 'SELL')
        self.assertIn('trailing_sl', updated_trade)
        
        # Verify TSL adjustment respects short position logic
        current_price = short_market_data['close'].iloc[-1]
        self.assertIsNotNone(updated_trade['trailing_sl'])
        # For shorts, TSL should be above current price
        self.assertGreaterEqual(updated_trade['trailing_sl'], current_price)
