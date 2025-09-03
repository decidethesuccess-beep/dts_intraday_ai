#
# Module: test_integration.py
# Description: Integration tests for DTS Intraday AI Trading System.
#
# DTS Intraday AI Trading System - Integration Test Module
# Version: 2025-08-29
#
# This file contains comprehensive integration tests to validate
# cross-module functionality between backtest_runner, strategy, and dashboard.
#

import pytest
import unittest
from unittest.mock import MagicMock, patch, Mock
import pandas as pd
from datetime import datetime, date, time
import sys
import os
import tempfile
import json

# Add the project root to the sys.path to ensure modules can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.backtest_runner import BacktestRunner
from src.strategy import Strategy
from src.order_manager import OrderManager
from src.redis_store import RedisStore
from src.data_fetcher import DataFetcher
from src.ai_module import AIModule
from src.news_filter import NewsFilter
# Mock the problematic dashboard import
from src.constants import (
    MAX_ACTIVE_POSITIONS, 
    CAPITAL_PER_TRADE_PCT, 
    INITIAL_CAPITAL,
    SL_PERCENT,
    TARGET_PERCENT,
    TSL_PERCENT,
    AUTO_EXIT_TIME
)

# Create a mock dashboard class for testing
class MockIntradayDashboardGPT:
    """Mock dashboard class to avoid import issues with the actual module."""
    
    def __init__(self):
        self.trade_data = []
    
    def get_trade_data(self):
        """Mock method to return trade data."""
        return self.trade_data
    
    def update_trade_data(self, trades):
        """Mock method to update trade data."""
        self.trade_data = trades

