# TradingView-Screener


---
[![PyPi](https://img.shields.io/badge/PyPi-0.3.0-yellow)](https://pypi.org/project/tradingview-screener/)
[![Downloads](https://pepy.tech/badge/tradingview-screener)](https://pepy.tech/project/tradingview-screener)
[![Downloads](https://pepy.tech/badge/tradingview-screener/month)](https://pepy.tech/project/tradingview-screener)

You can get the package directly from [PyPI](https://pypi.org/project/tradezero-api/)
```
pip install tradingview-screener
```
---

This package allows you to create stock screeners with TradingView's, and retrieve the data directly from the official
API (without doing any kind of web-scraping).


#### The following quick-guide will show you how to get started using the tradingview-package module

Import the function and the Enum class
```python
from tradingview_screener import get_scanner_data, Scanner
```

All the scanners available:
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

Then, to retrieve the data you must provide the scanner type
```python
df = Scanner.premarket_gainers.get_data()
```

And we get a DataFrame with the data:
```python
>>> df
```
```
    name  premarket_change     close    volume  market_cap_basic
0   VIRI         77.514793    0.6253   4047431      1.146199e+07
1   CXAI         45.310016    6.2900   1407773      5.398518e+07
2   BXRX         45.212766    1.8800    469498      4.861120e+06
3   SPPI         35.264301    0.6905    478063      1.417606e+08
4   MORF         30.944176   43.5300    239678      1.720921e+09
5   PTPI         29.166667    3.8400    828932      8.020600e+06
6   ARWR         21.918721   30.0200    630642      3.251471e+09
7   EDUC         21.076233    2.2300     44927      1.943064e+07
8   ASTS         20.183486    4.3600   1814082      8.723593e+08
9   ZFOX         18.348624    1.0900    460906      1.292519e+08
10  MEDP         16.511802  187.2600    598436      5.814453e+09
...

[50 rows x 5 columns]
```

If you aren't yet familiar with Pandas DataFrames, you can convert the output to a list of dictionaries like so:
```python
>>> df.to_dict('records')
```
```
[
    {'name': 'VIRI', 'premarket_change': 77.5147929, 'close': 0.6253, 'volume': 4047431, 'market_cap_basic': 11461993.0},
    {'name': 'CXAI', 'premarket_change': 45.3100159, 'close': 6.29, 'volume': 1407773, 'market_cap_basic': 53985175.00000001},
    {'name': 'BXRX', 'premarket_change': 45.21276596, 'close': 1.88, 'volume': 469498, 'market_cap_basic': 4861120.0},
    {'name': 'SPPI', 'premarket_change': 35.26430123, 'close': 0.6905, 'volume': 478063, 'market_cap_basic': 141760626.0},
    {'name': 'MORF', 'premarket_change': 30.94417643, 'close': 43.53, 'volume': 239678, 'market_cap_basic': 1720920967.0},
    ...
]
```

Or to get the most active during the pre-market session:
```python
>>> Scanner.premarket_most_active.get_data()
```
```
    name  premarket_volume     close     volume  market_cap_basic
0   MULN          27981441    0.0960  756912573      3.640486e+08
1   VIRI          16779935    0.6253    4047431      1.146199e+07
2   BBBY          12464514    0.1888  539779156      8.082502e+07
3   SPPI           8098728    0.6905     478063      1.417606e+08
4   ZFOX           5510783    1.0900     460906      1.292519e+08
5    FRC           5165413   16.0000   90150729      2.928000e+09
6   BXRX           4524110    1.8800     469498      4.861120e+06
7   XELA           3525650    0.0397   49643555      5.058590e+07
8   CXAI           2464392    6.2900    1407773      5.398518e+07
9   IDEX           2250652    0.0399   67497209      2.787359e+07
10  AGFY           2250428    0.2123    5197584      1.884452e+06
...

[50 rows x 5 columns]
```

Once you have the data you can filter the results however you want.  
In our case we only want stocks that have a pre-market change above 10% and a price bigger than $3 
```python
>>> filt = (df['premarket_change'] > 10) & (df['close'] > 3)
>>> df[filt]
```
```
    name  premarket_change    close   volume  market_cap_basic
1   CXAI         45.310016    6.290  1407773      5.398518e+07
4   MORF         30.944176   43.530   239678      1.720921e+09
5   PTPI         29.166667    3.840   828932      8.020600e+06
6   ARWR         21.918721   30.020   630642      3.251471e+09
8   ASTS         20.183486    4.360  1814082      8.723593e+08
10  MEDP         16.511802  187.260   598436      5.814453e+09
15  GDHG         12.159612    3.709     3492      1.854500e+08
16   PCT         11.368015    5.190  1294479      8.494532e+08
19  APLM         10.643564    4.040   159000      2.590733e+07

[9 rows x 5 columns]
```

-----  
You can also override the settings that are being passed to the API.

For example if you want to get the first 200 results instead of just 50:
```python
>>> Scanner.premarket_losers.get_data(range=[0, 200])
```
```
     name  premarket_change    close    volume  market_cap_basic
0    TCON        -51.123596   1.7800     18817      4.240412e+07
1    VYNT        -31.709091   0.5500    194750      3.447239e+06
2    NCPL        -27.626818   1.5199   6111277      9.228493e+06
3     FRC        -25.937500  16.0000  90150729      2.928000e+09
4     SFR        -25.500000   2.0000  16709427      9.651445e+07
..    ...               ...      ...       ...               ...
195  RBOT         -2.643172   2.2700    123525      2.859286e+08
196  HPCO         -2.640264   0.6060    151701      1.416420e+07
197  BLDP         -2.608696   4.6000   1776254      1.372613e+09
198   TRX         -2.601535   0.5343    205843      1.479665e+08
199   SOI         -2.573529   8.1600    185698      3.803123e+08

[200 rows x 5 columns]
```

You can also specify the columns you want to get
```python
>>> Scanner.premarket_gainers.get_data(range=[0, 10], columns=['name', 'close', 'premarket_change', 'logoid', 'description', 'type', 'VWAP', 'MACD.macd'])
```
```
   name    close  premarket_change  ...   type       VWAP MACD.macd
0  VIRI   0.6253         91.907884  ...  stock   0.644767  0.086156
1  BXRX   1.8800         43.617021  ...  stock   2.018500  0.082743
2  CXAI   6.2900         39.745628  ...  stock   7.100400  1.106645
3  SPPI   0.6905         34.047791  ...  stock   0.696000 -0.018506
4  MORF  43.5300         30.484723  ...  stock  43.910000  1.133547
5  ASTS   4.3600         25.688073  ...  stock   4.308333 -0.396030
6  ARWR  30.0200         21.585610  ...  stock  30.348067  0.864783
7  PTPI   3.8400         21.093750  ...  stock   4.450000  0.941922
8  EDUC   2.2300         21.076233  ...  stock   2.280000 -0.257153
9  AGFY   0.2123         17.192652  ...  stock   0.217233 -0.016040

[10 rows x 8 columns]
```

For the full list of columns have a look at the following dictionary (there are more that will be added in the future):
```python
>>> from tradingview_screener.screener import COLUMNS
>>> COLUMNS
```
```
{'1-Month High': 'High.1M',
 '1-Month Low': 'Low.1M',
 '1-Year Beta': 'beta_1_year',
 '3-Month High': 'High.3M',
 '3-Month Low': 'Low.3M',
 '3-Month Performance': 'Perf.3M',
 '52 Week High': 'price_52_week_high',
 '52 Week Low': 'price_52_week_low',
 '5Y Performance': 'Perf.5Y',
 '6-Month High': 'High.6M',
 '6-Month Low': 'Low.6M',
 '6-Month Performance': 'Perf.6M',
 'All Time High': 'High.All',
 'All Time Low': 'Low.All',
 'All Time Performance': 'Perf.All',
 'Aroon Down (14)': 'Aroon.Down',
 'Aroon Up (14)': 'Aroon.Up',
 ...}
```


## Creating Custom Stock Screeners

```python
from tradingview_screener import Query, Column
```


Create a query (like you would in a SQL database):
```python
q = Query().select('name', 'close', 'volume', 'relative_volume_10d_calc', 'market_cap_basic')
```

And to get the results we can call `get_scanner_data()` which will return a tuple with the number of results `COUNT(*)`
that matched our query, and the actual data (as a pandas DataFrame):
```python
num_rows, df = q.get_scanner_data()
print('Number of rows:', num_rows)
```
```
Number of rows: 5271
```

And the data:
```python
df
```
```
    name      close   volume  relative_volume_10d_calc  market_cap_basic
0   SASI   0.421101     2176                  0.122958      4.536400e+06
1   BROG   5.050000      491                  0.170126      4.445781e+08
2   LAZR   6.020000  4643780                  0.644816      2.222977e+09
3    PIK   0.598500    88926                  0.682655      4.601384e+06
4   HAYW  12.040000  1464436                  0.986823      2.559983e+09
..   ...        ...      ...                       ...               ...
45  ATIP   0.271400   243505                  1.096411      5.628409e+07
46  CLFD  43.680000   242512                  0.736585      6.647937e+08
47  CRCT   9.130000    66012                  1.154169      2.003323e+09
48   ENZ   2.530000   118980                  0.529591      1.256469e+08
49  WLGS   2.220000  5589780                       NaN               NaN

[50 rows x 5 columns]
```

As you may have noticed, there are only 50 rows in our dataframe, while `num_rows` is 5271,  
this is because by default there is a `LIMIT` of 50, although you can override that by providing your own.
But, note that the more results you try to fetch, the more work the server needs to do, and therefore the network request
will take more time, so It's something to keep in mind.

You can also filter the results:
```python
q = Query().select('name', 'close', 'volume', 'relative_volume_10d_calc')\
    .where(
        Column('market_cap_basic').between(1_000_000, 50_000_000), 
        Column('relative_volume_10d_calc') > 1.2, 
        Column('MACD.macd') >= 'MACD.signal'
    )
q.get_scanner_data()
```
```
(493,
      name    close  volume  relative_volume_10d_calc
 0    CMPD  2.90000    1308                  1.806380
 1   ABNAF  0.08500    7210                  1.365401
 2    TARA  3.16000  102277                  1.697113
 3   FLYLF  0.74853   15000                  1.973632
 4   OGBLY  0.04000   45005                  6.980766
 ..    ...      ...     ...                       ...
 45   LPCN  0.26000  348622                  2.326042
 46   ELTP  0.03300  561900                  2.117304
 47   FNAM  0.70000    2000                  1.350348
 48     UK  1.04000  315203                  1.409103
 49   VERO  0.18880  218379                  1.435621
 
 [50 rows x 4 columns])
```

To order the results:
```python
q = Query().select('name', 'close', 'volume', 'relative_volume_10d_calc')\
    .where(
        Column('market_cap_basic').between(1_000_000, 50_000_000), 
        Column('relative_volume_10d_calc') > 1.2, 
        Column('MACD.macd') >= 'MACD.signal'
    )\
    .order_by('volume', ascending=False)
q.get_scanner_data()
```
```
(493,
     name    close    volume  relative_volume_10d_calc
 0    DXF  0.36990  92255915                 56.544501
 1   DPLS  0.00555  51685577                  1.528578
 2   LGHL  0.26800  48563857                 70.600598
 3   JZXN  0.26000  45771791                 82.053268
 4   PVSP  0.00060  45491685                  1.786331
 ..   ...      ...       ...                       ...
 45  RMSL  0.01290   1943387                  1.542694
 46  TIRX  1.63000   1937953                 43.849456
 47  TNXP  0.52000   1870167                  2.578986
 48    MF  1.30000   1837216                108.688496
 49  EWRC  0.00280   1761115                 11.767738
 
 [50 rows x 4 columns])
```

To get the slice `[5:15]`:
```python
q = Query().select('name', 'close', 'volume', 'relative_volume_10d_calc')\
    .where(
        Column('market_cap_basic').between(1_000_000, 50_000_000), 
        Column('relative_volume_10d_calc') > 1.2, 
        Column('MACD.macd') >= 'MACD.signal'
    )\
    .order_by('volume', ascending=False)\
    .offset(5)\
    .limit(15)
q.get_scanner_data()
```
```
(493,
    name    close    volume  relative_volume_10d_calc
 0  INTK  0.00050  32999277                  3.749458
 1  BIEL  0.00040  26141639                  1.350728
 2  GSUN  1.35000  24240204                 98.543864
 3  FTXP  0.00020  21113909                  1.894780
 4  IGEX  0.00080  20660879                  1.211745
 5  HPNN  0.00090  16051557                  2.295840
 6  SGMD  0.00020  15761527                  2.232289
 7  ERBB  0.00102  14257745                  1.805648
 8  ASTA  0.00220  13801619                  1.537809
 9  BANT  0.00020  13514923                  1.573909)
```

### Reusing Scanners

To avoid rewriting the same query again and again, you can save the query to a variable and just call 
`get_scanner_data()` again and again to get the latest data:
```python
top_50_bullish = Query().select('name', 'close', 'volume', 'relative_volume_10d_calc')\
    .where(
        Column('market_cap_basic').between(1_000_000, 50_000_000), 
        Column('relative_volume_10d_calc') > 1.2, 
        Column('MACD.macd') >= 'MACD.signal'
    )\
    .order_by('volume', ascending=False)\
    .limit(50)
```

And you can just call it like so:
```python
top_50_bullish.get_scanner_data()
```
```
(493,
     name    close    volume  relative_volume_10d_calc
 0    DXF  0.36990  92255915                 56.544501
 1   DPLS  0.00555  51685577                  1.528578
 2   LGHL  0.26800  48563857                 70.600598
 3   JZXN  0.26000  45771791                 82.053268
 4   PVSP  0.00060  45491685                  1.786331
 ..   ...      ...       ...                       ...
 45  RMSL  0.01290   1943387                  1.542694
 46  TIRX  1.63000   1937953                 43.849456
 47  TNXP  0.52000   1870167                  2.578986
 48    MF  1.30000   1837216                108.688496
 49  EWRC  0.00280   1761115                 11.767738
 
 [50 rows x 4 columns])
```


```python
top_50_bullish.get_scanner_data()
```
```
(493,
     name    close    volume  relative_volume_10d_calc
 0    DXF  0.36990  92255915                 56.544501
 1   DPLS  0.00555  51685577                  1.528578
 2   LGHL  0.26800  48563857                 70.600598
 3   JZXN  0.26000  45771791                 82.053268
 4   PVSP  0.00060  45491685                  1.786331
 ..   ...      ...       ...                       ...
 45  RMSL  0.01290   1943387                  1.542694
 46  TIRX  1.63000   1937953                 43.849456
 47  TNXP  0.52000   1870167                  2.578986
 48    MF  1.30000   1837216                108.688496
 49  EWRC  0.00280   1761115                 11.767738
 
 [50 rows x 4 columns])
```


---

## Getting All The Stock Symbols

#### There is a function that allows you to get all the symbols from a given exchange.


Import the function
```python
from tradingview_screener import get_all_symbols
```

Get all the symbols in the US stock market:
```python
all_symbols = get_all_symbols()
```

```python
len(all_symbols)
```
```
18451
```

The first 10:
```python
all_symbols[:10]
```
```
['IIGD', 'TBGPF', 'HLAN', 'FVC', 'GLNG', 'MMC', 'PFHO', 'IDU', 'AMLH', 'IHT']
```

You can also filter them by exchange, valid exchanges include: `'AMEX', 'OTC', 'NYSE', 'NASDAQ'`
```python
symbols = get_all_symbols(exchanges={'NYSE', 'NASDAQ'})
len(symbols), symbols[:10]
```
```
(7633,
 ['TYRA',
  'ACRS',
  'RDNT',
  'DCI',
  'LIBY',
  'EGIO',
  'AGIO',
  'KRON',
  'BRO',
  'PINC'])
```

Get all OTC stocks:
```python
symbols = get_all_symbols(exchanges={'OTC'})
len(symbols), symbols[:10]
```
```
(7933,
 ['ADMQ',
  'CSTPF',
  'LSMG',
  'LMGIF',
  'PPMT',
  'JBFCF',
  'CVSI',
  'RXLSF',
  'STBFY',
  'GNZUF'])
```
