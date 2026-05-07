import pytest

from tradingview_screener.query import DEFAULT_RANGE, Query
from tradingview_screener.column import col
from tradingview_screener.screeners import (
    bond,
    cfd,
    coin,
    crypto,
    crypto_dex,
    forex,
    futures,
    options,
    stocks,
)


# --- unit tests (no network) ---


@pytest.mark.parametrize(
    ['factory', 'expected_market', 'expected_url'],
    [
        (stocks, 'america', 'https://scanner.tradingview.com/america/scan'),
        (crypto, 'crypto', 'https://scanner.tradingview.com/crypto/scan'),
        (crypto_dex, 'crypto', 'https://scanner.tradingview.com/crypto/scan'),
        (forex, 'forex', 'https://scanner.tradingview.com/forex/scan'),
        (futures, 'futures', 'https://scanner.tradingview.com/futures/scan'),
        (bond, 'bond', 'https://scanner.tradingview.com/bond/scan'),
        (cfd, 'cfd', 'https://scanner.tradingview.com/cfd/scan'),
        (coin, 'coin', 'https://scanner.tradingview.com/coin/scan'),
    ],
)
def test_standard_screener_url_and_market(factory, expected_market, expected_url):
    q = factory()
    assert q.url == expected_url
    assert q.query['markets'] == [expected_market]  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_stocks_custom_market():
    q = stocks('italy')
    assert q.url == 'https://scanner.tradingview.com/italy/scan'
    assert q.query['markets'] == ['italy']  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_standard_screeners_return_query_instance():
    for factory in (stocks, crypto, crypto_dex, forex, futures, bond, cfd, coin):
        assert isinstance(factory(), Query)


def test_coin_sort():
    q = coin()
    assert q.query['sort'] == {'sortBy': 'crypto_total_rank', 'sortOrder': 'asc'}  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_crypto_cex_filter():
    q = crypto()
    filter2 = q.query['filter2']  # pyright: ignore [reportTypedDictNotRequiredAccess]
    assert filter2['operator'] == 'and'
    assert {
        'expression': {'left': 'centralization', 'operation': 'equal', 'right': 'cex'}
    } in filter2['operands']


def test_crypto_dex_filter():
    q = crypto_dex()
    filter2 = q.query['filter2']  # pyright: ignore [reportTypedDictNotRequiredAccess]
    # top-level operator is 'and' with two operands (cex+USD block and spot block)
    assert filter2['operator'] == 'and'
    assert len(filter2['operands']) == 2


def test_bond_sort():
    q = bond()
    assert q.query['sort'] == {'sortBy': 'bond_snp_rating_lt', 'sortOrder': 'desc'}  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_options_url():
    q = options('NASDAQ:AAPL')
    assert q.url == 'https://scanner.tradingview.com/options/scan2?label-product=options-builder'


def test_options_no_markets_field():
    q = options('NASDAQ:AAPL')
    assert 'markets' not in q.query


def test_options_has_base_type_filter():
    q = options('NASDAQ:AAPL')
    filter2 = q.query['filter2']  # pyright: ignore [reportTypedDictNotRequiredAccess]
    assert filter2['operator'] == 'and'
    assert {'expression': {'left': 'type', 'operation': 'equal', 'right': 'option'}} in filter2[
        'operands'
    ]


def test_options_with_underlying():
    q = options('CME_MINI:ESM2026')
    assert q.query['index_filters'] == [  # pyright: ignore [reportTypedDictNotRequiredAccess]
        {'name': 'underlying_symbol', 'values': ['CME_MINI:ESM2026']}
    ]


def test_options_default_columns():
    q = options('NASDAQ:AAPL')
    assert 'delta' in q.query['columns']
    assert 'strike' in q.query['columns']
    assert 'iv' in q.query['columns']


def test_query_market_param():
    q = Query('crypto')
    assert q.url == 'https://scanner.tradingview.com/crypto/scan'
    assert q.query['markets'] == ['crypto']  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_query_default_market_unchanged():
    q = Query()
    assert q.url == 'https://scanner.tradingview.com/america/scan'
    assert q.query['markets'] == ['america']  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_screeners_do_not_share_range():
    q1 = stocks()
    q2 = crypto()
    q1.query['range'][0] = 99
    assert q2.query['range'][0] != 99


# --- integration tests ---


def test_stocks_returns_data():
    count, df = stocks().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_crypto_returns_data():
    count, df = crypto().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_coin_returns_data():
    count, df = coin().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_bond_returns_data():
    count, df = bond().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_crypto_dex_returns_data():
    count, df = crypto_dex().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_forex_returns_data():
    count, df = forex().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_futures_returns_data():
    count, df = futures().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_cfd_returns_data():
    count, df = cfd().limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_options_returns_data():
    # underlying_symbol is required by the API
    count, df = options('NASDAQ:AAPL').limit(5).get_scanner_data()
    assert count > 0
    assert len(df) == 5


def test_options_empty_result():
    """
    This is necessary to test the /scan2 API endpoint, because when the result its empty, the JSON is missing
    the `symbols` key. So make sure it handles that well.
    """
    count, df = (
        options('NASDAQ:AAPL').where(col('strike') > 12345290390).limit(10).get_scanner_data()
    )
    assert count == 0
    assert df.empty
