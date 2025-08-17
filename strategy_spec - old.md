DTS Intraday AI Strategy Specification

Version: 2025-08-15

Owner: DTS (Strategy Owner)

Status: Active Development

1. Strategy Overview

The DTS Intraday AI Trading System is a no-indicator, AI/NLP-driven, high-momentum stock trading strategy for NSE India.

It is designed to work for both BUY and SELL trades with strict risk management, capital rotation, and AI-based adaptive decision-making.

Noise reduction, minimal false entries, and AI-driven scoring ensure signal purity.

2. Core Philosophy

No traditional indicators (RSI, MACD, etc.)

AI/NLP based scoring for entry decisions

Momentum and volume spike detection

Circuit targeting (stocks with early strong moves, aiming for upper/lower circuits)

Risk-first execution with AI-TSL and AI leverage control

Market awareness for special conditions (holidays, partial sessions, volatile/range-bound days)

Noise-free trading with smart filters

3. Default Settings (as of 2025-08-15)
Setting	Default Value
Capital Allocation	10% of total capital per trade (max 10 concurrent trades)
Trade Direction	BUY + SELL enabled
Target Profit (TGT)	+10%
Stop Loss (SL)	-2%
Trailing Stop Loss (TSL)	1% for BUY, 1% for SELL (trailing from entry price)
TSL Mode	AI (options: classic / ai / min / max)
Trend Flip Exit	Always ON
Auto Exit Time	3:20 PM
Leverage	OFF (default)
AI Leverage	ON (default)
AI Optimization Module	ON (default) — Learns from past trades & adapts rules (scoring thresholds, trade duration, leverage tiers)
Broker	Angel One
Market Holiday Detection	ON (primary: NSE calendar, secondary: broker API)
News Sentiment Filter	ON — Skip BUY on negative news (score < -0.5); Skip SELL on strongly positive news (score > +0.5)
Noise Reduction Filter	ON
Min Profit Mode	Enabled — Activates in sideways or low-volatility markets; tightens AI-TSL to lock partial profits
4. AI/NLP Components

AI Scoring Engine: Rates trade signals using momentum, volume patterns, and news sentiment.

AI Trend Detection: Monitors real-time price flow to identify trend continuation or reversal.

AI-TSL: Adjusts the trailing stop loss dynamically from entry price based on:

Volatility (recent 5-min range)

News impact (positive/negative)

Trade duration (tightens after X minutes)

BUY and SELL trades managed separately

AI Leverage Manager: Determines leverage based on capital tier and trade quality score.

AI Optimization Module: Learns from past trades and adapts:

AI scoring thresholds

Trade duration limits

Leverage tiers
Does not modify hard SL/TGT values.

Integration: Gemini AI Studio is used for performance analysis and AI functions (API keys are placeholders in .env.example).

5. Capital & Leverage Rules

Capital Rotation: Freed capital is immediately available for new trades.

Leverage Control:

Manual mode via Leverage switch (default OFF)

AI mode via AI Leverage switch (default ON)

AI decides leverage based on capital tier and trade quality score:

High Score (>0.8) → full allowed leverage (DEFAULT_LEVERAGE_MULTIPLIER in .env.example)

Medium Score (0.5–0.8) → 50–75% of allowed leverage

Low Score (<0.5) → 0% leverage, capital-only trades

6. Special Market Awareness

Market Holiday Detection: NSE official calendar primary, Angel One API backup.

Partial Trading Day Adjustment: Tightens exits & avoids late entries.

Low Volatility Mode: Activates capital preservation rules.

Short Session Logic: AI adapts SL/TSL for shorter hours.

7. Exit Conditions

Target hit (+10% for BUY / -10% for SELL)

Stop Loss hit (-2% for BUY / +2% for SELL)

AI-TSL triggered (dynamic adjustment as defined in §4)

Trend flip detected (always on)

Auto-exit at 3:20 PM

Min Profit Mode triggers early TSL exit in sideways/low-volatility markets

8. AI Safety Layer

Market Regime Awareness – AI detects range-bound or low-volatility days and switches to capital preservation mode.

Profit-Lock Behavior – AI tightens TSL earlier in sideways markets to secure small wins.

Holiday & Short Session Logic – AI detects special trading days and adapts SL/TSL accordingly.

Leverage & Risk Balance – AI enforces daily leverage caps to prevent overexposure.

Continuous Learning vs. Overfitting – Rolling-window AI training avoids bias from recent unusual days.

Noise Filtering – Strict filters to prevent false entries in choppy markets.

Min Profit Mode – Activates early TSL exits to lock partial profits without overriding hard SL.

9. Dashboard & Settings

Dedicated Settings Page:

Leverage (default OFF)

AI Leverage (default ON)

TSL Mode dropdown (classic / ai / min / max, default ai)

AI Optimization Module switch (default ON)

News Sentiment Filter switch (default ON)

Noise Reduction switch (default ON)

Min Profit Mode switch (default ON)

Performance Reports: Daily, Weekly, Monthly, Yearly AI-generated analysis via Gemini AI Studio API.

Live Status Panel: Capital used, open trades, closed PnL, waitlisted leaderboard, pause/resume.

10. Data Sources

Market Data: Angel One Market Feed API (1-min LTP & OHLCV)

News Sentiment: AI/NLP processing of news headlines

Holiday Data: NSE official calendar + Angel One API backup

11. Notes

Strategy is fully automated but allows manual overrides.

Designed for noise-free execution.

Backtest engine simulates identical rules to live trading.

Capital diversification and rotation ensures optimal resource use.

This version fully resolves the previous gaps noted by Gemini: AI-TSL logic, AI Optimization Module, Min Profit Mode behavior, News Sentiment Filter thresholds, and Leverage application mapping, while remaining compatible with .env.example.

12. AI Webhook Integration

- **Purpose**: Provides AI-driven guidance, suggestions, and commentary for trades and system performance.
- **Source**: Gemini AI Studio API (configured via `GEMINI_API_KEY` in `.env`).
- **Functionality**:
    - Periodically (daily, weekly, monthly, yearly) generates commentary on trades.
    - Provides actionable suggestions, risk alerts, and improvement guidance.
    - AI comments include performance evaluation, trend insights, and capital allocation recommendations.
- **Dashboard Integration**:
    - Comments stored in Redis keys (`ai_comment:daily`, `ai_comment:weekly`, etc.)
    - `intraday_dashboard_GPT.py` reads these keys and displays the commentary on the front page panel.
    - Users can manually refresh or filter by timeframe.
- **Configuration**:
    - `GEMINI_API_KEY` required in `.env`.
    - Redis used for communication between AI webhook and dashboard.
- **Safety & Reliability**:
    - Timeout and exception handling included to prevent webhook failures from affecting live trading.
    - Comments do not automatically trigger trades; purely advisory.
