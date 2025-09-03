#
# Module: backtest_dashboard.py
# Description: Streamlit dashboard for backtest visualization.
#
# DTS Intraday AI Trading System - Backtest Dashboard
# Version: 2025-08-29
#
# This module provides a user interface to visualize the results of a backtest
# run, displaying performance metrics, trade logs, and PnL curves.
#

import streamlit as st
import pandas as pd
import json
import logging
import plotly.express as px

from typing import Dict, Any, List

from src.analytics_manager import AnalyticsManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# This is a placeholder for where your backtest results would be stored.
# In a real-world scenario, you might read from a file or a dedicated Redis key.
def load_backtest_results() -> Dict[str, Any]:
    """
    Simulates loading backtest results from a file.
    """
    try:
        # Placeholder for a JSON file containing backtest output
        with open("data/backtest_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        log.warning("Backtest results file not found. Using dummy data.")
        return {
            'summary': {
                'initial_capital': 1000000.0,
                'final_capital': 1005000.0,
                'total_pnl': 5000.0,
                'total_trades': 50,
                'winning_trades': 30,
                'win_rate_pct': 60.0
            },
            'closed_trades': [], # List of closed trades
            'retraining_events': [] # List of retraining events
        }
        
st.set_page_config(layout="wide")
st.title("📈 DTS Intraday AI Trading System - Backtest Dashboard")

# Instantiate AnalyticsManager
analytics_manager = AnalyticsManager()

# Load data using AnalyticsManager
closed_trades_df = analytics_manager._load_trade_log()
summary_data = analytics_manager.get_trade_summary()

# --- Summary Panel ---
st.header("📊 Performance Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Trades", summary_data['total_trades'])
col2.metric("💰 Total PnL", f"₹ {summary_data['total_pnl']:, .2f}")
col3.metric("📈 Winning Trades", summary_data['winning_trades'])
col4.metric("📉 Losing Trades", summary_data['losing_trades'])

st.metric("📊 Win Rate", f"{summary_data['win_rate']:.2f}%")
st.metric("💲 Avg. PnL per Trade", f"₹ {summary_data['average_pnl_per_trade']:, .2f}")

# --- AI Metrics Filter ---
st.header("🤖 AI Metrics Filter")
sentiment_filter = st.checkbox("Show only sentiment-influenced trades")

# --- Trade Log ---
st.header("📜 Closed Trades Log")
if not closed_trades_df.empty:
    df_trades = closed_trades_df.copy()
    
    if sentiment_filter:
        df_trades = df_trades[df_trades['news_sentiment_score'] != 0.0]

    st.dataframe(df_trades[['symbol', 'direction', 'entry_price', 'exit_price', 'quantity', 'pnl', 
                            'trade_duration', 'ai_confidence_score', 'news_sentiment_score', 
                            'ai_safety_activation', 'max_profit', 'max_drawdown']])
else:
    st.info("No closed trades to display. Run a backtest first.")

# --- PnL Curve ---
st.header("💹 PnL Curve")
pnl_curve_df = analytics_manager.get_pnl_curve()
if not pnl_curve_df.empty:
    fig = px.line(pnl_curve_df, x='exit_time', y='cumulative_pnl', title='Cumulative PnL Over Time')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data to display PnL curve.")

# --- Per-Symbol Analytics ---
st.header("📈 Per-Symbol PnL")
pnl_by_symbol_df = analytics_manager.get_pnl_by_symbol()
if not pnl_by_symbol_df.empty:
    fig_symbol = px.bar(pnl_by_symbol_df, x='symbol', y='total_pnl', title='Total PnL Per Symbol')
    st.plotly_chart(fig_symbol, use_container_width=True)
else:
    st.info("No data to display per-symbol PnL.")

# --- Per-Strategy Analytics ---
st.header("📊 Per-Strategy PnL")
pnl_by_strategy_df = analytics_manager.get_pnl_by_strategy()
if not pnl_by_strategy_df.empty:
    fig_strategy = px.bar(pnl_by_strategy_df, x='strategy_id', y='total_pnl', title='Total PnL Per Strategy')
    st.plotly_chart(fig_strategy, use_container_width=True)
else:
    st.info("No data to display per-strategy PnL.")

# --- Retraining Events (Still using dummy data for now) ---
st.header("🧠 AI Retraining Events")
# This part still relies on the dummy data from load_backtest_results for now
# as retraining events are not yet logged to trade_log.csv
results = load_backtest_results() # Reload dummy data for retraining events
retraining_events = results.get('retraining_events', [])

if retraining_events:
    df_retraining = pd.DataFrame(retraining_events)
    st.dataframe(df_retraining)
else:
    st.info("No AI retraining events recorded during this backtest.")