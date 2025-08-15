import datetime

"""
strategy.py
DTS Intraday AI Trading System - Strategy Logic Module

This file contains:
1. Trade Entry Conditions (BUY/SELL)
2. Trade Exit Conditions (TSL, SL, Target, Trend Reversal, Auto Exit)
3. Capital Allocation & Position Tracking
4. Signal Filtering (News Sentiment, Market Regime Awareness)
"""

from config import (
    INITIAL_CAPITAL,
    ANGELONE_API_KEY,
    ANGELONE_API_SECRET
)
from constants import (
    SL_PERCENT,
    TARGET_PERCENT,
    TSL_PERCENT,
    MAX_POSITIONS,
    CAPITAL_PER_TRADE_PERCENT
)

# === Strategy Parameters ===
SL = SL_PERCENT
TARGET = TARGET_PERCENT
TSL = TSL_PERCENT
CAPITAL_PER_TRADE = CAPITAL_PER_TRADE_PERCENT / 100
MAX_OPEN_POSITIONS = MAX_POSITIONS
MARKET_CLOSE_TIME = datetime.time(15, 20)

# === API Keys (if needed here) ===
api_key = ANGELONE_API_KEY
api_secret = ANGELONE_API_SECRET

# === State Variables ===
open_positions = []
closed_positions = []
available_capital = INITIAL_CAPITAL


# === Trade Entry Logic ===
def check_buy_signal(candle_data, ai_score, news_sentiment):
    """
    Determine whether to enter a BUY trade.
    candle_data: dict with OHLCV and timestamp
    ai_score: float from AI model
    news_sentiment: string or score ('positive', 'neutral', 'negative')
    Returns: bool
    """
    # Example logic: momentum, volume spike, AI score, sentiment
    momentum = candle_data['close'] > candle_data['open']
    volume_spike = candle_data['volume'] > 1.5 * candle_data.get('avg_volume', candle_data['volume'])
    ai_ok = ai_score > 0.7
    sentiment_ok = news_sentiment == 'positive'
    return momentum and volume_spike and ai_ok and sentiment_ok


def check_sell_signal(candle_data, ai_score, news_sentiment):
    """
    Determine whether to enter a SELL trade.
    """
    momentum = candle_data['close'] < candle_data['open']
    volume_spike = candle_data['volume'] > 1.5 * candle_data.get('avg_volume', candle_data['volume'])
    ai_ok = ai_score < -0.7
    sentiment_ok = news_sentiment == 'negative'
    return momentum and volume_spike and ai_ok and sentiment_ok


# === Trade Exit Logic ===
def check_exit_conditions(position, current_price, ai_trend_signal):
    """
    Evaluate if an open position should be exited.
    position: dict containing entry_price, direction, TSL, SL, target, etc.
    current_price: float
    ai_trend_signal: 'uptrend', 'downtrend', 'sideways'
    Returns: bool
    """
    direction = position['direction']
    entry_price = position['entry_price']
    sl = position['sl']
    target = position['target']
    tsl = position.get('tsl', sl)
    entry_time = position['entry_time']

    # Stop Loss
    if direction == 'BUY' and current_price <= tsl:
        return True
    if direction == 'SELL' and current_price >= tsl:
        return True

    # Target Hit
    if direction == 'BUY' and current_price >= target:
        return True
    if direction == 'SELL' and current_price <= target:
        return True

    # Trend Reversal
    if (direction == 'BUY' and ai_trend_signal == 'downtrend') or \
       (direction == 'SELL' and ai_trend_signal == 'uptrend'):
        return True

    # Time-based Auto Exit
    now = datetime.datetime.now()
    if now.time() >= MARKET_CLOSE_TIME:
        return True

    return False


# === Position Management ===
def open_new_position(symbol, direction, quantity, entry_price):
    """
    Create a new trade position.
    """
    global available_capital, open_positions
    capital_required = quantity * entry_price
    if available_capital < capital_required or len(open_positions) >= MAX_OPEN_POSITIONS:
        return None
    sl = entry_price * (1 - SL/100) if direction == 'BUY' else entry_price * (1 + SL/100)
    target = entry_price * (1 + TARGET/100) if direction == 'BUY' else entry_price * (1 - TARGET/100)
    position = {
        'symbol': symbol,
        'direction': direction,
        'quantity': quantity,
        'entry_price': entry_price,
        'sl': sl,
        'target': target,
        'tsl': sl,
        'entry_time': datetime.datetime.now()
    }
    open_positions.append(position)
    available_capital -= capital_required
    return position


def close_position(position, exit_price, reason):
    """
    Close an open position and log it.
    """
    global available_capital, open_positions, closed_positions
    pnl = 0
    if position['direction'] == 'BUY':
        pnl = (exit_price - position['entry_price']) * position['quantity']
    else:
        pnl = (position['entry_price'] - exit_price) * position['quantity']
    available_capital += exit_price * position['quantity']
    position['exit_price'] = exit_price
    position['exit_time'] = datetime.datetime.now()
    position['pnl'] = pnl
    position['exit_reason'] = reason
    open_positions.remove(position)
    closed_positions.append(position)
    return pnl


# === Utility Functions ===
def update_trailing_stop(position, current_price):
    """
    Adjust the trailing stop level if the trade moves in our favor.
    """
    direction = position['direction']
    tsl = position['tsl']
    entry_price = position['entry_price']
    if direction == 'BUY':
        new_tsl = max(tsl, current_price * (1 - TSL/100))
        position['tsl'] = new_tsl
    else:
        new_tsl = min(tsl, current_price * (1 + TSL/100))
        position['tsl'] = new_tsl


def is_market_closing():
    """Check if market close time is near."""
    now = datetime.datetime.now().time()
    return now >= MARKET_CLOSE_TIME


# === Main Signal Handler ===
def process_market_data(symbol, candle_data, ai_score, news_sentiment, ai_trend_signal):
    """
    Central entry point for processing each new candle.
    """
    global open_positions
    # Entry logic
    if len(open_positions) < MAX_OPEN_POSITIONS and available_capital > 0:
        if check_buy_signal(candle_data, ai_score, news_sentiment):
            quantity = int((available_capital * CAPITAL_PER_TRADE) // candle_data['close'])
            if quantity > 0:
                open_new_position(symbol, 'BUY', quantity, candle_data['close'])
        elif check_sell_signal(candle_data, ai_score, news_sentiment):
            quantity = int((available_capital * CAPITAL_PER_TRADE) // candle_data['close'])
            if quantity > 0:
                open_new_position(symbol, 'SELL', quantity, candle_data['close'])

    # Exit logic
    for position in open_positions[:]:
        update_trailing_stop(position, candle_data['close'])
        if check_exit_conditions(position, candle_data['close'], ai_trend_signal):
            close_position(position, candle_data['close'], 'exit_condition')