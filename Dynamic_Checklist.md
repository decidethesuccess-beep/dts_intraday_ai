# DTS Intraday AI Strategy - Dynamic Checklist

**Version:** 2025-08-16  
**Owner:** DTS  
**Advisory:** Always follow `strategy_spec.md` and `.env` when discussing trade logic.

---

## ✅ Core Modules & Status

| Module | Description | Status |
|--------|-------------|--------|
| ai_module.py | AI scoring, AI-driven optimization, TSL adjustments, trend-flip exit, min-profit mode | ✅ |
| ai_webhook.py | Sends/receives AI guidance via Gemini AI Studio | ✅ |
| backtest_dashboard.py | Streamlit dashboard for backtest results | ✅ |
| backtest_runner.py | Historical 1-min candle backtesting engine, top gainers filtering | ✅ |
| constants.py | Thresholds, TSL/SL/TGT, AI params, capital allocation | ✅ |
| data_fetcher.py | Angel One API, 1-min OHLCV/LTP, NSE EQ JSON loader, holiday awareness | ✅ |
| intraday_dashboard_GPT.py | Live dashboard: AI comments, signals, PnL from Redis | ✅ |
| live_stream.py | Real-time LTP/market feed ingestion into Redis | ✅ |
| order_manager.py | Sends orders via Angel One API, capital rotation, SL/TGT/TSL | ✅ |
| paper_trade_system.py | Paper trading simulation with AI TSL, trend-flip, capital rotation | ✅ |
| strategy.py | Main intraday strategy logic: AI scoring, trend detection, trade rules, hard SL/TGT, news filter | ✅ |
| utils.py | Helper functions: datetime, % calculations, symbol filtering, logging | ✅ |
| angel_order.py | Live order connector to Angel One (replaces dhan_order.py) | ✅ |
| config.py | Environment configuration, API keys/secrets, session settings | ✅ |
| news_filter.py | News sentiment analysis, filters negative news for BUY trades | ✅ |
| redis_store.py | Redis hub: AI comments, trade logs, live signals, dashboard updates | ✅ |

---

## 🧪 Testing Modules & Status

| Test Module | Scope | Status |
|-------------|-------|--------|
| test_backtest.py | Unit/integration tests for backtesting logic | ✅ |
| test_live_stream.py | Unit/integration tests for live data ingestion | ✅ |
| test_strategy.py | Unit/integration tests for strategy logic: trade signals, AI scoring, TSL, SL/TGT | ✅ |
| test_utils.py | Unit tests for utility/helper functions | ✅ |
| test_integration.py | End-to-end integration test: capital allocation, trade entry/exit, TSL, trend-flip, PnL | ✅ |

---

## ⏭ Next Steps / Pending

1. Ensure backtesting runs dynamically on **top 100 volume gainers** instead of static symbol lists.  
2. Confirm **AI TSL logic** fully triggers in backtests.  
3. Implement **live-news filters for SELL trades** and refine AI scoring with negative news check.  
4. Integrate **EOD analytics into dashboards**.  
5. Optimize **performance** for 30+ days historical simulations.  
6. Optional: Implement **auto-prioritization of signals** based on AI scoring.  
7. Prepare **deployment-ready setup** (Docker, secure secrets, automated tests).  
8. Document **complete workflow** for Gemini reference and for new team members.

---

**Notes for Gemini:**

- Focus on **specific errors** only; avoid unrelated code changes.  
- Always check if previous code is remembered; request the file if needed.  
- Maintain strict adherence to `strategy_spec.md` and `.env` for all trade logic.  
- Update the **Status column** whenever a module/test is completed or fixed.  
