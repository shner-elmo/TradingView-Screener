from __future__ import annotations

__all__ = ['Query', 'Column']

import pprint
from typing import TypedDict, Any, Literal

import requests
import pandas as pd

from tradingview_screener.constants import COLUMNS, MARKETS, HEADERS, URL


class FilterOperationDict(TypedDict):
    left: str
    operation: Literal[
        'greater',
        'egreater',
        'less',
        'eless',
        'equal',
        'nequal',
        'in_range',
        'not_in_range',
        'match',  # the same as: `LOWER(col) LIKE '%pattern%'`
        'crosses',
        'crosses_above',
        'crosses_below',
    ]
    right: Any


class SortByDict(TypedDict):
    sortBy: str
    sortOrder: Literal['asc', 'desc']


class QueryDict(TypedDict):
    """
    The fields that can be passed to the tradingview scan API
    """

    # TODO: test which optional ...
    markets: list[str]
    symbols: dict
    options: dict
    columns: list[str]
    filter: list[FilterOperationDict]
    sort: SortByDict
    range: list[int]  # a with two integers, i.e. `[0, 100]`


class Column:
    """
    A Column object represents a field in the tradingview stock screener,
    and it's used in SELECT queries and WHERE queries with the `Query` object.

    A `Column` supports all the comparison operations:
    `<`, `<=`, `>`, `>=`, `==`, `!=`, and also other methods like `between()`, `isin()`, etc.

    Examples:

    Some of the operations that you can do with `Column` objects:
    >>> Column('close') >= 2.5
    >>> Column('close').between(2.5, 15)
    >>> Column('high') > Column('VWAP')
    >>> Column('close').between(Column('EMA5'), Column('EMA20')
    >>> Column('type').isin(['stock', 'fund'])
    >>> Column('description').like('apple')  # the same as `description LIKE '%apple%'`
    """

    def __init__(self, name: str) -> None:
        """
        Create a column object from a given column name

        :param name: string, should be either a key or a value from the `COLUMNS` dictionary
        """
        # if `name` is a dictionary key: get its value. otherwise make sure that it's a
        # dictionary value.
        self.name = COLUMNS.get(name, name)

    # disable this method and do the column/field validation through the server
    # @classmethod
    # def from_unknown_name(cls, name: str) -> Column:
    #     """
    #     Create a column object from a column name that isn't in the `COLUMNS` dictionary
    #
    #     :param name: string, column name
    #     :return: Column
    #     """
    #     # close is just a temporary column, so it won't raise an error at `__init__`
    #     column = cls(name='close')
    #     column.name = name
    #     return column

    @staticmethod
    def _extract_value(obj) -> ...:
        if isinstance(obj, Column):
            return obj.name
        return obj

    def __gt__(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='greater', right=self._extract_value(other)
        )

    def __ge__(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='egreater', right=self._extract_value(other)
        )

    def __lt__(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='less', right=self._extract_value(other)
        )

    def __le__(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='eless', right=self._extract_value(other)
        )

    def __eq__(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='equal', right=self._extract_value(other)
        )

    def __ne__(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='nequal', right=self._extract_value(other)
        )

    def crosses(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='crosses', right=self._extract_value(other)
        )

    def crosses_above(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='crosses_above', right=self._extract_value(other)
        )

    def crosses_below(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='crosses_below', right=self._extract_value(other)
        )

    def between(self, left, right) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name,
            operation='in_range',
            right=[self._extract_value(left), self._extract_value(right)],
        )

    def not_between(self, left, right) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name,
            operation='not_in_range',
            right=[self._extract_value(left), self._extract_value(right)],
        )

    def isin(self, values) -> FilterOperationDict:
        return FilterOperationDict(left=self.name, operation='in_range', right=list(values))

    def like(self, other) -> FilterOperationDict:
        return FilterOperationDict(
            left=self.name, operation='match', right=self._extract_value(other)
        )

    def __repr__(self) -> str:
        return f'< Column({self.name!r}) >'


