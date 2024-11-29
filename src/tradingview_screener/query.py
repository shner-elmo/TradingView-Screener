from __future__ import annotations

__all__ = ['And', 'Or', 'Query']

import pprint
from typing import TYPE_CHECKING

import requests

from tradingview_screener.column import Column

if TYPE_CHECKING:
    import pandas as pd
    from typing import Literal, Any
    from typing_extensions import Self
    from tradingview_screener.models import (
        QueryDict,
        SortByDict,
        ScreenerDict,
        FilterOperationDict,
        OperationDict,
    )


DEFAULT_RANGE = [0, 50]
URL = 'https://scanner.tradingview.com/{market}/scan'
HEADERS = {
    'authority': 'scanner.tradingview.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'accept': 'text/plain, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    'Chrome/98.0.4758.102 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://www.tradingview.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.tradingview.com/',
    'accept-language': 'en-US,en;q=0.9,it;q=0.8',
}


def _impl_and_or_chaining(
    expressions: tuple[FilterOperationDict | OperationDict, ...], operator: Literal['and', 'or']
) -> OperationDict:
    # we want to wrap all the `FilterOperationDict` expressions with `{'expression': expr}`,
    # to know if it's an instance of `FilterOperationDict` we simply check if it has the `left` key,
    # which no other TypedDict has.
    lst = []
    for expr in expressions:
        if 'left' in expr:  # if isinstance(expr, FilterOperationDict): ...
            lst.append({'expression': expr})
        else:
            lst.append(expr)
    return {'operation': {'operator': operator, 'operands': lst}}


def And(*expressions: FilterOperationDict | OperationDict) -> OperationDict:
    return _impl_and_or_chaining(expressions, operator='and')


