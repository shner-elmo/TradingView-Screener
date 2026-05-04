"""
Drawdown screener: finds US stocks trading significantly below their 52-week high.

Criteria:
- Large-cap US stocks (market cap >= $2B)
- Currently >= 20% below their 52-week high
- Sorted by drawdown magnitude (largest first)
"""
from __future__ import annotations

import sys

sys.path.insert(0, 'src')

from tradingview_screener import Query
from tradingview_screener.column import Column


def run_drawdown_screener(min_drawdown_pct: float = 20.0, min_market_cap: float = 2e9, limit: int = 50):
    """
    Screen for stocks with a significant drawdown from their 52-week high.

    :param min_drawdown_pct: Minimum drawdown percentage from 52-week high (default 20%).
    :param min_market_cap: Minimum market cap in USD (default $2B).
    :param limit: Max number of results to return.
    """
    # below_pct(col, x) => close < col * x
    # 20% drawdown => close < 52wk_high * 0.80
    pct_threshold = 1.0 - (min_drawdown_pct / 100.0)

    count, df = (
        Query()
        .select('name', 'close', 'price_52_week_high', 'price_52_week_low', 'market_cap_basic', 'volume', 'sector')
        .where(
            Column('close').below_pct('price_52_week_high', pct_threshold),
            Column('market_cap_basic') >= min_market_cap,
            Column('price_52_week_high').not_empty(),
        )
        .order_by('market_cap_basic', ascending=False)
        .limit(limit)
        .get_scanner_data()
    )

    if df.empty:
        print('No results found.')
        return df

    df['drawdown_pct'] = ((df['close'] - df['price_52_week_high']) / df['price_52_week_high'] * 100).round(2)
    df['market_cap_B'] = (df['market_cap_basic'] / 1e9).round(2)

    display_cols = ['ticker', 'name', 'close', 'price_52_week_high', 'drawdown_pct', 'market_cap_B', 'sector']
    result = df[display_cols].sort_values('drawdown_pct')

    print(f'Total stocks matching criteria: {count}')
    print(f'Showing top {len(result)} by market cap (>= ${min_market_cap/1e9:.0f}B, drawdown >= {min_drawdown_pct:.0f}%)\n')
    print(result.to_string(index=False))
    return result


if __name__ == '__main__':
    run_drawdown_screener(min_drawdown_pct=20.0, min_market_cap=2_000_000_000, limit=50)