class Query:
    """
    This class allows you to perform SQL-like queries on the tradingview stock-screener.

    The `Query` object reppresents a query that can be made to the official tradingview API, and it
    stores all the data as JSON internally.

    Examples:

    To perform a simple query all you have to do is:
    >>> from tradingview_screener import Query
    >>> Query().get_scanner_data()
    (18060,
              ticker  name   close     volume  market_cap_basic
     0      AMEX:SPY   SPY  410.68  107367671               NaN
     1    NASDAQ:QQQ   QQQ  345.31   63475390               NaN
     2   NASDAQ:TSLA  TSLA  207.30   94879471      6.589904e+11
     3   NASDAQ:NVDA  NVDA  405.00   41677185      1.000350e+12
     4   NASDAQ:AMZN  AMZN  127.74  125309313      1.310658e+12
     ..          ...   ...     ...        ...               ...
     45     NYSE:UNH   UNH  524.66    2585616      4.859952e+11
     46  NASDAQ:DXCM  DXCM   89.29   14954605      3.449933e+10
     47      NYSE:MA    MA  364.08    3624883      3.429080e+11
     48    NYSE:ABBV  ABBV  138.93    9427212      2.452179e+11
     49     AMEX:XLK   XLK  161.12    8115780               NaN
     [50 rows x 5 columns])

    The `get_scanner_data()` method will return a tuple with the first element being the number of
    records that were found (like a `COUNT(*)`), and the second element contains the data that was
    found as a DataFrame.

    ---

    By default, the `Query` will select the columns: `name`, `close`, `volume`, `market_cap_basic`,
    but you override that
    >>> (Query()
    ...  .select('open', 'high', 'low', 'VWAP', 'MACD.macd', 'RSI', 'Price to Earnings Ratio (TTM)')
    ...  .get_scanner_data())
    (18060,
              ticker    open     high  ...  MACD.macd        RSI  price_earnings_ttm
     0      AMEX:SPY  414.19  414.600  ...  -5.397135  29.113396                 NaN
     1    NASDAQ:QQQ  346.43  348.840  ...  -4.321482  34.335449                 NaN
     2   NASDAQ:TSLA  210.60  212.410  ... -12.224250  28.777229           66.752536
     3   NASDAQ:NVDA  411.30  412.060  ...  -8.738986  37.845668           97.835540
     4   NASDAQ:AMZN  126.20  130.020  ...  -2.025378  48.665666           66.697995
     ..          ...     ...      ...  ...        ...        ...                 ...
     45     NYSE:UNH  525.99  527.740  ...   6.448129  54.614775           22.770713
     46  NASDAQ:DXCM   92.73   92.988  ...  -2.376942  52.908093           98.914368
     47      NYSE:MA  366.49  368.285  ...  -7.496065  22.614078           31.711800
     48    NYSE:ABBV  138.77  143.000  ...  -1.708497  27.117232           37.960054
     49     AMEX:XLK  161.17  162.750  ...  -1.520828  36.868658                 NaN
     [50 rows x 8 columns])

    You can find the 250+ columns available in `tradingview_screener.constants.COLUMNS`.

    Now let's do some queries using the `WHERE` statement, select all the stocks that the `close` is
    bigger or equal than 350
    >>> (Query()
    ...  .select('close', 'volume', '52 Week High')
    ...  .where(Column('close') >= 350)
    ...  .get_scanner_data())
    (159,
              ticker      close     volume  price_52_week_high
     0      AMEX:SPY     410.68  107367671              459.44
     1   NASDAQ:NVDA     405.00   41677185              502.66
     2    NYSE:BRK.A  503375.05       7910           566569.97
     3      AMEX:IVV     412.55    5604525              461.88
     4      AMEX:VOO     377.32    5638752              422.15
     ..          ...        ...        ...                 ...
     45  NASDAQ:EQIX     710.39     338549              821.63
     46     NYSE:MCK     448.03     527406              465.90
     47     NYSE:MTD     976.25     241733             1615.97
     48  NASDAQ:CTAS     496.41     464631              525.37
     49   NASDAQ:ROP     475.57     450141              508.90
     [50 rows x 4 columns])

    You can even use other columns in these kind of operations
    >>> (Query()
    ...  .select('close', 'VWAP')
    ...  .where(Column('close') >= Column('VWAP'))
    ...  .get_scanner_data())
    (9044,
               ticker   close        VWAP
     0    NASDAQ:AAPL  168.22  168.003333
     1    NASDAQ:META  296.73  296.336667
     2   NASDAQ:GOOGL  122.17  121.895233
     3     NASDAQ:AMD   96.43   96.123333
     4    NASDAQ:GOOG  123.40  123.100000
     ..           ...     ...         ...
     45       NYSE:GD  238.25  238.043333
     46     NYSE:GOLD   16.33   16.196667
     47      AMEX:SLV   21.18   21.041667
     48      AMEX:VXX   27.08   26.553333
     49      NYSE:SLB   55.83   55.676667
     [50 rows x 3 columns])

    Let's find all the stocks that the price is between the EMA 5 and 20, and the type is a stock
    or fund
    >>> (Query()
    ...  .select('close', 'volume', 'EMA5', 'EMA20', 'type')
    ...  .where(
    ...     Column('close').between(Column('EMA5'), Column('EMA20')),
    ...     Column('type').isin(['stock', 'fund'])
    ...  )
    ...  .get_scanner_data())
    (1730,
              ticker   close     volume        EMA5       EMA20   type
     0   NASDAQ:AMZN  127.74  125309313  125.033517  127.795142  stock
     1      AMEX:HYG   72.36   35621800   72.340776   72.671058   fund
     2      AMEX:LQD   99.61   21362859   99.554272  100.346388   fund
     3    NASDAQ:IEF   90.08   11628236   89.856804   90.391503   fund
     4      NYSE:SYK  261.91    3783608  261.775130  266.343290  stock
     ..          ...     ...        ...         ...         ...    ...
     45     NYSE:EMN   72.58    1562328   71.088034   72.835394  stock
     46     NYSE:KIM   16.87    6609420   16.858920   17.096582   fund
     47  NASDAQ:COLM   71.34    1516675   71.073116   71.658864  stock
     48     NYSE:AOS   67.81    1586796   67.561619   67.903168  stock
     49  NASDAQ:IGIB   47.81    2073538   47.761338   48.026795   fund
     [50 rows x 6 columns])

    There are also the `ORDER BY`, `OFFSET`, and `LIMIT` statements.
    Let's select all the tickers with a market cap between 1M and 50M, that have a relative volume
    bigger than 1.2, and that the MACD is positive
    >>> (Query()
    ...  .select('name', 'close', 'volume', 'relative_volume_10d_calc')
    ...  .where(
    ...      Column('market_cap_basic').between(1_000_000, 50_000_000),
    ...      Column('relative_volume_10d_calc') > 1.2,
    ...      Column('MACD.macd') >= Column('MACD.signal')
    ...  )
    ...  .order_by('volume', ascending=False)
    ...  .offset(5)
    ...  .limit(15)
    ...  .get_scanner_data())
    (393,
             ticker  name   close    volume  relative_volume_10d_calc
     0     OTC:YCRM  YCRM  0.0120  19626514                  1.887942
     1     OTC:PLPL  PLPL  0.0002  17959914                  3.026059
     2  NASDAQ:ABVC  ABVC  1.3800  16295824                  1.967505
     3     OTC:TLSS  TLSS  0.0009  15671157                  1.877976
     4     OTC:GVSI  GVSI  0.0128  14609774                  2.640792
     5     OTC:IGEX  IGEX  0.0012  14285592                  1.274861
     6     OTC:EEGI  EEGI  0.0004  12094000                  2.224749
     7   NASDAQ:GLG   GLG  0.0591   9811974                  1.990526
     8  NASDAQ:TCRT  TCRT  0.0890   8262894                  2.630553
     9     OTC:INKW  INKW  0.0027   7196404                  1.497134)

    To avoid rewriting the same query again and again, you can save the query to a variable and
    just call `get_scanner_data()` again and again to get the latest data:
    >>> top_50_bullish = (Query()
    ...  .select('name', 'close', 'volume', 'relative_volume_10d_calc')
    ...  .where(
    ...      Column('market_cap_basic').between(1_000_000, 50_000_000),
    ...      Column('relative_volume_10d_calc') > 1.2,
    ...      Column('MACD.macd') >= Column('MACD.signal')
    ...  )
    ...  .order_by('volume', ascending=False)
    ...  .limit(50))
    >>> top_50_bullish.get_scanner_data()
    (393,
              ticker   name     close     volume  relative_volume_10d_calc
     0      OTC:BEGI   BEGI  0.001050  127874055                  3.349924
     1      OTC:HCMC   HCMC  0.000100  126992562                  1.206231
     2      OTC:HEMP   HEMP  0.000150  101382713                  1.775458
     3      OTC:SONG   SONG  0.000800   92640779                  1.805721
     4      OTC:APRU   APRU  0.001575   38104499                 29.028958
     ..          ...    ...       ...        ...                       ...
     45    OTC:BSHPF  BSHPF  0.001000     525000                  1.280899
     46     OTC:GRHI   GRHI  0.033000     507266                  1.845738
     47    OTC:OMGGF  OMGGF  0.035300     505000                  4.290059
     48  NASDAQ:GBNH   GBNH  0.273000     500412                  9.076764
     49    OTC:CLRMF  CLRMF  0.032500     496049                 17.560935
     [50 rows x 5 columns])
    """

    def __init__(self) -> None:
        # noinspection PyTypeChecker
        self.query: QueryDict = {
            'markets': ['america'],
            'symbols': {'query': {'types': []}, 'tickers': []},
            'options': {'lang': 'en'},
            'columns': ['name', 'close', 'volume', 'market_cap_basic'],
            # 'filter': ...,
            'sort': {'sortBy': 'Value.Traded', 'sortOrder': 'desc'},
            'range': [0, 50],
        }
        self.url = 'https://scanner.tradingview.com/america/scan'

    def set_markets(self, *markets: str) -> Query:
        """
        This method allows you to select the market/s which you want to query.

        By default, the screener will only scan US equities, but you can change it to scan any
        or even multiple markets, that includes a list of 67 countries, and also the following 
        commodities: `bonds`, `cfd`, `coin`, `crypto`, `economics2`, `euronext`, `forex`,
        `futures`, `options`.

        You may choose any value from `tradingview_screener.constants.MARKETS`.

        Examples:

        By default, the screener will search the `america` market
        >>> default_columns = ['close', 'market', 'country', 'currency']
        >>> Query().select(*default_columns).get_scanner_data()
        (17898,
                  ticker     close   market        country currency
         0      AMEX:SPY  419.9900  america  United States      USD
         1   NASDAQ:TSLA  201.7201  america  United States      USD
         2   NASDAQ:NVDA  416.3800  america  United States      USD
         3    NASDAQ:AMD  106.4499  america  United States      USD
         4    NASDAQ:QQQ  353.4000  america  United States      USD
         ..          ...       ...      ...            ...      ...
         45  NASDAQ:ADBE  538.0000  america  United States      USD
         46      NYSE:BA  188.9000  america  United States      USD
         47  NASDAQ:SBUX   90.9100  america  United States      USD
         48     NYSE:HUM  500.6350  america  United States      USD
         49     NYSE:CAT  227.3400  america  United States      USD
         [50 rows x 5 columns])

        But you can change it (note the difference between `market` and `country`)
        >>> (Query()
        ...  .select(*default_columns)
        ...  .set_markets('italy')
        ...  .get_scanner_data())
        (2346,
                ticker    close market      country currency
         0     MIL:UCG  23.9150  italy        Italy      EUR
         1     MIL:ISP   2.4910  italy        Italy      EUR
         2   MIL:STLAM  17.9420  italy  Netherlands      EUR
         3    MIL:ENEL   6.0330  italy        Italy      EUR
         4     MIL:ENI  15.4800  italy        Italy      EUR
         ..        ...      ...    ...          ...      ...
         45    MIL:UNI   5.1440  italy        Italy      EUR
         46   MIL:3OIS   0.4311  italy      Ireland      EUR
         47   MIL:3SIL  35.2300  italy      Ireland      EUR
         48   MIL:IWDE  69.1300  italy      Ireland      EUR
         49   MIL:QQQS  19.2840  italy      Ireland      EUR
         [50 rows x 5 columns])

        You can also select multiple markets
        >>> (Query()
        ...  .select(*default_columns)
        ...  .set_markets('america', 'israel', 'hongkong', 'switzerland')
        ...  .get_scanner_data())
        (23964,
                   ticker      close    market        country currency
         0       AMEX:SPY   420.1617   america  United States      USD
         1    NASDAQ:TSLA   201.2000   america  United States      USD
         2    NASDAQ:NVDA   416.7825   america  United States      USD
         3     NASDAQ:AMD   106.6600   america  United States      USD
         4     NASDAQ:QQQ   353.7985   america  United States      USD
         ..           ...        ...       ...            ...      ...
         45  NASDAQ:GOOGL   124.9200   america  United States      USD
         46     HKEX:1211   233.2000  hongkong          China      HKD
         47     TASE:ALHE  1995.0000    israel         Israel      ILA
         48      AMEX:BIL    91.4398   america  United States      USD
         49   NASDAQ:GOOG   126.1500   america  United States      USD
         [50 rows x 5 columns])

        You may also select different financial instruments
        >>> (Query()
        ...  .select('close', 'market')
        ...  .set_markets('cfd', 'crypto', 'futures', 'options')
        ...  .get_scanner_data())
        (118076,
                                 ticker  ...   market
         0          UNISWAP3ETH:WETHVGT  ...   crypto
         1   UNISWAP3POLYGON:BONKWMATIC  ...   crypto
         2   UNISWAP3ARBITRUM:WETHTROVE  ...   crypto
         3          UNISWAP3ETH:USDTBRD  ...   crypto
         4         UNISWAP3ETH:WBTCAUSD  ...   crypto
         ..                         ...  ...      ...
         45               NSE:IDEAF2024  ...  futures
         46         NSE:INDUSTOWERX2023  ...  futures
         47            NSE:INDUSTOWER1!  ...  futures
         48                  BIST:XU100  ...      cfd
         49              BYBIT:BTCUSD.P  ...   crypto
         [50 rows x 3 columns])

        To select all the avaialble markets you can do this trick
        >>> from tradingview_screener.constants import MARKETS
        >>> len(MARKETS)
        76
        >>> (Query()
        ...  .select('close', 'market')
        ...  .set_markets(*MARKETS)
        ...  .get_scanner_data())  # notice how many records we find: over 240k
        (241514,
                                 ticker  ...   market
         0          UNISWAP3ETH:WETHVGT  ...   crypto
         1   UNISWAP3POLYGON:BONKWMATIC  ...   crypto
         2   UNISWAP3ARBITRUM:WETHTROVE  ...   crypto
         3          UNISWAP3ETH:USDTBRD  ...   crypto
         4         UNISWAP3ETH:WBTCAUSD  ...   crypto
         ..                         ...  ...      ...
         45               NSE:IDEAF2024  ...  futures
         46            NSE:INDUSTOWER1!  ...  futures
         47         NSE:INDUSTOWERX2023  ...  futures
         48                  BIST:XU100  ...      cfd
         49              BYBIT:BTCUSD.P  ...   crypto

         [50 rows x 3 columns])

        :param markets: one or more markets from `tradingview_screener.constants.MARKETS`
        :return: Self
        """
        if len(markets) == 1:
            market = markets[0]
            assert market in MARKETS

            self.url = URL.format(market=market)
            self.query['markets'] = [market]

        elif len(markets) >= 1:
            for m in markets:
                assert m in MARKETS

            self.url = URL.format(market='global')
            self.query['markets'] = list(markets)

        return self

    def set_tickers(self, *tickers: str) -> Query:
        """
        Set the tickers you wish to receive information on.

        Examples:

        >>> Query().limit(5).get_scanner_data()
        (17879,
                 ticker  name   close     volume  market_cap_basic
         0  NASDAQ:TSLA  TSLA  248.50  118559595      7.887376e+11
         1     AMEX:SPY   SPY  445.52   62066984               NaN
         2  NASDAQ:NVDA  NVDA  455.72   47389801      1.125628e+12
         3   NASDAQ:QQQ   QQQ  372.58   35846281               NaN
         4  NASDAQ:AAPL  AAPL  178.18   65600673      2.785707e+12)

        >>> q = Query().select('name', 'market', 'close', 'volume', 'VWAP', 'MACD.macd')
        >>> q.set_tickers('NASDAQ:TSLA').get_scanner_data()
        (2,
                 ticker  name   market   close     volume        VWAP  MACD.macd
         0  NASDAQ:TSLA  TSLA  america  248.50  118559595  250.563333   0.730376
         1  NASDAQ:NVDA  NVDA  america  455.72   47389801  458.163333   7.927189)

        >>> q.set_tickers('NYSE:GME', 'AMEX:SPY', 'MIL:RACE', 'HOSE:VIX').get_scanner_data()
        (4,
              ticker  name   market     close    volume          VWAP    MACD.macd
         0  HOSE:VIX   VIX  vietnam  19800.00  26292400  19883.333333  1291.359459
         1  AMEX:SPY   SPY  america    445.52  62066984    445.720000     0.484263
         2  NYSE:GME   GME  america     17.71   4693902     17.853333    -0.660342
         3  MIL:RACE  RACE    italy    279.30    246547    279.033327    -1.398701)

        :param tickers: One or more tickers, syntax: `exchange:symbol`
        :return: Self
        """
        # no need to select the market if we specify the symbol we want
        # noinspection PyTypedDict
        self.query.pop('markets', None)

        self.query['symbols'] = {'tickers': list(tickers)}
        self.url = 'https://scanner.tradingview.com/global/scan'
        return self

    def select(self, *columns: Column | str) -> Query:
        self.query['columns'] = [
            col.name if isinstance(col, Column) else Column(col).name for col in columns
        ]
        return self

    def where(self, *expressions: FilterOperationDict) -> Query:
        self.query['filter'] = list(expressions)  # convert tuple[dict] -> list[dict]
        return self

    def order_by(self, column: Column | str, ascending: bool = True) -> Query:
        column = column.name if isinstance(column, Column) else Column(column).name
        sort_order = 'asc' if ascending else 'desc'
        # noinspection PyTypeChecker
        self.query['sort'] = SortByDict(sortBy=column, sortOrder=sort_order)
        return self

    def offset(self, offset: int) -> Query:
        self.query['range'][0] = offset
        return self

    def limit(self, limit: int) -> Query:
        self.query['range'][1] = limit
        return self

    # def set_options(self, options) -> None:
    #     raise NotImplementedError

    def get_scanner_data(self, **kwargs) -> tuple[int, pd.DataFrame]:
        """
        Perform a POST web-request and return the data from the API as a DataFrame.

        Note that you can pass extra keyword-arguments that will be forwarded to `requests.post()`,
        this can be very useful if you want to pass your own headers/cookies.

        (if you have paid for a live data add-on with TradingView, you want to pass your own
        headers and cookies to access that real-time data)

        :param kwargs: kwargs to pass to `requests.post()`
        :return: a tuple consisting of: (total_count, dataframe)
        """
        kwargs.setdefault('headers', HEADERS)
        kwargs.setdefault('timeout', 20)
        r = requests.post(self.url, json=self.query, **kwargs)

        if r.status_code >= 400:
            # add the body to the error message for debugging purposes
            r.reason += f'\n Body: {r.text}\n'
            r.raise_for_status()

        json_obj = r.json()
        rows_count = json_obj['totalCount']
        data = json_obj['data']

        df = pd.DataFrame(
            data=([row['s'], *row['d']] for row in data),
            columns=['ticker', *self.query.get('columns', ())],
        )
        return rows_count, df

    def copy(self) -> Query:
        new = Query()
        new.query = self.query.copy()
        return new

    def __repr__(self) -> str:
        return f'< {pprint.pformat(self.query)} >'

    def __eq__(self, other) -> bool:
        return isinstance(other, Query) and self.query == other.query
