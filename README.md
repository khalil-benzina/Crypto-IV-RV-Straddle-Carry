## Crypto IV–RV Straddle Carry

### Setup
- Python 3.10+
- `pip install -r requirements.txt`

### Generate Weekly Sample
```
python build_weekly.py
```
Writes `data/weekly_ivrv_<start>_to_<end>.csv` with RV, IV proxy, signal.

### Run Backtest
```
python backtest.py data/weekly_ivrv_<start>_to_<end>.csv --benchmark-signal -1.0
```
Prints headline metrics and saves `data/ivrv_results_<start>_to_<end>.csv` with strategy and benchmark equity curves