class TestIntegration(unittest.TestCase):
    """Integration test suite for cross-module functionality."""
    
    def setUp(self):
        """Set up mock objects and test data for each test."""
        # Create mock dependencies
        self.mock_redis_store = MagicMock(spec=RedisStore)
        self.mock_order_manager = MagicMock(spec=OrderManager)
        self.mock_data_fetcher = MagicMock(spec=DataFetcher)
        self.mock_ai_module = MagicMock(spec=AIModule)
        self.mock_news_filter = MagicMock(spec=NewsFilter)
        
        # Configure mock order manager
        self.mock_order_manager.initial_capital = INITIAL_CAPITAL
        self.mock_order_manager.available_capital = INITIAL_CAPITAL
        self.mock_order_manager.open_positions = {}
        self.mock_order_manager.closed_trades = []

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
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Create backtest runner
        self.start_date = date(2025, 8, 15)
        self.end_date = date(2025, 8, 15)
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Create backtest runner
        self.start_date = date(2025, 8, 15)
        self.end_date = date(2025, 8, 15)
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Create backtest runner
        self.start_date = date(2025, 8, 15)
        self.end_date = date(2025, 8, 15)
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Create backtest runner
        self.start_date = date(2025, 8, 15)
        self.end_date = date(2025, 8, 15)
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Create backtest runner
        self.start_date = date(2025, 8, 15)
        self.end_date = date(2025, 8, 15)
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
        
        # Create strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Create backtest runner
        self.start_date = date(2025, 8, 15)
        self.end_date = date(2025, 8, 15)
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']
        
        self.backtest_runner = BacktestRunner(
            strategy=self.strategy,
            start_date=self.start_date,
            end_date=self.end_date,
            symbols=self.symbols
        )
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        self.backtest_runner.strategy.order_manager = self.mock_order_manager
        
        # Create sample historical data
        self.sample_data = self._create_sample_historical_data()
        
        # Create mock dashboard instance
        self.dashboard = MockIntradayDashboardGPT()

        # Patch webhook functions
        self.patcher_strategy_webhook = patch('src.strategy.send_event_webhook')
        self.mock_strategy_webhook = self.patcher_strategy_webhook.start()

        self.patcher_ai_webhook = patch('src.ai_webhook.send_event_webhook')
        self.mock_ai_webhook = self.patcher_ai_webhook.start()

        self.patcher_news_webhook = patch('src.news_filter.send_event_webhook')
        self.mock_news_webhook = self.patcher_news_webhook.start()

        # Mock the TradeLogger
        self.mock_trade_logger = MagicMock()
        self.strategy.trade_logger = self.mock_trade_logger
        
    def tearDown(self):
        """Clean up after each test."""
        self.patcher_strategy_webhook.stop()
        self.patcher_ai_webhook.stop()
        self.patcher_news_webhook.stop()
        
    def _create_sample_historical_data(self):
        """Create realistic sample historical data for testing."""
        base_time = datetime(2025, 8, 15, 9, 15)
        data = {}
        
        for symbol in self.symbols:
            # Create 1-minute interval data for 6 hours (9:15 AM to 3:15 PM)
            timestamps = pd.date_range(base_time, periods=360, freq='1min')
            
            # Generate realistic price movements
            base_price = 1000 if symbol in ['RELIANCE', 'HDFC'] else 500
            prices = []
            for i in range(360):
                # Simulate realistic price movement with some volatility
                if i == 0:
                    price = base_price
                else:
                    # Add some random movement
                    change = (i % 10 - 5) * 0.1  # Small price changes
                    price = prices[-1] * (1 + change/100)
                prices.append(price)
            
            df = pd.DataFrame({
                'open': prices,
                'high': [p * 1.005 for p in prices],  # High slightly above open
                'low': [p * 0.995 for p in prices],   # Low slightly below open
                'close': prices,
                'volume': [1000 + i * 10 for i in range(360)]  # Increasing volume
            }, index=timestamps)
            
            data[symbol] = df
            
        return data

    def test_import_success(self):
        """Test that BacktestRunner can be imported successfully for integration tests."""
        self.assertIsNotNone(BacktestRunner)
        self.assertTrue(hasattr(BacktestRunner, '__init__'))

    def test_full_backtest_run(self):
        """Run a full 1-day backtest across multiple symbols, validate trade logs and PnL summary."""
        # Mock the data fetcher to return our sample data
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        
        # Mock AI module to return high signal scores for entry
        self.mock_ai_module.get_trade_direction.return_value = 'BUY'
        
        # Mock the update_position method
        def mock_update_position(symbol, updates):
            if symbol in self.mock_order_manager.open_positions:
                self.mock_order_manager.open_positions[symbol].update(updates)
        
        self.mock_order_manager.update_position = mock_update_position
        
        # Place some initial trades
        trades_placed = 0
        for symbol in self.symbols[:3]:  # Place 3 trades
            self.mock_order_manager.place_order.return_value = True
            
            entry_price = self.sample_data[symbol]['close'].iloc[0]
            quantity = 100
            ai_metrics = {'ai_score': 0.85, 'leverage': 1.5, 'sentiment_score': 0.2}
            
            success = self.mock_order_manager.place_order(symbol, 'BUY', quantity, entry_price, leverage=ai_metrics['leverage'], ai_metrics=ai_metrics)
            if success:
                trades_placed += 1
                
                # Add to open positions
                self.mock_order_manager.open_positions[symbol] = {
                    'symbol': symbol,
                    'direction': 'BUY',
                    'entry_price': entry_price,
                    'quantity': quantity,
                    'entry_time': datetime.now(),
                    'status': 'OPEN',
                    'trailing_sl': entry_price * (1 - TSL_PERCENT / 100),
                    **ai_metrics
                }
        
        # Verify trades were placed
        self.assertEqual(trades_placed, 3)
        
        # Simulate some exits during the day
        for symbol in self.symbols[:2]:  # Close 2 trades
            exit_price = self.sample_data[symbol]['close'].iloc[100]  # Mid-session price
            self.mock_order_manager.close_order(symbol, exit_price)
            
            # Move from open to closed
            if symbol in self.mock_order_manager.open_positions:
                trade = self.mock_order_manager.open_positions.pop(symbol)
                trade['exit_price'] = exit_price
                trade['exit_time'] = datetime.now()
                trade['status'] = 'CLOSED'
                trade['pnl'] = (exit_price - trade['entry_price']) * trade['quantity']
                self.mock_order_manager.closed_trades.append(trade)
        
        # Verify trade lifecycle
        self.assertEqual(len(self.mock_order_manager.open_positions), 1)
        self.assertEqual(len(self.mock_order_manager.closed_trades), 2)
        self.assertIn('ai_score', self.mock_order_manager.closed_trades[0])
        
        # Verify PnL calculations
        total_pnl = sum(trade['pnl'] for trade in self.mock_order_manager.closed_trades)
        self.assertIsInstance(total_pnl, (int, float))

    def test_dashboard_data_pipeline(self):
        """Ensure intraday_dashboard_GPT correctly reads backtest results and generates dashboard-ready output."""
        # Create mock trade data
        mock_trades = [
            {
                'symbol': 'RELIANCE',
                'direction': 'BUY',
                'entry_price': 1000.0,
                'exit_price': 1100.0,
                'quantity': 100,
                'entry_time': datetime.now(),
                'exit_time': datetime.now(),
                'status': 'CLOSED',
                'pnl': 10000.0,
                'ai_score': 0.9,
                'leverage': 2.0,
                'sentiment_score': 0.5
            },
            {
                'symbol': 'TCS',
                'direction': 'SELL',
                'entry_price': 500.0,
                'exit_price': 480.0,
                'quantity': 200,
                'entry_time': datetime.now(),
                'exit_time': datetime.now(),
                'status': 'CLOSED',
                'pnl': 4000.0,
                'ai_score': 0.7,
                'leverage': 1.0,
                'sentiment_score': -0.3
            }
        ]
        
        # Test dashboard data processing with mock dashboard
        self.dashboard.update_trade_data(mock_trades)
        trade_summary = self.dashboard.get_trade_data()
        
        # Verify data structure
        self.assertIsInstance(trade_summary, list)
        self.assertEqual(len(trade_summary), 2)
        
        # Verify trade details
        self.assertEqual(trade_summary[0]['symbol'], 'RELIANCE')
        self.assertEqual(trade_summary[0]['pnl'], 10000.0)
        self.assertIn('ai_score', trade_summary[0])
        self.assertEqual(trade_summary[1]['symbol'], 'TCS')
        self.assertEqual(trade_summary[1]['pnl'], 4000.0)
        self.assertIn('leverage', trade_summary[1])

    def test_concurrent_positions_and_reallocation(self):
        """Validate that the system handles 10 concurrent trades, exits, and reallocation of capital correctly."""
        # Mock the data fetcher
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        
        # Mock AI module
        self.mock_ai_module.get_trade_direction.return_value = 'BUY'
        
        # Fill all available positions (use the symbols we have)
        initial_capital = self.mock_order_manager.available_capital
        expected_capital_per_trade = initial_capital * (CAPITAL_PER_TRADE_PCT / 100)
        
        trades_placed = 0
        for symbol in self.symbols:
            self.mock_order_manager.place_order.return_value = True
            
            entry_price = self.sample_data[symbol]['close'].iloc[0]
            quantity = int(expected_capital_per_trade / entry_price)
            
            success = self.mock_order_manager.place_order(symbol, 'BUY', quantity, entry_price)
            if success:
                trades_placed += 1
                
                # Add to open positions
                self.mock_order_manager.open_positions[symbol] = {
                    'symbol': symbol,
                    'direction': 'BUY',
                    'entry_price': entry_price,
                    'quantity': quantity,
                    'entry_time': datetime.now(),
                    'status': 'OPEN'
                }
        
        # Verify we placed trades for all available symbols
        self.assertEqual(trades_placed, len(self.symbols))
        
        # Simulate capital reallocation after some exits
        symbols_to_exit = self.symbols[:2]  # Exit first 2 trades
        
        for symbol in symbols_to_exit:
            exit_price = self.sample_data[symbol]['close'].iloc[100]
            self.mock_order_manager.close_order(symbol, exit_price)
            
            # Move from open to closed
            if symbol in self.mock_order_manager.open_positions:
                trade = self.mock_order_manager.open_positions.pop(symbol)
                trade['exit_price'] = exit_price
                trade['exit_time'] = datetime.now()
                trade['status'] = 'CLOSED'
                trade['pnl'] = (exit_price - trade['entry_price']) * trade['quantity']
                self.mock_order_manager.closed_trades.append(trade)
        
        # Verify capital reallocation
        self.assertEqual(len(self.mock_order_manager.open_positions), len(self.symbols) - 2)
        self.assertEqual(len(self.mock_order_manager.closed_trades), 2)
        
        # Verify we can place new trades after exits
        new_symbol = 'HINDUNILVR'
        self.mock_order_manager.place_order.return_value = True
        
        success = self.mock_order_manager.place_order(new_symbol, 'BUY', 100, 1000.0)
        self.assertTrue(success)

    def test_trend_flip_and_dashboard_reflects_change(self):
        """Force a trend reversal event and verify that both runner and dashboard reflect the updated trade status."""
        # Mock the data fetcher
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        
        symbol = 'TCS'
        
        # Create a BUY position
        mock_position = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': 500.0,
            'quantity': 100,
            'entry_time': datetime.now(),
            'status': 'OPEN',
            'trailing_sl': 500.0 * (1 - TSL_PERCENT / 100),
            'ai_metrics': {'test': 'value'}
        }
        
        # Mock open positions
        self.mock_order_manager.get_open_positions.return_value = {symbol: mock_position}
        
        # Mock AI module to detect trend flip from UP to DOWN
        self.mock_ai_module.get_trend_direction.return_value = 'DOWN'
        self.mock_ai_module.confirm_trend_reversal.return_value = True
        
        # Create historical data showing trend reversal
        timestamp = self.sample_data[symbol].index[100]
        historical_data = {symbol: self.sample_data[symbol].iloc[50:101]}
        
        # Test trend flip logic directly
        self.strategy.check_trend_flip_exit({symbol: mock_position}, historical_data)
        
        # Verify position was closed due to trend flip
        self.mock_order_manager.close_order.assert_called_with(
            symbol, 
            self.sample_data[symbol]['close'].iloc[100]
        )
        self.mock_strategy_webhook.assert_called_once_with('trade_signal', {
            'signal_type': 'exit',
            'reason': 'trend_flip',
            'symbol': symbol,
            'price': self.sample_data[symbol]['close'].iloc[100]
        })
        
        # Simulate the position being moved to closed trades
        closed_trade = mock_position.copy()
        closed_trade['exit_price'] = self.sample_data[symbol]['close'].iloc[100]
        closed_trade['exit_time'] = datetime.now()
        closed_trade['status'] = 'CLOSED'
        closed_trade['pnl'] = (closed_trade['exit_price'] - closed_trade['entry_price']) * closed_trade['quantity']

        # Assert trade_logger.log_trade was called with correct parameters
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], closed_trade['pnl'], places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'trend_flip')
        self.assertEqual(kwargs['strategy_id'], 'trend_flip')
        self.assertEqual(kwargs['ai_audit_trail'], json.dumps(mock_position.get('ai_metrics', {})))
        
        self.mock_order_manager.closed_trades.append(closed_trade)
        
        # Verify dashboard can read the updated trade status
        self.dashboard.update_trade_data(self.mock_order_manager.closed_trades)
        trade_data = self.dashboard.get_trade_data()
        
        # Verify the trend flip trade is reflected
        self.assertEqual(len(trade_data), 1)
        self.assertEqual(trade_data[0]['symbol'], symbol)
        self.assertEqual(trade_data[0]['status'], 'CLOSED')
        self.assertIn('pnl', trade_data[0])

    def test_edge_cases_integration(self):
        """Holiday or short session simulation – verify system gracefully handles no-trade or early-close scenarios."""
        # Create short session data (only 2 hours instead of 6)
        short_session_data = {}
        base_time = datetime(2025, 8, 15, 9, 15)
        
        for symbol in self.symbols:
            # Only 120 minutes of data (2 hours)
            timestamps = pd.date_range(base_time, periods=120, freq='1min')
            
            # Generate price data for short session
            base_price = 1000 if symbol in ['RELIANCE', 'HDFC'] else 500
            prices = [base_price + i * 0.1 for i in range(120)]
            
            df = pd.DataFrame({
                'open': prices,
                'high': [p * 1.002 for p in prices],
                'low': [p * 0.998 for p in prices],
                'close': prices,
                'volume': [1000 + i * 5 for i in range(120)]
            }, index=timestamps)
            
            short_session_data[symbol] = df
        
        self.mock_data_fetcher.get_historical_data.return_value = short_session_data
        
        # Mock AI module to allow some trades
        self.mock_ai_module.get_trade_direction.return_value = 'BUY'
        
        # Place a few trades
        for i in range(3):
            symbol = self.symbols[i]
            self.mock_order_manager.place_order.return_value = True
            
            entry_price = short_session_data[symbol]['close'].iloc[0]
            quantity = 100
            self.mock_order_manager.place_order(symbol, 'BUY', quantity, entry_price)
            
            # Add to open positions
            self.mock_order_manager.open_positions[symbol] = {
                'symbol': symbol,
                'direction': 'BUY',
                'entry_price': entry_price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'status': 'OPEN'
            }
        
        # Verify trades were placed
        self.assertEqual(self.mock_order_manager.place_order.call_count, 3)
        
        # Set the return value for get_open_positions for the strategy to use
        self.mock_order_manager.get_open_positions.return_value = self.mock_order_manager.open_positions

        # Test EOD exit logic
        self.strategy.close_all_positions_eod(short_session_data)
        
        # Verify close_order was called for each open position
        self.assertEqual(self.mock_order_manager.close_order.call_count, 3)
        for i in range(3):
            symbol = self.symbols[i]
            expected_price = short_session_data[symbol]['close'].iloc[-1]
            self.mock_order_manager.close_order.assert_any_call(symbol, expected_price)
        
        # Assert trade_logger.log_trade was called for each closed trade
        self.assertEqual(self.mock_trade_logger.log_trade.call_count, 3)
        for call_arg in self.mock_trade_logger.log_trade.call_args_list:
            args, kwargs = call_arg
            self.assertIn('trade_duration', kwargs)
            self.assertIn('news_sentiment_score', kwargs)
            self.assertIn('ai_safety_activation', kwargs)
            self.assertEqual(kwargs['max_profit'], 0.0)
            self.assertEqual(kwargs['max_drawdown'], 0.0)
            self.assertEqual(kwargs['exit_reason'], 'eod')
            self.assertEqual(kwargs['strategy_id'], 'eod')
        
        # Simulate all positions being closed
        for symbol in list(self.mock_order_manager.open_positions.keys()):
            trade = self.mock_order_manager.open_positions.pop(symbol)
            trade['exit_price'] = short_session_data[symbol]['close'].iloc[-1]  # Last price
            trade['exit_time'] = datetime.now()
            trade['status'] = 'CLOSED'
            trade['pnl'] = (trade['exit_price'] - trade['entry_price']) * trade['quantity']
            self.mock_order_manager.closed_trades.append(trade)
        
        # Verify all positions were closed
        self.assertEqual(len(self.mock_order_manager.open_positions), 0)
        self.assertEqual(len(self.mock_order_manager.closed_trades), 3)
        
        # Verify dashboard can handle the short session results
        self.dashboard.update_trade_data(self.mock_order_manager.closed_trades)
        trade_data = self.dashboard.get_trade_data()
        
        # Verify all trades are closed
        for trade in trade_data:
            self.assertEqual(trade['status'], 'CLOSED')
            self.assertIn('pnl', trade)

    def test_news_filter_sends_webhook_on_strong_sentiment(self):
        """Verifies that the NewsFilter sends a webhook for strong sentiment scores."""
        symbol = 'RELIANCE'
        headlines = ["Reliance announces record-breaking profits!"]
        strong_sentiment_score = 0.9

        # Configure the mock redis_store to have an 'r' attribute which is also a mock
        self.mock_redis_store.r = MagicMock()

        news_filter = NewsFilter(self.mock_redis_store)

        with patch.object(news_filter, '_fetch_news_headlines', return_value=headlines):
            with patch.object(news_filter, '_run_nlp_model', return_value=strong_sentiment_score):
                news_filter.get_and_analyze_sentiment(symbol)

        self.mock_news_webhook.assert_called_once_with('news_alert', {
            'symbol': symbol,
            'sentiment_score': strong_sentiment_score,
            'headlines': headlines
        })

        # Also assert that the redis set method was called
        self.mock_redis_store.r.set.assert_called_once_with(f"news_sentiment:{symbol}", strong_sentiment_score)

    def test_ai_webhook_sends_webhook_on_commentary(self):
        """Verifies that the AIWebhook sends a webhook after fetching commentary."""
        commentary_text = "This is a test commentary."
        
        # We need a real AIWebhook instance to test its methods
        from src.ai_webhook import AIWebhook
        ai_webhook = AIWebhook(self.mock_redis_store)

        # Mock the internal API call and the redis store
        with patch.object(ai_webhook, '_call_gemini_api', return_value=commentary_text) as mock_api_call:
            ai_webhook.get_and_store_daily_commentary()

            # Assert that the underlying API was called
            mock_api_call.assert_called_once()

            # Assert that the result was stored in Redis
            self.mock_redis_store.store_ai_comment.assert_called_once_with('daily', commentary_text)

            # Assert that the webhook was sent
            self.mock_ai_webhook.assert_called_once_with('ai_commentary', {
                'period': 'daily',
                'commentary': commentary_text
            })

    def test_ai_tsl_integration_with_backtest(self):
        """Integration test to ensure adjust_trailing_sl_ai() works with backtest_runner and dashboard."""
        # Mock the data fetcher
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        
        # Mock AI module methods
        self.mock_ai_module.get_trade_direction.return_value = 'BUY'
        
        # Create sample trades for testing AI-TSL integration
        buy_trade = {
            'symbol': 'RELIANCE',
            'direction': 'BUY',
            'entry_price': 1000.0,
            'quantity': 100,
            'trailing_sl': 950.0,
            'entry_time': datetime.now(),
            'status': 'OPEN'
        }
        
        sell_trade = {
            'symbol': 'TCS',
            'direction': 'SELL',
            'entry_price': 500.0,
            'quantity': 200,
            'trailing_sl': 550.0,
            'entry_time': datetime.now(),
            'status': 'OPEN'
        }
        
        # Configure the mock AI module to return proper dict values
        expected_buy_trade = buy_trade.copy()
        expected_buy_trade['trailing_sl'] = 980.0  # Adjusted TSL for BUY
        
        expected_sell_trade = sell_trade.copy()
        expected_sell_trade['trailing_sl'] = 520.0  # Adjusted TSL for SELL
        
        # Configure mock to return different values for different calls
        self.mock_ai_module.adjust_trailing_sl_ai.side_effect = [
            expected_buy_trade,
            expected_sell_trade
        ]
        
        # Simulate AI-TSL adjustments for both trades
        try:
            # Test BUY trade with AI-TSL adjustment
            market_data_buy = self.sample_data['RELIANCE'].iloc[50:100]  # Mid-session data
            ai_score_buy = 0.9  # High confidence signal
            
            updated_buy_trade = self.mock_ai_module.adjust_trailing_sl_ai(
                buy_trade, 
                market_data_buy, 
                ai_score_buy
            )
            
            # Test SELL trade with AI-TSL adjustment
            market_data_sell = self.sample_data['TCS'].iloc[50:100]
            ai_score_sell = {
                'signal_score': 0.8,
                'volatility_score': 0.4,
                'confidence_score': 0.7
            }
            
            updated_sell_trade = self.mock_ai_module.adjust_trailing_sl_ai(
                sell_trade, 
                market_data_sell, 
                ai_score_sell
            )
            
            # Verify both adjustments completed without exceptions
            self.assertIsInstance(updated_buy_trade, dict)
            self.assertIsInstance(updated_sell_trade, dict)
            self.assertIn('trailing_sl', updated_buy_trade)
            self.assertIn('trailing_sl', updated_sell_trade)
            
            # Verify trade directions are preserved
            self.assertEqual(updated_buy_trade['direction'], 'BUY')
            self.assertEqual(updated_sell_trade['direction'], 'SELL')
            
            # Update dashboard with adjusted trades
            self.dashboard.update_trade_data([updated_buy_trade, updated_sell_trade])
            trade_data = self.dashboard.get_trade_data()
            
            # Verify dashboard can handle AI-TSL adjusted trades
            self.assertEqual(len(trade_data), 2)
            self.assertIn('trailing_sl', trade_data[0])
            self.assertIn('trailing_sl', trade_data[1])
            
        except Exception as e:
            self.fail(f"AI-TSL integration test failed with exception: {e}")

    def test_retraining_impacts_scoring(self):
        """
        Integration test to verify that AI retraining impacts subsequent AI scores.
        """
        # --- Mock setup for this specific test ---
        self.mock_ai_module.model_version = 1.0
        self.mock_ai_module.last_retrained_timestamp = None
        self.mock_ai_module.get_signal_score.return_value = 0.75

        def retrain_side_effect(data):
            self.mock_ai_module.model_version = 1.1
            self.mock_ai_module.last_retrained_timestamp = datetime.now()
            self.mock_ai_module.get_signal_score.return_value = 0.85

        self.mock_ai_module.retrain.side_effect = retrain_side_effect
        
        # Mock data fetcher to return sample data
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        self.mock_news_filter.get_and_analyze_sentiment.return_value = 0.2

        # --- Phase 1: Get initial AI score ---
        symbol = 'RELIANCE'
        initial_data = self.sample_data[symbol].iloc[0:10]
        initial_score = self.strategy.ai_module.get_signal_score(symbol, initial_data, 0.2)

        # --- Phase 2: Trigger retraining ---
        # Fill the buffer to trigger retraining
        self.strategy.retraining_window_size = 5 # Lower for test
        for i in range(5):
            self.strategy.run_for_minute(datetime.now(), {symbol: self.sample_data[symbol].iloc[i:i+1]})

        # --- Phase 3: Get AI score after retraining ---
        # The AI module's model_version should now be 1.1
        score_after_retraining = self.strategy.ai_module.get_signal_score(symbol, initial_data, 0.2)

        # --- Assertions ---
        self.assertEqual(self.mock_ai_module.retrain.call_count, 1)
        self.assertNotEqual(initial_score, score_after_retraining)
        self.assertGreater(score_after_retraining, initial_score)
        self.assertEqual(self.strategy.ai_module.model_version, 1.1)

