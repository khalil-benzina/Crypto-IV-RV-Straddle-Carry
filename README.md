## Crypto IV–RV Straddle Carry

Small research sandbox for comparing implied volatility (IV) to realized volatility (RV) on BTC/ETH weekly samples, then running a simple carry backtest.

### Setup
- Python 3.10+
- `pip install pandas numpy requests yfinance`

### Generate Weekly Sample
```
python build_weekly.py --start 2025-09-01 --end 2025-11-14
```
Writes `data/weekly_ivrv_*.csv` with RV, IV proxy, and signal columns.

### Run Backtest
```
python backtest.py data/weekly_ivrv_2025-09-01_to_2025-11-14.csv --benchmark-signal -1.0
```
Prints headline metrics and saves `data/ivrv_results_*.csv` with strategy and benchmark equity curves.

### Repo Notes
- `data/` is gitignored; keep local outputs there.
- Extend `Backtester` to plug in cost presets or new benchmarks as they arrive.
