"""
US Stock Drawdown Screener

Finds US stocks with the highest drawdown over the last year, using
TradingView's pre-computed `Perf.Y` (1-year performance %) field to sort
directly in the API, and `price_52_week_high` for the peak-to-current drop.

Usage:
    python screener_drawdown.py <sessionid>
    python screener_drawdown.py  # reads TRADINGVIEW_SESSION env var
"""
import os
import sys

import pandas as pd

from tradingview_screener import Query, col


def run_screener(session_id: str | None = None) -> pd.DataFrame:
    cookies = {'sessionid': session_id} if session_id else None
    kwargs = {'cookies': cookies} if cookies else {}

    print("Fetching US stocks from TradingView...")
    count, df = (
        Query()
        .select(
            'name',
            'close',
            'price_52_week_high',
            'price_52_week_low',
            'Perf.Y',         # 1-year performance % (pre-computed)
            'Perf.6M',
            'Perf.3M',
            'market_cap_basic',
            'sector',
            'exchange',
        )
        .where(
            col('market_cap_basic') > 100_000_000,  # >$100M market cap
            col('typespecs').has(['common']),          # common shares only
            col('exchange').not_in(['OTC']),           # exclude OTC
            col('Perf.Y').not_empty(),
        )
        .order_by('Perf.Y', ascending=True)           # worst performers first
        .set_markets('america')
        .limit(50)
        .get_scanner_data(**kwargs)
    )

    print(f"Total US stocks matched filters: {count:,}")

    df['drawdown_from_52wk_high_%'] = (
        (df['price_52_week_high'] - df['close']) / df['price_52_week_high'] * 100
    )
    df['market_cap_B'] = df['market_cap_basic'] / 1e9

    return df


def main():
    session_id = (
        sys.argv[1] if len(sys.argv) > 1 else os.environ.get('TRADINGVIEW_SESSION')
    )

    df = run_screener(session_id)

    display_cols = {
        'name': 'Ticker',
        'close': 'Price',
        'price_52_week_high': '52W High',
        'drawdown_from_52wk_high_%': 'Drop from 52W High %',
        'Perf.Y': '1Y Perf %',
        'Perf.6M': '6M Perf %',
        'Perf.3M': '3M Perf %',
        'market_cap_B': 'Mkt Cap ($B)',
        'sector': 'Sector',
        'exchange': 'Exchange',
    }

    top = df[list(display_cols)].rename(columns=display_cols)

    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 160)
    pd.set_option('display.float_format', '{:.2f}'.format)

    print("\nTop 50 US stocks with highest drawdown in the last year:\n")
    print(top.to_string(index=False))


if __name__ == '__main__':
    main()
