from __future__ import annotations

from enum import Enum
from typing import Iterable

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


def get_all_symbols(
    exchanges: Iterable[str] | None = None,
    market: str = 'america',
) -> list[str]:
    """
    Get a list with all the symbols filtered by a given exchange.

    Valid exchanges: {'AMEX', 'OTC', 'NYSE', 'NASDAQ'}

    :param exchanges: a set which contains the exchanges you want to keep (all the rest will be ignored)
    :param market: ...
    :return: list of symbols
    """
    exchanges = {x.upper() for x in exchanges}
    r = requests.get(URL.format(market=market))
    data = r.json()['data']  # [{'s': 'NYSE:HKD', 'd': []}, {'s': 'NASDAQ:ALTY', 'd': []}...]

    symbols = []
    for dct in data:
        exchange, symbol = dct['s'].split(':')
        if exchange in exchanges:
            symbols.append(symbol)
    return symbols
