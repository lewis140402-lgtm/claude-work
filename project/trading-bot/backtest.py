#!/usr/bin/env python3
"""
Backtest the SMA crossover strategy against buy-and-hold, honestly.

    python3 backtest.py SPY

Reads data/<symbol>_daily.csv (from fetch_data.py), runs the strategy from
strategy.py with a 1-day execution lag (no lookahead) and a small assumed
transaction cost per trade, and writes:
  - backtest_report.md: strategy vs buy-and-hold, side by side, plus a
    plain verdict on whether the strategy actually won
  - equity_curve.png: both equity curves plotted together

Any symbol starting with SYNTH_ is treated as synthetic test data and the
report is stamped accordingly — synthetic results are for verifying the
backtest math works, never evidence about real strategy performance.
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import DATA_DIR, ROOT, STARTING_CAPITAL
from strategy import add_signal

TRANSACTION_COST_BPS = 5  # 0.05% per position change — a conservative stand-in for spread/slippage


def load_prices(symbol: str) -> pd.DataFrame:
    path = DATA_DIR / f"{symbol}_daily.csv"
    if not path.exists():
        raise SystemExit(f"No data at {path}. Run fetch_data.py (or synthetic_data.py for a dry run) first.")
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def run_backtest(df: pd.DataFrame) -> pd.DataFrame:
    df = add_signal(df)
    df["position"] = df["signal"].shift(1).fillna(0)
    df["daily_return"] = df["close"].pct_change().fillna(0)

    trade_happened = df["position"].diff().fillna(0) != 0
    cost = trade_happened * (TRANSACTION_COST_BPS / 10_000)

    df["strategy_return"] = df["position"] * df["daily_return"] - cost
    df["equity_strategy"] = STARTING_CAPITAL * (1 + df["strategy_return"]).cumprod()
    df["equity_buyhold"] = STARTING_CAPITAL * (1 + df["daily_return"]).cumprod()
    return df


def compute_metrics(df: pd.DataFrame, equity_col: str, return_col: str) -> dict:
    equity = df[equity_col]
    years = (df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25
    total_return = equity.iloc[-1] / STARTING_CAPITAL - 1
    cagr = (equity.iloc[-1] / STARTING_CAPITAL) ** (1 / years) - 1 if years > 0 else float("nan")
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_drawdown = drawdown.min()
    daily_returns = df[return_col]
    sharpe = (
        (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        if daily_returns.std() > 0 else float("nan")
    )
    return {
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "years": years,
    }


def plot_equity(df: pd.DataFrame, symbol: str, out_path):
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["equity_strategy"], label="SMA 50/200 strategy")
    plt.plot(df["date"], df["equity_buyhold"], label=f"Buy & hold {symbol}")
    plt.title(f"{symbol}: strategy vs buy-and-hold (paper money, starting £{STARTING_CAPITAL:,.0f})")
    plt.xlabel("Date")
    plt.ylabel("Equity (£)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()


def write_report(symbol: str, df: pd.DataFrame, strat_metrics: dict, hold_metrics: dict, num_trades: int, out_path):
    is_synthetic = symbol.upper().startswith("SYNTH")
    lines = []
    if is_synthetic:
        lines.append("# ⚠️ SYNTHETIC TEST DATA — NOT A REAL BACKTEST")
        lines.append("")
        lines.append(
            "This run used randomly generated price data to verify the backtest "
            "engine's math and reporting work correctly. It says nothing about "
            "how this strategy would perform on real markets. Run `fetch_data.py` "
            "with real Alpaca market data and re-run this backtest before drawing "
            "any conclusion about the strategy."
        )
        lines.append("")
    lines.append(f"# Backtest Report: {symbol}")
    lines.append("")
    lines.append(f"Period: {df['date'].iloc[0].date()} to {df['date'].iloc[-1].date()} "
                 f"({strat_metrics['years']:.1f} years)")
    lines.append(f"Starting paper capital: £{STARTING_CAPITAL:,.0f}")
    lines.append(f"Assumed transaction cost: {TRANSACTION_COST_BPS} bps per position change")
    lines.append(f"Number of trades (position changes): {num_trades}")
    lines.append("")
    lines.append("| Metric | SMA 50/200 Strategy | Buy & Hold |")
    lines.append("|---|---|---|")
    lines.append(f"| Total return | {strat_metrics['total_return']:.1%} | {hold_metrics['total_return']:.1%} |")
    lines.append(f"| CAGR | {strat_metrics['cagr']:.1%} | {hold_metrics['cagr']:.1%} |")
    lines.append(f"| Max drawdown | {strat_metrics['max_drawdown']:.1%} | {hold_metrics['max_drawdown']:.1%} |")
    lines.append(f"| Sharpe ratio (annualised) | {strat_metrics['sharpe']:.2f} | {hold_metrics['sharpe']:.2f} |")
    lines.append("")

    beat_on_return = strat_metrics["total_return"] > hold_metrics["total_return"]
    beat_on_drawdown = strat_metrics["max_drawdown"] > hold_metrics["max_drawdown"]  # less negative = better
    lines.append("## Verdict")
    lines.append("")
    if beat_on_return:
        lines.append(
            f"The strategy beat buy-and-hold on total return "
            f"({strat_metrics['total_return']:.1%} vs {hold_metrics['total_return']:.1%}) over this period."
        )
    else:
        lines.append(
            f"The strategy did **not** beat buy-and-hold on total return "
            f"({strat_metrics['total_return']:.1%} vs {hold_metrics['total_return']:.1%}) over this period. "
            "This is the normal outcome for trend-following strategies during periods without a sustained "
            "downtrend to sit out — the historical base rate for this kind of strategy beating a simple "
            "index hold is low. That's real information, not a bug."
        )
    lines.append("")
    if beat_on_drawdown:
        lines.append(
            f"It did reduce max drawdown ({strat_metrics['max_drawdown']:.1%} vs "
            f"{hold_metrics['max_drawdown']:.1%}), which is the actual case for a trend strategy — "
            "smoother ride, not necessarily a higher end number."
        )
    else:
        lines.append("It did not meaningfully reduce drawdown either, in this run.")
    lines.append("")
    lines.append("![Equity curve](equity_curve.png)")
    lines.append("")
    lines.append(
        "Past performance (real or synthetic) is not evidence of future results. "
        "This report is a decision input, not a guarantee — see `../OPERATIONS.md` "
        "and the top-level constraint: this project stays paper money only."
    )
    ROOT.joinpath(out_path).write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Backtest the SMA crossover strategy vs buy-and-hold.")
    parser.add_argument("symbol", nargs="?", default="SPY")
    args = parser.parse_args()

    df = load_prices(args.symbol)
    df = run_backtest(df)
    df = df.dropna(subset=["equity_strategy", "equity_buyhold"]).reset_index(drop=True)

    num_trades = int((df["position"].diff().fillna(0) != 0).sum())
    strat_metrics = compute_metrics(df, "equity_strategy", "strategy_return")
    hold_metrics = compute_metrics(df, "equity_buyhold", "daily_return")

    plot_equity(df, args.symbol, ROOT / "equity_curve.png")
    write_report(args.symbol, df, strat_metrics, hold_metrics, num_trades, "backtest_report.md")

    print(f"Report written to backtest_report.md, chart to equity_curve.png")
    print(f"Strategy total return: {strat_metrics['total_return']:.1%} | "
          f"Buy&hold: {hold_metrics['total_return']:.1%}")


if __name__ == "__main__":
    main()
