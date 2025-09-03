# DTS Intraday AI Strategy Specification

**Version:** 2025-08-24  
**Owner:** DTS (Strategy Owner)  
**Status:** Active Development  

---

## 1. Strategy Overview
The **DTS Intraday AI Trading System** is a **no-indicator**, **AI/NLP-driven**, **high-momentum stock trading strategy** for **NSE India**.  

- Supports both **BUY** and **SELL** trades.  
- Implements **strict risk management**, **capital rotation**, and **adaptive AI decision-making**.  
- Focused on **noise reduction**, **minimal false entries**, and **AI-driven scoring** for signal purity.  

---

## 2. Core Philosophy
- **No traditional indicators** (RSI, MACD, etc.).  
- **AI/NLP-based scoring** for entries.  
- **Momentum & volume spike detection**.  
- **Circuit targeting** for early strong moves.  
- **AI-TSL & AI leverage control**.  
- **Market awareness** (holidays, volatile or range-bound sessions).  
- **Noise-free execution** with smart filters.  

---

## 3. Default Settings (as of 2025-08-16)

| Setting               | Default Value                               |
|-----------------------|---------------------------------------------|
| Capital Allocation    | 10% per trade (max 10 concurrent trades)    |
| Trade Direction       | BUY + SELL enabled                          |
| Target Profit (TGT)   | +10%                                        |
| Stop Loss (SL)        | -2%                                         |
| Trailing Stop Loss    | 1% BUY, 1% SELL (from entry price)          |
| TSL Mode              | AI (classic / ai / min / max)               |
| Trend Flip Exit       | Always ON                                   |
| Auto Exit Time        | 3:20 PM IST                                 |

---

## 4. AI-Driven Position Sizing
Position sizing uses **AI signal scores** with a **tiered leverage model** to maximize capital efficiency:

| Signal Score Range | Leverage Multiplier |
|--------------------|---------------------|
| ≥ 0.80             | 5.0x                |
| 0.50 − 0.79        | 3.5x                |
| < 0.50             | 1.0x                |

**Rationale:** Deploy significant capital only when AI confidence is high, combining momentum, volume, and sentiment.

---

## 5. Risk Management
- **Capital Allocation:** Fixed % of total capital per trade.  
- **Max Positions:** Configurable concurrent trade limit.  
- **Dynamic AI Leverage:** Adjusts leverage based on AI score.  
- **Trend-Flip Exit:** Exits on strong reversals.  
- **AI-TSL:** Continuous trailing SL adjustments.  
- **Hard SL/TGT:** Mandatory SL and TGT levels.  
- **Guaranteed Auto-Exit:** Closes all positions at 3:20 PM IST.  

---

## 6. Core Modules
- `strategy.py` – Main trading logic.  
- `data_fetcher.py` – Market data retrieval (Angel One API).  
- `ai_module.py` – AI scoring, leverage, and AI-TSL.  
- `order_manager.py` – Trade execution and tracking.  
- `news_filter.py` – Sentiment-based filtering.  
- `redis_store.py` – Real-time state management.  
- `live_stream.py` – Live market data ingestion.  
- `backtest_runner.py` – Historical simulation.  

---

## 7. Exit Conditions
- **Trend-Flip Exit:** Always ON, highest priority.  
- **AI-TSL:** Dynamic exits in profit.  
- **Hard SL/TGT:** -2% SL, +10% TGT (configurable via `.env`).  
- **Auto-Exit:** 3:20 PM IST.  
- **Min Profit Mode:** Locks partial profits early.  

---

## 8. AI/ML Integration
- **AI Scoring:** 0.0–1.0 scoring based on momentum, volume, and news.  
- **AI Leverage:** Adjusts size and leverage dynamically.  
- **AI-TSL:** Optimizes exits.  
- **Trend-Flip:** Detects and exits on reversals.  
- **Continuous Learning:** Rolling-window optimization prevents overfitting.  
- **Noise Filtering:** Reduces false entries.  
- **Min Profit Mode:** Early partial exits.  

---

## 9. Dashboard & Settings
- **Settings Panel:** AI leverage, TSL mode, noise reduction, sentiment filter, min-profit mode.  
- **Performance Reports:** Daily, weekly, monthly, yearly (via Gemini AI Studio).  
- **Live Status Panel:** Capital used, open trades, PnL, waitlist, pause/resume.  

---

## 10. Data Sources
- **Market Data:** Angel One Market Feed API (1-min OHLCV).  
- **News Sentiment:** AI/NLP from headlines.  
- **Holiday Data:** NSE calendar + Angel One API.  
- **Symbols:** NSE EQ JSON feed, cached in CSV/memory.  

---

## 11. AI Webhook Integration
- **Purpose:** AI-driven guidance, trade commentary, and alerts.  
- **Source:** Gemini AI Studio API (`GEMINI_API_KEY`).  
- **Functions:** Commentary, suggestions, risk alerts, improvement tips.  
- **Dashboard Integration:** Comments stored in Redis and displayed on dashboard.  
- **Safety:** Timeout and exception handling; advisory only.  

---

## 12. Test Coverage & Verification (as of 2025-08-24)
- **Unit Tests:** Cover core modules, AI-TSL, SL/TGT, utilities.  
- **Backtest Tests:** Validate allocation, rotation, exits, PnL, edge conditions.  
- **Integration Tests:** Confirm end-to-end workflows:  
  - `test_full_backtest_run`  
  - `test_dashboard_data_pipeline`  
  - `test_concurrent_positions_and_reallocation`  
  - `test_trend_flip_and_dashboard_reflects_change`  
  - `test_edge_cases_integration`  

**Results:** 36/36 tests passing, tagged release `v0.3-integration-tests`.  
**Mocks & Isolation:** Problematic dependencies (e.g., dashboard) replaced with mock classes for CI/CD stability.  

---
