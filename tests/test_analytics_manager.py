#
# Module: test_analytics_manager.py
# Description: Unit tests for the AnalyticsManager class.
#
# DTS Intraday AI Trading System - Analytics Manager Unit Tests
# Version: 2025-09-02
#

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
import json

# Set up the path to import from the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the class to be tested
from src.analytics_manager import AnalyticsManager

class TestAnalyticsManager(unittest.TestCase):
    """
    Test suite for the AnalyticsManager class.
    """

    def setUp(self):
        """
        Set up a dummy trade log for each test.
        """
        self.dummy_trade_log_path = "data/dummy_trade_log.csv"
        self.audit_trail_data = {
            'T001': {"ai_score": 0.8, "leverage": 2.0},
            'T002': {"ai_score": 0.6, "leverage": 1.0}
        }
        # Create a dummy trade log file
        dummy_data = {
            'trade_id': ['T001', 'T002', 'T003', 'T004'],
            'symbol': ['AAPL', 'GOOG', 'AAPL', 'MSFT'],
            'strategy_id': ['S1', 'S2', 'S1', 'S2'],
            'entry_time': ['2025-01-01 09:30:00', '2025-01-01 10:00:00', '2025-01-01 11:00:00', '2025-01-01 12:00:00'],
            'exit_time': ['2025-01-01 09:45:00', '2025-01-01 10:15:00', '2025-01-01 11:30:00', '2025-01-01 12:30:00'],
            'pnl': [100.0, -50.0, 200.0, -25.0],
            'ai_confidence_score': [0.8, 0.6, 0.9, 0.7],
            'ai_audit_trail': [json.dumps(self.audit_trail_data['T001']), json.dumps(self.audit_trail_data['T002']), None, "invalid_json"]
        }
        self.dummy_df = pd.DataFrame(dummy_data)
        self.dummy_df.to_csv(self.dummy_trade_log_path, index=False)

        self.analytics_manager = AnalyticsManager(trade_log_path=self.dummy_trade_log_path)

    def tearDown(self):
        """
        Clean up dummy trade log and generated files after each test.
        """
        if os.path.exists(self.dummy_trade_log_path):
            os.remove(self.dummy_trade_log_path)
        # Clean up generated PnL curve image if it exists
        output_path = "data/test_pnl_curve.png"
        if os.path.exists(output_path):
            os.remove(output_path)

    def test_generate_pnl_curve(self):
        """
        Tests that the PnL curve is generated and saved as an image.
        """
        output_path = "data/test_pnl_curve.png"
        self.analytics_manager.generate_pnl_curve(output_path=output_path)
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)

    def test_generate_analytics_report(self):
        """
        Tests that the analytics report is generated and printed.
        """
        # We can't easily test the print output, so we'll just check that the function runs without errors
        try:
            self.analytics_manager.generate_analytics_report()
        except Exception as e:
            self.fail(f"generate_analytics_report() raised {e} unexpectedly!")

    def test_get_all_ai_audit_trails(self):
        """
        Tests that the AI audit trails are correctly parsed from the trade log.
        """
        audit_trails = self.analytics_manager.get_all_ai_audit_trails()
        self.assertEqual(len(audit_trails), 4)
        self.assertEqual(audit_trails['T001'], self.audit_trail_data['T001'])
        self.assertEqual(audit_trails['T002'], self.audit_trail_data['T002'])
        self.assertEqual(audit_trails['T003'], {})
        self.assertEqual(audit_trails['T004'], {"error": "Could not parse audit trail."})

if __name__ == '__main__':
    unittest.main()
