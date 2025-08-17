#
# File: config.py
# Description: Centralized configuration loader for the DTS Intraday AI Trading System.
#
# This module loads all environment variables from the .env file, providing
# a single source of truth for all configurable settings across the application.
#

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    A class to hold all configuration settings loaded from the .env file.
    This provides a clean, object-oriented way to access settings.
    """
    # Angel One Keys
    ANGELONE_CLIENT_CODE = os.getenv("ANGELONE_CLIENT_CODE")
    ANGELONE_API_SECRET = os.getenv("ANGELONE_API_SECRET")
    ANGELONE_PUBLISHER_API_KEY = os.getenv("ANGELONE_PUBLISHER_API_KEY")
    ANGELONE_PUBLISHER_SECRET = os.getenv("ANGELONE_PUBLISHER_SECRET")
    ANGELONE_HISTORICAL_API_KEY = os.getenv("ANGELONE_HISTORICAL_API_KEY")
    ANGELONE_HISTORICAL_SECRET = os.getenv("ANGELONE_HISTORICAL_SECRET")
    ANGELONE_MARKET_API_KEY = os.getenv("ANGELONE_MARKET_API_KEY")
    ANGELONE_MARKET_SECRET = os.getenv("ANGELONE_MARKET_SECRET")
    ANGELONE_PASSWORD = os.getenv("ANGELONE_PASSWORD")
    ANGELONE_TOTP_SECRET = os.getenv("ANGELONE_TOTP_SECRET")
    REDIRECT_URL = os.getenv("REDIRECT_URL")
    
    # Strategy Parameters
    TRADE_MODE = os.getenv("TRADE_MODE", "paper")
    CAPITAL_PER_TRADE_PCT = float(os.getenv("CAPITAL_PER_TRADE_PCT", 10.0))
    MAX_ACTIVE_POSITIONS = int(os.getenv("MAX_ACTIVE_POSITIONS", 10))
    TSL_PERCENT = float(os.getenv("TSL_PERCENT", 1.0))
    SL_PERCENT = float(os.getenv("SL_PERCENT", 2.0))
    TARGET_PERCENT = float(os.getenv("TARGET_PERCENT", 10.0))
    MIN_PROFIT_MODE = os.getenv("MIN_PROFIT_MODE", "enabled")
    TOP_N_SYMBOLS = int(os.getenv("TOP_N_SYMBOLS", 100))
    INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", 1000000.0))
    DEFAULT_LEVERAGE_MULTIPLIER = float(os.getenv("DEFAULT_LEVERAGE_MULTIPLIER", 5.0))
    
    # Market Hours
    MARKET_OPEN_TIME = os.getenv("MARKET_OPEN_TIME", "09:15")
    MARKET_CLOSE_TIME = os.getenv("MARKET_CLOSE_TIME", "15:30")
    COOLDOWN_PERIOD_SECONDS = int(os.getenv("COOLDOWN_PERIOD_SECONDS", 300))
    AUTO_EXIT_TIME = os.getenv("AUTO_EXIT_TIME", "15:20")

    # System Identity & Debug
    PUBLIC_IP = os.getenv("PUBLIC_IP")
    MAC_ADDRESS = os.getenv("MAC_ADDRESS")
    DEBUG = os.getenv("DEBUG", "false").lower() == 'true'

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_URL = os.getenv("REDIS_URL")

    # AI Integration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    @classmethod
    def validate_config(cls):
        """
        Validates essential configuration settings.
        """
        if not cls.ANGELONE_CLIENT_CODE:
            logging.warning("ANGELONE_CLIENT_CODE is not set in .env")
        if not cls.TRADE_MODE in ['paper', 'live']:
            raise ValueError(f"Invalid TRADE_MODE: {cls.TRADE_MODE}. Must be 'paper' or 'live'.")

# Instantiate the config object to be used throughout the application
config = Config()

# Call the validation method to check for missing keys on startup
config.validate_config()
