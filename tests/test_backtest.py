from src.backtest_runner import BacktestRunner
import unittest

class TestBacktestRunner(unittest.TestCase):
    """Test suite for the BacktestRunner class."""
    
    def test_import_success(self):
        """Test that BacktestRunner can be imported successfully."""
        self.assertIsNotNone(BacktestRunner)
        self.assertTrue(hasattr(BacktestRunner, '__init__'))
