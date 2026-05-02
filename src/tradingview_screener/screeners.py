from __future__ import annotations

from tradingview_screener.query import Query, DEFAULT_RANGE, URL


def stocks(market: str = 'america') -> Query:
    """
    Screener for stocks (common, preferred, DRs, and non-ETF funds), filtered to primary listings
    only and sorted by market cap descending.

    :param market: Market/country to scan, e.g. ``'america'``, ``'italy'``, ``'germany'``.
        Defaults to ``'america'``.
    """
    return Query(market)


def coin() -> Query:
    """
    Screener for crypto coins (CoinMarketCap universe), sorted by overall rank ascending.
    """
    q = Query()
    q.url = URL.format(market='coin')
    q.query = {
        'markets': ['coin'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': [
            'ticker-view',
            'crypto_total_rank',
            'close',
            'type',
            'typespecs',
            'pricescale',
            'minmov',
            'fractional',
            'minmove2',
            'currency',
            '24h_close_change|5',
            'market_cap_calc',
            'fundamental_currency_code',
            '24h_vol_cmc',
            'circulating_supply',
            '24h_vol_to_market_cap',
            'socialdominance',
            'crypto_common_categories.tr',
            'TechRating_1D',
            'TechRating_1D.tr',
        ],
        'sort': {'sortBy': 'crypto_total_rank', 'sortOrder': 'asc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def crypto() -> Query:
    """
    Screener for centralised-exchange (CEX) crypto pairs, sorted by 24 h volume descending.
    """
    q = Query()
    q.url = URL.format(market='crypto')
    q.query = {
        'markets': ['crypto'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': [
            'ticker-view',
            'exchange.tr',
            'provider-id',
            'close',
            'type',
            'typespecs',
            'pricescale',
            'minmov',
            'fractional',
            'minmove2',
            'currency',
            '24h_close_change|5',
            '24h_vol|5',
            '24h_vol_change|5',
            'TechRating_1D',
            'TechRating_1D.tr',
        ],
        'filter2': {
            'operator': 'and',
            'operands': [
                {'expression': {'left': 'centralization', 'operation': 'equal', 'right': 'cex'}}
            ],
        },
        'sort': {'sortBy': '24h_vol|5', 'sortOrder': 'desc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def crypto_dex() -> Query:
    """
    Screener for decentralised-exchange (DEX) spot pairs priced in USD, sorted by 24 h transaction
    count descending.
    """
    q = Query()
    q.url = URL.format(market='crypto')
    q.query = {
        'markets': ['crypto'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': [
            'ticker-view',
            'blockchain-id.tr',
            'blockchain-id',
            'exchange.tr',
            'provider-id',
            'close',
            'type',
            'typespecs',
            'pricescale',
            'minmov',
            'fractional',
            'minmove2',
            'currency',
            '24h_close_change|5',
            'dex_txs_count_24h',
            'dex_trading_volume_24h',
            'dex_txs_count_uniq_24h',
            'dex_total_liquidity',
            'fully_diluted_value',
            'TechRating_1D',
            'TechRating_1D.tr',
        ],
        'filter2': {
            'operator': 'and',
            'operands': [
                {
                    'operation': {
                        'operator': 'and',
                        'operands': [
                            {
                                'expression': {
                                    'left': 'centralization',
                                    'operation': 'equal',
                                    'right': 'dex',
                                }
                            },
                            {
                                'expression': {
                                    'left': 'currency_id',
                                    'operation': 'equal',
                                    'right': 'USD',
                                }
                            },
                        ],
                    }
                },
                {
                    'operation': {
                        'operator': 'or',
                        'operands': [
                            {
                                'operation': {
                                    'operator': 'and',
                                    'operands': [
                                        {
                                            'expression': {
                                                'left': 'type',
                                                'operation': 'equal',
                                                'right': 'spot',
                                            }
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                },
            ],
        },
        'sort': {'sortBy': 'dex_txs_count_24h', 'sortOrder': 'desc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def forex() -> Query:
    """
    Screener for forex currency pairs, sorted by traded value descending.
    """
    q = Query()
    q.url = URL.format(market='forex')
    q.query = {
        'markets': ['forex'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': ['name', 'close', 'volume', 'currency'],
        'sort': {'sortBy': 'Value.Traded', 'sortOrder': 'desc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def futures() -> Query:
    """
    Screener for futures contracts, sorted by traded value descending.
    """
    q = Query()
    q.url = URL.format(market='futures')
    q.query = {
        'markets': ['futures'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': ['name', 'close', 'volume', 'currency'],
        'sort': {'sortBy': 'Value.Traded', 'sortOrder': 'desc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def bond() -> Query:
    """
    Screener for bonds, sorted by S&P long-term rating descending.
    """
    q = Query()
    q.url = URL.format(market='bond')
    q.query = {
        'markets': ['bond'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': [
            'ticker-view',
            'exchange.tr',
            'source-logoid',
            'isin-displayed',
            'yield_to_worst',
            'close_pct',
            'close_net',
            'type',
            'typespecs',
            'fundamental_currency_code',
            'current_coupon',
            'maturity_date',
            'redemption_type.tr',
            'bond_issuer_type.tr',
            'bond_snp_rating_lt.tr',
            'bond_fitch_rating_lt.tr',
        ],
        'sort': {'sortBy': 'bond_snp_rating_lt', 'sortOrder': 'desc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def cfd() -> Query:
    """
    Screener for CFDs (contracts for difference), sorted by traded value descending.
    """
    q = Query()
    q.url = URL.format(market='cfd')
    q.query = {
        'markets': ['cfd'],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': ['name', 'close', 'volume', 'currency'],
        'sort': {'sortBy': 'Value.Traded', 'sortOrder': 'desc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def dividend_calendar(market: str = 'america') -> Query:
    """
    Screener for stocks with an upcoming ex-dividend date, sorted by ex-dividend date ascending.

    Returns only primary listings that have a known upcoming ex-dividend date, making it easy
    to build a dividend calendar for any market.

    Examples:

    >>> dividend_calendar().get_scanner_data()  # upcoming dividends in the US market
    >>> dividend_calendar('germany').get_scanner_data()

    To get dividends going ex in the next 7 days:

    >>> import time
    >>> now = int(time.time())
    >>> week = 7 * 24 * 3600
    >>> (dividend_calendar()
    ...  .where(
    ...      Column('dividend_ex_date_upcoming') > now,
    ...      Column('dividend_ex_date_upcoming') < now + week,
    ...  )
    ...  .get_scanner_data())

    :param market: Market/country to scan. Defaults to ``'america'``.
    """
    import time

    q = Query()
    q.url = URL.format(market=market)
    q.query = {
        'markets': [market],
        'symbols': {},
        'options': {'lang': 'en'},
        'columns': [
            'name',
            'close',
            'dividend_ex_date_upcoming',
            'dividend_payment_date_upcoming',
            'dps_common_stock_prim_issue_fq',
            'dividends_yield_current',
        ],
        'filter': [
            {'left': 'is_primary', 'operation': 'equal', 'right': True},
            {
                'left': 'dividend_ex_date_upcoming',
                'operation': 'greater',
                'right': int(time.time()),
            },
        ],
        'sort': {'sortBy': 'dividend_ex_date_upcoming', 'sortOrder': 'asc'},
        'range': DEFAULT_RANGE.copy(),
        'ignore_unknown_fields': False,
    }
    return q


def options(underlying: str) -> Query:
    """
    :param underlying: The underlying symbol to filter by, e.g. ``'CME_MINI:ESM2026'``.
    """
    q = Query()
    q.url = 'https://scanner.tradingview.com/options/scan2?label-product=options-builder'
    q.query = {
        'columns': [
            'ask',
            'bid',
            'currency',
            'delta',
            'expiration',
            'gamma',
            'iv',
            'option-type',
            'pricescale',
            'rho',
            'root',
            'strike',
            'theoPrice',
            'theta',
            'vega',
            'bid_iv',
            'ask_iv',
        ],
        'filter2': {
            'operator': 'and',
            'operands': [{'expression': {'left': 'type', 'operation': 'equal', 'right': 'option'}}],
        },
        'ignore_unknown_fields': False,
        'index_filters': [{'name': 'underlying_symbol', 'values': [underlying]}],
        'options': {'lang': 'en'},
        'range': DEFAULT_RANGE.copy(),
    }
    return q
