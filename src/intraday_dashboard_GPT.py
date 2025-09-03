#
# Module: intraday_dashboard_GPT.py
# Description: Streamlit dashboard for live trading visualization.
#
# DTS Intraday AI Trading System - Live Dashboard
# Version: 2025-08-29
#
# This module creates a real-time, interactive dashboard using Streamlit.
# It displays key metrics, open positions, PnL, and AI commentary by
# fetching data directly from the Redis store.
#

import streamlit as st
import pandas as pd
import json
import logging
import plotly.express as px
from typing import Dict, Any, List
from datetime import date

from src.redis_store import RedisStore
from src import holiday_manager
from src.analytics_manager import AnalyticsManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

st.set_page_config(layout="wide")

@st.cache_resource
def get_redis_store():
    """Initializes and returns a single RedisStore instance."""
    return RedisStore()

def display_dashboard():
    """
    Main function to run the Streamlit dashboard.
    """
    st.title("📊 DTS Intraday AI Trading System - Live Dashboard")
    redis_store = get_redis_store()
    analytics_manager = AnalyticsManager() # Instantiate AnalyticsManager
    
    if not redis_store.is_connected():
        st.error("🚨 Could not connect to Redis. Please check your Redis configuration.")
        return

    # Check for holiday mode
    if holiday_manager.is_trading_holiday(date.today()):
        st.warning("🚨 Today is a trading holiday! System operating in Holiday Mode. No trades will be executed.")

    # --- Live Status Panel ---
    st.header("📈 Live Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_capital = redis_store.get_capital()
        st.metric("💰 Current Capital", f"₹ {current_capital:,.2f}" if current_capital is not None else "N/A")
        
    with col2:
        open_positions = redis_store.get_open_positions()
        st.metric("📊 Open Positions", len(open_positions))
        
    with col3:
        # PnL logic - calculated from trade_log.csv using AnalyticsManager
        summary_data = analytics_manager.get_trade_summary()
        st.metric("💸 Realized PnL", f"₹ {summary_data['total_pnl']:, .2f}")

    with col4:
        model_version = redis_store.get("ai_model_version")
        st.metric("🤖 AI Model Version", f"v{float(model_version):.1f}" if model_version else "N/A")
    
    # --- Actionable Controls ---
    st.header("🔧 Controls")
    if st.button("Pause Trading System"):
        # Placeholder for Redis flag or command to pause the system
        st.info("System has been paused. Please unpause to resume.")

    # --- Open Positions Table ---
    st.header("📈 Open Positions")
    if open_positions:
        positions_list = []
        for symbol, trade in open_positions.items():
            ai_metrics_raw = redis_store.get(f"ai_metrics:{symbol}")
            tsl_movement_raw = redis_store.get(f"tsl_movement:{symbol}")
            
            ai_metrics = json.loads(ai_metrics_raw) if ai_metrics_raw else {}
            tsl_movement = json.loads(tsl_movement_raw) if tsl_movement_raw else {}

            trade['ai_score'] = ai_metrics.get('ai_score', 'N/A')
            trade['leverage'] = ai_metrics.get('leverage', 'N/A')
            trade['sentiment'] = ai_metrics.get('sentiment_score', 'N/A')
            trade['tsl'] = tsl_movement.get('new_tsl', trade.get('trailing_sl', 'N/A'))
            positions_list.append(trade)

        df_open_positions = pd.DataFrame(positions_list)
        st.dataframe(df_open_positions[['symbol', 'direction', 'entry_price', 'quantity', 'entry_time', 
                                        'leverage', 'ai_score', 'news_sentiment_score', 'ai_safety_activation', 'tsl']])
    else:
        st.info("No open positions currently.")

    # --- Closed Trades Log (from trade_log.csv) ---
    st.header("📜 Closed Trades Log")
    closed_trades_df = analytics_manager._load_trade_log()
    if not closed_trades_df.empty:
        st.dataframe(closed_trades_df[['symbol', 'direction', 'entry_price', 'exit_price', 'pnl', 'exit_reason', 'strategy_id']])

        st.subheader("AI Decision Audit Trail")
        trade_ids = closed_trades_df['trade_id'].tolist()
        selected_trade_id = st.selectbox("Select a Trade ID to view its AI Audit Trail", trade_ids)

        if selected_trade_id:
            all_audit_trails = analytics_manager.get_all_ai_audit_trails()
            audit_trail = all_audit_trails.get(selected_trade_id)
            if audit_trail:
                st.json(audit_trail)
            else:
                st.warning("No AI audit trail found for the selected trade.")

    else:
        st.info("No closed trades to display.")

    # --- PnL Curve (from trade_log.csv) ---
    st.header("💹 PnL Curve")
    pnl_curve_df = analytics_manager.get_pnl_curve()
    if not pnl_curve_df.empty:
        fig = px.line(pnl_curve_df, x='exit_time', y='cumulative_pnl', title='Cumulative PnL Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to display PnL curve.")

    # --- Per-Symbol Analytics (from trade_log.csv) ---
    st.header("📈 Per-Symbol PnL")
    pnl_by_symbol_df = analytics_manager.get_pnl_by_symbol()
    if not pnl_by_symbol_df.empty:
        fig_symbol = px.bar(pnl_by_symbol_df, x='symbol', y='total_pnl', title='Total PnL Per Symbol')
        st.plotly_chart(fig_symbol, use_container_width=True)
    else:
        st.info("No data to display per-symbol PnL.")

    # --- Per-Strategy Analytics (from trade_log.csv) ---
    st.header("📊 Per-Strategy PnL")
    pnl_by_strategy_df = analytics_manager.get_pnl_by_strategy()
    if not pnl_by_strategy_df.empty:
        fig_strategy = px.bar(pnl_by_strategy_df, x='strategy_id', y='total_pnl', title='Total PnL Per Strategy')
        st.plotly_chart(fig_strategy, use_container_width=True)
    else:
        st.info("No data to display per-strategy PnL.")

    # --- AI Event Log ---
    st.header("🤖 AI Event Log")
    # This is a simplified event log. A more robust implementation would use a dedicated Redis list or stream.
    event_logs = []
    last_retrained_timestamp = redis_store.get("ai_model_version") # Assuming model_version is updated on retraining
    if last_retrained_timestamp:
        event_logs.append(f"AI model last retrained (version): {last_retrained_timestamp}")

    for symbol, trade in open_positions.items():
        tsl_movement_raw = redis_store.get(f"tsl_movement:{symbol}")
        if tsl_movement_raw:
            tsl_movement = json.loads(tsl_movement_raw)
            if tsl_movement.get("new_tsl") != tsl_movement.get("old_tsl"):
                event_logs.append(f"TSL for {symbol} moved from {tsl_movement['old_tsl']:.2f} to {tsl_movement['new_tsl']:.2f}")
        
        ai_metrics_raw = redis_store.get(f"ai_metrics:{symbol}")
        if ai_metrics_raw:
            ai_metrics = json.loads(ai_metrics_raw)
            if ai_metrics.get('trend_flip_confirmation'):
                event_logs.append(f"Trend-flip confirmed for {symbol}")

        # Log AI Safety Activation
        if trade.get('ai_safety_activation') and trade['ai_safety_activation'] != 'none':
            event_logs.append(f"AI Safety Activated for {symbol}: {trade['ai_safety_activation']}")

    if event_logs:
        for log_entry in event_logs:
            st.text(log_entry)
    else:
        st.info("No new AI events.")

    # --- AI Insights Panel ---
    st.header("🤖 AI Insights & Commentary")
    ai_commentary = redis_store.get_ai_comment('daily')
    if ai_commentary:
        st.info(ai_commentary)
    else:
        st.warning("No daily AI commentary available yet.")

    # --- Leaderboard/Watchlist ---
    st.header("🏅 Waitlisted Leaderboard")
    top_signals = redis_store.get_top_signals()
    if top_signals:
        df_top_signals = pd.DataFrame(top_signals.items(), columns=['Symbol', 'AI Score'])
        st.dataframe(df_top_signals)
    else:
        st.info("No AI signals available. Waiting for scoring engine.")
        
# Run the dashboard
if __name__ == "__main__":
    display_dashboard()