## Crypto IV–RV Straddle Carry

### Setup
- Python 3.10+
- `pip install pandas numpy requests yfinance`

### Generate Weekly Sample
```
python build_weekly.py
```
Writes `data/weekly_ivrv_<start>_to_<end>.csv` with RV, IV proxy, signal.

### Run Backtest
```
python backtest.py data/weekly_ivrv_<start>_to_<end>.csv --benchmark-signal -1.0
```
Prints headline metrics and saves `data/ivrv_results_<start>_to_<end>.csv` with strategy and benchmark equity curves.

### Repo Notes
- `data/` is gitignored; keep local outputs there.
- Extend `Backtester` to plug in cost presets or new benchmarks as they arrive.
