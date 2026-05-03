"""
US Stock Drawdown Screener

Finds US stocks with the highest drawdown from their 52-week high.
Requires a TradingView session cookie.

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

    print("Fetching US stocks from TradingView...")
    count, df = (
        Query()
        .select(
            'name',
            'close',
            'price_52_week_high',
            'price_52_week_low',
            'market_cap_basic',
            'volume',
            'sector',
            'exchange',
        )
        .where(
            col('market_cap_basic') > 100_000_000,   # >$100M market cap
            col('typespecs').has(['common']),           # common shares only
            col('exchange').not_in(['OTC']),            # exclude OTC
            col('price_52_week_high').not_empty(),
            col('close').not_empty(),
        )
        .set_markets('america')
        .limit(3000)
        .get_scanner_data(**(dict(cookies=cookies) if cookies else {}))
    )

    print(f"Total US stocks scanned: {count:,}")

    df['drawdown_pct'] = (
        (df['price_52_week_high'] - df['close']) / df['price_52_week_high'] * 100
    )
    df['market_cap_B'] = df['market_cap_basic'] / 1e9

    df_sorted = df.sort_values('drawdown_pct', ascending=False)

    return df_sorted


def main():
    session_id = (
        sys.argv[1] if len(sys.argv) > 1 else os.environ.get('TRADINGVIEW_SESSION')
    )

    df = run_screener(session_id)

    top = df[
        ['name', 'close', 'price_52_week_high', 'drawdown_pct', 'market_cap_B', 'sector', 'exchange']
    ].head(50)

    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 120)
    pd.set_option('display.float_format', '{:.2f}'.format)

    print("\nTop 50 US stocks with highest drawdown from 52-week high:\n")
    print(
        top.rename(columns={
            'name': 'Ticker',
            'close': 'Price',
            'price_52_week_high': '52W High',
            'drawdown_pct': 'Drawdown %',
            'market_cap_B': 'Mkt Cap ($B)',
            'sector': 'Sector',
            'exchange': 'Exchange',
        }).to_string(index=False)
    )


if __name__ == '__main__':
    main()
