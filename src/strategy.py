#
# Module: strategy.py
# Description: Orchestrates all modules and makes entry/exit decisions.
#
# DTS Intraday AI Trading System - Strategy Orchestrator
# Version: 2025-08-29
#
# Note: Added a new master method `check_exit_conditions` to consolidate all
# exit logic and simplify the main loop in the backtest runner.
#
import logging
from datetime import datetime, time, timedelta
import os
import sys
import pandas as pd
import json

# Add the project root to the sys.path to ensure modules can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary dependencies.
from src.redis_store import RedisStore
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher
from src.ai_module import AIModule
from src.news_filter import NewsFilter
from src.constants import MAX_ACTIVE_POSITIONS, TSL_PERCENT, SL_PERCENT, TARGET_PERCENT, AUTO_EXIT_TIME
from src.config import get_config
from src.ai_webhook import send_event_webhook
from src.trade_logger import TradeLogger

# Set up logging for the module
logger = logging.getLogger(__name__)

# Fix: Renamed class back to `Strategy` to align with tests.
class Strategy:
    """
    Orchestrates all modules and makes entry/exit decisions based on
    market data, AI signals, and risk management rules.
    """
    # ✅ FIX: Updated the constructor to accept all key dependencies to align with
    # the system architecture and fix test failures.
    def __init__(self, redis_store: RedisStore, order_manager: OrderManager,
                 data_fetcher: DataFetcher, ai_module: AIModule, news_filter: NewsFilter):
        """
        Initializes the trading strategy with all necessary dependencies.
        """
        self.config = get_config()
        self.redis_store = redis_store
        self.order_manager = order_manager
        self.data_fetcher = data_fetcher
        self.ai_module = ai_module
        self.news_filter = news_filter
        self.trade_logger = TradeLogger()
        
        # Strategy parameters from config
        self.max_active_positions = self.config.get("MAX_ACTIVE_POSITIONS", MAX_ACTIVE_POSITIONS)
        self.sl_percent = self.config.get("SL_PERCENT", SL_PERCENT)
        self.target_percent = self.config.get("TARGET_PERCENT", TARGET_PERCENT)
        self.tsl_percent = self.config.get("TSL_PERCENT", TSL_PERCENT)
        self.auto_exit_time = self.config.get("AUTO_EXIT_TIME", AUTO_EXIT_TIME)
        # ✅ FIX: Added the `min_profit_mode` attribute to the Strategy class
        self.min_profit_mode = self.config.get("MIN_PROFIT_MODE", False)
        self.min_profit_threshold = self.config.get("MIN_PROFIT_THRESHOLD", 0.5)
        self.min_profit_percentage_exit = self.config.get("MIN_PROFIT_PERCENTAGE_EXIT", 0.2)

        # AI Safety Layer
        self.profit_lock_threshold = self.config.get("PROFIT_LOCK_THRESHOLD", 5.0)
        self.profit_lock_tsl_percent = self.config.get("PROFIT_LOCK_TSL_PERCENT", 1.0)
        self.holiday_leverage_multiplier = self.config.get("HOLIDAY_SESSION_LEVERAGE_MULTIPLIER", 0.5)
        # Safety caps (fallbacks keep behavior stable if constants not defined)
        self._max_leverage_cap = self.config.get("DAILY_LEVERAGE_CAP", 5.0)
        self.crash_guard_threshold = self.config.get("CRASH_GUARD_THRESHOLD", 3.0) # Default to 3% market drop
        self.is_crash_active = False # Flag to indicate if crash guard is active

        # AI Retraining
        self.retraining_window_size = self.config.get("AI_RETRAINING_WINDOW_SIZE", 1000)
        self.retraining_interval = timedelta(minutes=self.config.get("AI_RETRAINING_INTERVAL_MINUTES", 60))
        self.retraining_data_buffer = pd.DataFrame()
        self.last_retraining_check = datetime.min

    def run_for_minute(self, timestamp: datetime, historical_data: dict):
        """
        Main loop for a single minute of the trading day.
        """
        # Step 0: Collect data for retraining
        self.collect_retraining_data(timestamp, historical_data)

        # Step 1: Check for exit signals on existing positions
        self.check_exit_conditions(timestamp, historical_data)

        # Step 1.5: Check for profit lock
        self.check_profit_lock(historical_data)
        
        # Step 1.75: Check for market crash and activate crash guard
        self.check_crash_guard(historical_data)

        # Step 2: Check for new entry signals
        self.check_entry_signals(timestamp, historical_data)

        # Step 3: Check and trigger AI retraining
        self.check_and_trigger_retraining(timestamp)

    def collect_retraining_data(self, timestamp: datetime, historical_data: dict):
        """
        Collects and buffers data for AI model retraining.
        """
        for symbol, data in historical_data.items():
            if not data.empty:
                latest_data = data.iloc[-1:].copy()
                latest_data['symbol'] = symbol
                latest_data['timestamp'] = timestamp
                sentiment_score = self.news_filter.get_and_analyze_sentiment(symbol)
                latest_data['sentiment_score'] = sentiment_score
                self.retraining_data_buffer = pd.concat([self.retraining_data_buffer, latest_data], ignore_index=True)

    def check_and_trigger_retraining(self, timestamp: datetime):
        """
        Checks if conditions are met to trigger AI model retraining.
        """
        buffer_size = len(self.retraining_data_buffer)
        time_since_last_retrain = timestamp - (self.ai_module.last_retrained_timestamp or datetime.min)

        trigger_by_size = buffer_size >= self.retraining_window_size
        trigger_by_time = self.ai_module.last_retrained_timestamp and (timestamp - self.ai_module.last_retrained_timestamp >= self.retraining_interval)

        if trigger_by_size or trigger_by_time:
            logger.info(f"Triggering AI retraining. Reason: {'size' if trigger_by_size else 'time'}.")
            self.ai_module.retrain(self.retraining_data_buffer)
            # Clear the buffer after retraining
            self.retraining_data_buffer = pd.DataFrame()
            send_event_webhook('ai_retraining', {'reason': 'size' if trigger_by_size else 'time', 'buffer_size': buffer_size})

    def check_crash_guard(self, historical_data: dict):
        """
        Checks for a market-wide crash and activates crash guard if detected.
        """
        # Placeholder for fetching NIFTY 50 data.
        # In a real scenario, this would fetch live NIFTY data or use a pre-loaded NIFTY data stream.
        # For now, we'll assume 'NIFTY50' is a key in historical_data for demonstration.
        nifty_data = historical_data.get('NIFTY50')

        if nifty_data is None or nifty_data.empty:
            logger.debug("NIFTY50 data not available for crash guard check.")
            self.is_crash_active = False
            return

        # Assuming 'open' and 'close' prices are available in NIFTY data
        # Calculate percentage drop from open
        nifty_open = nifty_data['open'].iloc[0]
        nifty_current = nifty_data['close'].iloc[-1]

        if nifty_open == 0: # Avoid division by zero
            self.is_crash_active = False
            return

        percentage_drop = ((nifty_open - nifty_current) / nifty_open) * 100

        if percentage_drop >= self.crash_guard_threshold:
            self.is_crash_active = True
            logger.warning(f"CRASH GUARD ACTIVATED: NIFTY50 dropped by {percentage_drop:.2f}% (Threshold: {self.crash_guard_threshold}%)")
            send_event_webhook('safety_alert', {'reason': 'market_crash', 'drop_percent': percentage_drop})
            # Update ai_safety_activation for all open positions
            for symbol, trade in self.order_manager.get_open_positions().items():
                self.order_manager.update_position(symbol, {'ai_safety_activation': 'market_crash'})
        else:
            self.is_crash_active = False
            logger.debug(f"Crash guard not active. NIFTY50 drop: {percentage_drop:.2f}%")

    def check_profit_lock(self, historical_data: dict):
        """
        Checks if any open position has reached the profit lock threshold and updates the TSL.
        """
        open_positions = self.order_manager.get_open_positions()
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue

            current_price = historical_data[symbol]['close'].iloc[-1]
            pnl_percent = (current_price - trade['entry_price']) / trade['entry_price'] * 100

            if pnl_percent >= self.profit_lock_threshold:
                new_tsl = current_price * (1 - self.profit_lock_tsl_percent / 100)
                if new_tsl > trade.get('trailing_sl', 0):
                    self.order_manager.update_position(symbol, {'trailing_sl': new_tsl, 'ai_safety_activation': 'profit_lock'})
                    logger.info(f"Profit lock triggered for {symbol}. TSL updated to {new_tsl}.")

    def check_min_profit_exit(self, historical_data: dict):
        """
        Checks if any open position has reached the minimum profit threshold and closes it.
        """
        if not self.min_profit_mode:
            return

        open_positions = self.order_manager.get_open_positions()
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue

            current_price = historical_data[symbol]['close'].iloc[-1]
            pnl_percent = (current_price - trade['entry_price']) / trade['entry_price'] * 100

            if pnl_percent >= self.min_profit_threshold:
                # Calculate the exit price to lock in minimum profit
                if trade['direction'] == 'BUY':
                    exit_price = trade['entry_price'] * (1 + self.min_profit_percentage_exit / 100)
                    # Ensure we are closing at a profit, not a loss
                    if current_price >= exit_price:
                        trade_to_close = self.order_manager.get_open_positions().get(symbol)
                        if trade_to_close and self.order_manager.close_order(symbol, current_price):
                            pnl = (current_price - trade_to_close['entry_price']) * trade_to_close['quantity']
                            trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                            news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                            ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                            ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                            self.trade_logger.log_trade(
                                trade_id=trade_to_close.get('trade_id', 'N/A'),
                                symbol=symbol,
                                entry_time=trade_to_close['entry_time'],
                                entry_price=trade_to_close['entry_price'],
                                exit_time=datetime.now(),
                                exit_price=current_price,
                                pnl=pnl,
                                trade_duration=trade_duration,
                                exit_reason='min_profit',
                                strategy_id='min_profit',
                                ai_confidence_score=trade_to_close.get('ai_score', 0),
                                news_sentiment_score=news_sentiment_score,
                                ai_safety_activation=ai_safety_activation,
                                max_profit=0.0,
                                max_drawdown=0.0,
                                ai_audit_trail=ai_audit_trail
                            )
                            logger.info(f"Min profit exit triggered for {symbol}. Position closed at {current_price} to lock in {pnl_percent:.2f}% profit.")
                            send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'min_profit', 'symbol': symbol, 'price': current_price})
                elif trade['direction'] == 'SELL':
                    exit_price = trade['entry_price'] * (1 - self.min_profit_percentage_exit / 100)
                    # Ensure we are closing at a profit, not a loss
                    if current_price <= exit_price:
                        trade_to_close = self.order_manager.get_open_positions().get(symbol)
                        if trade_to_close and self.order_manager.close_order(symbol, current_price):
                            pnl = (trade_to_close['entry_price'] - current_price) * trade_to_close['quantity']
                            trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                            news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                            ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                            ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                            self.trade_logger.log_trade(
                                trade_id=trade_to_close.get('trade_id', 'N/A'),
                                symbol=symbol,
                                entry_time=trade_to_close['entry_time'],
                                entry_price=trade_to_close['entry_price'],
                                exit_time=datetime.now(),
                                exit_price=current_price,
                                pnl=pnl,
                                trade_duration=trade_duration,
                                exit_reason='min_profit',
                                strategy_id='min_profit',
                                ai_confidence_score=trade_to_close.get('ai_score', 0),
                                news_sentiment_score=news_sentiment_score,
                                ai_safety_activation=ai_safety_activation,
                                max_profit=0.0,
                                max_drawdown=0.0,
                                ai_audit_trail=ai_audit_trail
                            )
                            logger.info(f"Min profit exit triggered for {symbol}. Position closed at {current_price} to lock in {pnl_percent:.2f}% profit.")
                            send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'min_profit', 'symbol': symbol, 'price': current_price})

    def check_exit_conditions(self, timestamp: datetime, historical_data: dict):
        """
        Consolidates all exit logic checks into a single master method.
        """
        open_positions = self.order_manager.get_open_positions()

        # Only proceed if there are open positions
        if open_positions:
            # Check for various exit signals
            self.check_hard_sl_target(open_positions, historical_data)
            self.check_ai_tsl_exit(open_positions, historical_data)
            self.check_trend_flip_exit(open_positions, historical_data)
            self.check_min_profit_exit(historical_data) # Call min profit exit check

        # Check for end-of-day exit
        self.check_eod_exit(timestamp.time(), historical_data)

    def check_hard_sl_target(self, open_positions, historical_data):
        """
        Checks for hard stop-loss or target profit exits.
        """
        # ✅ FIX: Wrap the loop with `list()` to prevent `RuntimeError`.
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue

            current_price = historical_data[symbol]['close'].iloc[-1]
            
            # Get base SL and TGT prices
            base_sl_price = trade['entry_price'] * (1 - self.sl_percent / 100)
            base_tgt_price = trade['entry_price'] * (1 + self.target_percent / 100)

            # Get sentiment score for sentiment-aware adjustment
            sentiment_score = self.ai_module.get_sentiment_score(symbol)

            # Adjust SL/TGT based on sentiment
            result = self.ai_module.adjust_sl_target_sentiment_aware(
                base_sl_price, base_tgt_price, trade['direction'], sentiment_score
            )
            if not result or len(result) != 2:
                sl_price, tgt_price = None, None
            else:
                sl_price, tgt_price = result

            if trade['direction'] == 'BUY':
                if current_price <= sl_price:
                    trade_to_close = trade
                    if trade_to_close and self.order_manager.close_order(symbol, current_price):
                        pnl = (current_price - trade_to_close['entry_price']) * trade_to_close['quantity']
                        trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                        news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                        ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                        ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                        self.trade_logger.log_trade(
                            trade_id=trade_to_close.get('trade_id', 'N/A'),
                            symbol=symbol,
                            entry_time=trade_to_close['entry_time'],
                            entry_price=trade_to_close['entry_price'],
                            exit_time=datetime.now(),
                            exit_price=current_price,
                            pnl=pnl,
                            trade_duration=trade_duration,
                            exit_reason='stop_loss',
                            strategy_id='hard_sl',
                            ai_confidence_score=trade_to_close.get('ai_score', 0),
                            news_sentiment_score=news_sentiment_score,
                            ai_safety_activation=ai_safety_activation,
                            max_profit=0.0,
                            max_drawdown=0.0,
                            ai_audit_trail=ai_audit_trail
                        )
                        logger.info(f"Position for {symbol} closed due to Hard SL (AI-adjusted) at {current_price}.")
                        send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'stop_loss', 'symbol': symbol, 'price': current_price})
                elif current_price >= tgt_price:
                    trade_to_close = trade
                    if trade_to_close and self.order_manager.close_order(symbol, current_price):
                        pnl = (current_price - trade_to_close['entry_price']) * trade_to_close['quantity']
                        trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                        news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                        ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                        ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                        self.trade_logger.log_trade(
                            trade_id=trade_to_close.get('trade_id', 'N/A'),
                            symbol=symbol,
                            entry_time=trade_to_close['entry_time'],
                            entry_price=trade_to_close['entry_price'],
                            exit_time=datetime.now(),
                            exit_price=current_price,
                            pnl=pnl,
                            trade_duration=trade_duration,
                            exit_reason='target_profit',
                            strategy_id='hard_target',
                            ai_confidence_score=trade_to_close.get('ai_score', 0),
                            news_sentiment_score=news_sentiment_score,
                            ai_safety_activation=ai_safety_activation,
                            max_profit=0.0,
                            max_drawdown=0.0,
                            ai_audit_trail=ai_audit_trail
                        )
                        logger.info(f"Position for {symbol} closed due to Hard TGT (AI-adjusted) at {current_price}.")
                        send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'target_profit', 'symbol': symbol, 'price': current_price})
            elif trade['direction'] == 'SELL':
                if current_price >= sl_price: # For SELL, SL is above entry
                    trade_to_close = trade
                    if trade_to_close and self.order_manager.close_order(symbol, current_price):
                        pnl = (trade_to_close['entry_price'] - current_price) * trade_to_close['quantity']
                        trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                        news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                        ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                        ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                        self.trade_logger.log_trade(
                            trade_id=trade_to_close.get('trade_id', 'N/A'),
                            symbol=symbol,
                            entry_time=trade_to_close['entry_time'],
                            entry_price=trade_to_close['entry_price'],
                            exit_time=datetime.now(),
                            exit_price=current_price,
                            pnl=pnl,
                            trade_duration=trade_duration,
                            exit_reason='stop_loss',
                            strategy_id='hard_sl',
                            ai_confidence_score=trade_to_close.get('ai_score', 0),
                            news_sentiment_score=news_sentiment_score,
                            ai_safety_activation=ai_safety_activation,
                            max_profit=0.0,
                            max_drawdown=0.0,
                            ai_audit_trail=ai_audit_trail
                        )
                        logger.info(f"Position for {symbol} closed due to Hard SL (AI-adjusted) at {current_price}.")
                        send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'stop_loss', 'symbol': symbol, 'price': current_price})
                elif current_price <= tgt_price: # For SELL, TGT is below entry
                    trade_to_close = trade
                    if trade_to_close and self.order_manager.close_order(symbol, current_price):
                        pnl = (trade_to_close['entry_price'] - current_price) * trade_to_close['quantity']
                        trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                        news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                        ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                        ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                        self.trade_logger.log_trade(
                            trade_id=trade_to_close.get('trade_id', 'N/A'),
                            symbol=symbol,
                            entry_time=trade_to_close['entry_time'],
                            entry_price=trade_to_close['entry_price'],
                            exit_time=datetime.now(),
                            exit_price=current_price,
                            pnl=pnl,
                            trade_duration=trade_duration,
                            exit_reason='target_profit',
                            strategy_id='hard_target',
                            ai_confidence_score=trade_to_close.get('ai_score', 0),
                            news_sentiment_score=news_sentiment_score,
                            ai_safety_activation=ai_safety_activation,
                            max_profit=0.0,
                            max_drawdown=0.0,
                            ai_audit_trail=ai_audit_trail
                        )
                        logger.info(f"Position for {symbol} closed due to Hard TGT (AI-adjusted) at {current_price}.")
                        send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'target_profit', 'symbol': symbol, 'price': current_price})

    def check_ai_tsl_exit(self, open_positions, historical_data):
        """
        Applies volatility-aware AI-driven trailing stop-loss with leverage adjustments.
        """
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue

            current_price = historical_data[symbol]['close'].iloc[-1]
            tsl_details = self.ai_module.get_tsl_movement(symbol, trade, historical_data[symbol])

            if trade['direction'] == 'BUY':
                # Get the TSL from profit lock, if it exists and is tighter
                profit_locked_tsl = trade.get('trailing_sl', 0)
                # If profit_locked_tsl is greater than the AI-calculated new_tsl, use profit_locked_tsl
                # This ensures the TSL doesn't loosen if profit lock has set a tighter one
                effective_new_tsl = max(tsl_details["new_tsl"], profit_locked_tsl)

                if effective_new_tsl != trade.get('trailing_sl', 0):
                    self.order_manager.update_position(symbol, {'trailing_sl': effective_new_tsl})
                    logger.info(f"AI-TSL updated for {symbol}: {tsl_details['tsl_percent']:.2f}% (vol:{tsl_details['volatility']:.2f}, lev:{tsl_details['leverage']}, pnl:{tsl_details['pnl_percent']:.2f}%)")
                
                if current_price <= trade.get('trailing_sl', 0):
                    trade_to_close = self.order_manager.get_open_positions().get(symbol)
                    if trade_to_close and self.order_manager.close_order(symbol, current_price):
                        pnl = (current_price - trade_to_close['entry_price']) * trade_to_close['quantity']
                        trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                        news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                        ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                        ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                        self.trade_logger.log_trade(
                            trade_id=trade_to_close.get('trade_id', 'N/A'),
                            symbol=symbol,
                            entry_time=trade_to_close['entry_time'],
                            entry_price=trade_to_close['entry_price'],
                            exit_time=datetime.now(),
                            exit_price=current_price,
                            pnl=pnl,
                            trade_duration=trade_duration,
                            exit_reason='ai_tsl',
                            strategy_id='ai_tsl',
                            ai_confidence_score=trade_to_close.get('ai_score', 0),
                            news_sentiment_score=news_sentiment_score,
                            ai_safety_activation=ai_safety_activation,
                            max_profit=0.0,
                            max_drawdown=0.0,
                            ai_audit_trail=ai_audit_trail
                        )
                        logger.info(f"AI-TSL hit for {symbol}. Position closed at {current_price}.")
                        send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'ai_tsl', 'symbol': symbol, 'price': current_price})
                    
            else:  # SELL direction
                # Get the TSL from profit lock, if it exists and is tighter (lower for SELL)
                profit_locked_tsl = trade.get('trailing_sl', float('inf'))
                # If profit_locked_tsl is less than the AI-calculated new_tsl, use profit_locked_tsl
                effective_new_tsl = min(tsl_details["new_tsl"], profit_locked_tsl)

                if effective_new_tsl != trade.get('trailing_sl', float('inf')):
                    self.order_manager.update_position(symbol, {'trailing_sl': effective_new_tsl})
                    logger.info(f"AI-TSL updated for {symbol} (SHORT): {tsl_details['tsl_percent']:.2f}% (vol:{tsl_details['volatility']:.2f}, lev:{tsl_details['leverage']}, pnl:{tsl_details['pnl_percent']:.2f}%)")
                
                if current_price >= trade.get('trailing_sl', float('inf')):
                    trade_to_close = self.order_manager.get_open_positions().get(symbol)
                    if trade_to_close and self.order_manager.close_order(symbol, current_price):
                        pnl = (trade_to_close['entry_price'] - current_price) * trade_to_close['quantity']
                        trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                        news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                        ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                        ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                        self.trade_logger.log_trade(
                            trade_id=trade_to_close.get('trade_id', 'N/A'),
                            symbol=symbol,
                            entry_time=trade_to_close['entry_time'],
                            entry_price=trade_to_close['entry_price'],
                            exit_time=datetime.now(),
                            exit_price=current_price,
                            pnl=pnl,
                            trade_duration=trade_duration,
                            exit_reason='ai_tsl',
                            strategy_id='ai_tsl',
                            ai_confidence_score=trade_to_close.get('ai_score', 0),
                            news_sentiment_score=news_sentiment_score,
                            ai_safety_activation=ai_safety_activation,
                            max_profit=0.0,
                            max_drawdown=0.0,
                            ai_audit_trail=ai_audit_trail
                        )
                        logger.info(f"AI-TSL hit for {symbol} (SHORT). Position closed at {current_price}.")
                        send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'ai_tsl', 'symbol': symbol, 'price': current_price})

    def check_trend_flip_exit(self, open_positions, historical_data):
        """
        Checks for a trend flip signal, with AI confirmation, to exit a position early.
        """
        # ✅ FIX: Wrap the loop with `list()` to prevent `RuntimeError`.
        for symbol, trade in list(open_positions.items()):
            if symbol not in historical_data or historical_data[symbol].empty:
                continue
            
            data = historical_data[symbol]
            current_trend = self.ai_module.get_trend_direction(data)
            
            exit_condition = False
            if trade['direction'] == 'BUY' and current_trend == 'DOWN':
                if self.ai_module.confirm_trend_reversal(symbol, data):
                    logger.info(f"AI confirmed trend flip for {symbol} (BUY to DOWN).")
                    exit_condition = True
                else:
                    logger.info(f"AI denied trend flip for {symbol} (BUY to DOWN). Holding position.")
            elif trade['direction'] == 'SELL' and current_trend == 'UP':
                if self.ai_module.confirm_trend_reversal(symbol, data):
                    logger.info(f"AI confirmed trend flip for {symbol} (SELL to UP).")
                    exit_condition = True
                else:
                    logger.info(f"AI denied trend flip for {symbol} (SELL to UP). Holding position.")
            
            if exit_condition:
                trade_to_close = self.order_manager.get_open_positions().get(symbol)
                if trade_to_close and self.order_manager.close_order(symbol, data['close'].iloc[-1]):
                    current_price = data['close'].iloc[-1]
                    pnl = (current_price - trade_to_close['entry_price']) * trade_to_close['quantity'] if trade_to_close['direction'] == 'BUY' else (trade_to_close['entry_price'] - current_price) * trade_to_close['quantity']
                    trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                    news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                    ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                    ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                    self.trade_logger.log_trade(
                        trade_id=trade_to_close.get('trade_id', 'N/A'),
                        symbol=symbol,
                        entry_time=trade_to_close['entry_time'],
                        entry_price=trade_to_close['entry_price'],
                        exit_time=datetime.now(),
                        exit_price=current_price,
                        pnl=pnl,
                        trade_duration=trade_duration,
                        exit_reason='trend_flip',
                        strategy_id='trend_flip',
                        ai_confidence_score=trade_to_close.get('ai_score', 0),
                        news_sentiment_score=news_sentiment_score,
                        ai_safety_activation=ai_safety_activation,
                        max_profit=0.0,
                        max_drawdown=0.0,
                        ai_audit_trail=ai_audit_trail
                    )
                    logger.info(f"Position for {symbol} closed due to AI-confirmed trend flip.")
                    send_event_webhook('trade_signal', {'signal_type': 'exit', 'reason': 'trend_flip', 'symbol': symbol, 'price': data['close'].iloc[-1]})

    def check_entry_signals(self, timestamp: datetime, historical_data: dict):
        """
        Checks for new trade entry signals based on AI scoring and news sentiment.
        """
        if len(self.order_manager.get_open_positions()) >= self.max_active_positions:
            logger.info("Max active positions reached. Skipping entry signal check.")
            return

        # Adjust leverage for holidays or special sessions
        leverage_multiplier_adj = 1.0
        if self.data_fetcher.is_holiday_or_special_session():
            leverage_multiplier_adj = self.holiday_leverage_multiplier
            logger.info(f"Holiday/special session detected. Applying leverage multiplier of {leverage_multiplier_adj}.")

        # Further adjust leverage if crash guard is active
        if self.is_crash_active:
            leverage_multiplier_adj *= 0.1 # Significantly reduce leverage during a crash
            logger.warning(f"Crash guard active. Further reducing leverage to {leverage_multiplier_adj}.")

        for symbol, data in historical_data.items():
            if data.empty:
                continue

            # 1. Get News Sentiment
            sentiment_score = self.news_filter.get_and_analyze_sentiment(symbol)
            try:
                score_val = float(sentiment_score)
            except (TypeError, ValueError):
                score_val = 0.0
            logger.info(f"Sentiment for {symbol}: {score_val:.2f}")

            # Skip BUY if sentiment is too negative
            if sentiment_score < -0.5: # Threshold for negative sentiment
                logger.info(f"Skipping BUY for {symbol} due to negative sentiment ({sentiment_score:.2f}).")
                continue

            # 2. Get AI Metrics
            ai_metrics = self.ai_module.get_ai_metrics(symbol, data, sentiment_score)
            signal_score = ai_metrics["ai_score"]
            circuit_potential = ai_metrics.get("circuit_potential", 0.0) # Get circuit potential
            # NOTE (before): leverage was forced to 1.0 or halved under some sentiment paths
            # Determine AI leverage:
            leverage = self._resolve_ai_leverage(signal_score, sentiment_score)
            
            # Apply holiday/special session adjustment
            leverage *= leverage_multiplier_adj

            logger.info(f"Signal score for {symbol}: {signal_score:.2f}")
            logger.info(f"Leverage for {symbol}: {leverage:.2f}x")
            logger.info(f"Circuit potential for {symbol}: {circuit_potential:.2f}")

            # 3. Determine Trade Direction (AI-driven)
            trade_direction = self.ai_module.get_trade_direction(symbol)

            # Add condition for circuit targeting: if high circuit potential, lower the entry threshold
            entry_threshold = 0.7
            if circuit_potential > 0.7: # If circuit potential is high
                entry_threshold = 0.6 # Lower the required signal score for entry
                logger.info(f"Lowering entry threshold for {symbol} due to high circuit potential.")

            if trade_direction and signal_score > entry_threshold: # Example threshold for entry
                # 4. Calculate position size
                entry_price = data['close'].iloc[-1]
                quantity = 10 # Placeholder

                # Add news sentiment and initial AI safety status to ai_metrics
                ai_metrics['news_sentiment_score'] = score_val
                ai_metrics['ai_safety_activation'] = 'none' # Default, will be updated if safety layer activates

                # 5. Place Order
                success = self.order_manager.place_order(symbol, trade_direction, quantity, entry_price, leverage=leverage, ai_metrics=ai_metrics)
                if success:
                    logger.info(f"Placed {trade_direction} order for {symbol} at {entry_price} with {leverage}x leverage.")
                    send_event_webhook('trade_signal', {
                        'signal_type': 'entry',
                        'symbol': symbol,
                        'direction': trade_direction,
                        'price': entry_price,
                        'quantity': quantity,
                        'leverage': leverage,
                        'signal_score': signal_score
                    })
                else:
                    logger.warning(f"Failed to place {trade_direction} order for {symbol}.")

    def close_all_positions_eod(self, historical_data: dict):
        """
        Closes all open positions at the end of the day.
        """
        open_positions = self.order_manager.get_open_positions()
        for symbol, trade in list(open_positions.items()):
            if symbol in historical_data and not historical_data[symbol].empty:
                current_price = historical_data[symbol]['close'].iloc[-1]
                trade_to_close = trade
                if trade_to_close and self.order_manager.close_order(symbol, current_price):
                    pnl = (current_price - trade_to_close['entry_price']) * trade_to_close['quantity'] if trade_to_close['direction'] == 'BUY' else (trade_to_close['entry_price'] - current_price) * trade_to_close['quantity']
                    trade_duration = (datetime.now() - trade_to_close['entry_time']).total_seconds()
                    news_sentiment_score = trade_to_close.get('news_sentiment_score', 0.0)
                    ai_safety_activation = trade_to_close.get('ai_safety_activation', 'none')
                    ai_audit_trail = json.dumps(trade_to_close.get('ai_metrics', {}))
                    self.trade_logger.log_trade(
                        trade_id=trade_to_close.get('trade_id', 'N/A'),
                        symbol=symbol,
                        entry_time=trade_to_close['entry_time'],
                        entry_price=trade_to_close['entry_price'],
                        exit_time=datetime.now(),
                        exit_price=current_price,
                        pnl=pnl,
                        trade_duration=trade_duration,
                        exit_reason='eod',
                        strategy_id='eod',
                        ai_confidence_score=trade_to_close.get('ai_score', 0),
                        news_sentiment_score=news_sentiment_score,
                        ai_safety_activation=ai_safety_activation,
                        max_profit=0.0,
                        max_drawdown=0.0,
                        ai_audit_trail=ai_audit_trail
                    )
                    logger.info(f"EOD exit for {symbol} at {current_price}.")

    def check_eod_exit(self, current_time, historical_data: dict):
        """
        Triggers an end-of-day exit at the specified time.
        """
        try:
            eod_time = datetime.strptime(self.auto_exit_time, "%H:%M").time()
            if current_time >= eod_time:
                open_positions = self.order_manager.get_open_positions()
                if open_positions:
                    self.close_all_positions_eod(historical_data)
                    send_event_webhook('safe_timeout', {'reason': 'end_of_day_exit', 'time': str(current_time)})
        except ValueError:
            logger.error(f"Invalid AUTO_EXIT_TIME format in config: {self.auto_exit_time}")

    def _resolve_ai_leverage(self, ai_score: float, sentiment_score: float) -> float:
        """
        Honor AI-provided leverage directly if available; otherwise use spec curve.
        Clamp to max leverage cap. Keep logic minimal & transparent.
        """
        # Try AI module first
        ai_leverage = None
        try:
            # Prefer keyword args to be robust against ai_module signatures
            ai_leverage = self.ai_module.get_leverage(
                signal_score=ai_score, sentiment_score=sentiment_score
            )
        except AttributeError:
            # ai_module has no get_leverage – use default curve
            pass
        except TypeError:
            # ai_module.get_leverage exists but signature differs; try positional
            try:
                ai_leverage = self.ai_module.get_leverage(ai_score, sentiment_score)
            except Exception:
                ai_leverage = None
        except Exception:
            ai_leverage = None

        if ai_leverage is None:
            ai_leverage = self._default_leverage_curve(ai_score)

        # Clamp safety
        if ai_leverage is None:
            ai_leverage = 1.0
        try:
            ai_leverage = float(ai_leverage)
        except Exception:
            ai_leverage = 1.0

        if ai_leverage < 1.0:
            ai_leverage = 1.0
        if ai_leverage > self._max_leverage_cap:
            ai_leverage = self._max_leverage_cap

        return ai_leverage

    @staticmethod
    def _default_leverage_curve(ai_score: float) -> float:
        """
        Spec-defined curve:
          ≥ 0.80 -> 5.0x
          0.50–0.79 -> 3.5x
          < 0.50 -> 1.0x
        """
        try:
            s = float(ai_score)
        except Exception:
            return 1.0
        if s >= 0.80:
            return 5.0
        if s >= 0.50:
            return 3.5
        return 1.0