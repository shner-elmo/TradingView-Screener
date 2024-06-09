import pytest

from tradingview_screener.query import Query, Column


@pytest.mark.parametrize(
    ['markets', 'expected_url'],
    [
        (['crypto'], 'https://scanner.tradingview.com/crypto/scan'),
        (['forex'], 'https://scanner.tradingview.com/forex/scan'),
        (['america'], 'https://scanner.tradingview.com/america/scan'),
        (['israel'], 'https://scanner.tradingview.com/israel/scan'),
        (['america', 'israel'], 'https://scanner.tradingview.com/global/scan'),
        (['crypto', 'israel'], 'https://scanner.tradingview.com/global/scan'),
    ],
)
def test_set_markets(markets: list[str], expected_url: str):
    q = Query().set_markets(*markets)

    assert q.url == expected_url
    assert q.query['markets'] == markets  # pyright: ignore [reportTypedDictNotRequiredAccess]


def test_limit_and_offset():
    from tradingview_screener.query import DEFAULT_RANGE

    original_range = DEFAULT_RANGE.copy()

    _, df = Query().get_scanner_data()
    assert len(df) == DEFAULT_RANGE[1]

    _, df = Query().limit(10).get_scanner_data()
    assert len(df) == 10

    _, df = Query().offset(10).get_scanner_data()
    assert len(df) == DEFAULT_RANGE[1] - 10

    _, df = Query().offset(10).limit(15).get_scanner_data()
    assert len(df) == 5

    # finally we want to make sure that `offset()` or `limit()` dont mutate `DEFAULT_RANGE`
    # (happens if we dont copy the
    assert DEFAULT_RANGE == original_range


def test_order_by():
    _, df = Query().select('close').order_by('close', ascending=True).get_scanner_data()
    assert df['close'].is_monotonic_increasing

    _, df = Query().select('close').order_by('close', ascending=False).get_scanner_data()
    assert df['close'].is_monotonic_decreasing

    _, df = (
        Query()
        .select('dividends_yield_current')
        .order_by('dividends_yield_current', nulls_first=True)
        .get_scanner_data()
    )
    assert df['dividends_yield_current'].isna().is_monotonic_decreasing

    _, df = (
        Query()
        .select('dividends_yield_current')
        .order_by('dividends_yield_current', nulls_first=False)
        .get_scanner_data()
    )
    assert df['dividends_yield_current'].isna().is_monotonic_increasing


def test_query_above_pct():
    count, df = (
        Query().where(Column('close').above_pct('price_52_week_low', 0.99)).get_scanner_data()
    )
    assert count >= 0

    count, _ = Query().where(Column('close').above_pct('price_52_week_low', 1)).get_scanner_data()
    assert count == 0

    count, _ = (
        Query().where(Column('close').above_pct('price_52_week_low', 1.01)).get_scanner_data()
    )
    assert count == 0

    _, df = Query().where(Column('close').above_pct('price_52_week_high', 0.99)).get_scanner_data()
    df['pct'] = df[['price_52_week_high', 'close']].pct_change(axis=1)['close']
    assert df['pct'].min() > 0.03


def test_get_scanner_data():
    # make sure that we raise an exception when the status code is not ok
    from requests import HTTPError

    with pytest.raises(HTTPError):
        Query().limit(-5).get_scanner_data()


def test_and_or_chaining():
    from tradingview_screener.default_screeners import stock_screener2, etf_screener

    # this dictionary/JSON was taken from the website, to make sure its reproduced correctly from
    # the function calls.
    dct = {
        'operator': 'and',
        'operands': [
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
                                            'right': 'stock',
                                        }
                                    },
                                    {
                                        'expression': {
                                            'left': 'typespecs',
                                            'operation': 'has',
                                            'right': ['common'],
                                        }
                                    },
                                ],
                            }
                        },
                        {
                            'operation': {
                                'operator': 'and',
                                'operands': [
                                    {
                                        'expression': {
                                            'left': 'type',
                                            'operation': 'equal',
                                            'right': 'stock',
                                        }
                                    },
                                    {
                                        'expression': {
                                            'left': 'typespecs',
                                            'operation': 'has',
                                            'right': ['preferred'],
                                        }
                                    },
                                ],
                            }
                        },
                        {
                            'operation': {
                                'operator': 'and',
                                'operands': [
                                    {
                                        'expression': {
                                            'left': 'type',
                                            'operation': 'equal',
                                            'right': 'dr',
                                        }
                                    }
                                ],
                            }
                        },
                        {
                            'operation': {
                                'operator': 'and',
                                'operands': [
                                    {
                                        'expression': {
                                            'left': 'type',
                                            'operation': 'equal',
                                            'right': 'fund',
                                        }
                                    },
                                    {
                                        'expression': {
                                            'left': 'typespecs',
                                            'operation': 'has_none_of',
                                            'right': ['etf'],
                                        }
                                    },
                                ],
                            }
                        },
                    ],
                }
            }
        ],
    }
    assert stock_screener2.query['filter2'] == dct  # pyright: ignore [reportTypedDictNotRequiredAccess]

    dct = {
        'operator': 'and',
        'operands': [
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
                                            'left': 'typespecs',
                                            'operation': 'has',
                                            'right': ['etn'],
                                        }
                                    }
                                ],
                            }
                        },
                        {
                            'operation': {
                                'operator': 'and',
                                'operands': [
                                    {
                                        'expression': {
                                            'left': 'typespecs',
                                            'operation': 'has',
                                            'right': ['etf'],
                                        }
                                    }
                                ],
                            }
                        },
                        {
                            'operation': {
                                'operator': 'and',
                                'operands': [
                                    {
                                        'expression': {
                                            'left': 'type',
                                            'operation': 'equal',
                                            'right': 'structured',
                                        }
                                    }
                                ],
                            }
                        },
                    ],
                }
            }
        ],
    }
    assert etf_screener.query['filter2'] == dct  # pyright: ignore [reportTypedDictNotRequiredAccess]
