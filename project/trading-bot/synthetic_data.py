#!/usr/bin/env python3
"""
Generate a synthetic 5-year daily price series purely to test the backtest
engine's mechanics (no network access needed). This is NOT real market data
and results from it must never be reported as evidence of strategy
performance — see backtest.py's synthetic-data warning banner.

    python3 synthetic_data.py SYNTH_SPY
"""
import argparse

import numpy as np
import pandas as pd

from common import DATA_DIR

ANNUAL_DRIFT = 0.08
ANNUAL_VOL = 0.18
TRADING_DAYS_PER_YEAR = 252


def generate(years: int = 5, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = years * TRADING_DAYS_PER_YEAR
    daily_drift = ANNUAL_DRIFT / TRADING_DAYS_PER_YEAR
    daily_vol = ANNUAL_VOL / np.sqrt(TRADING_DAYS_PER_YEAR)
    daily_returns = rng.normal(daily_drift, daily_vol, n)
    price = 300 * np.cumprod(1 + daily_returns)

    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=n)
    df = pd.DataFrame({
        "date": dates,
        "open": price * (1 - 0.001),
        "high": price * 1.003,
        "low": price * 0.997,
        "close": price,
        "volume": rng.integers(1_000_000, 5_000_000, n),
    })
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic price data for testing the backtest engine.")
    parser.add_argument("symbol", nargs="?", default="SYNTH_SPY")
    parser.add_argument("--years", type=int, default=5)
    args = parser.parse_args()

    if not args.symbol.upper().startswith("SYNTH"):
        raise SystemExit("Symbol must start with 'SYNTH' to make clear this is not real market data.")

    df = generate(args.years)
    path = DATA_DIR / f"{args.symbol}_daily.csv"
    df.to_csv(path, index=False)
    print(f"Wrote {len(df)} synthetic daily bars -> {path}")


if __name__ == "__main__":
    main()
