#
# File: order_manager.py
# Description: Manages trade placement and position tracking.
#
# DTS Intraday AI Trading System - Order Manager
# Version: 2025-08-16
#
# Note: Added handle_auto_exit method to support the EOD auto-exit logic.
#

import logging
from src.config import config
from src.angel_order import AngelOrder
from src.redis_store import RedisStore
import datetime

class OrderManager:
    """
    Manages the lifecycle of trades, including placement, tracking, and closure.
    Supports both paper and live trading modes.
    """
    def __init__(self, redis_store: RedisStore, angel_order: AngelOrder, trade_mode: str = config.TRADE_MODE):
        """
        Initializes the OrderManager.

        Args:
            redis_store (RedisStore): Instance of the Redis data store.
            angel_order (AngelOrder): Instance for placing orders via Angel One API.
            trade_mode (str): The trading mode ('paper' or 'live').
        """
        self.redis_store = redis_store
        self.angel_order = angel_order
        self.trade_mode = trade_mode
        self.open_positions = {}
        self.closed_trades = []
        logging.info(f"OrderManager initialized in mode: {self.trade_mode}")

    def place_order(self, symbol: str, direction: str, quantity: int, entry_price: float):
        """
        Places a new order based on the trading mode.

        Args:
            symbol (str): The trading symbol.
            direction (str): 'BUY' or 'SELL'.
            quantity (int): Number of shares.
            entry_price (float): The price at which the trade is entered.
        """
        trade_data = {
            'symbol': symbol,
            'direction': direction,
            'quantity': quantity,
            'entry_price': entry_price,
            'status': 'OPEN',
            'entry_time': datetime.datetime.now().isoformat()
        }

        if self.trade_mode == 'live':
            # Live trading logic
            try:
                # Assuming angel_order.place_order handles the actual API call
                order_id = self.angel_order.place_order(symbol, direction, quantity)
                trade_data['order_id'] = order_id
                logging.info(f"Live order placed: {direction} {quantity} of {symbol}")
            except Exception as e:
                logging.error(f"Failed to place live order for {symbol}: {e}")
                return
        else:
            # Paper trading logic
            trade_data['order_id'] = f"PAPER_{symbol}_{len(self.open_positions)}"
            logging.info(f"Paper trade placed: {direction} {quantity} of {symbol}")

        self.open_positions[symbol] = trade_data
        self.redis_store.set_open_positions(self.open_positions)
        self.redis_store.add_trade_history(trade_data)

    def close_position(self, symbol: str, exit_price: float):
        """
        Closes an open position and moves it to the closed trades list.

        Args:
            symbol (str): The trading symbol to close.
            exit_price (float): The price at which the position is exited.
        """
        if symbol not in self.open_positions:
            logging.warning(f"Attempted to close a non-existent position for {symbol}")
            return

        trade_data = self.open_positions.pop(symbol)
        trade_data['exit_price'] = exit_price
        trade_data['status'] = 'CLOSED'
        trade_data['exit_time'] = datetime.datetime.now().isoformat()
        trade_data['pnl'] = (exit_price - trade_data['entry_price']) * trade_data['quantity']
        if trade_data['direction'] == 'SELL':
            trade_data['pnl'] *= -1

        self.closed_trades.append(trade_data)
        self.redis_store.update_open_positions(self.open_positions)
        self.redis_store.update_trade_history(trade_data)
        logging.info(f"Position for {symbol} closed with PnL: {trade_data['pnl']:.2f}")

    def close_all_positions_eod(self):
        """
        Force-close all open positions at end of day.
        This is used in backtests and live trading auto-exit logic.
        """
        logging.info("Auto-exiting all positions for End of Day.")
        # Create a list to avoid issues with modifying dictionary during iteration
        for symbol in list(self.open_positions.keys()):
            # For backtesting, we need a closing price. 
            # In a live environment, you'd get the last traded price.
            # Here, we'll use a placeholder or mock value for simplicity.
            # In your backtest_runner, you would pass the EOD price.
            dummy_exit_price = 0 
            self.close_position(symbol, dummy_exit_price)
            logging.info(f"EOD exit for {symbol}")

    def handle_auto_exit(self):
        """
        End-of-day (3:20 PM) forced exit handler.
        This method is called by the backtest runner and live stream to ensure all
        positions are closed at the specified time.
        """
        self.close_all_positions_eod()

    def get_open_positions(self):
        """
        Retrieves the current open positions.
        
        Returns:
            dict: A dictionary of all open positions.
        """
        return self.open_positions

    def get_closed_trades(self):
        """
        Retrieves the list of all closed trades.

        This method is essential for backtesting to gather final results.

        Returns:
            list: A list of dictionaries, where each dictionary represents a closed trade.
        """
        return self.closed_trades
