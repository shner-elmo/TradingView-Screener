from __future__ import annotations

import requests

from tradingview_screener.query import Query
from tradingview_screener.constants import URL


DEFAULT_COLUMNS = ['name', 'close', 'volume', 'market_cap_basic']  # for the scanners


class Scanner:
    """
    This class contains some of the most common stock-screeners, to use them you just need to call
    `get_scanner_data()` on any given stock-screener.

    Examples:

    Get the full list of scanners:
    >>> from tradingview_screener import Scanner
    >>> Scanner.names()
    ['premarket_gainers',
     'premarket_losers',
     'premarket_most_active',
     'premarket_gappers',
     'postmarket_gainers',
     'postmarket_losers',
     'postmarket_most_active']

    Get the Pre-Market gainers
    >>> Scanner.premarket_gainers.get_scanner_data()
    (18060,
              ticker  name  ...  premarket_change_abs  premarket_volume
     0   NASDAQ:APLM  APLM  ...               0.72200          30551043
     1      OTC:RNVA  RNVA  ...               0.00005            200000
     2      OTC:OCLN  OCLN  ...               0.00690            220000
     3   NASDAQ:BKYI  BKYI  ...               0.09740           8826676
     4    NASDAQ:ICU   ICU  ...               0.28790           7527703
     ..          ...   ...  ...                   ...               ...
     45     OTC:BSEM  BSEM  ...               0.25000               200
     46     NYSE:SWI   SWI  ...               0.76000              5425
     47     NYSE:BPT   BPT  ...               0.45000               380
     48    NYSE:HOUS  HOUS  ...               0.39000               200
     49   NASDAQ:HCM   HCM  ...               1.40000              1950
     [50 rows x 8 columns])

    Get the most active tickers during the Post-Market session (highest volume)
    >>> Scanner.postmarket_most_active.get_scanner_data()
    (18060,
              ticker  name  ...  postmarket_change_abs  postmarket_volume
     0   NASDAQ:MCOM  MCOM  ...                -0.0001           12432509
     1   NASDAQ:AAPL  AAPL  ...                -0.2000           10364140
     2      AMEX:XLF   XLF  ...                -0.0100            8813170
     3      NYSE:BAC   BAC  ...                -0.0100            8741713
     4   NASDAQ:INTC  INTC  ...                -0.0600            8493758
     ..          ...   ...  ...                    ...                ...
     45      NYSE:PG    PG  ...                 0.2200            1895116
     46     NYSE:BMY   BMY  ...                -0.0700            1875806
     47  NASDAQ:TQQQ  TQQQ  ...                -0.0200            1870908
     48   NASDAQ:WBD   WBD  ...                -0.0003            1865705
     49    NYSE:SNAP  SNAP  ...                -0.0100            1852715
     [50 rows x 8 columns])

    """

    premarket_gainers = (
        Query()
        .select(*DEFAULT_COLUMNS, 'premarket_change', 'premarket_change_abs', 'premarket_volume')
        .order_by('premarket_change', ascending=False)
    )
    premarket_losers = (
        Query()
        .select(*DEFAULT_COLUMNS, 'premarket_change', 'premarket_change_abs', 'premarket_volume')
        .order_by('premarket_change', ascending=True)
    )
    premarket_most_active = (
        Query()
        .select(*DEFAULT_COLUMNS, 'premarket_change', 'premarket_change_abs', 'premarket_volume')
        .order_by('premarket_volume', ascending=False)
    )
    premarket_gappers = (
        Query()
        .select(*DEFAULT_COLUMNS, 'premarket_change', 'premarket_change_abs', 'premarket_volume')
        .order_by('premarket_gap', ascending=False)
    )

    postmarket_gainers = (
        Query()
        .select(*DEFAULT_COLUMNS, 'postmarket_change', 'postmarket_change_abs', 'postmarket_volume')
        .order_by('postmarket_change', ascending=False)
    )
    postmarket_losers = (
        Query()
        .select(*DEFAULT_COLUMNS, 'postmarket_change', 'postmarket_change_abs', 'postmarket_volume')
        .order_by('postmarket_change', ascending=True)
    )
    postmarket_most_active = (
        Query()
        .select(*DEFAULT_COLUMNS, 'postmarket_change', 'postmarket_change_abs', 'postmarket_volume')
        .order_by('postmarket_volume', ascending=False)
    )

    @classmethod
    def names(cls) -> list[str]:
        return [x for x in cls.__dict__.keys() if not x.startswith('_') and x != 'names']


def get_all_symbols(market: str = 'america') -> list[str]:
    """
    Get all the symbols of a given market.

    Examples:

    >>> from tradingview_screener import get_all_symbols
    >>> get_all_symbols()
    ['OTC:BMVVF',
     'OTC:BRQL',
     'NYSE:EFC/PA',
     'NASDAQ:NVCR',
     'NASDAQ:OMIC',
     ...

    >>> len(get_all_symbols())
    18060

    The default market is `america`, but you can change it with any market from
    `tradingview_screener.constants.MARKETS`:
    >>> get_all_symbols(market='switzerland')
    ['BX:UN01',
     'BX:XFNT',
     'BX:ZPDE',
     'BX:0QF',
     'BX:BSN',
     ...

    For instance, to get all the crypto tickers:
    >>> get_all_symbols(market='crypto')
    ['KRAKEN:KNCEUR',
     'TRADERJOE:WETHEWAVAX_FE15C2',
     'UNISWAP:DBIWETH_DEDF7B',
     'KUCOIN:DIABTC',
     'QUICKSWAP:WIXSWMATIC_F87B83.USD',
     ...

    >>> len(get_all_symbols(market='futures'))
    75205

    >>> len(get_all_symbols(market='bonds'))
    1090

    >>> len(get_all_symbols(market='germany'))
    13251

    >>> len(get_all_symbols(market='israel'))
    1034

    :param market: any market from `tradingview_screener.constants.MARKETS`, default 'america'
    :return: list of tickers
    """
    r = requests.get(URL.format(market=market))
    r.raise_for_status()
    data = r.json()['data']  # [{'s': 'NYSE:HKD', 'd': []}, {'s': 'NASDAQ:ALTY', 'd': []}...]

    return [dct['s'] for dct in data]
