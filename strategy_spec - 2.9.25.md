DTS Intraday AI Strategy Specification

======================================

Version: 2025-08-31
Owner: DTS (Strategy Owner)
Status: Active Development (Phases 1–4 complete, 79/79 tests passing)

1. Strategy Overview

The DTS Intraday AI Trading System is an automated intraday trading framework for NSE equities.
It combines high-frequency data analysis, AI-driven decision-making, and robust risk management.

Core features include:

Symbol filtering (NSE_EQ only).

Entry & exit rules with SL, TGT, TSL, and trend reversal.

AI-based scoring with volume, momentum, sentiment, and circuit targeting.

AI-driven trailing stop-loss (AI-TSL).

AI safety layer for regime awareness, leverage control, and holiday detection.

Rolling-window retraining for continuous adaptability.

Integrated NSE holiday calendar with API + JSON fallback (via holiday_manager.py).

2. Symbol Universe

Loads NSE EQ symbols from Angel One static JSON.

Filters out illiquid / non-EQ instruments.

Universe size dynamically restricted to ~100 high-volume gainers per day.

3. Entry & Exit Rules

Entry Window: Only between 09:20 – 15:20 IST.

Exit Window: Forced exit at 15:20 IST.

Risk Management:

Stop Loss (SL): –2%

Target (TGT): +10%

Trailing SL (TSL): 1% minimum, volatility-aware via AI-TSL.

Trend Reversal Exit: Always enabled (both long & short).

Capital Allocation:

10% of total capital per trade.

Max 10 concurrent trades.

Capital recycling when trades exit.

4. AI Integration
4.1 AI Scoring

Combines volume spikes, momentum, sentiment (via Finnhub), and circuit potential.

Produces AI Confidence Score (0–1).

Higher score → higher priority for entry.

4.2 AI-TSL

Volatility-aware trailing SL.

Adjusts dynamically based on intraday ATR/volatility.

Tightens faster in sideways markets.

4.3 AI Safety Layer

Market regime awareness (detects low-volatility days).

Profit-lock behavior (secure partial gains).

Min-profit exits to avoid reversals.

Holiday & short-session guardrails (via live NSE API + JSON fallback).

Leverage caps enforced.

4.4 Rolling-Window Retraining

AI retrains periodically based on rolling window of market data.

Triggers: time-based or size-based.

Prevents overfitting while adapting to market conditions.

4.5 Live NSE Calendar Integration

Uses NSE official API (https://www.nseindia.com/api/holiday-master?type=trading) for trading holidays.

Logic centralized in holiday_manager.py (separate from utils.py).

Fallback to local /data/holidays.json when API fails or offline.

Dashboard highlights Holiday Mode when active.

Integrated with AI Safety Layer to block/adjust trades.

5. Milestones / Phases
✅ Phase 1 – Data & Backtest Foundation

Symbol universe filtering (NSE_EQ only).

Historical 1-min OHLCV fetch.

Backtest engine setup with Streamlit dashboard.

✅ Completed.

✅ Phase 2 – Entry & Exit Logic

Entry window freeze at 09:20 IST.

SL/TGT/TSL basic setup.

Trend reversal exits enabled.

Auto-exit at 15:20 IST.

✅ Completed.

✅ Phase 3 – AI Integration

3.1 News Sentiment Filter → Finnhub integration.

3.2 AI Scoring Logic → Volume + momentum + sentiment.

3.3 AI-TSL → Volatility-aware trailing stop-loss.

✅ Completed.

✅ Phase 4 – Advanced AI Modules

4.1 AI Safety Layer → Holiday guard, crash guard, leverage cap.

4.2 Profit-Lock Mode → Exit tightening after intraday profit thresholds.

4.3 Minimum Profit Mode → Auto-exit to secure small gains.

4.4 Circuit Targeting → AI lowers entry thresholds for circuit-move potential.

4.5 Rolling-Window AI Retraining → Adaptive learning with time/size triggers.

4.6 Live NSE Calendar Integration → Official API + JSON fallback via holiday_manager.py, dashboard “Holiday Mode.”

✅ Completed (79/79 tests passing).

⏳ Phase 5 – Performance Analytics & Reports

Trade logs, PnL curves.

Per-strategy & per-symbol analytics.

AI decision audit trail.

⏳ Phase 6 – Live Deployment (Paper Trading)

Real-time Redis streaming.

Paper-trade execution via Angel One API.

Dashboard for monitoring live positions.

⏳ Phase 7 – Live Deployment (Production)

Cloud deployment (Render/Oracle/GCP/AWS).

Automated trading with safeguards.

Failover handling.

⏳ Phase 8 – Continuous Learning & Optimization

Ongoing retraining using rolling windows.

Adaptive thresholds.

Strategy refinements via live feedback.

6. Current Status

✅ Phases 1–4 fully implemented (including NSE holiday calendar via holiday_manager.py).

✅ 79/79 tests passing (as of 2025-08-31).

⏳ Next milestone: Phase 5 (Performance Analytics & Reports).