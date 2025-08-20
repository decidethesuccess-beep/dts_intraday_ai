DTS Intraday AI Strategy Specification

Version: 2025-08-16
Owner: DTS (Strategy Owner)
Status: Active Development

Strategy Overview

The DTS Intraday AI Trading System is a no-indicator, AI/NLP-driven, high-momentum stock trading strategy for NSE India.

It supports both BUY and SELL trades with strict risk management, capital rotation, and AI-based adaptive decision-making.

Noise reduction, minimal false entries, and AI-driven scoring ensure signal purity.

Core Philosophy

No traditional indicators (RSI, MACD, etc.)

AI/NLP-based scoring for entry decisions

Momentum and volume spike detection

Circuit targeting (early strong moves aiming for upper/lower circuits)

Risk-first execution with AI-TSL and AI leverage control

Market awareness for special conditions (holidays, partial sessions, volatile/range-bound days)

Noise-free trading with smart filters

Default Settings (as of 2025-08-16)

Setting

Default Value

Capital Allocation

10% per trade (max 10 concurrent trades)

Trade Direction

BUY + SELL enabled

Target Profit (TGT)

+10%

Stop Loss (SL)

-2%

Trailing Stop Loss (TSL)

1% for BUY, 1% for SELL (from entry price)

TSL Mode

AI (classic / ai / min / max)

Trend Flip Exit

Always ON

Auto Exit Time

3:20 PM IST

AI-Driven Position Sizing

Position sizing is a crucial part of risk management and is determined by the AI signal score. This strategy uses a tiered leverage model instead of a linear one to avoid over-allocation on low-confidence signals and to maximize capital on high-confidence trades.

Signal Score Range

Leverage Multiplier

≥0.80

5.0x

0.50−0.79

3.5x

<0.50

1.0x

Rationale: This ensures that significant capital is only deployed when the AI system has very high conviction, based on a combination of momentum, volume, and news sentiment.

Risk Management

Capital Allocation: Fixed percentage of total capital per trade.

Max Positions: Limits concurrent open trades to a configurable number.

Dynamic AI Leverage: AI module dynamically adjusts leverage based on signal score.

Trend-Flip Exit: Automatically exits a position if the AI detects a strong trend reversal.

AI-TSL: AI module continuously adjusts the trailing stop loss for each open position.

Hard SL/TGT: Mandatory stop loss and target profit levels.

Guaranteed Auto-Exit: All open positions are auto-closed at a fixed time before market close to prevent overnight risk.

Core Modules

strategy.py: Main trading logic.

data_fetcher.py: Retrieves market data from Angel One API.

ai_module.py: Core AI scoring engine, AI-TSL, and AI leverage.

order_manager.py: Manages trade placement and position tracking.

news_filter.py: Filters trades based on news sentiment.

redis_store.py: Real-time state management.

live_stream.py: Manages live market data ingestion.

backtest_runner.py: Historical simulation engine.

Exit Conditions

Trend-Flip Exit: Always ON, highest priority.

AI-TSL: Dynamic exit, active for open positions in profit.

Hard SL/TGT: -2% SL, +10% TGT (configurable via .env).

Auto-Exit: 3:20 PM IST.

Min Profit Mode: Early TSL exits to lock partial profits.

AI/ML Integration

AI Scoring: AI model rates trade signals (0.0 to 1.0) using momentum, volume spikes, and news sentiment.

AI Leverage: AI-driven position sizing to adjust leverage based on signal confidence.

AI-TSL: Dynamically adjusts TSL to optimize exit points.

Trend-Flip: AI detects trend reversals and triggers immediate exit.

Continuous Learning: Rolling-window optimization prevents overfitting.

Noise Filtering: Prevents false entries.

Min Profit Mode: Early TSL exits to lock partial profits.

Dashboard & Settings

Dedicated Settings Page: Leverage, AI Leverage, TSL Mode, AI Optimization, News Sentiment Filter, Noise Reduction, Min Profit Mode

Performance Reports: Daily, Weekly, Monthly, Yearly via Gemini AI Studio

Live Status Panel: Capital used, open trades, closed PnL, waitlisted leaderboard, pause/resume

Data Sources

Market Data: Angel One Market Feed API (1-min LTP & OHLCV)

News Sentiment: AI/NLP from news headlines

Holiday Data: NSE calendar + Angel One API backup

NSE EQ Symbols: Loaded from Angel One static JSON (link), filtered, stored in memory/CSV for live/backtest modules

Notes

Fully automated, allows manual overrides

Noise-free execution

Backtest simulates identical live rules

Capital rotation ensures optimal use

Compatible with .env.example placeholders

AI Webhook Integration

Purpose: Provides AI-driven guidance, suggestions, and trade commentary

Source: Gemini AI Studio API (GEMINI_API_KEY)

Functionality: Daily/weekly/monthly/yearly trade commentary, actionable suggestions, risk alerts, improvement guidance

Dashboard Integration: Comments stored in Redis keys, displayed on intraday_dashboard_GPT.py front panel

Safety: Timeout/exception handling; advisory only, does not execute trades automatically.