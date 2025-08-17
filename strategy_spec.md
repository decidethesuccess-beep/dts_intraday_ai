DTS Intraday AI Strategy Specification

Version: 2025-08-15
Owner: DTS (Strategy Owner)
Status: Active Development

1. Strategy Overview

The DTS Intraday AI Trading System is a no-indicator, AI/NLP-driven, high-momentum stock trading strategy for NSE India.

It supports both BUY and SELL trades with strict risk management, capital rotation, and AI-based adaptive decision-making.

Noise reduction, minimal false entries, and AI-driven scoring ensure signal purity.

2. Core Philosophy

No traditional indicators (RSI, MACD, etc.)

AI/NLP-based scoring for entry decisions

Momentum and volume spike detection

Circuit targeting (early strong moves aiming for upper/lower circuits)

Risk-first execution with AI-TSL and AI leverage control

Market awareness for special conditions (holidays, partial sessions, volatile/range-bound days)

Noise-free trading with smart filters

3. Default Settings (as of 2025-08-15)
Setting	Default Value
Capital Allocation	10% per trade (max 10 concurrent trades)
Trade Direction	BUY + SELL enabled
Target Profit (TGT)	+10%
Stop Loss (SL)	-2%
Trailing Stop Loss (TSL)	1% for BUY, 1% for SELL (from entry price)
TSL Mode	AI (classic / ai / min / max)
Trend Flip Exit	Always ON
Auto Exit Time	3:20 PM
Leverage	OFF (default)
AI Leverage	ON (default)
AI Optimization Module	ON — adapts scoring thresholds, trade duration, leverage tiers
Broker	Angel One
Market Holiday Detection	ON (NSE calendar primary, broker API secondary)
News Sentiment Filter	ON — Skip BUY if score < -0.5; Skip SELL if score > +0.5
Noise Reduction Filter	ON
Min Profit Mode	Enabled — tightens AI-TSL in low-volatility markets
4. AI/NLP Components

AI Scoring Engine: Rates signals using momentum, volume, news sentiment

AI Trend Detection: Monitors real-time price flow for trend continuation/reversal

AI-TSL: Adjusts trailing SL dynamically based on volatility, news impact, and trade duration; BUY/SELL separately

AI Leverage Manager: Determines leverage using capital tier and trade quality score

AI Optimization Module: Learns from past trades, adapts scoring thresholds, trade duration, leverage tiers; does not modify hard SL/TGT

Integration: Gemini AI Studio for performance analysis and AI functions

5. Capital & Leverage Rules

Capital Rotation: Freed capital immediately available for new trades

Leverage Control: Manual (default OFF) or AI mode (default ON); AI maps trade quality scores to leverage:

High (>0.8) → full allowed leverage

Medium (0.5–0.8) → 50–75% leverage

Low (<0.5) → 0% leverage

6. Special Market Awareness

Market Holiday Detection: NSE calendar primary, Angel One API backup

Partial Trading Day Adjustment: Tightens exits, avoids late entries

Low Volatility Mode: Capital preservation rules

Short Session Logic: AI adapts SL/TSL for shorter hours

7. Exit Conditions

Target hit (+10% BUY / -10% SELL)

Stop Loss hit (-2% BUY / +2% SELL)

AI-TSL triggered

Trend flip detected

Auto-exit at 3:20 PM

Min Profit Mode triggers early TSL exit

8. AI Safety Layer

Market Regime Awareness – preserves capital on range-bound days

Profit-Lock Behavior – tightens TSL in sideways markets

Holiday & Short Session Logic – adapts SL/TSL for special days

Leverage & Risk Balance – enforces daily leverage caps

Continuous Learning – rolling-window avoids overfitting

Noise Filtering – prevents false entries

Min Profit Mode – early TSL exits to lock partial profits

9. Dashboard & Settings

Dedicated Settings Page: Leverage, AI Leverage, TSL Mode, AI Optimization, News Sentiment Filter, Noise Reduction, Min Profit Mode

Performance Reports: Daily, Weekly, Monthly, Yearly via Gemini AI Studio

Live Status Panel: Capital used, open trades, closed PnL, waitlisted leaderboard, pause/resume

10. Data Sources

Market Data: Angel One Market Feed API (1-min LTP & OHLCV)

News Sentiment: AI/NLP from news headlines

Holiday Data: NSE calendar + Angel One API backup

NSE EQ Symbols: Loaded from Angel One static JSON (link), filtered, stored in memory/CSV for live/backtest modules

11. Notes

Fully automated, allows manual overrides

Noise-free execution

Backtest simulates identical live rules

Capital rotation ensures optimal use

Compatible with .env.example placeholders

12. AI Webhook Integration

Purpose: Provides AI-driven guidance, suggestions, and trade commentary

Source: Gemini AI Studio API (GEMINI_API_KEY)

Functionality: Daily/weekly/monthly/yearly trade commentary, actionable suggestions, risk alerts, improvement guidance

Dashboard Integration: Comments stored in Redis keys, displayed on intraday_dashboard_GPT.py front panel

Safety: Timeout/exception handling; advisory only, does not trigger trades