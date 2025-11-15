import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import timedelta

ANNUAL_DAYS = 365
DERIBIT_DVOL_ENDPOINT = "https://www.deribit.com/api/v2/public/get_volatility_index_data"

# returns df with columns: date, close
def fetch_btc_data(start_date, end_date):
    btc = yf.download("BTC-USD", start=start_date, end=end_date, interval="1d") # download BTC daily prices
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)

    btc = btc.reset_index()[["Date", "Close"]].rename(columns={"Date": "date", "Close": "close"}) 
    btc["date"] = pd.to_datetime(btc["date"]).dt.date
    btc = btc.reset_index(drop=True)
    return btc 

# returns df with columns: snapshot_friday, rv_trailing_7d_ann, rv_next_7d_ann
def compute_rv(btc):
    btc["log_ret"] = np.log(btc["close"]).diff() # calculate daily log returns
    btc["rv_trailing_7d_ann"] = np.sqrt(ANNUAL_DAYS) * btc["log_ret"].rolling(7).std() # calculate trailing 7-day annualized rv 

    # extract fridays
    btc["weekday"] = pd.to_datetime(btc["date"]).dt.weekday
    friday_idx = btc.index[btc["weekday"] == 4].tolist()

    # for each friday, compute the next 7-days' annualized rv
    rows = []
    for idx in friday_idx:
        rv_trailing = btc.loc[idx, "rv_trailing_7d_ann"] # get trailing 7-day annualized rv for the friday

        start = idx + 1
        end = idx + 7

        if end >= len(btc):
            continue

        rvs_forward = btc.loc[start:end, "log_ret"].dropna()
        if len(rvs_forward) < 7:
            continue

        rv_next = np.sqrt(ANNUAL_DAYS) * rvs_forward.std(ddof=1) # get next 7-days' annualized rv

        rows.append({
            "snapshot_friday": str(btc.loc[idx, "date"]),
            "rv_trailing_7d_ann": float(rv_trailing),
            "rv_next_7d_ann": float(rv_next),
        })

    return pd.DataFrame(rows)

# fetch IV for each Friday from DVOL index
def get_dvol(date_str):
    try:
        ts = pd.Timestamp(date_str).tz_localize("UTC")
        end_ms = int(ts.replace(hour=23, minute=59).timestamp() * 1000)
        start_ms = int((ts - timedelta(hours=48)).timestamp() * 1000)

        r = requests.get(
            DERIBIT_DVOL_ENDPOINT,
            params={
                "currency": "BTC",
                "start_timestamp": start_ms,
                "end_timestamp": end_ms,
                "resolution": "3600",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json().get("result", {}).get("data", [])

        if not data:
            return None

        close = data[-1][4]
        return close / 100 if close > 1.5 else close
    except:
        return None

# generate signal based on the spread between IV and RV
def generate_signal(spread):
    if spread > 0:
        return -1 # short IV
    elif spread < 0:
        return +1 # long IV
    return 0 # no signal


def build_weekly_ivrv(start_date, end_date):
    btc = fetch_btc_data(start_date, end_date)
    weekly = compute_rv(btc)

    weekly["iv_proxy_dvol"] = weekly["snapshot_friday"].apply(get_dvol)
    weekly = weekly.dropna(subset=["iv_proxy_dvol"])

    weekly["iv_minus_rv_trailing"] = weekly["iv_proxy_dvol"] - weekly["rv_trailing_7d_ann"]
    weekly["signal"] = weekly["iv_minus_rv_trailing"].apply(generate_signal)

    # drop rows with missing values
    weekly = weekly.dropna()
    filename = f"data/weekly_ivrv_{start_date}_to_{end_date}.csv"
    weekly.to_csv(filename, index=False)
    print(f"Saved {filename}")

if __name__ == "__main__":
    start_date = "2025-09-01"
    end_date = "2025-11-14"

    build_weekly_ivrv(start_date, end_date)