"""
Thin wrapper around the Alpaca paper trading REST API. Every function here
calls assert_paper_mode() first — if ALPACA_BASE_URL ever points anywhere
other than paper-api.alpaca.markets, every function in this module refuses
to run. Do not remove that guard.
"""
import requests

from common import ALPACA_API_KEY, ALPACA_BASE_URL, ALPACA_SECRET_KEY, assert_paper_mode

HEADERS = {"APCA-API-KEY-ID": ALPACA_API_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY}


def get_account() -> dict:
    assert_paper_mode()
    resp = requests.get(f"{ALPACA_BASE_URL}/v2/account", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_position(symbol: str) -> dict | None:
    assert_paper_mode()
    resp = requests.get(f"{ALPACA_BASE_URL}/v2/positions/{symbol}", headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def place_market_order(symbol: str, qty: float, side: str) -> dict:
    assert_paper_mode()
    if side not in ("buy", "sell"):
        raise ValueError(f"side must be 'buy' or 'sell', got {side!r}")
    resp = requests.post(
        f"{ALPACA_BASE_URL}/v2/orders",
        headers=HEADERS,
        json={
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_recent_bars(symbol: str, limit: int = 250) -> list[dict]:
    """Enough daily bars to compute the 200-day SMA plus a margin."""
    from common import ALPACA_DATA_URL
    assert_paper_mode()
    resp = requests.get(
        f"{ALPACA_DATA_URL}/v2/stocks/{symbol}/bars",
        headers=HEADERS,
        params={"timeframe": "1Day", "limit": limit, "adjustment": "all"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("bars", [])
