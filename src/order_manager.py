#
# File: order_manager.py
# Description: Manages trade placement and position tracking.
#
# DTS Intraday AI Trading System - Order Manager
# Version: 2025-08-29
#
# Note: Removed the circular import of BacktestRunner.
#
import logging
from src.config import get_config
from src.angel_order import AngelOrder
from src.redis_store import RedisStore
import datetime

# FIX: Define a global variable for configuration
config = get_config()

class OrderManager:
    """
    Manages the lifecycle of trades, including placement, tracking, and closure.
    Supports both paper and live trading modes.
    """
    def __init__(self, redis_store: RedisStore, angel_order: AngelOrder, trade_mode: str = None):
        """
        Initializes the OrderManager.

        Args:
            redis_store (RedisStore): Instance of the Redis data store.
            angel_order (AngelOrder): Instance for placing orders via Angel One API.
            trade_mode (str): The trading mode ('paper' or 'live').
        """
        self.redis_store = redis_store
        self.angel_order = angel_order
        
        # FIX: Access TRADE_MODE via dict-style .get() to avoid AttributeError
        if trade_mode is None:
            trade_mode = config.get("TRADE_MODE", "paper")
            
        self.trade_mode = trade_mode
        self.open_positions = {}
        
        
        # 🔑 Initialize capital management properties
        self.initial_capital = config.get("INITIAL_CAPITAL", 1000000.0)
        self.available_capital = self.initial_capital
        self.daily_leverage_cap = config.get("DAILY_LEVERAGE_CAP", 20.0)
        self.daily_exposure_cap = config.get("DAILY_EXPOSURE_CAP", 500000.0)
        self.current_leverage = 0.0
        self.current_exposure = 0.0
        
        logging.info(f"OrderManager initialized in '{self.trade_mode}' mode with {self.initial_capital} capital.")

    def place_order(self, symbol: str, direction: str, quantity: int, entry_price: float, leverage: float = 1.0, ai_metrics: dict = None):
        """
        Places a new order for a given symbol.
        
        Args:
            symbol (str): The symbol to trade.
            direction (str): 'BUY' or 'SELL'.
            quantity (int): Number of shares/units to trade.
            entry_price (float): The price at which the trade is entered.
            leverage (float): The leverage to apply to the trade.
            ai_metrics (dict): A dictionary of AI metrics associated with the trade.
        """
        trade_value = quantity * entry_price
        
        # Check for sufficient capital
        if trade_value > self.available_capital * leverage:
            logging.warning(f"Insufficient capital to place trade for {symbol}. Needed: {trade_value}, Available: {self.available_capital}")
            return False

        # Check against daily leverage and exposure caps
        if self.current_leverage + leverage > self.daily_leverage_cap:
            logging.warning(f"Daily leverage cap reached. Cannot place trade for {symbol}.")
            return False
        
        if self.current_exposure + trade_value > self.daily_exposure_cap:
            logging.warning(f"Daily exposure cap reached. Cannot place trade for {symbol}.")
            return False

        # If a trade for this symbol is already open, do not place a new one.
        if symbol in self.open_positions:
            logging.warning(f"Position for {symbol} is already open. Skipping new entry.")
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
        
        self.open_positions[symbol] = trade
        # 🔑 Deduct the capital used for the trade
        self.available_capital -= trade_value
        self.current_leverage += leverage
        self.current_exposure += trade_value
        logging.info(f"Order placed for {symbol}. Available capital: {self.available_capital}")
        return True

    def close_order(self, symbol: str, exit_price: float):
        """
        Closes an open position for a given symbol.
        
        Args:
            symbol (str): The symbol to close.
            exit_price (float): The price at which the trade is exited.
        """
        if symbol not in self.open_positions:
            logging.warning(f"Cannot close position for {symbol}. No open position found.")
            return False

        trade = self.open_positions.pop(symbol)
        trade['exit_price'] = exit_price
        trade['exit_time'] = datetime.now()
        trade['status'] = 'CLOSED'
        
        # 🔑 Calculate and restore capital
        entry_value = trade['quantity'] * trade['entry_price']
        exit_value = trade['quantity'] * exit_price
        pnl = exit_value - entry_value
        
        self.available_capital += entry_value + pnl # Restore initial capital plus PnL
        self.current_leverage -= trade.get('leverage', 1.0)
        self.current_exposure -= entry_value
        
        trade['pnl'] = pnl
        self.redis_store.add_closed_trade(trade)
        
        logging.info(f"Position for {symbol} closed. PnL: {pnl:.2f}. New available capital: {self.available_capital:.2f}")
        return True
    
    def close_all_positions_eod(self, historical_data: dict):
        """
        Closes all open positions at the end of the day.
        """
        logging.info("Auto-exiting all positions for End of Day.")
        # Create a list to avoid issues with modifying dictionary during iteration
        for symbol in list(self.open_positions.keys()):
            if symbol in historical_data and not historical_data[symbol].empty:
                exit_price = historical_data[symbol]['close'].iloc[-1]
                self.close_order(symbol, exit_price)
                logging.info(f"EOD exit for {symbol} at {exit_price}")
            else:
                # If no historical data is available, close with a dummy price (or handle as an error)
                self.close_order(symbol, 0)
                logging.warning(f"EOD exit for {symbol} with no price data available.")

    def handle_auto_exit(self, historical_data: dict):
        """
        End-of-day (3:20 PM) forced exit handler.
        This method is called by the backtest runner and live stream to ensure all
        positions are closed at the specified time.
        """
        self.close_all_positions_eod(historical_data)

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
            list: A list of dictionaries, where each
        """
        return self.redis_store.get_all_closed_trades()
    
    def update_position(self, symbol, updates):
        """
        Updates an open position with new data.
        """
        if symbol in self.open_positions:
            self.open_positions[symbol].update(updates)
            logging.info(f"Position for {symbol} updated with: {updates}")
        else:
            logging.warning(f"Attempted to update non-existent position for {symbol}")