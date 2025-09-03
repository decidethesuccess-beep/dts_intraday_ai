import csv
import os
from datetime import datetime
from threading import Lock

class TradeLogger:
    def __init__(self, log_file_path='data/trade_log.csv'):
        self.log_file_path = log_file_path
        self.lock = Lock()
        self._initialize_file()

    def _initialize_file(self):
        with self.lock:
            if not os.path.exists(self.log_file_path) or os.path.getsize(self.log_file_path) == 0:
                with open(self.log_file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'trade_id', 'symbol', 'entry_time', 'entry_price', 
                        'exit_time', 'exit_price', 'pnl', 'trade_duration', 
                        'exit_reason', 'strategy_id', 'ai_confidence_score', 
                        'news_sentiment_score', 'ai_safety_activation', 
                        'max_profit', 'max_drawdown', 'ai_audit_trail'
                    ])

    def log_trade(self, trade_id, symbol, entry_time, entry_price, exit_time, 
                  exit_price, pnl, trade_duration, exit_reason, strategy_id, 
                  ai_confidence_score, news_sentiment_score, ai_safety_activation, 
                  max_profit, max_drawdown, ai_audit_trail='{}'):
        with self.lock:
            with open(self.log_file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    trade_id, symbol, entry_time, entry_price, exit_time, 
                    exit_price, pnl, trade_duration, exit_reason, strategy_id, 
                    ai_confidence_score, news_sentiment_score, ai_safety_activation, 
                    max_profit, max_drawdown, ai_audit_trail
                ])
