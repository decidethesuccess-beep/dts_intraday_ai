#
# Module: constants.py
# Description: Centralized file for all system-wide constants.
#
# DTS Intraday AI Trading System - Constants
# Version: 2025-08-15
#

# ===============================
# 📦 Trading Modes
# ===============================
# These constants define the operational mode of the trading system.
# They are used across various modules (e.g., strategy, backtest_runner, order_manager)
# to switch between different behaviors.

BACKTEST_MODE = 'backtest'
LIVE_MODE = 'live'
PAPER_MODE = 'paper'

# ===============================
# ⚙️ Strategy and System Parameters
# ===============================
# The following constants are loaded from the .env file, but are defined here
# to prevent import errors and provide fallbacks.

# Trading mode
TRADE_MODE = 'paper'

# Stop Loss percentage
SL_PERCENT = 2.0

# Target profit percentage
TARGET_PERCENT = 10.0

# Trailing Stop Loss percentage
TSL_PERCENT = 1.0

# Initial capital for simulations
INITIAL_CAPITAL = 1000000.0

# Default leverage multiplier
DEFAULT_LEVERAGE_MULTIPLIER = 5.0

# Capital allocation percentage per trade
CAPITAL_PER_TRADE_PCT = 10.0

# Maximum number of concurrent positions
MAX_ACTIVE_POSITIONS = 10

# Number of top symbols to auto-subscribe
TOP_N_SYMBOLS = 100

# ===============================
# ⏰ Market Timings
# ===============================
# Market hours and cool-down periods.

MARKET_OPEN_TIME = '09:15'
MARKET_CLOSE_TIME = '15:30'
COOLDOWN_PERIOD_SECONDS = 300

# ===============================
# 🧠 AI & System Flags
# ===============================
# Flags for enabling/disabling AI features and system debug mode.

DEBUG = True
MIN_PROFIT_MODE = False
AI_OPTIMIZATION_ENABLED = False
AI_LEVERAGE_ENABLED = False
