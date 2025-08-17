#
# Module: intraday_dashboard_GPT.py
# Description: Streamlit dashboard for live trading visualization.
#
# DTS Intraday AI Trading System - Live Dashboard
# Version: 2025-08-15
#
# This module creates a real-time, interactive dashboard using Streamlit.
# It displays key metrics, open positions, PnL, and AI commentary by
# fetching data directly from the Redis store.
#

import streamlit as st
import pandas as pd
import json
import logging
from typing import Dict, Any, List

from src.redis_store import RedisStore

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

st.set_page_config(layout="wide")

@st.cache_resource
def get_redis_store():
    """Initializes and returns a single RedisStore instance."""
    return RedisStore()

def display_dashboard():
    """Main function to run the Streamlit dashboard."""
    st.title("📊 DTS Intraday AI Trading System - Live Dashboard")
    redis_store = get_redis_store()
    
    if not redis_store.is_connected():
        st.error("🚨 Could not connect to Redis. Please check your Redis configuration.")
        return

    # --- Live Status Panel ---
    st.header("📈 Live Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_capital = redis_store.get_capital()
        st.metric("💰 Current Capital", f"₹ {current_capital:,.2f}" if current_capital is not None else "N/A")
        
    with col2:
        open_positions = redis_store.get_open_positions()
        st.metric("📊 Open Positions", len(open_positions))
        
    with col3:
        # PnL logic - this would be calculated from closed trades
        closed_trades = redis_store.get_all_closed_trades()
        total_pnl = sum(trade['pnl'] for trade in closed_trades)
        st.metric("💸 Realized PnL", f"₹ {total_pnl:,.2f}")
    
    # --- Actionable Controls ---
    st.header("🔧 Controls")
    if st.button("Pause Trading System"):
        # Placeholder for Redis flag or command to pause the system
        st.info("System has been paused. Please unpause to resume.")

    # --- Open Positions Table ---
    st.header("📈 Open Positions")
    if open_positions:
        df_open_positions = pd.DataFrame(list(open_positions.values()))
        st.dataframe(df_open_positions)
    else:
        st.info("No open positions currently.")

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
