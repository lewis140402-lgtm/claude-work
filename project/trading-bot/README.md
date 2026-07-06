# Paper Trading Bot (optional side project)

Simple SMA 50/200 crossover ("golden cross") strategy, paper-traded via
Alpaca. **Never connects to a live account** — every function that can
place an order checks `ALPACA_BASE_URL` contains `paper-api` first and
refuses to run otherwise (`common.py::assert_paper_mode`).

## Important: what could and couldn't be run in this build session

This project was built in a sandboxed environment whose network policy
blocks `data.alpaca.markets` and `paper-api.alpaca.markets` (confirmed via
the proxy's own status endpoint — not a guess). So:

- **The backtest engine, metrics, and reporting are fully built and tested**
  — `synthetic_data.py` generates a 5-year random-walk price series and
  `backtest.py` runs against it end-to-end, producing `backtest_report.md`
  and `equity_curve.png`, both committed to this repo as proof the pipeline
  works mechanically.
- **That committed report is synthetic data and says nothing about real
  strategy performance** — it's clearly stamped "NOT A REAL BACKTEST" for
  exactly that reason. Do not treat it as a result.
- **You need to run the real backtest yourself**: get free Alpaca paper
  keys, fill in `.env`, then run `python3 fetch_data.py SPY` followed by
  `python3 backtest.py SPY` from your own machine (or any environment with
  normal internet access). That produces the honest 5-year result the top
  level task asked for.
- The live paper-trading loop (`run_daily.py`, `weekly_update.py`) is built
  against Alpaca's real API shape but is likewise untested against a live
  connection for the same reason — read the code before trusting it, and
  run a few days manually before leaving it unattended.

## Setup

```bash
cd trading-bot
pip3 install -r requirements.txt
cp .env.example .env
# fill in your Alpaca PAPER keys
```

## Order of operations

1. `python3 fetch_data.py SPY` — real 5-year daily bars
2. `python3 backtest.py SPY` — honest backtest vs buy-and-hold, read the verdict
3. **Only if the backtest result is one you're comfortable acting on**:
   start running `python3 run_daily.py` once per trading day (a scheduled
   trigger works well for this — see `../OPERATIONS.md`)
4. `python3 weekly_update.py` once a week — logs real paper performance to
   `PERFORMANCE.md`

## Strategy

50-day SMA vs 200-day SMA, long-only, no leverage, one symbol (`SPY` by
default — trading the index itself makes the strategy-vs-buy-and-hold
comparison as direct as possible). Signal is computed on the prior day's
close and acted on the next day (no lookahead), with a 5bps assumed cost
per position change baked into the backtest as a stand-in for spread and
slippage.

This is a deliberately simple, well-known approach — not a claim that it
beats the market. The backtest exists specifically to find out honestly,
one way or the other, before any paper capital moves.

## Files

- `common.py` — config + the paper-mode safety guard
- `strategy.py` — signal generation
- `fetch_data.py` — real 5-year historical data from Alpaca
- `synthetic_data.py` — synthetic data generator, testing only
- `backtest.py` — backtest engine, metrics, report + chart
- `broker.py` — Alpaca paper account/order wrapper
- `run_daily.py` — daily signal check + paper order if it flipped
- `weekly_update.py` — appends to `PERFORMANCE.md`
- `PERFORMANCE.md` — the running evidence log
