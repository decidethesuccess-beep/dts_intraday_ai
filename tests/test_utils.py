#
# Module: test_utils.py
# Description: Unit tests for utils.py.
#
# DTS Intraday AI Trading System - Utilities Test Module
# Version: 2025-08-15
#
# This file contains unit tests for the helper functions in utils.py,
# ensuring that calculations, datetime parsing, and formatting are correct.
#

import unittest
from unittest.mock import patch
from datetime import datetime, time
import sys
import os

# --- FIX for ModuleNotFoundError when running tests from a subdirectory ---
# Dynamically adds the project root to the Python path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
# --------------------------------------------------------------------------

# Now the import will work correctly
from src.utils import setup_logging, is_market_open, calculate_position_size, format_currency

class TestUtils(unittest.TestCase):
    """
    Test suite for the utility functions.
    """
    def test_is_market_open(self):
        """
        Tests the market open time check with different scenarios.
        """
        with patch('src.utils.datetime') as mock_datetime:
            # Test a time within market hours
            mock_datetime.now.return_value = datetime(2025, 8, 15, 10, 30)
            mock_datetime.strptime.side_effect = lambda t, f: datetime.strptime(t, f)
            mock_datetime.time.return_value = time(10, 30)
            self.assertTrue(is_market_open("09:15", "15:30"))
            
            # Test a time before market open
            mock_datetime.now.return_value = datetime(2025, 8, 15, 9, 0)
            mock_datetime.time.return_value = time(9, 0)
            self.assertFalse(is_market_open("09:15", "15:30"))

            # Test a time after market close
            mock_datetime.now.return_value = datetime(2025, 8, 15, 16, 0)
            mock_datetime.time.return_value = time(16, 0)
            self.assertFalse(is_market_open("09:15", "15:30"))

    def test_calculate_position_size(self):
        """
        Tests the position size calculation based on capital and AI score.
        """
        capital = 100000.0
        capital_pct = 10.0
        
        # Test with high AI score (leverage=5.0)
        signal_score = 0.90
        size_high_score = calculate_position_size(capital, capital_pct, signal_score)
        self.assertAlmostEqual(size_high_score, capital * 0.1 * 5.0)
        
        # Test with medium AI score (leverage=3.5)
        signal_score = 0.60
        size_medium_score = calculate_position_size(capital, capital_pct, signal_score)
        self.assertAlmostEqual(size_medium_score, capital * 0.1 * 3.5)
        
        # Test with low AI score (leverage=1.0)
        signal_score = 0.40
        size_low_score = calculate_position_size(capital, capital_pct, signal_score)
        self.assertAlmostEqual(size_low_score, capital * 0.1 * 1.0)
        
    def test_format_currency(self):
        """
        Tests the currency formatting function.
        """
        self.assertEqual(format_currency(1234567.89), "₹ 1,234,567.89")
        self.assertEqual(format_currency(1234.5), "₹ 1,234.50")
        self.assertEqual(format_currency(99.99), "₹ 99.99")

if __name__ == '__main__':
    unittest.main()
