import pandas as pd
import os
import logging
import plotly.graph_objects as go
import json

logger = logging.getLogger(__name__)

class AnalyticsManager:
    def __init__(self, trade_log_path='data/trade_log.csv'):
        self.trade_log_path = trade_log_path

    def _load_trade_log(self):
        if not os.path.exists(self.trade_log_path):
            logger.warning(f"Trade log file not found at {self.trade_log_path}. Returning empty DataFrame.")
            return pd.DataFrame()
        try:
            df = pd.read_csv(self.trade_log_path)
            # Ensure necessary columns are in correct format
            if 'entry_time' in df.columns:
                df['entry_time'] = pd.to_datetime(df['entry_time'])
            if 'exit_time' in df.columns:
                df['exit_time'] = pd.to_datetime(df['exit_time'])
            if 'pnl' in df.columns:
                df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            return df
        except Exception as e:
            logger.error(f"Error loading trade log from {self.trade_log_path}: {e}")
            return pd.DataFrame()

    def get_pnl_curve(self):
        df = self._load_trade_log()
        if df.empty:
            return pd.DataFrame({'timestamp': [], 'cumulative_pnl': []})
        
        # Sort by exit_time to ensure correct cumulative PnL
        df = df.sort_values(by='exit_time')
        df['cumulative_pnl'] = df['pnl'].cumsum()
        return df[['exit_time', 'cumulative_pnl']]

    def get_pnl_by_symbol(self):
        df = self._load_trade_log()
        if df.empty:
            return pd.DataFrame({'symbol': [], 'total_pnl': []})
        
        pnl_by_symbol = df.groupby('symbol')['pnl'].sum().reset_index()
        pnl_by_symbol.columns = ['symbol', 'total_pnl']
        return pnl_by_symbol

    def get_pnl_by_strategy(self):
        df = self._load_trade_log()
        if df.empty:
            return pd.DataFrame({'strategy_id': [], 'total_pnl': []})
        
        pnl_by_strategy = df.groupby('strategy_id')['pnl'].sum().reset_index()
        pnl_by_strategy.columns = ['strategy_id', 'total_pnl']
        return pnl_by_strategy

    def generate_pnl_curve(self, output_path="pnl_curve.png"):
        df = self.get_pnl_curve()
        if df.empty:
            logger.warning("No data to generate PnL curve.")
            return

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['exit_time'], y=df['cumulative_pnl'], mode='lines', name='Cumulative PnL'))
        fig.update_layout(title='Cumulative PnL Curve',
                          xaxis_title='Time',
                          yaxis_title='Cumulative PnL',
                          hovermode="x unified")
        fig.write_image(output_path)
        logger.info(f"PnL curve saved to {output_path}")

    def generate_analytics_report(self):
        summary = self.get_trade_summary()
        pnl_by_symbol = self.get_pnl_by_symbol()
        pnl_by_strategy = self.get_pnl_by_strategy()

        print("\n--- Trade Summary ---")
        for k, v in summary.items():
            if isinstance(v, float):
                print(f"{k.replace('_', ' ').title()}: {v:.2f}")
            else:
                print(f"{k.replace('_', ' ').title()}: {v}")

        print("\n--- PnL by Symbol ---")
        if not pnl_by_symbol.empty:
            print(pnl_by_symbol.to_string(index=False))
        else:
            print("No PnL data by symbol.")

        print("\n--- PnL by Strategy ---")
        if not pnl_by_strategy.empty:
            print(pnl_by_strategy.to_string(index=False))
        else:
            print("No PnL data by strategy.")

    def get_trade_summary(self):
        df = self._load_trade_log()
        if df.empty:
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'average_pnl_per_trade': 0.0
            }
        
        total_trades = len(df)
        total_pnl = df['pnl'].sum()
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] <= 0]) # Including zero PnL as non-winning
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
        average_pnl_per_trade = total_pnl / total_trades if total_trades > 0 else 0.0

        return {
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'average_pnl_per_trade': average_pnl_per_trade
        }

    def get_all_ai_audit_trails(self):
        df = self._load_trade_log()
        if df.empty or 'ai_audit_trail' not in df.columns:
            return {}

        audit_trails = {}
        for index, row in df.iterrows():
            trade_id = row['trade_id']
            try:
                audit_trail_json = row['ai_audit_trail']
                if pd.notna(audit_trail_json):
                    audit_trails[trade_id] = json.loads(audit_trail_json)
                else:
                    audit_trails[trade_id] = {}
            except (json.JSONDecodeError, TypeError):
                audit_trails[trade_id] = {"error": "Could not parse audit trail."}
        return audit_trails
