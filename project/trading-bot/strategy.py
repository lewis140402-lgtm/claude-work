"""
Strategy: 50/200-day SMA crossover ("golden cross" momentum).

Long the symbol whenever the 50-day simple moving average is above the
200-day simple moving average; flat (cash) otherwise. No shorting, no
leverage, no options — the simplest possible expression of "ride the
trend, sit out the rest" so the backtest is easy to audit line by line.

This is deliberately not a sophisticated strategy. The point of Phase 5 is
an honest, working paper-trading loop with real evidence attached — not a
strategy that's likely to beat the index (most timing strategies don't,
after costs; that's exactly what the backtest below is for finding out).
"""
import pandas as pd

from common import LONG_WINDOW, SHORT_WINDOW


def add_signal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sma_short"] = df["close"].rolling(SHORT_WINDOW).mean()
    df["sma_long"] = df["close"].rolling(LONG_WINDOW).mean()
    df["signal"] = 0
    df.loc[df["sma_short"] > df["sma_long"], "signal"] = 1
    # Only act once both averages exist
    df.loc[df["sma_long"].isna(), "signal"] = 0
    return df