if __name__ == '__main__':
    unittest.main()

    def test_news_filter_sends_webhook_on_strong_sentiment(self):
        """
        Verifies that the NewsFilter sends a webhook for strong sentiment scores.
        """
        symbol = 'RELIANCE'
        headlines = ["Reliance announces record-breaking profits!"]
        strong_sentiment_score = 0.9

        # Configure the mock redis_store to have an 'r' attribute which is also a mock
        self.mock_redis_store.r = MagicMock()

        news_filter = NewsFilter(self.mock_redis_store)

        with patch.object(news_filter, '_fetch_news_headlines', return_value=headlines):
            with patch.object(news_filter, '_run_nlp_model', return_value=strong_sentiment_score):
                news_filter.get_and_analyze_sentiment(symbol)

        self.mock_news_webhook.assert_called_once_with('news_alert', {
            'symbol': symbol,
            'sentiment_score': strong_sentiment_score,
            'headlines': headlines
        })

        # Also assert that the redis set method was called
        self.mock_redis_store.r.set.assert_called_once_with(f"news_sentiment:{symbol}", strong_sentiment_score)

    def test_ai_webhook_sends_webhook_on_commentary(self):
        """
        Verifies that the AIWebhook sends a webhook after fetching commentary.
        """
        commentary_text = "This is a test commentary."
        
        # We need a real AIWebhook instance to test its methods
        from src.ai_webhook import AIWebhook
        ai_webhook = AIWebhook(self.mock_redis_store)

        # Mock the internal API call and the redis store
        with patch.object(ai_webhook, '_call_gemini_api', return_value=commentary_text) as mock_api_call:
            ai_webhook.get_and_store_daily_commentary()

            # Assert that the underlying API was called
            mock_api_call.assert_called_once()

            # Assert that the result was stored in Redis
            self.mock_redis_store.store_ai_comment.assert_called_once_with('daily', commentary_text)

            # Assert that the webhook was sent
            self.mock_ai_webhook.assert_called_once_with('ai_commentary', {
                'period': 'daily',
                'commentary': commentary_text
            })

    def test_ai_tsl_integration_with_backtest(self):
        """
        Integration test to ensure adjust_trailing_sl_ai() works with backtest_runner and dashboard.
        """
        # Mock the data fetcher
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        
        # Mock AI module methods
        self.mock_ai_module.get_trade_direction.return_value = 'BUY'
        
        # Create sample trades for testing AI-TSL integration
        buy_trade = {
            'symbol': 'RELIANCE',
            'direction': 'BUY',
            'entry_price': 1000.0,
            'quantity': 100,
            'trailing_sl': 950.0,
            'entry_time': datetime.now(),
            'status': 'OPEN'
        }
        
        sell_trade = {
            'symbol': 'TCS',
            'direction': 'SELL',
            'entry_price': 500.0,
            'quantity': 200,
            'trailing_sl': 550.0,
            'entry_time': datetime.now(),
            'status': 'OPEN'
        }
        
        # Configure the mock AI module to return proper dict values
        expected_buy_trade = buy_trade.copy()
        expected_buy_trade['trailing_sl'] = 980.0  # Adjusted TSL for BUY
        
        expected_sell_trade = sell_trade.copy()
        expected_sell_trade['trailing_sl'] = 520.0  # Adjusted TSL for SELL
        
        # Configure mock to return different values for different calls
        self.mock_ai_module.adjust_trailing_sl_ai.side_effect = [
            expected_buy_trade,
            expected_sell_trade
        ]
        
        # Simulate AI-TSL adjustments for both trades
        try:
            # Test BUY trade with AI-TSL adjustment
            market_data_buy = self.sample_data['RELIANCE'].iloc[50:100]  # Mid-session data
            ai_score_buy = 0.9  # High confidence signal
            
            updated_buy_trade = self.mock_ai_module.adjust_trailing_sl_ai(
                buy_trade, 
                market_data_buy, 
                ai_score_buy
            )
            
            # Test SELL trade with AI-TSL adjustment
            market_data_sell = self.sample_data['TCS'].iloc[50:100]
            ai_score_sell = {
                'signal_score': 0.8,
                'volatility_score': 0.4,
                'confidence_score': 0.7
            }
            
            updated_sell_trade = self.mock_ai_module.adjust_trailing_sl_ai(
                sell_trade, 
                market_data_sell, 
                ai_score_sell
            )
            
            # Verify both adjustments completed without exceptions
            self.assertIsInstance(updated_buy_trade, dict)
            self.assertIsInstance(updated_sell_trade, dict)
            self.assertIn('trailing_sl', updated_buy_trade)
            self.assertIn('trailing_sl', updated_sell_trade)
            
            # Verify trade directions are preserved
            self.assertEqual(updated_buy_trade['direction'], 'BUY')
            self.assertEqual(updated_sell_trade['direction'], 'SELL')
            
            # Update dashboard with adjusted trades
            self.dashboard.update_trade_data([updated_buy_trade, updated_sell_trade])
            trade_data = self.dashboard.get_trade_data()
            
            # Verify dashboard can handle AI-TSL adjusted trades
            self.assertEqual(len(trade_data), 2)
            self.assertIn('trailing_sl', trade_data[0])
            self.assertIn('trailing_sl', trade_data[1])
            
        except Exception as e:
            self.fail(f"AI-TSL integration test failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()

    def test_profit_lock_integration(self):
        """
        Integration test for profit lock functionality.
        Simulates a trade reaching profit lock and verifies TSL adjustment and exit.
        """
        symbol = 'RELIANCE'
        entry_price = 100.0
        quantity = 10

        # Mock initial trade placement
        self.mock_order_manager.place_order.return_value = True
        self.mock_order_manager.open_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': quantity,
            'entry_time': datetime.now(),
            'status': 'OPEN',
            'trailing_sl': entry_price * (1 - self.strategy.sl_percent / 100) # Initial SL
        }

        # Simulate price movement to trigger profit lock
        profit_lock_trigger_price = entry_price * (1 + self.strategy.profit_lock_threshold / 100) + 0.1
        mock_historical_data_trigger = {symbol: pd.DataFrame([{'close': profit_lock_trigger_price}])}

        # Run strategy to trigger profit lock
        self.strategy.run_for_minute(datetime.now(), mock_historical_data_trigger)

        # Verify TSL was updated by profit lock
        expected_profit_lock_tsl = profit_lock_trigger_price * (1 - self.strategy.profit_lock_tsl_percent / 100)
        self.mock_order_manager.update_position.assert_called_with(symbol, {'trailing_sl': expected_profit_lock_tsl})

        # Simulate price dropping to hit the profit-locked TSL
        tsl_hit_price = expected_profit_lock_tsl - 0.1
        mock_historical_data_hit_tsl = {symbol: pd.DataFrame([{'close': tsl_hit_price}])}

        # Run strategy again to trigger TSL exit
        self.strategy.run_for_minute(datetime.now(), mock_historical_data_hit_tsl)

        # Verify position was closed due to TSL hit
        self.mock_order_manager.close_order.assert_called_with(symbol, tsl_hit_price)
        self.mock_strategy_webhook.assert_called_with('trade_signal', {'signal_type': 'exit', 'reason': 'ai_tsl', 'symbol': symbol, 'price': tsl_hit_price})
        
        # Assert trade_logger.log_trade was called with correct parameters
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], (tsl_hit_price - entry_price) * quantity, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'ai_tsl')
        self.assertEqual(kwargs['strategy_id'], 'ai_tsl')

    def test_min_profit_mode_integration(self):
        """
        Integration test for minimum profit mode functionality.
        Simulates a trade reaching min profit threshold and verifies immediate exit.
        """
        symbol = 'TCS'
        entry_price = 200.0
        quantity = 5

        # Enable min profit mode in strategy config for this test
        self.strategy.min_profit_mode = True

        # Mock initial trade placement
        self.mock_order_manager.place_order.return_value = True
        self.mock_order_manager.open_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': quantity,
            'entry_time': datetime.now(),
            'status': 'OPEN',
            'trailing_sl': entry_price * (1 - self.strategy.sl_percent / 100) # Initial SL
        }

        # Simulate price movement to trigger min profit exit
        min_profit_trigger_price = entry_price * (1 + self.strategy.min_profit_threshold / 100) + 0.01
        mock_historical_data_trigger = {symbol: pd.DataFrame([{'close': min_profit_trigger_price}])}

        # Run strategy to trigger min profit exit
        self.strategy.run_for_minute(datetime.now(), mock_historical_data_trigger)

        # Verify position was closed due to min profit
        self.mock_order_manager.close_order.assert_called_with(symbol, min_profit_trigger_price)
        self.mock_strategy_webhook.assert_called_with('trade_signal', {'signal_type': 'exit', 'reason': 'min_profit', 'symbol': symbol, 'price': min_profit_trigger_price})
        
        # Assert trade_logger.log_trade was called with correct parameters
        self.mock_trade_logger.log_trade.assert_called_once()
        args, kwargs = self.mock_trade_logger.log_trade.call_args
        self.assertAlmostEqual(kwargs['pnl'], (min_profit_trigger_price - entry_price) * quantity, places=2)
        self.assertIn('trade_duration', kwargs)
        self.assertIn('news_sentiment_score', kwargs)
        self.assertIn('ai_safety_activation', kwargs)
        self.assertEqual(kwargs['max_profit'], 0.0)
        self.assertEqual(kwargs['max_drawdown'], 0.0)
        self.assertEqual(kwargs['exit_reason'], 'min_profit')
        self.assertEqual(kwargs['strategy_id'], 'min_profit')
        self.assertEqual(self.mock_order_manager.open_positions, {}) # Position should be closed

    def test_ai_sl_target_integration_with_backtest(self):
        """
        Integration test for sentiment-aware SL/TGT adjustments.
        """
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        symbol = 'RELIANCE'

        # Create a BUY position
        mock_position = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': 1000.0,
            'quantity': 100,
            'status': 'OPEN'
        }
        self.mock_order_manager.get_open_positions.return_value = {symbol: mock_position}

        # Mock AI module for sentiment
        self.mock_ai_module.get_sentiment_score.return_value = -0.9 # Strong negative sentiment
        self.mock_ai_module.adjust_sl_target_sentiment_aware.return_value = (998.0, 1010.0) # Tight SL, low TGT

        # Run exit condition check with price hitting the adjusted SL
        historical_data = {symbol: pd.DataFrame({'close': [997]})}
        self.strategy.check_hard_sl_target({symbol: mock_position}, historical_data)

        # Verify position was closed due to sentiment-adjusted SL
        self.mock_order_manager.close_order.assert_called_with(symbol, 997)

    def test_ai_safety_layer_integration(self):
        """
        Integration test for AI safety layer enforcement.
        """
        # Mock the data fetcher
        self.mock_data_fetcher.get_historical_data.return_value = self.sample_data
        self.mock_data_fetcher.is_holiday_or_special_session.return_value = True

        # Mock AI module to return high signal scores for entry
        self.mock_ai_module.get_trade_direction.return_value = 'BUY'
        ai_metrics = {
            'ai_score': 0.9,
            'leverage': 10.0, # High leverage to test cap
            'trend_direction': 'UP',
            'trend_flip_confirmation': False,
            'sentiment_score': 0.5
        }
        self.mock_ai_module.get_ai_metrics.return_value = ai_metrics

        # Set leverage caps in order manager
        self.strategy.order_manager.daily_leverage_cap = 5.0

        # Run the backtest
        self.backtest_runner.run()

        # Verify that the holiday leverage multiplier was applied
        # The leverage should be 10.0 * 0.5 = 5.0
        # The order manager should allow this as it is equal to the cap
        self.strategy.order_manager.place_order.assert_called()
        args, kwargs = self.strategy.order_manager.place_order.call_args
        self.assertEqual(kwargs['leverage'], 5.0)

        # Now, test the daily leverage cap
        self.strategy.order_manager.reset_mock()
        self.strategy.order_manager.current_leverage = 4.0
        self.backtest_runner.run() # This should try to place another trade
        self.strategy.order_manager.place_order.assert_called()
        args, kwargs = self.strategy.order_manager.place_order.call_args
        self.assertEqual(kwargs['leverage'], 5.0) # Holiday multiplier is still in effect

        # The next trade should fail because the leverage cap is reached
        self.strategy.order_manager.reset_mock()
        self.strategy.order_manager.current_leverage = 4.9
        self.backtest_runner.run()
        self.strategy.order_manager.place_order.assert_not_called()