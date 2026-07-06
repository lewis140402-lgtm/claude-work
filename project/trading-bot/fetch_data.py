#!/usr/bin/env python3
"""
Pull 5 years of daily bars from Alpaca's Market Data API and save to CSV.

    python3 fetch_data.py SPY

Requires ALPACA_API_KEY / ALPACA_SECRET_KEY in .env (the same paper-trading
keys work for market data — no separate data subscription needed for daily
bars on major symbols).

NOTE: this could not be run inside the sandboxed session this project was
built in — outbound access to data.alpaca.markets is blocked by that
session's network policy (see README.md). Run this yourself once you have
your Alpaca keys, in an environment with normal internet access.
"""
import argparse
import sys
from datetime import datetime, timedelta, timezone

import requests

from common import ALPACA_API_KEY, ALPACA_DATA_URL, ALPACA_SECRET_KEY, DATA_DIR

BARS_URL = "{base}/v2/stocks/{symbol}/bars"


def fetch_daily_bars(symbol: str, years: int = 5) -> list[dict]:
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        raise SystemExit("Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env first.")

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=365 * years + 5)
    headers = {"APCA-API-KEY-ID": ALPACA_API_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY}

    bars = []
    params = {
        "timeframe": "1Day",
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "adjustment": "all",
        "limit": 10000,
    }
    url = BARS_URL.format(base=ALPACA_DATA_URL, symbol=symbol)

    while True:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        bars.extend(payload.get("bars", []))
        token = payload.get("next_page_token")
        if not token:
            break
        params["page_token"] = token

    return bars


def save_csv(symbol: str, bars: list[dict]):
    path = DATA_DIR / f"{symbol}_daily.csv"
    with open(path, "w") as f:
        f.write("date,open,high,low,close,volume\n")
        for bar in bars:
            date = bar["t"][:10]
            f.write(f"{date},{bar['o']},{bar['h']},{bar['l']},{bar['c']},{bar['v']}\n")
    print(f"Wrote {len(bars)} daily bars -> {path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch 5 years of daily bars from Alpaca for backtesting.")
    parser.add_argument("symbol", nargs="?", default="SPY")
    parser.add_argument("--years", type=int, default=5)
    args = parser.parse_args()

    bars = fetch_daily_bars(args.symbol, args.years)
    if not bars:
        print(f"No bars returned for {args.symbol}.", file=sys.stderr)
        sys.exit(1)
    save_csv(args.symbol, bars)


if __name__ == "__main__":
    main()
