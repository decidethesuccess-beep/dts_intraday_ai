#
# Module: utils.py
# Description: A collection of general utility functions for the trading system.
#
# DTS Intraday AI Trading System - Utilities
# Version: 2025-08-15
#

import datetime
import logging
import math
from dotenv import load_dotenv
import os
from src.constants import (
    INITIAL_CAPITAL,
    CAPITAL_PER_TRADE_PCT,
    DEFAULT_LEVERAGE_MULTIPLIER,
)

def get_today_str():
    """
    Returns the current date as a string in 'YYYY-MM-DD' format.
    
    Returns:
        str: The formatted date string.
    """
    return datetime.date.today().strftime('%Y-%m-%d')

def calculate_pnl(trade):
    """
    Calculates the Profit and Loss (PnL) for a given trade.
    
    Args:
        trade (dict): A dictionary representing a single trade,
                      containing 'direction', 'entry_price', 'exit_price', and 'quantity'.
    
    Returns:
        float: The calculated PnL.
    """
    try:
        if trade['direction'] == 'BUY':
            pnl = (trade['exit_price'] - trade['entry_price']) * trade['quantity']
        elif trade['direction'] == 'SELL':
            pnl = (trade['entry_price'] - trade['exit_price']) * trade['quantity']
        else:
            logging.warning(f"Invalid trade direction: {trade.get('direction')}")
            pnl = 0.0
        return pnl
    except KeyError as e:
        logging.critical(f"Missing key in trade data: {e}. Cannot calculate PnL.")
        return 0.0
    except Exception as e:
        logging.critical(f"An unexpected error occurred during PnL calculation: {e}")
        return 0.0

def calculate_position_size(entry_price):
    """
    Calculates the number of shares to trade based on capital allocation and leverage.

    Args:
        entry_price (float): The price at which the position will be entered.
    
    Returns:
        int: The calculated integer quantity of shares.
    """
    if not entry_price or entry_price <= 0:
        logging.warning("Entry price is zero or invalid, returning 0 position size.")
        return 0
    
    try:
        # Calculate the total capital allocated for this trade
        trade_capital = INITIAL_CAPITAL * (CAPITAL_PER_TRADE_PCT / 100)
        
        # Apply the default leverage multiplier
        trade_value = trade_capital * DEFAULT_LEVERAGE_MULTIPLIER
        
        # Calculate the quantity and round down to the nearest integer
        quantity = math.floor(trade_value / entry_price)

        return quantity
    except Exception as e:
        logging.critical(f"An error occurred during position size calculation: {e}")
        return 0

def load_env_vars():
    """
    Loads environment variables from the .env file.
    
    Returns:
        None
    """
    load_dotenv()
    logging.info("Environment variables loaded from .env file.")

# You can add other utility functions here as needed.
