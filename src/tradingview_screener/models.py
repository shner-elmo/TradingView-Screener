from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Any, Literal, NotRequired


class FilterOperationDict(TypedDict):
    left: str
    operation: Literal[
        'greater',
        'egreater',
        'less',
        'eless',
        'equal',
        'nequal',
        'in_range',  # equivalent to SQL `BETWEEN` or `IN (...)`
        'not_in_range',
        'empty',
        'nempty',
        'crosses',
        'crosses_above',
        'crosses_below',
        'match',  # the same as: `LOWER(col) LIKE '%pattern%'`
        'nmatch',  # not match
        # simple match, there is no method for this operation as of right now, because it does
        # the same thing as `match`
        'smatch',
        'has',  # set must contain one of the values
        'has_none_of',  # set must NOT contain ANY of the values
        'above%',
        'below%',
        'in_range%',
        'not_in_range%',
        'in_day_range',
        'in_week_range',
        'in_month_range',
    ]
    right: Any  # its optional when the operation is `empty` or `nempty`


class SortByDict(TypedDict):
    sortBy: str
    sortOrder: Literal['asc', 'desc']
    nullsFirst: NotRequired[bool]


class SymbolsDict(TypedDict, total=False):
    query: dict[Literal['types'], list[str]]
    tickers: list[str]
    symbolset: list[str]
    watchlist: dict[Literal['id'], int]
    groups: list[dict[Literal['type', 'values'], str]]
    # for example [{'type': 'index', 'values': ['DJ:DJU']}]


class ExpressionDict(TypedDict):
    expression: FilterOperationDict


class OperationComparisonDict(TypedDict):
    operator: Literal['and', 'or']
    operands: list[OperationDict | ExpressionDict]


class OperationDict(TypedDict):
    operation: OperationComparisonDict


class QueryDict(TypedDict, total=False):
    """
    The fields that can be passed to the tradingview scan API
    """

    markets: list[str]
    symbols: SymbolsDict
    options: dict[str, Any]  # example: `{"options": {"lang": "en"}}`
    columns: list[str]
    filter: list[FilterOperationDict]
    filter2: OperationComparisonDict
    sort: SortByDict
    range: list[int]  # list with two integers, i.e. `[0, 100]`
    ignore_unknown_fields: bool  # default false
    preset: Literal['index_components_market_pages', 'pre-market-gainers']  # there are many
    # other presets (these are just some a examples)
    price_conversion: dict[Literal['to_symbol'], bool] | dict[
        Literal['to_currency'], str  # this string should be the currency in lower-case
    ]


class ScreenerRowDict(TypedDict):
    s: str  # symbol (NASDAQ:AAPL)
    d: list  # data, list of values


class ScreenerDict(TypedDict):
    totalCount: int
    data: list[ScreenerRowDict]
