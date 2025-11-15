## Crypto IV–RV Straddle Carry

### Setup
- Python 3.10+
- `pip install -r requirements.txt`

### Get data for weekly sample
```
python build_weekly.py
```

### Run Backtest
```
python backtest.py data/weekly_ivrv_<start>_to_<end>.csv --benchmark-signal <signal>
```
