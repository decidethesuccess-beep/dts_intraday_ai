# Debugging History

## 2025-08-16 – Integration Test Fixes

- ❌ Issue 1: `pytest` failed (`no tests ran`)  
  ✅ Fix: Switched to `unittest` (`python -m unittest tests.test_integration`)  

- ❌ Issue 2: `mock_run_for_minute.call_count 0 != 4`  
  ✅ Fix: Corrected patch path (`strategy.run_for_minute`) + debug prints  

- ✅ Result: Backtest pipeline ran 4 candles, integration test passed  

**Advisory:** Always follow `strategy_spec.md` and `.env` when discussing trade logic.
