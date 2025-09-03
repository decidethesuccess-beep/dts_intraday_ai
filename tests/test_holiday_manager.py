import pytest
from unittest.mock import patch, MagicMock, ANY
from datetime import date, datetime, timedelta
import json
import requests

# Import the module to be tested
from src import holiday_manager
from src.redis_store import RedisStore

# Mock data for NSE API response
MOCK_NSE_API_RESPONSE = {
    "data": [
        {"tradingDate": "26-Jan-2025", "weekDay": "Sunday", "description": "Republic Day"},
        {"tradingDate": "15-Aug-2025", "weekDay": "Friday", "description": "Independence Day"},
    ]
}

# Mock data for local holidays.json
MOCK_LOCAL_HOLIDAYS_JSON = {
    "tradingHolidays": [
        {"tradingDate": "02-Oct-2025", "weekDay": "Thursday", "description": "Mahatma Gandhi Jayanti"},
        {"tradingDate": "25-Dec-2025", "weekDay": "Thursday", "description": "Christmas"}
    ]
}

@pytest.fixture
def mock_redis_store_instance():
    """Fixture to mock the redis_store instance within holiday_manager."""
    with patch('src.holiday_manager.redis_store', spec=RedisStore) as mock_instance:
        mock_instance.is_connected.return_value = True
        mock_instance.set_holidays = MagicMock()
        mock_instance.get_holidays = MagicMock(return_value=None)
        mock_instance.get_holiday_refresh_timestamp = MagicMock(return_value=None)
        yield mock_instance

@pytest.fixture(autouse=True)
def reset_holiday_manager_state(mock_redis_store_instance):
    """Resets the internal state of holiday_manager before each test and ensures mock_redis_store is used."""
    holiday_manager._trading_holidays.clear()
    # Reset mocks for each test
    mock_redis_store_instance.set_holidays.reset_mock()
    mock_redis_store_instance.get_holidays.reset_mock()
    mock_redis_store_instance.get_holiday_refresh_timestamp.reset_mock()
    mock_redis_store_instance.get_holidays.return_value = None
    mock_redis_store_instance.get_holiday_refresh_timestamp.return_value = None
    yield

@patch('requests.get')
@patch('builtins.open', new_callable=MagicMock)
@patch('json.load')
def test_load_holidays_from_api_success(mock_json_load, mock_open, mock_requests_get, mock_redis_store_instance):
    """Test successful loading of holidays from NSE API."""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = MOCK_NSE_API_RESPONSE
    mock_requests_get.return_value.raise_for_status.return_value = None

    holiday_manager.load_holidays()

    assert date(2025, 1, 26) in holiday_manager._trading_holidays
    assert date(2025, 8, 15) in holiday_manager._trading_holidays
    mock_redis_store_instance.set_holidays.assert_called_once()
    args, kwargs = mock_redis_store_instance.set_holidays.call_args
    assert date(2025, 1, 26) in args[0]
    assert date(2025, 8, 15) in args[0]
    assert args[1] == holiday_manager.DAILY_EXPIRY_SECONDS

@patch('requests.get', side_effect=requests.exceptions.RequestException)
@patch('builtins.open', new_callable=MagicMock)
@patch('json.load')
def test_load_holidays_api_fallback_to_json(mock_json_load, mock_open, mock_requests_get, mock_redis_store_instance):
    """Test fallback to local JSON when API fails."""
    mock_json_load.return_value = MOCK_LOCAL_HOLIDAYS_JSON
    mock_open.return_value.__enter__.return_value = mock_open.return_value

    holiday_manager.load_holidays()

    assert date(2025, 10, 2) in holiday_manager._trading_holidays
    assert date(2025, 12, 25) in holiday_manager._trading_holidays
    mock_redis_store_instance.set_holidays.assert_called_once()
    args, kwargs = mock_redis_store_instance.set_holidays.call_args
    assert date(2025, 10, 2) in args[0]
    assert date(2025, 12, 25) in args[0]
    assert args[1] == (365 * 24 * 60 * 60) # Long expiry for static JSON

@patch('requests.get')
def test_load_holidays_from_redis_cache(mock_requests_get, mock_redis_store_instance):
    """Test loading holidays from fresh Redis cache."""
    mock_redis_store_instance.get_holidays.return_value = {date(2025, 1, 1), date(2025, 1, 2)}
    mock_redis_store_instance.get_holiday_refresh_timestamp.return_value = datetime.now() - timedelta(hours=1)

    holiday_manager.load_holidays()

    assert date(2025, 1, 1) in holiday_manager._trading_holidays
    assert date(2025, 1, 2) in holiday_manager._trading_holidays
    mock_requests_get.assert_not_called() # API should not be called if cache is fresh

