import os
import csv
from datetime import datetime
import pytest
import json
from src.trade_logger import TradeLogger

@pytest.fixture
def temp_log_file(tmp_path):
    """Create a temporary log file for testing."""
    log_file = tmp_path / "test_trade_log.csv"
    yield str(log_file)
    if os.path.exists(log_file):
        os.remove(log_file)

def test_trade_logger_init(temp_log_file):
    """Test that the trade logger initializes correctly and creates the header."""
    logger = TradeLogger(log_file_path=temp_log_file)
    assert os.path.exists(temp_log_file)
    with open(temp_log_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [
            'trade_id', 'symbol', 'entry_time', 'entry_price', 
            'exit_time', 'exit_price', 'pnl', 'trade_duration', 
            'exit_reason', 'strategy_id', 'ai_confidence_score', 
            'news_sentiment_score', 'ai_safety_activation', 
            'max_profit', 'max_drawdown', 'ai_audit_trail'
        ]

def test_log_trade(temp_log_file):
    """Test that a trade is logged correctly."""
    logger = TradeLogger(log_file_path=temp_log_file)
    ai_metrics = {"ai_score": 0.85, "leverage": 5.0, "trend_direction": "UP"}
    trade_data = {
        'trade_id': 'test_id_1',
        'symbol': 'RELIANCE',
        'entry_time': datetime(2025, 9, 1, 10, 0, 0),
        'entry_price': 2500.0,
        'exit_time': datetime(2025, 9, 1, 11, 0, 0),
        'exit_price': 2550.0,
        'pnl': 50.0,
        'trade_duration': 3600.0, # 1 hour in seconds
        'exit_reason': 'target_profit',
        'strategy_id': 'hard_target',
        'ai_confidence_score': 0.85,
        'news_sentiment_score': 0.7,
        'ai_safety_activation': 'none',
        'max_profit': 60.0,
        'max_drawdown': -10.0,
        'ai_audit_trail': json.dumps(ai_metrics)
    }
    logger.log_trade(**trade_data)

    with open(temp_log_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        logged_trade = next(reader)
        assert logged_trade == [
            'test_id_1', 'RELIANCE', str(datetime(2025, 9, 1, 10, 0, 0)), '2500.0', 
            str(datetime(2025, 9, 1, 11, 0, 0)), '2550.0', '50.0', '3600.0', 
            'target_profit', 'hard_target', '0.85', '0.7', 'none', '60.0', '-10.0',
            json.dumps(ai_metrics)
        ]
