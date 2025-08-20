# DTS Intraday AI Strategy - Live Checklist & Error Tracker

**Version:** 2025-08-16  
**Owner:** DTS  
**Advisory:** Always follow `strategy_spec.md` and `.env` when discussing trade logic.

---

## ✅ Core Modules & Status

| Module | Description | Status | Notes / Last Updated |
|--------|-------------|--------|-------------------|
| ai_module.py | AI scoring, AI TSL, trend-flip exit, min-profit | ✅ / ❌ | |
| ai_webhook.py | Sends/receives AI guidance via Gemini AI Studio | ✅ / ❌ | |
| backtest_dashboard.py | Streamlit dashboard for backtest results | ✅ / ❌ | |
| backtest_runner.py | Historical 1-min candle backtesting engine | ✅ / ❌ | |
| constants.py | Thresholds, TSL/SL/TGT, AI params, capital allocation | ✅ / ❌ | |
| data_fetcher.py | Angel One API: 1-min OHLCV/LTP, NSE EQ JSON, holidays | ✅ / ❌ | |
| intraday_dashboard_GPT.py | Live dashboard: AI comments, signals, PnL from Redis | ✅ / ❌ | |
| live_stream.py | Real-time LTP/market feed ingestion into Redis | ✅ / ❌ | |
| order_manager.py | Sends orders via Angel One API, capital rotation, SL/TGT/TSL | ✅ / ❌ | |
| paper_trade_system.py | Paper trading simulation: AI TSL, trend-flip, capital rotation | ✅ / ❌ | |
| strategy.py | Main intraday strategy logic: AI scoring, trend detection, hard SL/TGT, news filter | ✅ / ❌ | |
| utils.py | Helper functions: datetime, % calculations, symbol filtering, logging | ✅ / ❌ | |
| angel_order.py | Live order connector to Angel One | ✅ / ❌ | |
| config.py | Environment config, API keys/secrets, trading sessions | ✅ / ❌ | |
| news_filter.py | News sentiment filter for BUY trades | ✅ / ❌ | |
| redis_store.py | Redis hub: AI comments, trade logs, signals, dashboards | ✅ / ❌ | |

---

## 🧪 Testing Modules & Status

| Test Module | Scope | Status | Last Run / Notes |
|-------------|-------|--------|----------------|
| test_backtest.py | Unit/integration tests for backtesting logic | ✅ / ❌ | |
| test_live_stream.py | Unit/integration tests for live data ingestion | ✅ / ❌ | |
| test_strategy.py | Unit/integration tests for strategy logic: trade signals, AI scoring, TSL, SL/TGT | ✅ / ❌ | |
| test_utils.py | Unit tests for utility/helper functions | ✅ / ❌ | |
| test_integration.py | End-to-end integration test: capital allocation, trade entry/exit, TSL, trend-flip, PnL | ✅ / ❌ | |

---

## ⚠️ Terminal / Runtime Errors

| Module / Test | Last Error Message | Occurred On | Priority |
|---------------|-----------------|------------|---------|
| Example: backtest_runner.py | TypeError: 'strptime() argument 1 must be str, not datetime.date | 2025-08-16 | High |
| Example: test_run_orchestration_flow | AssertionError: Expected close_all_positions_eod to be called once | 2025-08-16 | Medium |

> **Usage:** Gemini should fill this section when a test or module throws an error and update the status columns above accordingly.

---

## ⏭ Next Steps / Focus

1. Address **high-priority errors** first as per the Terminal / Runtime Errors table.  
2. Confirm **AI TSL and trend-flip exit logic** fully triggers in backtests.  
3. Ensure **live news filter** works for both BUY and SELL trades.  
4. Optimize **backtest performance** for multiple days/top volume gainers.  
5. Integrate **EOD analytics** into dashboards.  
6. Optional: Implement **auto-prioritization of signals** based on AI scoring.  
7. Prepare **deployment-ready setup** (Docker, secrets, automated tests).  
8. Update checklist after every module/test fix or completion.

---

**Advisory Notes for Gemini:**  

- Focus **only on errors listed** in the Terminal / Runtime Errors section.  
- Never create new unrelated code; always follow `strategy_spec.md` and `.env`.  
- Request full module code if previous work is not remembered.  
- Keep the Status columns up to date after every fix.  