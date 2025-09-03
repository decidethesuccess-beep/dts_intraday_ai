import logging
import requests
import json
from datetime import datetime, date, time, timedelta
from src.redis_store import RedisStore

# Initialize RedisStore
redis_store = RedisStore()

# Global variable for caching holidays in local memory (for quick lookups after initial load)
_trading_holidays = set()

NSE_HOLIDAY_API_URL = "https://www.nseindia.com/api/holiday-master?type=trading"
HOLIDAYS_JSON_PATH = "d:/dts_intraday_ai/data/holidays.json"

# Constants for Redis keys and expiry
REDIS_HOLIDAYS_KEY = 'trading_holidays'
REDIS_HOLIDAYS_TIMESTAMP_KEY = 'trading_holidays_last_refresh'
DAILY_EXPIRY_SECONDS = 24 * 60 * 60 # 24 hours

def load_holidays():
    """
    Loads trading holidays from Redis cache, NSE API, or falls back to a local JSON file.
    Caches the holidays in Redis and a global set.
    """
    global _trading_holidays
    _trading_holidays.clear() # Clear existing holidays before loading new ones

    # 1. Try to load from Redis cache
    cached_holidays = redis_store.get_holidays()
    last_refresh_timestamp = redis_store.get_holiday_refresh_timestamp()

    if cached_holidays and last_refresh_timestamp:
        # Check if cache is still fresh (within the last 24 hours)
        if (datetime.now() - last_refresh_timestamp).total_seconds() < DAILY_EXPIRY_SECONDS:
            _trading_holidays.update(cached_holidays)
            logging.info("Successfully loaded holidays from Redis cache.")
            return
        else:
            logging.info("Redis cache for holidays is stale. Attempting refresh from API.")

    holidays_from_api = set()
    try:
        # 2. Attempt to fetch from NSE API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(NSE_HOLIDAY_API_URL, headers=headers, timeout=5)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        for holiday in data.get('data', []):
            holiday_date_str = holiday.get('tradingDate')
            if holiday_date_str:
                try:
                    # Assuming format like "26-Jan-2025"
                    holiday_date = datetime.strptime(holiday_date_str, "%d-%b-%Y").date()
                    holidays_from_api.add(holiday_date)
                except ValueError:
                    logging.warning(f"Could not parse holiday date from API: {holiday_date_str}")
        
        if holidays_from_api:
            _trading_holidays.update(holidays_from_api)
            redis_store.set_holidays(holidays_from_api, DAILY_EXPIRY_SECONDS)
            logging.info("Successfully loaded and cached holidays from NSE API.")
        else:
            logging.warning("NSE API returned no holiday data. Falling back to local JSON.")
            _load_holidays_from_json_fallback()

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch holidays from NSE API: {e}. Falling back to local JSON.")
        _load_holidays_from_json_fallback()
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from NSE API response. Falling back to local JSON.")
        _load_holidays_from_json_fallback()
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading holidays from API: {e}. Falling back to local JSON.")
        _load_holidays_from_json_fallback()

def _load_holidays_from_json_fallback():
    """Helper to load holidays from the local JSON file and cache them in Redis."""
    global _trading_holidays
    try:
        with open(HOLIDAYS_JSON_PATH, 'r') as f:
            data = json.load(f)
            json_holidays = set()
            for holiday in data.get('tradingHolidays', []):
                holiday_date_str = holiday.get('tradingDate')
                if holiday_date_str:
                    try:
                        # Assuming format like "26-Jan-2025"
                        holiday_date = datetime.strptime(holiday_date_str, "%d-%b-%Y").date()
                        json_holidays.add(holiday_date)
                    except ValueError:
                        logging.warning(f"Could not parse holiday date from JSON: {holiday_date_str}")
            _trading_holidays = json_holidays
            # Store fallback holidays in Redis with a very long expiry (e.g., 1 year) as they are static
            redis_store.set_holidays(json_holidays, 365 * 24 * 60 * 60) 
            logging.info("Successfully loaded holidays from local JSON fallback and cached in Redis.")
    except FileNotFoundError:
        logging.error(f"Holiday JSON file not found at {HOLIDAYS_JSON_PATH}")
        _trading_holidays = set() # Ensure it's empty if file not found
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {HOLIDAYS_JSON_PATH}")
        _trading_holidays = set()
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading holidays from JSON: {e}")
        _trading_holidays = set()

def is_trading_holiday(check_date: date) -> bool:
    """
    Checks if a given date is a trading holiday (including weekends).
    Ensures holiday data is loaded if not already.
    """
    global _trading_holidays
    
    # Ensure holidays are loaded at least once
    if not _trading_holidays:
        load_holidays()
    
    # Check for weekend
    if check_date.weekday() >= 5: # Saturday (5) or Sunday (6)
        return True
        
    # Check against loaded holidays
    return check_date in _trading_holidays

def refresh_holidays():
    """
    Forces a refresh of the trading holiday data from the primary source (NSE API).
    """
    logging.info("Forcing refresh of trading holiday data from NSE API.")
    # Invalidate Redis cache by setting a very short expiry or deleting the key
    redis_store.set_holidays(set(), 1) # Set empty set with 1 second expiry to force reload
    load_holidays()
    logging.info("Trading holiday data refresh forced and reloaded.")
