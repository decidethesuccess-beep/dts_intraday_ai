#
# Module: paper_trade_system.py
# Description: Simulates trades based on strategy signals.
#
# DTS Intraday AI Trading System - Paper Trade Simulator
# Version: 2025-08-15
#
# This module simulates all trade placements, exits, and PnL tracking.
# It uses Redis as a central hub for state management.
#

import logging
from typing import Dict, Any, List
import uuid
from datetime import datetime, timedelta

from src.redis_store import RedisStore
from src.constants import INITIAL_CAPITAL, MAX_ACTIVE_POSITIONS, CAPITAL_PER_TRADE_PCT, COOLDOWN_PERIOD_SECONDS

log = logging.getLogger(__name__)

class PaperTradeSystem:
    """
    Simulates a complete trading system, including capital management,
    position tracking, and logging to Redis.
    """
    def __init__(self, redis_store: RedisStore):
        self.redis_store = redis_store
        self.initial_capital = float(INITIAL_CAPITAL)
        self.max_positions = int(MAX_ACTIVE_POSITIONS)
        self.capital_per_trade = self.initial_capital * (float(CAPITAL_PER_TRADE_PCT) / 100)
        
        # Initialize capital in Redis if it's not set
        if self.redis_store.get_capital() is None:
            self.redis_store.set_capital(self.initial_capital)
            log.info(f"Initial capital set to {self.initial_capital}")

    def enter_position(self, symbol: str, direction: str, entry_price: float, quantity: int, trade_id: str):
        """
        Simulates entering a new trade and records it.
        """
        # Check if max positions are reached
        active_positions_count = self.redis_store.get_active_positions_count()
        if active_positions_count >= self.max_positions:
            log.warning(f"Cannot open new trade for {symbol}. Max positions ({self.max_positions}) reached.")
            return False

        # Check for capital availability
        current_capital = self.redis_store.get_capital()
        trade_cost = entry_price * quantity
        if trade_cost > current_capital:
            log.warning(f"Cannot open new trade for {symbol}. Insufficient capital.")
            return False
            
        trade_log = {
            'trade_id': trade_id,
            'symbol': symbol,
            'direction': direction,
            'status': 'open',
            'entry_price': entry_price,
            'quantity': quantity,
            'entry_time': datetime.now().isoformat()
        }
        self.redis_store.add_open_position(trade_log)
        self.redis_store.update_capital(-trade_cost)
        self.redis_store.add_to_cooldown(symbol, COOLDOWN_PERIOD_SECONDS)
        log.info(f"Opened new {direction} position for {symbol} at {entry_price}. Trade ID: {trade_id}")
        return True

    def exit_position(self, trade_id: str, exit_price: float, exit_reason: str):
        """
        Simulates exiting an existing trade and logs the PnL.
        """
        position = self.redis_store.get_open_position(trade_id)
        if not position:
            log.warning(f"Trade ID {trade_id} not found. Cannot exit.")
            return False

        pnl = (exit_price - position['entry_price']) * position['quantity'] if position['direction'] == 'BUY' \
              else (position['entry_price'] - exit_price) * position['quantity']
        
        closed_trade_log = {
            **position,
            'status': 'closed',
            'exit_price': exit_price,
            'exit_time': datetime.now().isoformat(),
            'exit_reason': exit_reason,
            'pnl': pnl
        }
        
        self.redis_store.remove_open_position(trade_id)
        self.redis_store.add_closed_trade(closed_trade_log)
        self.redis_store.update_capital(position['entry_price'] * position['quantity'] + pnl) # Return capital + profit
        log.info(f"Closed position for {position['symbol']} with PnL: {pnl:.2f}. Reason: {exit_reason}")
        return True

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retrieves a summary of the paper trading performance.
        """
        closed_trades = self.redis_store.get_all_closed_trades()
        total_pnl = sum(trade['pnl'] for trade in closed_trades)
        total_trades = len(closed_trades)
        winning_trades = sum(1 for trade in closed_trades if trade['pnl'] > 0)
        
        return {
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        }
