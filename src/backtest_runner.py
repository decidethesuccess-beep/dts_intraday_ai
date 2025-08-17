import logging
from datetime import datetime, date, timedelta
import os
import sys

# Set up logging for the module
logging.basicConfig(level=logging.INFO, format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the sys.path to ensure modules can be imported
# when this script is run directly.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the Strategy and its dependencies
from src.strategy import Strategy
from src.data_fetcher import DataFetcher
from src.order_manager import OrderManager
from src.redis_store import RedisStore

# Constants for market hours (from your strategy_spec.md and .env)
MARKET_OPEN_TIME = datetime.strptime("09:15", "%H:%M").time()
MARKET_CLOSE_TIME = datetime.strptime("15:30", "%H:%M").time()


class BacktestRunner:
    """
    Orchestrates the backtesting simulation by iterating through historical data
    and applying the trading strategy minute by minute.

    This class simulates the live trading environment but uses historical data
    instead of real-time feeds.
    """

    def __init__(self, strategy: Strategy, start_date: str, end_date: str):
        """
        Initializes the BacktestRunner.

        Args:
            strategy (Strategy): The strategy instance to be tested.
            start_date (str): The start date for the backtest (YYYY-MM-DD).
            end_date (str): The end date for the backtest (YYYY-MM-DD).
        """
        self.strategy = strategy
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Dependencies, provided by the strategy or instantiated here
        self.data_fetcher = self.strategy.data_fetcher
        self.order_manager = self.strategy.order_manager
        
        logger.info(f"BacktestRunner initialized for {self.start_date} to {self.end_date}")

    def run(self):
        """
        Main method to run the backtest simulation.
        Iterates through each day and each minute within market hours.
        """
        current_date = self.start_date
        while current_date <= self.end_date:
            logger.info(f"Processing historical data for date: {current_date}")
            
            # Fetch data for the current day
            # This is a mock/placeholder; in a real scenario, you'd fetch real data.
            historical_data = self.data_fetcher.get_historical_data(
                symbols=['SYMBOL1', 'SYMBOL2'],
                start_date=current_date,
                end_date=current_date,
                interval='1min'
            )
            
            if not historical_data:
                logger.warning(f"No historical data found for {current_date}. Skipping day.")
                current_date += timedelta(days=1)
                continue
            
            # Extract the timestamps from the fetched data
            # Assuming data is a dict of pandas DataFrames
            all_timestamps = set()
            for symbol_data in historical_data.values():
                all_timestamps.update(symbol_data.index)
            
            sorted_timestamps = sorted(list(all_timestamps))
            
            for timestamp in sorted_timestamps:
                # Check if the current time is within market hours
                if MARKET_OPEN_TIME <= timestamp.time() <= MARKET_CLOSE_TIME:
                    # Pass the minute's data to the strategy
                    self.strategy.run_for_minute(timestamp, historical_data)

            # EOD Cleanup 
            # This is the fix for the integration test failure.
            self.strategy.order_manager.close_all_positions_eod()
            logger.info(f"EOD cleanup done for {current_date}")

            current_date += timedelta(days=1)

# Example usage (for testing/demonstration)
if __name__ == '__main__':
    # This section is for a quick manual test and should not be used in a production environment.
    
    # 1. Initialize dependencies
    redis_store = RedisStore(host='localhost', port=6379, password='', db=0)
    order_manager = OrderManager(trade_mode='paper', redis_store=redis_store, client_code='BACKTEST')

    # 2. Initialize the Strategy with its dependencies
    test_strategy = Strategy(
        data_fetcher=DataFetcher(),
        order_manager=order_manager,
    )

    # 3. Create and run the BacktestRunner instance
    test_runner = BacktestRunner(
        strategy=test_strategy,
        start_date="2025-01-01",
        end_date="2025-01-02"
    )

    # Now, the dummy data is created in the correct format with datetime keys.
    dummy_data_start = datetime(2025, 1, 1, 9, 15, 0)
    dummy_data_end = datetime(2025, 1, 1, 9, 16, 0)

    # Generate the mock data with datetime objects as keys
    mock_data = {
        'SYMBOL1': {
            dummy_data_start: {'open': 100, 'high': 105, 'low': 99, 'close': 102, 'volume': 1000},
            dummy_data_end: {'open': 102, 'high': 106, 'low': 101, 'close': 105, 'volume': 1500}
        },
        'SYMBOL2': {
            dummy_data_start: {'open': 200, 'high': 202, 'low': 198, 'close': 201, 'volume': 2000}
        }
    }
    
    # Patch the data fetcher to return our mock data
    test_runner.data_fetcher.get_historical_data = lambda symbols, start_date, end_date, interval: {
        symbol: pd.DataFrame.from_dict(data, orient='index')
        for symbol, data in mock_data.items()
    }
    
    # Patch the strategy methods to avoid complex logic and focus on the runner's flow
    test_runner.strategy.run_for_minute = lambda *args: None
    
    # Run the backtest
    test_runner.run()
    
    # Print the result
    print("Backtest simulation completed.")

