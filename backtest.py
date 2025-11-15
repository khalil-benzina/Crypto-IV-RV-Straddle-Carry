import pandas as pd
import numpy as np
import argparse

class Backtester:
    def __init__(self, weekly: pd.DataFrame):
        """
        weekly df must have:
        - snapshot_friday
        - rv_trailing_7d_ann
        - rv_next_7d_ann
        - iv_proxy_dvol
        - signal
        """
        self.weekly = weekly.copy().reset_index(drop=True)

    def run(self) -> pd.DataFrame:
        w = self.weekly

        w["pnl_strategy"] = w["signal"] * (w["rv_next_7d_ann"] - w["iv_proxy_dvol"])
        w["equity_strategy"] = w["pnl_strategy"].cumsum()

        return w

    @staticmethod
    def compute_metrics(pnl: pd.Series, equity: pd.Series) -> dict:
        pnl = pnl.dropna()
        avg = pnl.mean()
        std = pnl.std(ddof=1)
        sharpe = avg / std if std != 0 else np.nan
        win_rate = (pnl > 0).mean()

        rolling_max = equity.cummax()
        drawdown = equity - rolling_max
        max_dd = drawdown.min()

        return {
            "avg_pnl": avg,
            "std_pnl": std,
            "sharpe": sharpe,
            "win_rate": win_rate,
            "max_drawdown": max_dd,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run IV–RV backtest on a weekly CSV file.")
    parser.add_argument("input_file", help="Path to the weekly IVRV CSV file")
    args = parser.parse_args()

    # Load CSV passed from terminal
    weekly = pd.read_csv(args.input_file)

    bt = Backtester(weekly)
    result = bt.run()

    metrics = bt.compute_metrics(
        result["pnl_strategy"],
        result["equity_strategy"]
    )

    print("=== IV–RV Carry Strategy Results ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    # Output filename mirrors input name
    output_file = args.input_file.replace("weekly_ivrv", "ivrv_results")
    result.to_csv(output_file, index=False)

    print(f"Saved {output_file}")