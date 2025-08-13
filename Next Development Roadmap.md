\# 📌 DTS Intraday AI Trading System — Next Development Roadmap



\## 1. Immediate Actions (This Week)

\- \[ ] \*\*Sync with Gemini\*\*  

&nbsp; - Share `strategy\_spec.md` with Gemini team for coding alignment.  

&nbsp; - Ensure all modules follow updated AI Safety Layer logic.

&nbsp; 

\- \[ ] \*\*Top-100 Volume Gainers Filtering\*\*  

&nbsp; - Finalize Angel One API script to fetch and rank symbols daily.  

&nbsp; - Save daily symbol list in `data/symbols/YYYY-MM-DD.csv`.



\- \[ ] \*\*30-Day Backtest Run\*\*  

&nbsp; - Integrate updated filtering into `backtest\_runner.py`.  

&nbsp; - Save outputs in `backtest\_results/`.  

&nbsp; - Verify TSL, SL, TGT, trend-flip logic matches live mode.



---



\## 2. Short Term (Next 2–3 Weeks)

\- \[ ] \*\*Streamlit Backtest Dashboard Enhancements\*\*  

&nbsp; - Add symbol filter + date range selection.  

&nbsp; - Display PnL summary, trade log, and capital allocation chart.  

&nbsp; - Export results to CSV/Excel directly from dashboard.



\- \[ ] \*\*Capital Management Simulation\*\*  

&nbsp; - Implement concurrent position cap (10 trades, 10% each).  

&nbsp; - Add capital recycling when positions exit.



\- \[ ] \*\*News Filter Integration\*\*  

&nbsp; - Pull sentiment data into `strategy.py`.  

&nbsp; - Skip BUY trades on negative news, skip SELL trades on positive news.



---



\## 3. Medium Term (Next 1–2 Months)

\- \[ ] \*\*Cloud Readiness \& CI/CD\*\*  

&nbsp; - Set up GitHub Actions for automated testing + deployment.  

&nbsp; - Prepare Dockerfile for portable environment.  

&nbsp; - Decide on Render / Oracle / Other for hosting.



\- \[ ] \*\*Live Mode Enhancements\*\*  

&nbsp; - Add daily AI market regime detection.  

&nbsp; - Integrate profit-lock behavior in sideways markets.



\- \[ ] \*\*Performance Analytics\*\*  

&nbsp; - Create rolling performance metrics (Win%, Avg PnL, Max DD).  

&nbsp; - Compare actual vs. predicted trade outcomes.



---



\## 4. Long Term (Ongoing Improvements)

\- \[ ] Continuous learning model updates without overfitting.  

\- \[ ] Adaptive capital allocation based on AI scoring.  

\- \[ ] Expand to F\&O instruments once equity version is stable.



---



\## 📂 Folder Structure Plan

dts\_intraday\_ai/

│

├── strategy\_spec.md

├── Next Development Roadmap.md

├── data/

│ ├── symbols/ # Daily symbol lists

│ ├── historical/ # Historical OHLCV

│

├── backtest\_results/ # PnL \& logs from backtests

├── dashboards/ # Streamlit apps

│

├── src/

│ ├── strategy.py

│ ├── backtest\_runner.py

│ ├── intraday\_dashboard\_GPT.py

│ ├── live\_stream.py

│ ├── redis\_store.py

│ ├── angel\_order.py



