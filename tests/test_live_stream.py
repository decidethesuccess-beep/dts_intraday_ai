#
# Module: test_live_stream.py
# Description: Unit and integration tests for live_stream.py.
#
# DTS Intraday AI Trading System - Live Stream Test Module
# Version: 2025-08-15
#
# This file contains tests to validate the live data streaming component,
# ensuring it can correctly ingest real-time market data and update the
# Redis store for the rest of the system to use.
#

import unittest
from unittest.mock import MagicMock, patch

# Note: As live_stream.py was not provided, this test file assumes a basic
# structure where a LiveStreamer class exists.
from src.live_stream import LiveStreamer

class TestLiveStream(unittest.TestCase):
    """
    Test suite for the live data streaming module.
    """
    @patch('src.live_stream.RedisStore')
    @patch('src.live_stream.AngelOneAPI') # Mock the Angel One API for live data
    def setUp(self, mock_api, mock_redis):
        """
        Set up mock objects and the LiveStreamer instance for testing.
        """
        self.mock_redis_store = mock_redis.return_value
        self.mock_angel_api = mock_api.return_value
        self.live_streamer = LiveStreamer(self.mock_redis_store)

    def test_live_data_ingestion_and_redis_update(self):
        """
        Verifies that data is received from the mocked API and
        correctly stored in Redis.
        """
        # Mock the data received from the live stream
        mock_data = {
            'symbol': 'INFY',
            'ltp': 1500.50,
            'timestamp': '2025-08-15T10:00:00'
        }
        
        # Simulate receiving a data tick
        self.live_streamer._on_data_received(mock_data)
        
        # Check that Redis methods were called correctly
        self.mock_redis_store.set_ltp_for_symbol.assert_called_with('INFY', 1500.50)
        self.mock_redis_store.set_last_trade_time.assert_called_with('INFY', '2025-08-15T10:00:00')

    def test_reconnection_logic_on_error(self):
        """
        Simulates an error in the live stream and verifies that the
        reconnection logic is triggered.
        """
        with patch.object(self.live_streamer, 'connect_to_stream') as mock_connect:
            self.live_streamer._on_error("Connection lost.")
            
            # Check if the connection method was called again
            self.assertTrue(mock_connect.called)
            
if __name__ == '__main__':
    unittest.main()
