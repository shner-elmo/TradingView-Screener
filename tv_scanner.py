import requests
import pandas as pd
import warnings

HEADERS = {
    'authority': 'scanner.tradingview.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'accept': 'text/plain, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://www.tradingview.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.tradingview.com/',
    'accept-language': 'en-US,en;q=0.9,it;q=0.8',
}


class TradingViewScanner:

    def __init__(self, cookies: str = None):
        """
        A class for getting data from TradingView's scanners, it's possible to provide your own cookies
        but not necessary, for more on that check out the test for this module
        """
        if cookies is not None:
            HEADERS['cookie'] = cookies

        self.columns = ["symbol", "premarket_close", "premarket_change", "premarket_change_perc", "premarket_volume",
                        "premarket_gap_perc", "close", "change_perc", "volume", "market_cap", "description"]
        self.scanners = {
            'pm_gainers': '{"filter":[{"left":"premarket_change","operation":"nempty"},{"left":"type","operation":"equal","right":"stock"},{"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},{"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}],"options":{"active_symbols_only":true,"lang":"en"},"markets":["america"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["logoid","name","premarket_close","premarket_change_abs","premarket_change","premarket_volume","premarket_gap","close","change","volume","market_cap_basic","description","type","subtype","update_mode","pricescale","minmov","fractional","minmove2","currency","fundamental_currency_code"],"sort":{"sortBy":"premarket_change","sortOrder":"desc"},"range":[0,50]}',
            'pm_losers': '{"filter":[{"left":"premarket_change","operation":"nempty"},{"left":"type","operation":"equal","right":"stock"},{"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},{"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}],"options":{"active_symbols_only":true,"lang":"en"},"markets":["america"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["logoid","name","premarket_close","premarket_change_abs","premarket_change","premarket_volume","premarket_gap","close","change","volume","market_cap_basic","description","type","subtype","update_mode","pricescale","minmov","fractional","minmove2","currency","fundamental_currency_code"],"sort":{"sortBy":"premarket_change","sortOrder":"asc"},"range":[0,50]}',
            'pm_most_active': '{"filter":[{"left":"volume","operation":"nempty"},{"left":"type","operation":"equal","right":"stock"},{"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},{"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}],"options":{"active_symbols_only":true,"lang":"en"},"markets":["america"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["logoid","name","premarket_close","premarket_change_abs","premarket_change","premarket_volume","premarket_gap","close","change","volume","market_cap_basic","description","type","subtype","update_mode","pricescale","minmov","fractional","minmove2","currency","fundamental_currency_code"],"sort":{"sortBy":"volume","sortOrder":"desc"},"range":[0,50]}',
            'pm_gappers': '{"filter":[{"left":"premarket_gap","operation":"nempty"},{"left":"type","operation":"equal","right":"stock"},{"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},{"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}],"options":{"active_symbols_only":true,"lang":"en"},"markets":["america"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["logoid","name","premarket_close","premarket_change_abs","premarket_change","premarket_volume","premarket_gap","close","change","volume","market_cap_basic","description","type","subtype","update_mode","pricescale","minmov","fractional","minmove2","currency","fundamental_currency_code"],"sort":{"sortBy":"premarket_gap","sortOrder":"desc"},"range":[0,50]}'
        }

    def get_data(self, scanner_type: str, return_type: str = 'df'):
        """
        return a DataFrame or a dictionary with the scanner data,
        currently there are three types of scanners; PM gainers (sorted by PM chg%), PM losers (sorted by PM chg%),
        and PM most active (sorted by volume).

        :param scanner_type: must be one of the following: 'pm_gainers', 'pm_losers', 'pm_most_active'.
        :param return_type: 'df' or 'dict'
        :return: pandas.DataFrame or dictionary or None if request is unsuccessful
        """
        if scanner_type not in self.scanners.keys():
            raise KeyError(f"Error: Given scanner_type is not valid, must be one of the following: "
                           f"{list(self.scanners.keys())}")

        r = requests.post('https://scanner.tradingview.com/america/scan',
                          headers=HEADERS, data=self.scanners[scanner_type])
        if r.status_code != 200:
            warnings.warn(f'Response is empty, status code: {r.status_code}')
            return None

        data = r.json()['data']
        split_columns = [[row['s']] + row['d'] for row in data]

        df = pd.DataFrame(data=split_columns)
        df = df.drop(columns=[0, 1, 13, 14, 15, 16, 17, 18, 19, 20, 21])
        df.columns = self.columns
        df = df.set_index('symbol')

        if return_type == 'dict':
            return df.to_dict('index')
        return df
