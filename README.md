<div align="center">
    
  <a href="https://pypi.org/project/tradingview-screener">
    <img alt="PyPi Version"
         src="https://badge.fury.io/py/tradingview-screener.svg?icon=si%3Apython">
  </a>
  <a href="https://pypi.org/project/tradingview-screener">
    <img alt="Supported Python versions"
         src="https://img.shields.io/pypi/pyversions/tradingview-screener.svg?color=%2334D058">
  </a>
  <a href="https://pepy.tech/project/tradingview-screener">
    <img alt="Downloads"
         src="https://static.pepy.tech/badge/tradingview-screener">
  </a>
  <a href="https://pepy.tech/project/tradingview-screener">
    <img alt="Downloads"
         src="https://static.pepy.tech/badge/tradingview-screener/month">
  </a>
    
</div>


## Overview

```bash
pip install tradingview-screener
```

`tradingview-screener` is a Python package that allows you to create custom stock screeners using TradingView's official
API. This package retrieves data directly from TradingView without the need for web scraping or HTML parsing.


### Key Features

- **Over 3000 Fields**: OHLC, indicators, fundamental metrics, and much more.
- **Multiple Markets**: Stocks, crypto, forex, CFD, futures, bonds, and more.
- **Customizable Timeframes**: Choose timeframes like 1 minute, 5 minutes, 1 hour, or 1 day for each field.
- **Filter and sort** the results using a SQL-like syntax, with support for And/Or operators for advanced filtering.


### Links

