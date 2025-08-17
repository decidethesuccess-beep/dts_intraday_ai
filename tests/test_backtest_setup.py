import unittest
from datetime import datetime, date
from unittest.mock import MagicMock
import pandas as pd

from src.backtest_runner import BacktestRunner
from src.strategy import Strategy
from src.order_manager import OrderManager
from src.data_fetcher import DataFetcher

class TestBacktestRunner(unittest.TestCase):

    def setUp(self):
        """
        Set up a mock Strategy and BacktestRunner for unit tests.
        Ensures dates are passed as strings and historical data is pandas DataFrames.
        """
        # 1. Create a mock DataFetcher
        self.mock_data_fetcher = MagicMock(spec=DataFetcher)
        
        # Mock historical data (datetime-indexed DataFrames)
        dummy_start = datetime(2025, 8, 15, 9, 15)
        dummy_end = datetime(2025, 8, 15, 9, 16)
        self.mock_historical_data = {
            'SYMBOL1': pd.DataFrame.from_dict({
                dummy_start: {'open': 100, 'high': 105, 'low': 99, 'close': 102, 'volume': 1000},
                dummy_end: {'open': 102, 'high': 106, 'low': 101, 'close': 105, 'volume': 1500}
            }, orient='index'),
            'SYMBOL2': pd.DataFrame.from_dict({
                dummy_start: {'open': 200, 'high': 202, 'low': 198, 'close': 201, 'volume': 2000}
            }, orient='index')
        }
        self.mock_data_fetcher.get_historical_data.return_value = self.mock_historical_data

        # 2. Create a mock OrderManager
        self.mock_order_manager = MagicMock(spec=OrderManager)
        
        # 3. Create a mock Strategy using the mocks above
        self.mock_strategy = MagicMock(spec=Strategy)
        self.mock_strategy.data_fetcher = self.mock_data_fetcher
        self.mock_strategy.order_manager = self.mock_order_manager
        
        # Patch strategy.run_for_minute to avoid executing real logic
        self.mock_strategy.run_for_minute = MagicMock()
        
        # 4. Initialize the BacktestRunner with string dates
        self.runner = BacktestRunner(
            strategy=self.mock_strategy,
            start_date="2025-08-15",
            end_date="2025-08-15"
        )
