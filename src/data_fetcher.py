#
# Module: data_fetcher.py
# Description: Retrieves market data from the Angel One API.
#
# DTS Intraday AI Trading System - Data Fetcher
# Version: 2025-08-15
#

import logging
import pandas as pd
import datetime

class DataFetcher:
    """
    Handles retrieval of market data (OHLCV, LTP) from the Angel One API.
    """

    def __init__(self, api_client=None):
        """
        Initializes the DataFetcher with an optional API client.
        
        Args:
            api_client: An instance of the Angel One API client.
        """
        self.api_client = api_client
        logging.info("DataFetcher initialized.")

    def get_tradable_symbols(self):
        """
        Fetches and filters the list of tradable symbols from a static source.
        
        This method simulates fetching the list of symbols from the Angel One static JSON,
        as described in the strategy specification.
        
        Returns:
            list: A list of filtered, tradable stock symbols (e.g., ['RELIANCE', 'TCS']).
        """
        # In a real-world scenario, you would fetch from the URL
        # and filter based on SEM_EXM_EXCH_ID = NSE, SEM_SEGMENT = E, SEM_SERIES = EQ.
        
        # For backtesting, we can return a sample list.
        return ['TATAMOTORS', 'RELIANCE', 'TCS', 'INFY']

    def get_historical_data(self, symbol, from_date, to_date, interval='1min'):
        """
        Retrieves historical OHLCV data for a given symbol and time range.
        
        Args:
            symbol (str): The stock symbol.
            from_date (str): Start date/time in 'YYYY-MM-DD HH:MM' format.
            to_date (str): End date/time in 'YYYY-MM-DD HH:MM' format.
            interval (str): The data interval (e.g., '1min', '5min').
            
        Returns:
            pd.DataFrame: A DataFrame with OHLCV data.
        """
        logging.info(f"Fetching historical data for {symbol} from {from_date} to {to_date}")
        
        # This is a mock implementation for backtesting.
        # It generates dummy 1-minute data for a single day.
        
        start_time = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M')
        end_time = datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M')
        
        index = pd.date_range(start_time, end_time, freq='1T')
        data = {
            'open': [1000 + i * 0.1 for i in range(len(index))],
            'high': [1005 + i * 0.1 for i in range(len(index))],
            'low': [995 + i * 0.1 for i in range(len(index))],
            'close': [1002 + i * 0.1 for i in range(len(index))],
            'volume': [1000 + i * 10 for i in range(len(index))]
        }
        df = pd.DataFrame(data, index=index)
        
        return df

    def get_latest_price(self, symbol):
        """
        Retrieves the latest traded price (LTP) for a given symbol.
        
        Args:
            symbol (str): The stock symbol.
            
        Returns:
            float: The latest traded price.
        """
        # This is a mock implementation for backtesting.
        return 1000.0