- [GitHub Repository](https://github.com/shner-elmo/TradingView-Screener)
- [Documentation](https://shner-elmo.github.io/TradingView-Screener/3.0.0/tradingview_screener.html)
- [Fields](https://shner-elmo.github.io/TradingView-Screener/fields/stocks.html)
- [Screeners](https://shner-elmo.github.io/TradingView-Screener/screeners/stocks/america.html)

Note that throughout the documentation, "field" and "column" are used interchangeably.
Same with "Scanner" and "Screener".

## Quickstart

Here’s a simple example to get you started:

```python
from tradingview_screener import Query

(Query()
 .select('name', 'close', 'volume', 'market_cap_basic')
 .get_scanner_data())
```

**Output:**

```
(17580,
          ticker  name   close     volume  market_cap_basic
 0   NASDAQ:NVDA  NVDA  127.25  298220762      3.130350e+12
 1      AMEX:SPY   SPY  558.70   33701795               NaN
 2   NASDAQ:TSLA  TSLA  221.10   73869589      7.063350e+11
 3    NASDAQ:QQQ   QQQ  480.26   29102854               NaN
 4    NASDAQ:AMD   AMD  156.40   76693809      2.531306e+11
 ..          ...   ...     ...        ...               ...
 45   NASDAQ:PDD   PDD  144.22    8653323      2.007628e+11
 46     NYSE:JPM   JPM  214.52    5639973      6.103447e+11
 47     NYSE:JNJ   JNJ  160.16    7274621      3.855442e+11
 48  NASDAQ:SQQQ  SQQQ    7.99  139721164               NaN
 49  NASDAQ:ASTS  ASTS   34.32   32361315      9.245616e+09
 
 [50 rows x 5 columns])
```

By default, the result is limited to 50 rows. You can adjust this limit, but be mindful of server load and potential
bans.

A more advanced query:

```python
from tradingview_screener import Query, col

(Query()
 .select('name', 'close', 'volume', 'relative_volume_10d_calc')
 .where(
     col('market_cap_basic').between(1_000_000, 50_000_000),
     col('relative_volume_10d_calc') > 1.2,
     col('MACD.macd') >= col('MACD.signal')
 )
 .order_by('volume', ascending=False)
 .offset(5)
 .limit(25)
 .get_scanner_data())
```

<br>

## Real-Time Data Access

To access real-time data, you need to pass your session cookies, as even free real-time data requires authentication.

### Verify Update Mode

You can run this query to get an overview on the `update_mode` you get for each exchange:
```python
from tradingview_screener import Query

_, df = Query().select('exchange', 'update_mode').limit(1_000_000).get_scanner_data()
df.groupby('exchange')['update_mode'].value_counts()
```
```
exchange  update_mode          
AMEX      delayed_streaming_900    3255
NASDAQ    delayed_streaming_900    4294
NYSE      delayed_streaming_900    2863
OTC       delayed_streaming_900    7129
```

### Using rookiepy

`rookiepy` is a library that loads the cookies from your local browser.
So if you are logged in on Chrome (or whatever browser you use), it will use the same session.

1. Install `rookiepy`:

    ```bash
    pip install rookiepy
    ```

2. Load the cookies:

    ```python
    import rookiepy
    cookies = rookiepy.to_cookiejar(rookiepy.chrome(['.tradingview.com']))  # replace chrome() with your browser
    ```

3. Pass the cookies when querying:

    ```python
    Query().get_scanner_data(cookies=cookies)
    ```

Now, if you re-run the update mode check:

```python
_, df = Query().select('exchange', 'update_mode').limit(1_000_000).get_scanner_data(cookies=cookies)
df.groupby('exchange')['update_mode'].value_counts()
```
```
exchange  update_mode          
AMEX      streaming                3256
NASDAQ    streaming                4286
NYSE      streaming                2860
OTC       delayed_streaming_900    7175
```
We now get live-data for all exchanges except `OTC` (because my subscription dosent include live-data for OTC tickers).


### Other Ways For Loading Cookies

<details>
<summary>Extract Cookies Manually</summary>

1. Go to [TradingView](https://www.tradingview.com)
2. Open the developer tools (`Ctrl + Shift + I`)
3. Navigate to the `Application` tab.
4. Go to `Storage > Cookies > https://www.tradingview.com/`
5. Copy the value of `sessionid`
6. Pass it in your query:

    ```python
    cookies = {'sessionid': '<your-session-id>'}
    Query().get_scanner_data(cookies=cookies)
    ```

</details>


<details>
<summary>Authenticate via API</summary>

While it's possible to authenticate directly via API, TradingView has restrictions on login frequency, which may result
in CAPTCHA requests and account flagging (meaning this method won't work again until the cooldown expires and the CAPTCHA
is gone).  
If you wish to proceed, here’s how:

```python
from http.cookiejar import CookieJar

import requests
from tradingview_screener import Query


def authenticate(username: str, password: str) -> CookieJar:
    session = requests.Session()
    r = session.post(
       'https://www.tradingview.com/accounts/signin/', 
       headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.tradingview.com'}, 
       data={'username': username, 'password': password, 'remember': 'on'}, 
       timeout=60,
    )
    r.raise_for_status()
    if r.json().get('error'):
        raise Exception(f'Failed to authenticate: \n{r.json()}')
    return session.cookies


cookies = authenticate('<your-username-or-email>', '<your-password>')
Query().get_scanner_data(cookies=cookies)
```

</details>

## Comparison to Similar Packages

Unlike other Python libraries that have specific features like extracting the sentiment, or what not.
This package is but a (low-level) wrapper around TradingView's `/screener` API endpoint.

It merely documents the endpoint, by listing all the functions and operations available, the different fields you can 
use, the markets, instruments (even some that you wont find on TradingView's website), and so on.

This library is also a wrapper that makes it easier to generate those verbose JSON payloads.


## Robustness & Longevity

This package is designed to be future-proof. There are no hard-coded values in the package, all fields/columns and markets are documented on the website, which is updated
daily via a GitHub Actions script.

## How It Works

When using methods like `select()` or `where()`, the `Query` object constructs a dictionary representing the API
request. Here’s an example of the dictionary generated:

```python
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

The `get_scanner_data()` method sends this dictionary as a JSON payload to the TradingView API,
allowing you to query data using SQL-like syntax without knowing the specifics of the API.

## Feedback and Improvement

If this package has bought value to your projects, please consider starring it.
