import os
from dotenv import load_dotenv

"""
config.py

📌 Loads all environment variables for the DTS Intraday AI Trading System.

💡 This module:
1. Reads from `.env` file using `dotenv`.
2. Validates required keys are present.
3. Provides easy Python access to config values.
4. Keeps sensitive data out of the codebase.

Environment variables loaded:
- API keys & secrets for Angel One SmartAPI
- Dhan API keys
- Redis Cloud config
- Strategy & backtesting settings
- Market hours
- System identity (IP, MAC)
- Gemini AI Studio API key
- OpenAI API key
"""


# Load variables from .env
load_dotenv()

# Required environment variables
REQUIRED_KEYS = [
    "ANGELONE_API_KEY",
    "ANGELONE_CLIENT_ID",
    "ANGELONE_API_SECRET",
    "DHAN_API_KEY",
    "DHAN_API_SECRET",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_PASSWORD",
    "INITIAL_CAPITAL",
    "MARKET_OPEN",
    "MARKET_CLOSE",
    "SYSTEM_IP",
    "SYSTEM_MAC",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
]

# Validate required keys
missing = [key for key in REQUIRED_KEYS if os.getenv(key) is None]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# Config access
ANGELONE_API_KEY = os.getenv("ANGELONE_API_KEY")
ANGELONE_CLIENT_ID = os.getenv("ANGELONE_CLIENT_ID")
ANGELONE_API_SECRET = os.getenv("ANGELONE_API_SECRET")

DHAN_API_KEY = os.getenv("DHAN_API_KEY")
DHAN_API_SECRET = os.getenv("DHAN_API_SECRET")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL"))
MARKET_OPEN = os.getenv("MARKET_OPEN")  # e.g. "09:15"
MARKET_CLOSE = os.getenv("MARKET_CLOSE")  # e.g. "15:30"

SYSTEM_IP = os.getenv("SYSTEM_IP")
SYSTEM_MAC = os.getenv("SYSTEM_MAC")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    
