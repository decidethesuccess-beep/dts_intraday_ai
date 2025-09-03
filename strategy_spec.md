DTS Intraday AI Strategy Specification
======================================

Version: 2025-08-31  
Owner: DTS (Strategy Owner)  
Status: Active Development (Phases 1–5 complete, 84/84 tests passing)

1. Strategy Overview
---------------------

The DTS Intraday AI Trading System is an automated intraday trading framework for NSE equities.  
It combines high-frequency data analysis, AI-driven decision-making, and robust risk management.

Core features include:

- Symbol filtering (NSE_EQ only).
- Entry & exit rules with SL, TGT, TSL, and trend reversal.
- AI-based scoring with volume, momentum, sentiment, and circuit targeting.
- AI-driven trailing stop-loss (AI-TSL).
- AI safety layer for regime awareness, leverage control, and holiday detection.
- Rolling-window retraining for continuous adaptability.
- Integrated NSE holiday calendar with API + JSON fallback (via `holiday_manager.py`).
- Performance analytics with trade logs, PnL curves, per-strategy and per-symbol reporting, and AI audit trail.

2. Symbol Universe
------------------

- Loads NSE EQ symbols from Angel One static JSON.
- Filters out illiquid / non-EQ instruments.
- Universe size dynamically restricted to ~100 high-volume gainers per day.

3. Entry & Exit Rules
---------------------

**Entry Window:** 09:20 – 15:20 IST  
**Exit Window:** Forced exit at 15:20 IST  

**Risk Management:**
- Stop Loss (SL): –2%  
- Target (TGT): +10%  
- Trailing SL (TSL): 1% minimum, volatility-aware via AI-TSL  
- Trend Reversal Exit: Always enabled (both long & short)  

**Capital Allocation:**
- 10% of total capital per trade  
- Max 10 concurrent trades  
- Capital recycling when trades exit  

4. AI Integration
-----------------
### 4.1 AI Scoring
- Combines volume spikes, momentum, sentiment (via Finnhub), and circuit potential.  
- Produces AI Confidence Score (0–1).  
- Higher score → higher priority for entry.  

### 4.2 AI-TSL
- Volatility-aware trailing SL.  
- Adjusts dynamically based on intraday ATR/volatility.  
- Tightens faster in sideways markets.  

### 4.3 AI Safety Layer
- Market regime awareness (detects low-volatility days).  
- Profit-lock behavior (secure partial gains).  
- Min-profit exits to avoid reversals.  
- Holiday & short-session guardrails (via live NSE API + JSON fallback).  
- Leverage caps enforced.  

### 4.4 Rolling-Window Retraining
- Retrains periodically on rolling windows of market data.  
- Triggers: time-based or size-based.  
- Prevents overfitting while adapting.  

### 4.5 Live NSE Calendar Integration
- Uses NSE official API (`/api/holiday-master?type=trading`).  
- Centralized in `holiday_manager.py` (not `utils.py`).  
- Fallback to local `/data/holidays.json` when API unavailable.  
- Dashboard highlights Holiday Mode when active.  
- Integrated with AI Safety Layer to block/adjust trades.  

5. Milestones / Phases
----------------------

✅ **Phase 1 – Data & Backtest Foundation**  
- Symbol filtering (NSE_EQ only)  
- Historical 1-min OHLCV fetch  
- Backtest engine with Streamlit dashboard  
- ✅ Completed  

✅ **Phase 2 – Entry & Exit Logic**  
- Entry freeze at 09:20 IST  
- SL/TGT/TSL setup  
- Trend reversal exits  
- Auto-exit at 15:20 IST  
- ✅ Completed  

✅ **Phase 3 – AI Integration**  
- News Sentiment Filter (Finnhub)  
- AI Scoring (volume + momentum + sentiment)  
- AI-TSL (volatility-aware trailing stop-loss)  
- ✅ Completed  

✅ **Phase 4 – Advanced AI Modules**  
- AI Safety Layer (holiday guard, crash guard, leverage cap)  
- Profit-Lock Mode  
- Minimum Profit Mode  
- Circuit Targeting  
- Rolling-Window Retraining  
- Live NSE Calendar Integration via `holiday_manager.py`  
- ✅ Completed (79/79 tests passing)  

✅ **Phase 5 – Performance Analytics & Reports**  
- Trade logs + PnL curves  
- Per-strategy & per-symbol analytics  
- AI decision audit trail  
- Integrated into dashboards (`backtest_dashboard.py`, `intraday_dashboard_GPT.py`)  
- ✅ Completed (84/84 tests passing)  

⏳ **Phase 6 – Live Deployment (Paper Trading)**  
- Real-time Redis streaming  
- Paper execution via Angel One API  
- Dashboard monitoring of live positions  

⏳ **Phase 7 – Live Deployment (Production)**  
- Cloud deployment (Render/Oracle/GCP/AWS)  
- Automated trading with safeguards  
- Failover handling  

⏳ **Phase 8 – Continuous Learning & Optimization**  
- Ongoing retraining using rolling windows  
- Adaptive thresholds  
- Refinements via live feedback  

6. Current Status
-----------------
✅ Phases 1–5 fully implemented (including analytics + holiday calendar).  
✅ 84/84 tests passing (as of 2025-08-31).  
⏳ Next milestone: **Phase 6 (Live Paper Trading)**.  
