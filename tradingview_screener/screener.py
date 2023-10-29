from __future__ import annotations

from enum import Enum

import requests
import pandas as pd

from tradingview_screener.constants import URL, HEADERS, DEFAULT_API_SETTINGS


class Scanner(dict, Enum):
    premarket_gainers = {'sortBy': 'premarket_change', 'sortOrder': 'desc'}
    premarket_losers = {'sortBy': 'premarket_change', 'sortOrder': 'asc'}
    premarket_most_active = {'sortBy': 'premarket_volume', 'sortOrder': 'desc'}
    premarket_gappers = {'sortBy': 'premarket_gap', 'sortOrder': 'desc'}

    postmarket_gainers = {'sortBy': 'postmarket_change', 'sortOrder': 'desc'}
    postmarket_losers = {'sortBy': 'postmarket_change', 'sortOrder': 'asc'}
    postmarket_most_active = {'sortBy': 'postmarket_volume', 'sortOrder': 'desc'}

    @classmethod
    def names(cls) -> list[str]:
        return [x.name for x in cls]

    def get_data(self, **kwargs) -> pd.DataFrame:
        cols = DEFAULT_API_SETTINGS['columns'].copy()
        cols.insert(
            1, self.value['sortBy']
        )  # insert the column that we are sorting by, right after the symbol column
        kwargs.setdefault('columns', cols)  # use `setdefault()` so the user can override this
        return get_scanner_data(sort=self.value, **kwargs)[1]


def get_scanner_data(**kwargs) -> tuple[int, pd.DataFrame]:
    """
    Get a dataframe with the scanner data directly from the API

    :param kwargs: kwargs to override fields in the `local_settings` dictionary
    :return: Pandas DataFrame
    """
    local_settings = DEFAULT_API_SETTINGS.copy()  # copy() to avoid modifying the global settings
    local_settings.update(**kwargs)

    r = requests.post(
        URL.format(market='america'),
        headers=HEADERS,
        json=local_settings,
        timeout=10,
    )

    if r.status_code >= 400:
        r.reason += f'\n Body: {r.text}\n'  # add the body to the
        r.raise_for_status()

    json_obj = r.json()
    rows_count = json_obj['totalCount']
    data = json_obj['data']

    if data is None:
        return rows_count, pd.DataFrame(columns=local_settings['columns'])
    return rows_count, pd.DataFrame(
        data=(row['d'] for row in data), columns=local_settings['columns']
    )


def get_all_symbols(market: str = 'america') -> list[str]:
    """
    Get all the symbols of a given market.

    Examples:

    >>> get_all_symbols()
    ['OTC:BMVVF',
     'OTC:BRQL',
     'NYSE:EFC/PA',
     'NASDAQ:NVCR',
     'NASDAQ:OMIC',
     ...

    >>> len(get_all_symbols())
    18060

    The default market of is `america`, but you can change it with any market from
    `tradingview_screener.constants.MARKETS`:
    >>> get_all_symbols(market='switzerland')
    ['BX:DLY',
     'BX:DP4A',
     'BX:1SQ',
     'BX:49G',
     ...

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
