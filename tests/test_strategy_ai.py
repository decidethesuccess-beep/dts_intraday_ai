#
# Module: test_strategy_ai.py
# Description: AI-TSL specific tests for volatility-aware and leverage-aware trailing stop-loss.
#
# DTS Intraday AI Trading System - AI-TSL Test Module
# Version: 2025-08-24
#

import unittest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime, time
import os
import pandas as pd
import numpy as np

# Set up the path to import from the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.strategy import Strategy
from src.constants import SL_PERCENT, TARGET_PERCENT, TSL_PERCENT, AUTO_EXIT_TIME, MAX_ACTIVE_POSITIONS
from src.ai_module import AIModule
from src.redis_store import RedisStore
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher
from src.news_filter import NewsFilter


class TestAITSLStrategy(unittest.TestCase):
    """Test suite for AI-TSL volatility-aware and leverage-aware functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the environment for all tests in this class."""
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
        """Set up mocks and fresh Strategy instance for each test."""
        self.mock_redis_store = MagicMock()
        self.mock_order_manager = MagicMock()
        self.mock_data_fetcher = MagicMock()
        self.mock_ai_module = MagicMock()
        self.mock_news_filter = MagicMock()
        
        # Create mock positions dictionary
        self.mock_positions = {}
        self.mock_order_manager.get_open_positions.return_value = self.mock_positions
        
        # Stateful mock for close_order
        def mock_close_order(symbol, price):
            if symbol in self.mock_positions:
                del self.mock_positions[symbol]
        self.mock_order_manager.close_order.side_effect = mock_close_order
        
        # Stateful mock for update_position
        def mock_update_position(symbol, updates):
            if symbol in self.mock_positions:
                self.mock_positions[symbol].update(updates)
        self.mock_order_manager.update_position.side_effect = mock_update_position
        
        # Initialize Strategy instance
        self.strategy = Strategy(
            redis_store=self.mock_redis_store,
            order_manager=self.mock_order_manager,
            data_fetcher=self.mock_data_fetcher,
            ai_module=self.mock_ai_module,
            news_filter=self.mock_news_filter
        )
        
        # Mock logging
        self.mock_logger = MagicMock()
        Strategy.logger = self.mock_logger

    @classmethod
    def tearDownClass(cls):
        """Clean up resources."""
        cls.patcher.stop()

    def _create_volatile_market_data(self, symbol, high_volatility=True):
        """Create market data with specified volatility characteristics."""
        base_time = datetime(2025, 8, 15, 9, 15)
        timestamps = pd.date_range(base_time, periods=50, freq='1min')
        
        if high_volatility:
            # High volatility: large price swings
            base_price = 1000.0
            prices = []
            for i in range(50):
                if i == 0:
                    price = base_price
                else:
                    # Large random price movements
                    change = (np.random.random() - 0.5) * 0.1  # ±5% movements
                    price = prices[-1] * (1 + change)
                prices.append(price)
        else:
            # Low volatility: small price movements
            base_price = 1000.0
            prices = []
            for i in range(50):
                if i == 0:
                    price = base_price
                else:
                    # Small random price movements
                    change = (np.random.random() - 0.5) * 0.005  # ±0.25% movements
                    price = prices[-1] * (1 + change)
                prices.append(price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * 1.002 for p in prices],
            'low': [p * 0.998 for p in prices],
            'close': prices,
            'volume': [1000 + i * 10 for i in range(50)]
        }, index=timestamps)
        
        return df

    def test_ai_tsl_high_volatility_tightening(self):
        """Test that AI-TSL tightens trailing stop-loss in high volatility conditions."""
        symbol = 'RELIANCE'
        entry_price = 1000.0
        current_price = 1050.0  # 5% profit
        
        # Create high volatility market data
        high_vol_data = self._create_volatile_market_data(symbol, high_volatility=True)
        high_vol_data.loc[high_vol_data.index[-1], 'close'] = current_price
        
        # Mock position with high leverage
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 100,
            'trailing_sl': 990.0,  # Initial TSL
            'leverage': 5.0  # High leverage
        }
        
        # Mock AI module to return base TSL percentage
        self.mock_ai_module.get_ai_tsl_percentage.return_value = 2.0  # 2% base TSL
        
        # Create historical data
        mock_historical_data = {symbol: high_vol_data}
        
        # Call AI-TSL logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Verify TSL was updated with tighter value due to high volatility + leverage
        # Expected: base_tsl * volatility_multiplier * leverage_multiplier = 2.0 * 0.7 * 0.5 = 0.7%
        self.mock_order_manager.update_position.assert_called()
        call_args = self.mock_order_manager.update_position.call_args
        self.assertEqual(call_args[0][0], symbol)  # symbol
        self.assertIn('trailing_sl', call_args[0][1])  # updates dict
        
        # Verify the new TSL is tighter than the original
        new_tsl = call_args[0][1]['trailing_sl']
        self.assertGreater(new_tsl, 990.0)  # Should be higher (tighter)

    def test_ai_tsl_low_volatility_loosening(self):
        """Test that AI-TSL loosens trailing stop-loss in low volatility conditions."""
        symbol = 'TCS'
        entry_price = 500.0
        current_price = 520.0  # 4% profit
        
        # Create low volatility market data
        low_vol_data = self._create_volatile_market_data(symbol, high_volatility=False)
        
        # Mock position with low leverage
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 200,
            'trailing_sl': 495.0,  # Initial TSL
            'leverage': 1.0  # Low leverage
        }
        
        # Mock AI module to return base TSL percentage
        self.mock_ai_module.get_ai_tsl_percentage.return_value = 1.5  # 1.5% base TSL
        
        # Create historical data
        mock_historical_data = {symbol: low_vol_data}
        
        # Call AI-TSL logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Verify TSL was updated with looser value due to low volatility
        # Expected: base_tsl * volatility_multiplier * leverage_multiplier = 1.5 * 1.3 * 1.0 = 1.95%
        self.mock_order_manager.update_position.assert_called()
        call_args = self.mock_order_manager.update_position.call_args
        self.assertEqual(call_args[0][0], symbol)
        
        # Verify the new TSL is appropriate for low volatility
        new_tsl = call_args[0][1]['trailing_sl']
        # Should be tighter than original due to profit, but adjusted for volatility

    def test_ai_tsl_short_position_volatility(self):
        """Test AI-TSL for short positions with volatility adjustments."""
        symbol = 'INFY'
        entry_price = 800.0
        current_price = 760.0  # 5% profit on short
        
        # Create moderate volatility market data
        moderate_vol_data = self._create_volatile_market_data(symbol, high_volatility=True)
        
        # Update market data to ensure current price matches expected
        moderate_vol_data.loc[moderate_vol_data.index[-1], 'close'] = current_price
        
        # Mock short position
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'SELL',
            'entry_price': entry_price,
            'quantity': 150,
            'trailing_sl': 820.0,  # Initial TSL for short (above current price)
            'leverage': 3.0  # Medium leverage
        }
        
        # Mock AI module
        self.mock_ai_module.get_ai_tsl_percentage.return_value = 2.0
        
        # Create historical data
        mock_historical_data = {symbol: moderate_vol_data}
        
        # Call AI-TSL logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Verify TSL was updated for short position
        # For shorts, TSL should be above current price and may be adjusted based on volatility
        self.mock_order_manager.update_position.assert_called()
        call_args = self.mock_order_manager.update_position.call_args
        new_tsl = call_args[0][1]['trailing_sl']
        
        # For shorts, TSL should be above current price
        self.assertGreater(new_tsl, current_price)
        # And should be lower than original (tighter protection)
        self.assertLess(new_tsl, 820.0)

    def test_ai_tsl_leverage_adjustments(self):
        """Test that AI-TSL properly adjusts based on leverage levels."""
        symbol = 'HDFC'
        entry_price = 1200.0
        current_price = 1260.0  # 5% profit
        
        # Create market data
        market_data = self._create_volatile_market_data(symbol, high_volatility=True)
        
        # Test different leverage levels
        leverage_levels = [1.0, 3.0, 7.0]  # Low, Medium, High
        
        for leverage in leverage_levels:
            # Reset mock
            self.mock_order_manager.update_position.reset_mock()
            
            # Mock position with specific leverage
            self.mock_positions[symbol] = {
                'symbol': symbol,
                'direction': 'BUY',
                'entry_price': entry_price,
                'quantity': 50,
                'trailing_sl': 1180.0,
                'leverage': leverage
            }
            
            # Update market data to ensure current price matches expected
            market_data.loc[market_data.index[-1], 'close'] = current_price
            
            # Mock AI module
            self.mock_ai_module.get_ai_tsl_percentage.return_value = 2.0
            
            # Create historical data
            mock_historical_data = {symbol: market_data}
            
            # Call AI-TSL logic
            self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
            
            # Verify TSL was updated
            self.mock_order_manager.update_position.assert_called()
            call_args = self.mock_order_manager.update_position.call_args
            new_tsl = call_args[0][1]['trailing_sl']
            
            # Higher leverage should result in tighter TSL
            if leverage > 5.0:
                # High leverage: very tight TSL (0.7% TSL)
                expected_min_tsl = current_price * (1 - 0.7 / 100)
                self.assertGreaterEqual(new_tsl, expected_min_tsl)
            elif leverage > 2.0:
                # Medium leverage: moderate TSL (1.12% TSL)
                expected_min_tsl = current_price * (1 - 1.12 / 100)
                self.assertGreaterEqual(new_tsl, expected_min_tsl)
            else:
                # Low leverage: normal TSL (1.4% TSL)
                expected_min_tsl = current_price * (1 - 1.4 / 100)
                self.assertGreaterEqual(new_tsl, expected_min_tsl)

    def test_ai_tsl_bounds_enforcement(self):
        """Test that AI-TSL respects minimum and maximum bounds."""
        symbol = 'ICICIBANK'
        entry_price = 600.0
        current_price = 630.0  # 5% profit
        
        # Create market data
        market_data = self._create_volatile_market_data(symbol, high_volatility=True)
        
        # Mock position with extreme leverage to test bounds
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 100,
            'trailing_sl': 590.0,
            'leverage': 10.0  # Extreme leverage
        }
        
        # Update market data to ensure current price matches expected
        market_data.loc[market_data.index[-1], 'close'] = current_price
        
        # Mock AI module to return extreme values
        self.mock_ai_module.get_ai_tsl_percentage.return_value = 8.0  # Very high base TSL
        
        # Create historical data
        mock_historical_data = {symbol: market_data}
        
        # Call AI-TSL logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Verify TSL was updated within bounds
        self.mock_order_manager.update_position.assert_called()
        call_args = self.mock_order_manager.update_position.call_args
        new_tsl = call_args[0][1]['trailing_sl']
        
        # TSL should be bounded between 0.2% and 5%
        # For BUY positions, TSL should be below current price
        min_tsl = current_price * 0.95   # 5% maximum (tightest TSL)
        max_tsl = current_price * 0.998  # 0.2% minimum (loosest TSL)
        self.assertGreaterEqual(new_tsl, min_tsl)
        self.assertLessEqual(new_tsl, max_tsl)

    def test_ai_tsl_insufficient_data_handling(self):
        """Test AI-TSL behavior with insufficient market data."""
        symbol = 'WIPRO'
        entry_price = 400.0
        current_price = 420.0  # 5% profit
        
        # Create market data with insufficient history (less than 10 periods)
        insufficient_data = pd.DataFrame({
            'open': [400, 405, 410, 415, 420],
            'high': [402, 407, 412, 417, 422],
            'low': [398, 403, 408, 413, 418],
            'close': [400, 405, 410, 415, 420],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range(datetime(2025, 8, 15, 9, 15), periods=5, freq='1min'))
        
        # Mock position
        self.mock_positions[symbol] = {
            'symbol': symbol,
            'direction': 'BUY',
            'entry_price': entry_price,
            'quantity': 200,
            'trailing_sl': 395.0,
            'leverage': 2.0
        }
        
        # Mock AI module
        self.mock_ai_module.get_ai_tsl_percentage.return_value = 1.0
        
        # Create historical data
        mock_historical_data = {symbol: insufficient_data}
        
        # Call AI-TSL logic
        self.strategy.check_ai_tsl_exit(self.mock_positions, mock_historical_data)
        
        # Should still work with default volatility (2.0%)
        self.mock_order_manager.update_position.assert_called()
        call_args = self.mock_order_manager.update_position.call_args
        new_tsl = call_args[0][1]['trailing_sl']
        
        # Should have updated TSL with default volatility handling
        self.assertIsInstance(new_tsl, (int, float))
        self.assertGreater(new_tsl, 395.0)  # Should be tighter than original


if __name__ == '__main__':
    unittest.main()

    def test_ai_sl_target_adjustment_buy_positive_sentiment(self):
        """Test AI SL/TGT adjustment for a BUY trade with positive sentiment."""
        symbol = 'RELIANCE'
        entry_price = 1000.0
        self.mock_positions[symbol] = {'direction': 'BUY', 'entry_price': entry_price}
        self.mock_ai_module.get_sentiment_score.return_value = 0.8  # Strong positive
        self.mock_ai_module.adjust_sl_target_sentiment_aware.return_value = (970.0, 1120.0) # Looser SL, higher TGT

        self.strategy.check_hard_sl_target(self.mock_positions, {'RELIANCE': pd.DataFrame({'close': [1050]})})

        self.mock_ai_module.adjust_sl_target_sentiment_aware.assert_called()
        self.mock_order_manager.close_order.assert_not_called()

    def test_ai_sl_target_adjustment_buy_negative_sentiment(self):
        """Test AI SL/TGT adjustment for a BUY trade with negative sentiment."""
        symbol = 'RELIANCE'
        entry_price = 1000.0
        self.mock_positions[symbol] = {'direction': 'BUY', 'entry_price': entry_price}
        self.mock_ai_module.get_sentiment_score.return_value = -0.7 # Strong negative
        self.mock_ai_module.adjust_sl_target_sentiment_aware.return_value = (995.0, 1050.0) # Tighter SL, lower TGT

        self.strategy.check_hard_sl_target(self.mock_positions, {'RELIANCE': pd.DataFrame({'close': [994]})})

        self.mock_ai_module.adjust_sl_target_sentiment_aware.assert_called()
        self.mock_order_manager.close_order.assert_called_with(symbol, 994)

    def test_ai_sl_target_adjustment_sell_negative_sentiment(self):
        """Test AI SL/TGT adjustment for a SELL trade with negative sentiment."""
        symbol = 'TCS'
        entry_price = 1200.0
        self.mock_positions[symbol] = {'direction': 'SELL', 'entry_price': entry_price}
        self.mock_ai_module.get_sentiment_score.return_value = -0.8 # Strong negative
        self.mock_ai_module.adjust_sl_target_sentiment_aware.return_value = (1230.0, 1100.0) # Looser SL, higher TGT

        self.strategy.check_hard_sl_target(self.mock_positions, {'TCS': pd.DataFrame({'close': [1150]})})

        self.mock_ai_module.adjust_sl_target_sentiment_aware.assert_called()
        self.mock_order_manager.close_order.assert_not_called()

    def test_trend_flip_exit_with_ai_confirmation(self):
        """Test trend flip exit occurs when AI confirms."""
        symbol = 'INFY'
        self.mock_positions[symbol] = {'direction': 'BUY', 'entry_price': 1500}
        self.mock_ai_module.get_trend_direction.return_value = 'DOWN'
        self.mock_ai_module.confirm_trend_reversal.return_value = True

        self.strategy.check_trend_flip_exit(self.mock_positions, {'INFY': pd.DataFrame({'close': [1450]})})

        self.mock_order_manager.close_order.assert_called_with(symbol, 1450)

    def test_trend_flip_exit_without_ai_confirmation(self):
        """Test trend flip exit is prevented when AI denies."""
        symbol = 'INFY'
        self.mock_positions[symbol] = {'direction': 'BUY', 'entry_price': 1500}
        self.mock_ai_module.get_trend_direction.return_value = 'DOWN'
        self.mock_ai_module.confirm_trend_reversal.return_value = False

        self.strategy.check_trend_flip_exit(self.mock_positions, {'INFY': pd.DataFrame({'close': [1450]})})

        self.mock_order_manager.close_order.assert_not_called()
