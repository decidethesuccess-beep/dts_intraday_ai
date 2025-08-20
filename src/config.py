#
# Module: config.py
# Description: Manages the configuration and environment variables for the trading system.
#
# DTS Intraday AI Trading System - Configuration
# Version: 2025-08-18
#
# Note: This module provides a single point of access for all configuration,
#       fetching values from environment variables with safe fallbacks.
#

import os
import json

# Central configuration dictionary. This can be imported directly as `config`.
# It's populated with values from the .env file or with safe defaults.
config = {
    # Angel One credentials
    "ANGELONE_API_SECRET": os.getenv("ANGELONE_API_SECRET", "your_api_secret"),
    "ANGELONE_CLIENT_CODE": os.getenv("ANGELONE_CLIENT_CODE", "your_client_code"),
    "ANGELONE_AUTH_TOKEN": os.getenv("ANGELONE_AUTH_TOKEN", "your_auth_token"),
    "ANGELONE_PUBLISHER_API_KEY": os.getenv("ANGELONE_PUBLISHER_API_KEY", "your_publisher_api_key"),
    "ANGELONE_PUBLISHER_SECRET": os.getenv("ANGELONE_PUBLISHER_SECRET", "your_publisher_secret"),
    
    # Strategy parameters
    "TRADE_MODE": os.getenv("TRADE_MODE", "paper"),
    "INITIAL_CAPITAL": float(os.getenv("INITIAL_CAPITAL", 100000.0)),
    "CAPITAL_PER_TRADE_PCT": float(os.getenv("CAPITAL_PER_TRADE_PCT", 10.0)),
    "MAX_ACTIVE_POSITIONS": int(os.getenv("MAX_ACTIVE_POSITIONS", 5)),
    "TOP_N_SYMBOLS": int(os.getenv("TOP_N_SYMBOLS", 50)),
    "TSL_PERCENT": float(os.getenv("TSL_PERCENT", 2.0)),
    "SL_PERCENT": float(os.getenv("SL_PERCENT", 2.0)),
    "TARGET_PERCENT": float(os.getenv("TARGET_PERCENT", 10.0)),
    "DEFAULT_LEVERAGE_MULTIPLIER": float(os.getenv("DEFAULT_LEVERAGE_MULTIPLIER", 1.0)),

    # AI integration
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "your_gemini_api_key"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "your_openai_api_key"),
    
    # Redis configuration
    "REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
    "REDIS_PORT": int(os.getenv("REDIS_PORT", 6379)),
    "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", None),
    "REDIS_DB": int(os.getenv("REDIS_DB", 0)),

    # System & market timings
    "MARKET_OPEN_TIME": os.getenv("MARKET_OPEN_TIME", "09:15"),
    "MARKET_CLOSE_TIME": os.getenv("MARKET_CLOSE_TIME", "15:30"),
}

def get_config(key: str = None, default=None):
    """
    Returns configuration values from the central `config` dictionary.
    - If a key is provided, returns that specific config value.
    - If key is None, returns the entire config dictionary.
    
    Args:
        key (str, optional): The configuration key to retrieve. Defaults to None.
        default (optional): The default value if the key is not found.
    
    Returns:
        The configuration value or the entire dictionary.
    """
    if key:
        return config.get(key, default)
    return config
