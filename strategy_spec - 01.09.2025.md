# DTS Intraday AI Strategy Specification

**Version:** 2025-08-29  
**Owner:** DTS (Strategy Owner)  
**Status:** Active Development  

---

## 1. Strategy Overview  

The **DTS Intraday AI Trading System** is an AI-driven, intraday stock trading framework designed for the **NSE India (EQ segment)**.  

It combines:  
- **Momentum + Volume breakout detection**  
- **AI-based scoring and news sentiment filtering**  
- **Dynamic exits (SL, TSL, Target, Trend reversal, Profit-locking)**  
- **AI Safety Layer (Holiday guard, Crash guard, Daily leverage caps)**  
- **Rolling-window retraining for adaptability without overfitting**  

The system runs daily from **09:00–16:00 IST**, with entry windows frozen after **09:20 IST**. Auto-exit at **15:20 IST**.  

---

## 2. Data Sources  

- **Market Data:** Angel One SmartAPI (1-min OHLCV, real-time feeds).  
- **Symbol Universe:** Filtered NSE_EQ stocks (from Angel One JSON).  
- **News & Sentiment:** Finnhub API (general & ticker-specific news, sentiment-ready).  
- **Holiday Calendar:** NSE Holiday Calendar API (primary), local static fallback.  

---

## 3. Core Strategy Logic  

### 3.1 Entry Conditions  
- Universe: Top 100 daily volume gainers (from 09:15–09:20 window).  
- Long entry: Early-stage **+3–5% momentum with volume spike**.  
- Short entry: Early-stage **–3–5% downside with volume spike**.  
- AI Score (volume, price action, sentiment, momentum) must exceed threshold.  

### 3.2 Exit Conditions  
- Stop Loss (SL): –2%  
- Trailing SL (TSL): –1% (volatility-aware AI-TSL from Phase 3.3)  
- Target (TGT): +10%  
- Trend reversal: Always enabled for both BUY and SELL  
- Auto-exit: 15:20 IST  

### 3.3 Capital Allocation  
- 10% of capital per trade, max 10 parallel trades.  
- If all slots filled: pause entries.  
- AI may replace weakest trade with stronger candidate.  
- Leverage usage capped by AI Safety Layer.  

### 3.4 AI Safety Layer (New: Phase 3.4.1)  
1. **Market Regime Awareness** → Detect low-volatility or range-bound days, switch to capital preservation.  
2. **Holiday Guard** → NSE holiday auto-detection via API, fallback to local JSON/CSV.  
3. **Crash Guard** → AI detects market-wide crash (e.g., >NIFTY down 3% intraday) → auto reduce exposure or exit positions.  
4. **Leverage Cap** → Daily leverage limits enforced by AI.  
5. **Profit-Lock Mode** → Tighten exits when intraday profits cross defined thresholds.  
6. **Continuous Learning** → Rolling-window retraining, avoiding overfit.  

---

## 4. System Components  

- **Data Layer**: Market data feeds, news sentiment, holiday API.  
- **Redis Store**: Central memory for ticks, AI state, trade ledger.  
- **Strategy Core**: Scoring, entry/exit logic, AI-TSL, safety layer.  
- **Execution Layer**: Order routing via Angel One.  
- **Dashboard**: Streamlit-based backtest/live visualization.  
- **Backtesting Engine**: Supports historical 1-min replay, AI scoring, trade simulation.  

---

## 5. Milestones / Phases  

### ✅ Phase 1 – Data & Backtest Foundation  
- Symbol universe filtering (NSE_EQ only).  
- Historical 1-min OHLCV fetch.  
- Backtest engine setup with Streamlit dashboard.  
- ✅ Completed.  

### ✅ Phase 2 – Entry & Exit Logic  
- Entry window freeze at 09:20 IST.  
- SL/TGT/TSL basic setup.  
- Trend reversal exits enabled.  
- Auto-exit at 15:20 IST.  
- ✅ Completed.  

### ✅ Phase 3 – AI Integration  
- **3.1 News Sentiment Filter** → Finnhub integration.  
- **3.2 AI Scoring Logic** → Volume + momentum + sentiment.  
- **3.3 AI-TSL** → Volatility-aware trailing stop-loss.  
- ✅ Completed.  
- **3.4.1 AI Safety Layer** → (Holiday guard, Crash guard, Leverage cap). 🚧 *Next in progress*.  

### ⏳ Phase 4 – Advanced AI Modules  
- Profit-Lock Mode.  
- Minimum Profit Mode.  
- Circuit Targeting (momentum-to-circuit moves).  
- Rolling-window AI retraining.  

### ⏳ Phase 5 – Performance Analytics & Reports  
- Trade logs, PnL curves.  
- Per-strategy & per-symbol analytics.  
- AI decision audit trail.  

### ⏳ Phase 6 – Live Deployment (Paper Trading)  
- Real-time Redis streaming.  
- Paper-trade execution via Angel One API.  
- Dashboard for monitoring live positions.  

### ⏳ Phase 7 – Live Deployment (Production)  
- Cloud deployment (Render/Oracle/GCP/AWS).  
- Automated trading with safeguards.  
- Failover handling.  

### ⏳ Phase 8 – Continuous Learning & Optimization  
- Ongoing retraining using rolling windows.  
- Adaptive thresholds.  
- Strategy refinements via live feedback.  

---

## 6. Current Progress  

- **Phase 1–3.3**: ✅ Completed and stable (57 tests passing).  
- **Phase 3.4.1 AI Safety Layer**: 🚧 Pending implementation.  
- Next: Implement safety guards (holiday, crash, leverage) before moving to Phase 4.  

---
