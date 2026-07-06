#!/usr/bin/env python3
"""
The live (paper) trading loop — run this once per trading day, after market
close, e.g. via a scheduled trigger.

    python3 run_daily.py

Pulls recent bars for SYMBOL, computes the same SMA 50/200 signal used in
the backtest, and if the signal has flipped since the current position,
places a paper market order to match it. Does nothing if the signal
matches the current position already (idempotent — safe to run more than
once a day).

Cannot be exercised in the sandboxed session this project was built in —
data.alpaca.markets and paper-api.alpaca.markets are both blocked by that
session's network policy. Run this from your own machine or an environment
with normal internet access, with your Alpaca paper API keys in .env.
"""
import pandas as pd

from broker import get_account, get_position, get_recent_bars, place_market_order
from common import SYMBOL, assert_paper_mode
from strategy import add_signal


def latest_signal(symbol: str) -> int:
    bars = get_recent_bars(symbol)
    df = pd.DataFrame(bars)
    df = df.rename(columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
    df["date"] = pd.to_datetime(df["date"])
    df = add_signal(df)
    return int(df["signal"].iloc[-1])


def current_position_size(symbol: str) -> float:
    pos = get_position(symbol)
    return float(pos["qty"]) if pos else 0.0


def main():
    assert_paper_mode()
    signal = latest_signal(SYMBOL)
    held_qty = current_position_size(SYMBOL)
    account = get_account()
    equity = float(account["equity"])

    print(f"{SYMBOL}: signal={'LONG' if signal else 'FLAT'}, currently holding {held_qty} shares, equity £{equity:,.2f}")

    if signal == 1 and held_qty == 0:
        # Simple full-equity sizing: spend ~95% of equity to leave a cash buffer.
        bars = get_recent_bars(SYMBOL, limit=1)
        last_price = float(bars[-1]["c"])
        qty = int((equity * 0.95) // last_price)
        if qty > 0:
            order = place_market_order(SYMBOL, qty, "buy")
            print(f"Signal flipped to LONG — bought {qty} shares. Order: {order['id']}")
        else:
            print("Signal is LONG but equity too low to buy even 1 share.")
    elif signal == 0 and held_qty > 0:
        order = place_market_order(SYMBOL, held_qty, "sell")
        print(f"Signal flipped to FLAT — sold {held_qty} shares. Order: {order['id']}")
    else:
        print("No action needed — position already matches signal.")


if __name__ == "__main__":
    main()