def Or(*expressions: FilterOperationDict | OperationDict) -> OperationDict:
    return _impl_and_or_chaining(expressions, operator='or')


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
            'range': DEFAULT_RANGE.copy(),
        }
        self.url = 'https://scanner.tradingview.com/america/scan'

    def select(self, *columns: Column | str) -> Self:
        self.query['columns'] = [
            col.name if isinstance(col, Column) else Column(col).name for col in columns
        ]
        return self

    def where(self, *expressions: FilterOperationDict) -> Self:
        """
        Filter screener (expressions are joined with the AND operator)
        """
        self.query['filter'] = list(expressions)  # convert tuple[dict] -> list[dict]
        return self

    def where2(self, operation: OperationDict) -> Self:
        """
        Filter screener using AND/OR operators (nested expressions also allowed)

        Rules:
        1. The argument passed to `where2()` **must** be wrapped in `And()` or `Or()`.
        2. `And()` and `Or()` can accept one or more conditions as arguments.
        3. Conditions can be simple (e.g., `Column('field') == 'value'`) or complex, allowing nesting of `And()` and `Or()` to create intricate logical filters.
        4. Unlike the `where()` method, which only supports chaining conditions with the `AND` operator, `where2()` allows mixing and nesting of `AND` and `OR` operators.

        Examples:

        1. **Combining conditions with `OR` and nested `AND`:**
           ```python
           Query()
           .select('type', 'typespecs')
           .where2(
               Or(
                   And(Column('type') == 'stock', Column('typespecs').has(['common', 'preferred'])),
                   And(Column('type') == 'fund', Column('typespecs').has_none_of(['etf'])),
                   Column('type') == 'dr',
               )
           )
           ```

           This query filters entities where:
           - The `type` is `'stock'` and `typespecs` contains `'common'` or `'preferred'`, **OR**
           - The `type` is `'fund'` and `typespecs` does not contain `'etf'`, **OR**
           - The `type` is `'dr'`.

        2. **Mixing conditions with `OR`:**
           ```python
           Query().where2(
               Or(
                   And(col('type') == 'stock', col('typespecs').has(['common'])),
                   col('type') == 'fund',
               )
           )
           ```
           This query filters entities where:
           - The `type` is `'stock'` and `typespecs` contains `'common'`, **OR**
           - The `type` is `'fund'`.

        3. **Combining conditions with `AND`:**
           ```python
           Query()
           .set_markets('crypto')
           .where2(
               And(
                   col('exchange').isin(['UNISWAP3POLYGON', 'VERSEETH', 'a', 'fffffffff']),
                   col('currency_id') == 'USD',
               )
           )
           ```
           This query filters entities in the `'crypto'` market where:
           - The `exchange` is one of `'UNISWAP3POLYGON', 'VERSEETH', 'a', 'fffffffff'`, **AND**
           - The `currency_id` is `'USD'`.
        """
        self.query['filter2'] = operation['operation']
        return self

    def order_by(
        self, column: Column | str, ascending: bool = True, nulls_first: bool = False
    ) -> Self:
        """
        Applies sorting to the query results based on the specified column.

        Examples:

        >>> Query().order_by('volume', ascending=False)  # sort descending
        >>> Query().order_by('close', ascending=True)
        >>> Query().order_by('dividends_yield_current', ascending=False, nulls_first=False)

        :param column: Either a `Column` object or a string with the column name.
        :param ascending: Set to True for ascending order (default), or False for descending.
        :param nulls_first: If True, places `None` values at the beginning of the results. Defaults
        to False.
        :return: The updated query object.
        """
        dct: SortByDict = {
            'sortBy': column.name if isinstance(column, Column) else column,
            'sortOrder': 'asc' if ascending else 'desc',
            'nullsFirst': nulls_first,
        }
        self.query['sort'] = dct
        return self

    def limit(self, limit: int) -> Self:
        self.query.setdefault('range', DEFAULT_RANGE.copy())[1] = limit
        return self

    def offset(self, offset: int) -> Self:
        self.query.setdefault('range', DEFAULT_RANGE.copy())[0] = offset
        return self

    def set_markets(self, *markets: str) -> Self:
        """
        This method allows you to select the market/s which you want to query.

        By default, the screener will only scan US equities, but you can change it to scan any
        market or country, that includes a list of 67 countries, and also the following
        asset classes: `bonds`, `cfd`, `coin`, `crypto`, `euronext`, `forex`,
        `futures`, `options`.

        You may choose any value from `tradingview_screener.constants.MARKETS`.

        If you select multiple countries, you might want to

        Examples:

        By default, the screener will show results from the `america` market, but you can
        change it (note the difference between `market` and `country`)
        >>> columns = ['close', 'market', 'country', 'currency']
        >>> (Query()
        ...  .select(*columns)
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
        ...  .select(*columns)
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
        ...  .set_markets('cfd', 'crypto', 'forex', 'futures')
        ...  .get_scanner_data())
        (118076,
                                    ticker  ...  market
         0          UNISWAP3ETH:JUSTICEUSDT  ...  crypto
         1             UNISWAP3ETH:UAHGUSDT  ...  crypto
         2            UNISWAP3ETH:KENDUWETH  ...  crypto
         3         UNISWAP3ETH:MATICSTMATIC  ...  crypto
         4             UNISWAP3ETH:WETHETHM  ...  crypto
         ..                             ...  ...     ...
         45  UNISWAP:MUSICAIWETH_1F5304.USD  ...  crypto
         46                   CRYPTOCAP:FIL  ...     cfd
         47                   CRYPTOCAP:SUI  ...     cfd
         48                  CRYPTOCAP:ARBI  ...     cfd
         49                    CRYPTOCAP:OP  ...     cfd
         [50 rows x 3 columns])

        :param markets: one or more markets from `tradingview_screener.constants.MARKETS`
        :return: Self
        """
        if len(markets) == 1:
            market = markets[0]
            self.url = URL.format(market=market)
            self.query['markets'] = [market]
        else:  # len(markets) == 0 or len(markets) > 1
            self.url = URL.format(market='global')
            self.query['markets'] = list(markets)

        return self

    def set_tickers(self, *tickers: str) -> Self:
        """
        Set the tickers you wish to receive information on.

        Note that this resets the markets and sets the URL market to `global`.

        Examples:

        >>> q = Query().select('name', 'market', 'close', 'volume', 'VWAP', 'MACD.macd')
        >>> q.set_tickers('NASDAQ:TSLA').get_scanner_data()
        (1,
                 ticker  name   market  close   volume    VWAP  MACD.macd
         0  NASDAQ:TSLA  TSLA  america    186  3519931  185.53   2.371601)

        To set tickers from multiple markets we need to update the markets that include them:
        >>> (Query()
        ...  .set_markets('america', 'italy', 'vietnam')
        ...  .set_tickers('NYSE:GME', 'AMEX:SPY', 'MIL:RACE', 'HOSE:VIX')
        ...  .get_scanner_data())
        (4,
              ticker  name     close    volume  market_cap_basic
         0  HOSE:VIX   VIX  16700.00  33192500      4.568961e+08
         1  AMEX:SPY   SPY    544.35   1883562               NaN
         2  NYSE:GME   GME     23.80   3116758      1.014398e+10
         3  MIL:RACE  RACE    393.30    122878      1.006221e+11)

        :param tickers: One or more tickers, syntax: `exchange:symbol`
        :return: Self
        """
        self.query.setdefault('symbols', {})['tickers'] = list(tickers)
        self.set_markets()
        return self

    def set_index(self, *indexes: str) -> Self:
        """
        Scan only the equities that are in in the given index (or indexes).

        Note that this resets the markets and sets the URL market to `global`.

        Examples:

        >>> Query().set_index('SYML:SP;SPX').get_scanner_data()
        (503,
                   ticker   name    close    volume  market_cap_basic
         0    NASDAQ:NVDA   NVDA  1208.88  41238122      2.973644e+12
         1    NASDAQ:AAPL   AAPL   196.89  53103705      3.019127e+12
         2    NASDAQ:TSLA   TSLA   177.48  56244929      5.660185e+11
         3     NASDAQ:AMD    AMD   167.87  44795240      2.713306e+11
         4    NASDAQ:MSFT   MSFT   423.85  13621485      3.150183e+12
         5    NASDAQ:AMZN   AMZN   184.30  28021473      1.917941e+12
         6    NASDAQ:META   META   492.96   9379199      1.250410e+12
         7   NASDAQ:GOOGL  GOOGL   174.46  19660698      2.164346e+12
         8    NASDAQ:SMCI   SMCI   769.11   3444852      4.503641e+10
         9    NASDAQ:GOOG   GOOG   175.95  14716134      2.164346e+12
         10   NASDAQ:AVGO   AVGO  1406.64   1785876      6.518669e+11)

        You can set multiple indices as well, like the NIFTY 50 and UK 100 Index.
        >>> Query().set_index('SYML:NSE;NIFTY', 'SYML:TVC;UKX').get_scanner_data()
        (150,
                     ticker        name         close     volume  market_cap_basic
         0         NSE:INFY        INFY   1533.600000   24075302      7.623654e+10
         1          LSE:AZN         AZN  12556.000000    2903032      2.489770e+11
         2     NSE:HDFCBANK    HDFCBANK   1573.350000   18356108      1.432600e+11
         3     NSE:RELIANCE    RELIANCE   2939.899900    9279348      2.381518e+11
         4         LSE:LSEG        LSEG   9432.000000    2321053      6.395329e+10
         5   NSE:BAJFINANCE  BAJFINANCE   7191.399900    2984052      5.329685e+10
         6         LSE:BARC        BARC    217.250000   96238723      4.133010e+10
         7         NSE:SBIN        SBIN    829.950010   25061284      8.869327e+10
         8           NSE:LT          LT   3532.500000    5879660      5.816100e+10
         9         LSE:SHEL        SHEL   2732.500000    7448315      2.210064e+11)

        You can find the full list of indices in [`constants.INDICES`](constants.html#INDICES),
        just note that the syntax is
        `SYML:{source};{symbol}`.

        :param indexes: One or more strings representing the financial indexes to filter by
        :return: An instance of the `Query` class with the filter applied
        """
        self.query.setdefault('preset', 'index_components_market_pages')
        self.query.setdefault('symbols', {})['symbolset'] = list(indexes)
        # reset markets list and URL to `/global`
        self.set_markets()
        return self

    # def set_currency(self, currency: Literal['symbol', 'market'] | str) -> Self:
    #     """
    #     Change the currency of the screener.
    #
    #     Note that this changes *only* the currency of the columns of type `fundamental_price`,
    #     for example: `market_cap_basic`, `net_income`, `total_debt`. Other columns like `close` and
    #     `Value.Traded` won't change, because they are of a different type.
    #
    #     This can be particularly useful if you are querying tickers across different markets.
    #
    #     Examples:
    #
    #     >>> Query().set_currency('symbol')  # convert to symbol currency
    #     >>> Query().set_currency('market')  # convert to market currency
    #     >>> Query().set_currency('usd')  # or another currency
    #     >>> Query().set_currency('jpy')
    #     >>> Query().set_currency('eur')
    #     """
    #     # symbol currency -> self.query['price_conversion'] = {'to_symbol': True}
    #     # market currency -> self.query['price_conversion'] = {'to_symbol': False}
    #     # USD or other currency -> self.query['price_conversion'] = {'to_currency': 'usd'}
    #     if currency == 'symbol':
    #         self.query['price_conversion'] = {'to_symbol': True}
    #     elif currency == 'market':
    #         self.query['price_conversion'] = {'to_symbol': False}
    #     else:
    #         self.query['price_conversion'] = {'to_currency': currency}
    #     return self

    def set_property(self, key: str, value: Any) -> Self:
        self.query[key] = value
        return self

    def get_scanner_data_raw(self, **kwargs) -> ScreenerDict:
        """
        Perform a POST web-request and return the data from the API (dictionary).

        Note that you can pass extra keyword-arguments that will be forwarded to `requests.post()`,
        this can be very useful if you want to pass your own headers/cookies.

        >>> Query().select('close', 'volume').limit(5).get_scanner_data_raw()
        {
            'totalCount': 17559,
            'data': [
                {'s': 'NASDAQ:NVDA', 'd': [116.14, 312636630]},
                {'s': 'AMEX:SPY', 'd': [542.04, 52331224]},
                {'s': 'NASDAQ:QQQ', 'd': [462.58, 40084156]},
                {'s': 'NASDAQ:TSLA', 'd': [207.83, 76247251]},
                {'s': 'NASDAQ:SBUX', 'd': [95.9, 157211696]},
            ],
        }
        """
        self.query.setdefault('range', DEFAULT_RANGE.copy())

        kwargs.setdefault('headers', HEADERS)
        kwargs.setdefault('timeout', 20)
        r = requests.post(self.url, json=self.query, **kwargs)

        if not r.ok:
            # add the body to the error message for debugging purposes
            r.reason += f'\n Body: {r.text}\n'
            r.raise_for_status()

        return r.json()

    def get_scanner_data(self, **kwargs) -> tuple[int, pd.DataFrame]:
        """
        Perform a POST web-request and return the data from the API as a DataFrame (along with
        the number of rows/tickers that matched your query).

        Note that you can pass extra keyword-arguments that will be forwarded to `requests.post()`,
        this can be very useful if you want to pass your own headers/cookies.

        ### Live/Delayed data

        Note that to get live-data you have to authenticate, which is done by passing your cookies.
        Have a look in the README at the "Real-Time Data Access" sections.

        :param kwargs: kwargs to pass to `requests.post()`
        :return: a tuple consisting of: (total_count, dataframe)
        """
        import pandas as pd

        json_obj = self.get_scanner_data_raw(**kwargs)
        rows_count = json_obj['totalCount']
        data = json_obj['data']

        df = pd.DataFrame(
            data=([row['s'], *row['d']] for row in data),
            columns=['ticker', *self.query.get('columns', ())],  # pyright: ignore [reportArgumentType]
        )
        return rows_count, df

    def copy(self) -> Query:
        new = Query()
        new.query = self.query.copy()
        return new

    def __repr__(self) -> str:
        return f'< {pprint.pformat(self.query)}\n url={self.url!r} >'

    def __eq__(self, other) -> bool:
        return isinstance(other, Query) and self.query == other.query and self.url == other.url


# TODO: Query should have no defaults (except limit), and a separate module should have all the
#  default screeners
# TODO: add all presets
