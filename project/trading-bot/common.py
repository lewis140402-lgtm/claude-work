"""Shared config for the paper trading bot. Every entry point that can place
an order re-checks PAPER_BASE_URL contains 'paper-api' before doing anything —
see the guard in broker.py. This is not decorative: it's the thing standing
between this project and accidentally routing an order to a live account.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_DATA_URL = os.environ.get("ALPACA_DATA_URL", "https://data.alpaca.markets")

SYMBOL = os.environ.get("TRADING_SYMBOL", "SPY")
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

SHORT_WINDOW = 50   # days
LONG_WINDOW = 200   # days
STARTING_CAPITAL = 10_000.0  # paper money, purely for backtest/reporting scale


def assert_paper_mode():
    if "paper-api" not in ALPACA_BASE_URL:
        raise RuntimeError(
            f"ALPACA_BASE_URL '{ALPACA_BASE_URL}' does not look like a paper "
            "trading endpoint. Refusing to run — this project must never "
            "place orders against a live account."
        )
