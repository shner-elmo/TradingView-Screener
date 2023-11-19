
[![PyPi](https://img.shields.io/badge/PyPi-2.3.1-yellow)](https://pypi.org/project/tradingview-screener/)
[![Downloads](https://static.pepy.tech/badge/tradingview-screener)](https://pepy.tech/project/tradingview-screener)
[![Downloads](https://static.pepy.tech/badge/tradingview-screener/month)](https://pepy.tech/project/tradingview-screener)

```
pip install tradingview-screener
```

# About

This package allows you to create stock screeners with TradingView, and retrieve the data directly from the official
API (without doing any kind of web-scraping/HTML-parsing).

Some of its main features are:

- Get data from **over 3000 fields**, including OHLC, indicators, and fundamental data.
- Variety of markets, including equities, crypto, forex, futures, and bonds.
- **Choose the timeframe** for each field, such as 1 minute, 5 minutes, 1 hour, or 1 day.
- **Filter and sort** the results using SQL, a common database language.
- **Create and save** screeners to easily monitor the markets and identify trading opportunities.

You can find the docs [here](https://shner-elmo.github.io/TradingView-Screener/tradingview_screener.html),
and the source on [GitHub](https://github.com/shner-elmo/TradingView-Screener).

# Quickstart

## Builtin stock scanners

```python
from tradingview_screener import Scanner
```

Some of the pre-built scanners:
```python
>>> Scanner.names()
```
```
['premarket_gainers',
 'premarket_losers',
 'premarket_most_active',
 'premarket_gappers',
 'postmarket_gainers',
 'postmarket_losers',
 'postmarket_most_active']
```

Say we want to get the Pre-Market Gainers:
```python
n_rows, df = Scanner.premarket_gainers.get_scanner_data()
```

And we get a DataFrame with the data:
```python
>>> df
```
```
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

[50 rows x 8 columns]
```

With the following columns:
```python
>>> df.columns
```
```
Index(['ticker', 'name', 'close', 'volume', 'market_cap_basic',
       'premarket_change', 'premarket_change_abs', 'premarket_volume'],
      dtype='object')
```

If you aren't yet familiar with Pandas DataFrames, you can convert the output to a list of dictionaries like so:
```python
>>> df.to_dict('records')[:10]
```
```
[
    {'ticker': 'NASDAQ:APLM', 'name': 'APLM', 'close': 0.862, 'volume': 94235502, 'market_cap_basic': 146422699.0, 'premarket_change': 127.11267606, 'premarket_change_abs': 0.722, 'premarket_volume': 30551043}
    {'ticker': 'OTC:RNVA', 'name': 'RNVA', 'close': 0.0001, 'volume': 11050007, 'market_cap_basic': 2993432.0, 'premarket_change': 100.0, 'premarket_change_abs': 5e-05, 'premarket_volume': 200000}
    {'ticker': 'OTC:OCLN', 'name': 'OCLN', 'close': 0.0076, 'volume': 2543494, 'market_cap_basic': 9864586.0, 'premarket_change': 86.25, 'premarket_change_abs': 0.0069, 'premarket_volume': 220000}
    {'ticker': 'NASDAQ:BKYI', 'name': 'BKYI', 'close': 0.22, 'volume': 39926873, 'market_cap_basic': 2036156.0, 'premarket_change': 57.05916813, 'premarket_change_abs': 0.0974, 'premarket_volume': 8826676}
    {'ticker': 'NASDAQ:ICU', 'name': 'ICU', 'close': 1.02, 'volume': 46835892, 'market_cap_basic': 19834890.0, 'premarket_change': 36.3510101, 'premarket_change_abs': 0.2879, 'premarket_volume': 7527703}
    ...
]
```

## Creating custom stock screeners

```python
from tradingview_screener import Query, Column
```


Create a query (like you would in a SQL database):
```python
(Query()
 .select('name', 'close', 'volume', 'relative_volume_10d_calc', 'market_cap_basic')
 .get_scanner_data())
```
```
(18060,
          ticker  name  ...  relative_volume_10d_calc  market_cap_basic
 0      AMEX:SPY   SPY  ...                  1.112917               NaN
 1    NASDAQ:QQQ   QQQ  ...                  1.050254               NaN
 2   NASDAQ:TSLA  TSLA  ...                  0.784272      6.589904e+11
 3   NASDAQ:NVDA  NVDA  ...                  0.819148      1.000350e+12
 4   NASDAQ:AMZN  AMZN  ...                  2.206912      1.310658e+12
 ..          ...   ...  ...                       ...               ...
 45     NYSE:UNH   UNH  ...                  0.898852      4.859952e+11
 46  NASDAQ:DXCM  DXCM  ...                  2.763555      3.449933e+10
 47      NYSE:MA    MA  ...                  1.254684      3.429080e+11
 48    NYSE:ABBV  ABBV  ...                  2.007460      2.452179e+11
 49     AMEX:XLK   XLK  ...                  1.041988               NaN
 [50 rows x 6 columns])
```

Our dataframe only contains 50 rows, even though there are 5271 rows in total. 
This is because the default LIMIT is 50, but you can change that if you need to. 
Just keep in mind that the more rows you request, the heavier the load you're putting on the server, and the longer 
it will take to respond. 
And if you request too many rows, you might even get banned, so don't get crazy.



A more elaborate query:
```python
(Query()
 .select('name', 'close', 'volume', 'relative_volume_10d_calc')
 .where(
     Column('market_cap_basic').between(1_000_000, 50_000_000),
     Column('relative_volume_10d_calc') > 1.2,
     Column('MACD.macd') >= Column('MACD.signal')
 )
 .order_by('volume', ascending=False)
 .offset(5)
 .limit(25)
 .get_scanner_data())
```
```
(393,
          ticker  name     close    volume  relative_volume_10d_calc
 0      OTC:YCRM  YCRM  0.012000  19626514                  1.887942
 1      OTC:PLPL  PLPL  0.000200  17959914                  3.026059
 2   NASDAQ:ABVC  ABVC  1.380000  16295824                  1.967505
 3      OTC:TLSS  TLSS  0.000900  15671157                  1.877976
 4      OTC:GVSI  GVSI  0.012800  14609774                  2.640792
 ..          ...   ...       ...       ...                       ...
 15    AMEX:TPET  TPET  0.483999   2707793                  3.141248
 16     OTC:PWDY  PWDY  0.000700   2138674                  1.802687
 17  NASDAQ:FGEN  FGEN  0.476100   1846644                  1.385978
 18  NASDAQ:VVPR  VVPR  1.930000   1541197                 64.668412
 19     OTC:NAVB  NAVB  0.052000   1475558                  2.491307
 [20 rows x 5 columns])
```

For more examples have a look [here](https://shner-elmo.github.io/TradingView-Screener/tradingview_screener/query.html).

---


# How it works

When you call a method like `select()` or `where()` on the `Query` object,
it updates a dictionary that contains all the data to send to the API.

For example, the previous query creates the following dictionary:
```py
{
    'markets': ['america'],
    'symbols': {'query': {'types': []}, 'tickers': []},
    'options': {'lang': 'en'},
    'columns': ['name', 'close', 'volume', 'relative_volume_10d_calc'],
    'sort': {'sortBy': 'volume', 'sortOrder': 'desc'},
    'range': [5, 25],
    'filter': [
        {'left': 'market_cap_basic', 'operation': 'in_range', 'right': [1000000, 50000000]},
        {'left': 'relative_volume_10d_calc', 'operation': 'greater', 'right': 1.2},
        {'left': 'MACD.macd', 'operation': 'egreater', 'right': 'MACD.signal'},
    ],
}
```

When the `get_scanner_data()` method is called, it will dump that dictionary as a JSON and send it to the API.

Using this package, you can access and query TradingView data with a simple SQL syntax, without needing to know the 
details of TradingView's API.
