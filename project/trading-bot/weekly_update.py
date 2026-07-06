#!/usr/bin/env python3
"""
Run weekly to log real paper-trading performance vs the SPY benchmark.

    python3 weekly_update.py

Appends a row to performance_log.csv (date, equity, % return since start,
benchmark % return since start) and regenerates PERFORMANCE.md's table from
it, so the log is always in sync with the markdown. First run establishes
the baseline equity and benchmark price.

Same network caveat as the rest of this project — needs a real Alpaca
connection, which the sandboxed build session didn't have.
"""
import csv
from datetime import date
from pathlib import Path

from broker import get_account, get_recent_bars
from common import ROOT, SYMBOL, assert_paper_mode

LOG_PATH = ROOT / "performance_log.csv"
REPORT_PATH = ROOT / "PERFORMANCE.md"


def load_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH) as f:
        return list(csv.DictReader(f))


def save_log(rows: list[dict]):
    with open(LOG_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "equity", "return_pct", "benchmark_price", "benchmark_return_pct"])
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(rows: list[dict]) -> str:
    lines = [
        "# Paper Trading Performance Log",
        "",
        "**This is paper money only. No real funds are ever connected to this "
        "project.** Logged weekly by `weekly_update.py` — see `trading-bot/README.md`.",
        "",
        f"Symbol: {SYMBOL} | Strategy: SMA 50/200 crossover | Benchmark: buy-and-hold {SYMBOL}",
        "",
        "| Date | Paper Equity | Return since start | Benchmark return since start |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['date']} | £{float(row['equity']):,.2f} | "
            f"{float(row['return_pct']):+.1f}% | {float(row['benchmark_return_pct']):+.1f}% |"
        )
    lines += [
        "",
        "If the strategy line is consistently behind the benchmark line after "
        "8-12 weeks of real logging, that's the same signal as a losing "
        "backtest: stop, don't extend the experiment hoping it turns around.",
    ]
    return "\n".join(lines)


def main():
    assert_paper_mode()
    rows = load_log()

    account = get_account()
    equity = float(account["equity"])
    bars = get_recent_bars(SYMBOL, limit=1)
    price = float(bars[-1]["c"])

    if not rows:
        return_pct = 0.0
        benchmark_return_pct = 0.0
        base_equity, base_price = equity, price
    else:
        base_equity = float(rows[0]["equity"]) / (1 + float(rows[0]["return_pct"]) / 100)
        base_price = float(rows[0]["benchmark_price"]) / (1 + float(rows[0]["benchmark_return_pct"]) / 100)
        return_pct = (equity / base_equity - 1) * 100
        benchmark_return_pct = (price / base_price - 1) * 100

    rows.append({
        "date": date.today().isoformat(),
        "equity": f"{equity:.2f}",
        "return_pct": f"{return_pct:.2f}",
        "benchmark_price": f"{price:.2f}",
        "benchmark_return_pct": f"{benchmark_return_pct:.2f}",
    })
    save_log(rows)
    REPORT_PATH.write_text(render_markdown(rows))
    print(f"Logged: equity £{equity:,.2f} ({return_pct:+.1f}%) vs benchmark ({benchmark_return_pct:+.1f}%)")


if __name__ == "__main__":
    main()
