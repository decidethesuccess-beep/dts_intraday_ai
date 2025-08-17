\# DTS Intraday AI Strategy Specification  

\*\*Version:\*\* 2025-08-13  

\*\*Owner:\*\* DTS (Strategy Owner)  

\*\*Status:\*\* Active Development  



---



\## 1. Strategy Overview

The DTS Intraday AI Trading System is a \*\*no-indicator, AI/NLP-driven\*\*, high-momentum stock trading strategy for \*\*NSE India\*\*.  

It is designed to work for both \*\*BUY and SELL\*\* trades with strict risk management, capital rotation, and AI-based adaptive decision-making.  

Noise reduction, minimal false entries, and AI-driven scoring ensure \*\*signal purity\*\*.



---



\## 2. Core Philosophy

\- \*\*No traditional indicators\*\* (RSI, MACD, etc.)  

\- \*\*AI/NLP based\*\* scoring for entry decisions  

\- \*\*Momentum and volume spike detection\*\*  

\- \*\*Circuit targeting\*\* (stocks with early strong moves, aiming for upper/lower circuits)  

\- \*\*Risk-first execution\*\* with AI-TSL and AI leverage control  

\- \*\*Market awareness\*\* for special conditions (holidays, partial sessions, volatile/range-bound days)  

\- \*\*Noise-free trading\*\* with smart filters



---



\## 3. Default Settings (as of 2025-08-13)

| Setting | Default Value |

|---------|--------------|

| \*\*Capital Allocation\*\* | 10% of total capital per trade (max 10 concurrent trades) |

| \*\*Trade Direction\*\* | BUY + SELL enabled |

| \*\*Target Profit (TGT)\*\* | +10% |

| \*\*Stop Loss (SL)\*\* | -2% |

| \*\*Trailing Stop Loss (TSL)\*\* | 1% for BUY, -1% for SELL |

| \*\*TSL Mode\*\* | AI (options: classic / ai / min / max) |

| \*\*Trend Flip Exit\*\* | Always ON |

| \*\*Auto Exit Time\*\* | 3:20 PM |

| \*\*Leverage\*\* | OFF (default) |

| \*\*AI Leverage\*\* | ON (default) |

| \*\*AI Optimization Module\*\* | ON (default) — Learns from past trades \& adapts rules |

| \*\*Broker\*\* | Angel One |

| \*\*Market Holiday Detection\*\* | ON (primary: NSE calendar, secondary: broker API) |

| \*\*News Sentiment Filter\*\* | ON — Skip BUY on negative news; Skip SELL on strongly positive news |

| \*\*Noise Reduction Filter\*\* | ON |

| \*\*Min Profit Mode\*\* | Enabled — prioritize profit lock over minimal loss exit |



---



\## 4. AI/NLP Components

\- \*\*AI Scoring Engine\*\*: Rates trade signals based on momentum, volume patterns, and market sentiment.

\- \*\*AI Trend Detection\*\*: Monitors real-time price flow for trend continuation or reversal.

\- \*\*AI-TSL\*\*: Adjusts TSL dynamically based on volatility, market regime, and news.

\- \*\*AI Leverage Manager\*\*: Decides when and how much leverage to apply (based on capital tier: large, mid, small).

\- \*\*AI Optimization Module\*\*: Learns from past trade data and adapts rules for improved win rate.



---



\## 5. Capital \& Leverage Rules

\- \*\*Capital Rotation\*\*: Freed capital is immediately available for new trades.

\- \*\*Leverage Control\*\*:  

&nbsp; - Manual mode via `Leverage` switch (default OFF)  

&nbsp; - AI mode via `AI Leverage` switch (default ON)  

&nbsp; - AI decides leverage based on capital tier and trade quality score.



---



\## 6. Special Market Awareness

\- \*\*Market Holiday Detection\*\*: Uses NSE official calendar as primary source; Angel One API as fallback.

\- \*\*Partial Trading Day Adjustment\*\*: Tightens exits \& avoids late entries.

\- \*\*Low Volatility Mode\*\*: Activates capital preservation rules.

\- \*\*Short Session Logic\*\*: AI adapts SL/TSL for shorter market hours.



---



\## 7. Exit Conditions

1\. Target hit (+10% for BUY / -10% for SELL)  

2\. Stop Loss hit (-2% for BUY / +2% for SELL)  

3\. AI-TSL triggered  

4\. Trend flip detected (always on)  

5\. Auto-exit at 3:20 PM



---



\## 8. AI Safety Layer

1\. \*\*Market Regime Awareness\*\* – AI detects range-bound or low-volatility days and switches to capital preservation mode.

2\. \*\*Profit-Lock Behavior\*\* – AI tightens TSL earlier in sideways markets to secure small wins.

3\. \*\*Holiday \& Short Session Logic\*\* – AI detects special trading days and adapts SL/TSL accordingly.

4\. \*\*Leverage \& Risk Balance\*\* – AI enforces daily leverage caps to prevent overexposure.

5\. \*\*Continuous Learning vs. Overfitting\*\* – Rolling-window AI training avoids bias from recent unusual days.

6\. \*\*Noise Filtering\*\* – Strict filters to prevent false entries in choppy markets.

7\. \*\*Min Profit Mode\*\* – AI prioritizes securing profit rather than simply minimizing losses.



---



\## 9. Dashboard \& Settings

\- \*\*Dedicated Settings Page\*\* with all switches and dropdowns:

&nbsp; - `Leverage` (default OFF)

&nbsp; - `AI Leverage` (default ON)

&nbsp; - `TSL Mode` dropdown (classic / ai / min / max, default ai)

&nbsp; - `AI Optimization Module` switch (default ON)

&nbsp; - `News Sentiment Filter` switch (default ON)

&nbsp; - `Noise Reduction` switch (default ON)

&nbsp; - `Min Profit Mode` switch (default ON)

\- \*\*Performance Reports\*\*: Daily, Weekly, Monthly, Yearly AI-generated analysis via Gemini AI Studio API.

\- \*\*Live Status Panel\*\*: Capital used, open trades, closed PnL, waitlisted leaderboard, pause/resume.



---



\## 10. Data Sources

\- \*\*Market Data\*\*: Angel One Market Feed API (1-min LTP \& OHLCV)

\- \*\*News Sentiment\*\*: AI/NLP processing of news headlines (integrated filter)

\- \*\*Holiday Data\*\*: NSE official calendar + Angel One API backup



---



\## 11. Notes

\- Strategy is \*\*fully automated\*\* but allows manual overrides.

\- Designed for \*\*noise-free execution\*\*.

\- Backtest engine simulates identical rules to live trading.

\- Capital diversification and rotation ensures optimal resource use.



---



