from src.backtest_runner import BacktestRunner
import unittest

class TestIntegration(unittest.TestCase):
    """Test suite for integration testing."""
    
    def test_import_success(self):
        """Test that BacktestRunner can be imported successfully for integration tests."""
        self.assertIsNotNone(BacktestRunner)
        self.assertTrue(hasattr(BacktestRunner, '__init__'))