@patch('requests.get')
@patch('builtins.open', new_callable=MagicMock)
@patch('json.load')
def test_load_holidays_redis_cache_stale_forces_api(mock_json_load, mock_open, mock_requests_get, mock_redis_store_instance):
    """Test that stale Redis cache forces an API call."""
    mock_redis_store_instance.get_holidays.return_value = {date(2024, 1, 1)}
    mock_redis_store_instance.get_holiday_refresh_timestamp.return_value = datetime.now() - timedelta(days=2) # Stale

    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = MOCK_NSE_API_RESPONSE
    mock_requests_get.return_value.raise_for_status.return_value = None

    holiday_manager.load_holidays()

    mock_requests_get.assert_called_once_with(holiday_manager.NSE_HOLIDAY_API_URL, headers=ANY, timeout=5)
    assert date(2025, 1, 26) in holiday_manager._trading_holidays
    assert date(2025, 8, 15) in holiday_manager._trading_holidays
    assert date(2024, 1, 1) not in holiday_manager._trading_holidays # Old data should be cleared

@patch('requests.get')
@patch('builtins.open', new_callable=MagicMock)
@patch('json.load')
def test_refresh_holidays(mock_json_load, mock_open, mock_requests_get, mock_redis_store_instance):
    """Test refresh_holidays forces API call and updates cache."""
    # Simulate some old data in Redis
    mock_redis_store_instance.get_holidays.return_value = {date(2024, 1, 1)}
    mock_redis_store_instance.get_holiday_refresh_timestamp.return_value = datetime.now() - timedelta(days=10)

    # Configure API to return new data
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = MOCK_NSE_API_RESPONSE
    mock_requests_get.return_value.raise_for_status.return_value = None

    holiday_manager.refresh_holidays()

    mock_redis_store_instance.set_holidays.assert_called() # Should be called to invalidate and then to set new data
    mock_requests_get.assert_called_once() # API should be called
    assert date(2025, 1, 26) in holiday_manager._trading_holidays
    assert date(2024, 1, 1) not in holiday_manager._trading_holidays # Old data should be gone

# Helper for Any type matching in mocks
class Any(object):
    def __eq__(self, other):
        return True

@pytest.mark.parametrize("test_date, expected", [
    (date(2025, 1, 26), True),  # Republic Day from API
    (date(2025, 8, 15), True),  # Independence Day from API
    (date(2025, 9, 1), False),  # Normal trading day
    (date(2025, 9, 6), True),   # Saturday
    (date(2025, 9, 7), True),   # Sunday
])
@patch('requests.get')
@patch('builtins.open', new_callable=MagicMock)
@patch('json.load')
def test_is_trading_holiday_api_success(mock_json_load, mock_open, mock_requests_get, mock_redis_store_instance, test_date, expected):
    """Test is_trading_holiday function with API success and weekend checks."""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = MOCK_NSE_API_RESPONSE
    mock_requests_get.return_value.raise_for_status.return_value = None
    mock_json_load.return_value = MOCK_LOCAL_HOLIDAYS_JSON # This won't be used if API succeeds
    mock_open.return_value.__enter__.return_value = mock_open.return_value

    # Ensure holidays are loaded before checking
    holiday_manager.load_holidays()
    
    assert holiday_manager.is_trading_holiday(test_date) == expected

@pytest.mark.parametrize("test_date, expected", [
    (date(2025, 10, 2), True),  # Mahatma Gandhi Jayanti from JSON fallback
    (date(2025, 12, 25), True), # Christmas from JSON fallback
    (date(2025, 9, 1), False),  # Normal trading day (should still be false even with fallback)
])
@patch('requests.get', side_effect=requests.exceptions.RequestException) # Force JSON fallback for these tests
@patch('builtins.open', new_callable=MagicMock)
@patch('json.load')
def test_is_trading_holiday_json_fallback(mock_json_load, mock_open, mock_requests_get, mock_redis_store_instance, test_date, expected):
    """Test is_trading_holiday function with JSON fallback when API fails."""
    mock_json_load.return_value = MOCK_LOCAL_HOLIDAYS_JSON
    mock_open.return_value.__enter__.return_value = mock_open.return_value

    # Ensure holidays are loaded before checking
    holiday_manager.load_holidays()
    
    assert holiday_manager.is_trading_holiday(test_date) == expected
