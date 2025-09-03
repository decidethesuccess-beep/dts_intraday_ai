#
# Module: constants.py
# Description: Centralized file for all system-wide constants.
#
# DTS Intraday AI Trading System - Constants
# Version: 2025-08-20
#
# Note: Added the missing AUTO_EXIT_TIME constant to fix the ImportError.
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
AUTO_EXIT_TIME = '15:20' # ✅ FIX: Added missing constant for end-of-day exit.

# ===============================
# 🧠 AI & System Flags
# ===============================
# Flags for enabling/disabling AI features and system debug mode.

DEBUG = True
MIN_PROFIT_MODE = False
MIN_PROFIT_THRESHOLD = 0.5 # Percentage profit to trigger min profit mode
MIN_PROFIT_PERCENTAGE_EXIT = 0.2 # Percentage profit to lock in when min profit mode is active
AI_OPTIMIZATION_ENABLED = False
AI_LEVERAGE_ENABLED = False

# ===============================
# ⚡ Circuit Limits
# ===============================
# Constants related to stock circuit breakers and early detection.

NSE_CIRCUIT_LIMITS = [0.02, 0.05, 0.10, 0.20] # Common NSE circuit percentages (2%, 5%, 10%, 20%)
CIRCUIT_BREAKER_THRESHOLD = 0.05 # Threshold for early detection (e.g., 5% away from circuit)
