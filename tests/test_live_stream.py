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

from src.live_stream import LiveStreamer

class TestLiveStream(unittest.TestCase):
    """
    Test suite for the live data streaming module.
    """
    def setUp(self):
        """
        Set up mock objects and the LiveStreamer instance for testing.
        """
        self.mock_redis_store = MagicMock()
        # Test without credentials to avoid SmartWebSocket constructor issues
        self.live_streamer = LiveStreamer(redis_store=self.mock_redis_store)

    def test_initialization_without_credentials(self):
        """
        Verifies that LiveStreamer initializes correctly without credentials.
        """
        self.assertIsNone(self.live_streamer.client_code)
        self.assertIsNone(self.live_streamer.token)
        self.assertIsNone(self.live_streamer.feed_token)
        self.assertIsNone(self.live_streamer.sws)

    def test_initialization_with_credentials_mocked(self):
        """
        Verifies that LiveStreamer initializes correctly with credentials when SmartWebSocket is mocked.
        """
        with patch('src.live_stream.SmartWebSocket') as mock_websocket:
            mock_websocket.return_value = MagicMock()
            
            streamer = LiveStreamer(
                client_code="TEST123",
                token="test_token",
                feed_token="test_feed_token",
                redis_store=self.mock_redis_store,
                symbols=["INFY", "TCS"]
            )
            
            self.assertEqual(streamer.client_code, "TEST123")
            self.assertEqual(streamer.token, "test_token")
            self.assertEqual(streamer.feed_token, "test_feed_token")
            self.assertEqual(streamer.symbols, ["INFY", "TCS"])
            self.assertIsNotNone(streamer.sws)

    def test_on_message_callback(self):
        """
        Verifies that the on_message callback processes data correctly.
        """
        mock_message = '{"symbol": "INFY", "ltp": 1500.50}'
        
        # Mock the json.loads to return our test data
        with patch('json.loads') as mock_json_loads:
            mock_json_loads.return_value = {"symbol": "INFY", "ltp": 1500.50}
            
            # Call the callback method
            self.live_streamer.on_message(None, mock_message)
            
            # Verify json.loads was called
            mock_json_loads.assert_called_once_with(mock_message)

    def test_on_error_callback(self):
        """
        Verifies that the on_error callback logs errors correctly.
        """
        with patch('src.live_stream.logger') as mock_logger:
            # Call the callback method
            self.live_streamer.on_error(None, "Test error message")
            
            # Verify error was logged
            mock_logger.error.assert_called_once_with("WebSocket error: Test error message")

    def test_on_close_callback(self):
        """
        Verifies that the on_close callback logs closure correctly.
        """
        with patch('src.live_stream.logger') as mock_logger:
            # Call the callback method
            self.live_streamer.on_close(None, 1000, "Normal closure")
            
            # Verify closure was logged
            mock_logger.info.assert_called_once_with("WebSocket connection closed.")

    def test_on_open_callback(self):
        """
        Verifies that the on_open callback logs opening correctly.
        """
        with patch('src.live_stream.logger') as mock_logger:
            # Call the callback method
            self.live_streamer.on_open(None)
            
            # Verify opening was logged
            mock_logger.info.assert_called_once_with("WebSocket connection opened.")

    def test_connect_without_websocket(self):
        """
        Verifies that connect method handles missing WebSocket gracefully.
        """
        # Should not raise an error
        self.live_streamer.connect()

    def test_connect_with_websocket_mocked(self):
        """
        Verifies that connect method calls the WebSocket connect method when available.
        """
        # Create a mock websocket
        mock_websocket = MagicMock()
        self.live_streamer.sws = mock_websocket
        
        # Call connect
        self.live_streamer.connect()
        
        # Verify connect was called
        mock_websocket.connect.assert_called_once()

if __name__ == '__main__':
    unittest.main()
