from __future__ import annotations

from typing import TypedDict, Optional, Any, Literal

import pandas as pd

from tradingview_screener.screener import get_scanner_data, COLUMNS


class FilterOperationDict(TypedDict):
    left: str
    operation: Literal['greater', 'egreater', 'less', 'eless', 'equal', 'nequal', 'in_range', 'not_in_range']
    right: Any


class QueryDict(TypedDict):
    """
    The fields that can be passed to the tradingview scan API
    """
    # TODO: test which optional ...
    markets: Optional[list[str]]
    symbols: Optional[dict]
    options: Optional[dict]
    columns: Optional[list[str]]
    filter: Optional[list[FilterOperationDict]]
    sort: Optional[dict[str, str]]
    range: Optional[tuple[int, int]]


COLUMN_VALUES = set(COLUMNS.values())


class Column:
    """
    A Column object represents a field in the tradingview stock screener,
    and it can be used in SELECT queries and FILTER queries with the `Query` object.
    """
    def __init__(self, name: str) -> None:
        """
        Create a column object from a given column name

        :param name: string, should be either a key or a value from the `COLUMNS` dictionary
        """
        # if `name` is a dictionary key: get its value. otherwise make sure that it's a dictionary value
        if name in COLUMNS.keys():
            self.name = COLUMNS[name]
        elif name in COLUMN_VALUES:
            self.name = name
        else:
            raise ValueError(f'{name!r} is not a valid column. Must be key/value in the `COLUMNS` dictionary.')

    @classmethod
    def from_unknown_name(cls, name: str) -> Column:
        """
        Create a column object from a column name that isn't in the `COLUMNS` dictionary

        :param name: string, column name
        :return: Column
        """
        column = cls(name='close')  # close is just a temporary column, so it won't raise an error at `__init__`
        column.name = name
        return column

    def __gt__(self, other) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='greater', right=other)

    def __ge__(self, other) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='egreater', right=other)

    def __lt__(self, other) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='less', right=other)

    def __le__(self, other) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='eless', right=other)

    def __eq__(self, other) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='equal', right=other)

    def __ne__(self, other) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='nequal', right=other)

    def between(self, left, right) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='in_range', right=[left, right])

    def not_between(self, left, right) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='not_in_range', right=[left, right])

    def isin(self, values) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='in_range', right=list(values))


class Query:
    """
    This class allows you to perform SQL-like queries on the tradingview stock-screener.


    """
    def __init__(self) -> None:
        self.query: dict = {
            'markets': ['america'],
            'symbols': {'query': {'types': []}, 'tickers': []},
            'options': {'lang': 'en'},
            # 'columns': ...,
            # 'filter': ...,
            # 'sort': ...,
            # 'range': ...,
        }

    def select(self, *columns: Column | str) -> Query:
        self.query['columns'] = [col.name if isinstance(col, Column) else Column(col).name for col in columns]
        return self

    def where(self, *expressions: FilterOperationDict) -> Query:
        self.query['filter'] = list(expressions)  # convert tuple[dict] -> list[dict]
        return self

    def order_by(self, column: Column | str, ascending: bool = True) -> Query:
        column = column.name if isinstance(column, Column) else Column(column).name
        ascending = 'asc' if ascending else 'desc'
        self.query['sort'] = {'sortBy': column, 'sortOrder': ascending}
        return self

    def offset(self, offset: int) -> Query:
        limit = self.query.get('range', [0, 0])[1]
        self.query['range'] = (offset, limit)
        return self

    def limit(self, limit: int) -> Query:
        offset = self.query.get('range', [0, 0])[0]
        self.query['range'] = (offset, limit)
        return self

    # def set_options(self, options) -> None:
    #     raise NotImplementedError

    def get_scanner_data(self) -> tuple[int, pd.DataFrame]:
        return get_scanner_data(**self.query)

    def __repr__(self) -> str:
        return f'{__class__.__name__}({self.query!r})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Query) and self.query == other.query
