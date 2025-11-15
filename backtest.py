import pandas as pd
import numpy as np
import argparse

class Backtester:
    def __init__(self, weekly: pd.DataFrame, benchmark_signal_value):
        """
        weekly df must have:
        - snapshot_friday
        - rv_trailing_7d_ann
        - rv_next_7d_ann
        - iv_proxy_dvol
        - signal

        benchmark_signal_value:
        -1.0 -> always short vol
        0.0 -> always flat
        +1.0 -> always long vol
        None -> no benchmark
        """
        self.weekly = weekly.copy().reset_index(drop=True)
        self.benchmark_signal_value = benchmark_signal_value
    
    @staticmethod
    def _pnl(signal, rv_forward, iv):
        return signal * (rv_forward - iv)

    def run(self) -> pd.DataFrame:
        w = self.weekly

        w["pnl_strategy"] = self._pnl(w["signal"], w["rv_next_7d_ann"], w["iv_proxy_dvol"])
        w["equity_strategy"] = w["pnl_strategy"].cumsum()

        if self.benchmark_signal_value is not None:
            w["pnl_benchmark"] = self._pnl(self.benchmark_signal_value, w["rv_next_7d_ann"], w["iv_proxy_dvol"])
            w["equity_benchmark"] = w["pnl_benchmark"].cumsum()

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
    parser.add_argument(
        "--benchmark-signal",
        type=float,
        help="Benchmark signal value (default: -1.0 = always short vol)",
    )
    args = parser.parse_args()

    weekly = pd.read_csv(args.input_file)

    bt = Backtester(weekly, benchmark_signal_value=args.benchmark_signal)
    result = bt.run()

    strat_metrics = bt.compute_metrics(
        result["pnl_strategy"],
        result["equity_strategy"],
    )

    if args.benchmark_signal is not None:
        bench_metrics = bt.compute_metrics(
            result["pnl_benchmark"],
            result["equity_benchmark"],
        )


    print("\nIV–RV Carry Strategy (QD signal):")
    for k, v in strat_metrics.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, (int, float, float)) else f"  {k}: {v}")

    if args.benchmark_signal is not None:
        print("\nBenchmark (signal =", args.benchmark_signal, "):")
        for k, v in bench_metrics.items():
            print(f"  {k}: {v:.4f}" if isinstance(v, (int, float, float)) else f"  {k}: {v}")

    output_file = args.input_file.replace("weekly_ivrv", "ivrv_results")
    result.to_csv(output_file, index=False)
    print(f"\nSaved detailed results to {output_file}")