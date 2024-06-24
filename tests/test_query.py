import pytest

from tradingview_screener.query import Query, And, Or
from tradingview_screener.column import col


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
    query = Query().select('close', 'price_52_week_low').limit(100_000)

    # `X > (X * 1)` should always be false.
    count, _ = query.where(
        col('price_52_week_low').above_pct('price_52_week_low', 1)
    ).get_scanner_data()
    assert count == 0

    # this test case whould also pass, but I guess the TV's 52-week-low is updated at the end of
    # the day or smth.
    # # `X > (X * 0.99)` should always be true.
    # n_stocks = Query().get_scanner_data()[0]
    # count, _ = query.where(
    #     col('price_52_week_low').above_pct('price_52_week_low', 0.9)
    # ).get_scanner_data()
    # assert count == n_stocks

    # WHERE `close` is 10% higher than the `price_52_week_low`
    _, df = query.where(col('close').above_pct('price_52_week_low', 1.1)).get_scanner_data()
    assert (df['close'] > df['price_52_week_low'] * 1.1).all()

    # WHERE `close` is 10% higher than the `price_52_week_low`
    _, df = query.where(col('close').below_pct('price_52_week_low', 1.1)).get_scanner_data()
    assert (df['close'] < df['price_52_week_low'] * 1.1).all()

    # WHERE `close` is 3x higher than the `price_52_week_low`
    _, df = query.where(col('close').above_pct('price_52_week_low', 3)).get_scanner_data()
    assert (df['close'] > df['price_52_week_low'] * 3).all()

    # WHERE `close` is below 50% from `price_52_week_high`
    _, df = (
        Query()
        .select('close', 'price_52_week_high')
        .where(col('close').below_pct('price_52_week_high', 0.5))
        .get_scanner_data()
    )
    assert (df['close'] < df['price_52_week_high'] * 0.5).all()


def test_between_and_not_between():
    query = Query().select('close', 'VWAP').limit(100_000)

    c, df = query.where(col('close').between_pct('VWAP', 1.1, 1.3)).get_scanner_data()
    assert df['close'].between(df['VWAP'] * 1.1, df['VWAP'] * 1.3).all()

    # this should be the opposite, so we use the  `~` operator to invert it
    c, df = query.where(col('close').not_between_pct('VWAP', 1.1, 1.3)).get_scanner_data()
    assert (~df['close'].between(df['VWAP'] * 1.1, df['VWAP'] * 1.3)).all()


def test_get_scanner_data():
    # make sure that we raise an exception when the status code is not ok
    from requests import HTTPError

    with pytest.raises(HTTPError):
        Query().limit(-5).get_scanner_data()


def test_and_or_chaining():
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
    query = Query().where2(
        And(
            Or(
                And(col('type') == 'stock', col('typespecs').has(['common'])),
                And(col('type') == 'stock', col('typespecs').has(['preferred'])),
                And(col('type') == 'dr'),
                And(col('type') == 'fund', col('typespecs').has_none_of(['etf'])),
            )
        )
    )
    assert query.query['filter2'] == dct  # pyright: ignore [reportTypedDictNotRequiredAccess]
    # make sure the API accepts this filtering
    count, _ = query.get_scanner_data()
    assert count > 0

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
    query = Query().where2(
        And(
            Or(
                And(col('typespecs').has(['etn'])),
                And(col('typespecs').has(['etf'])),
                And(col('type') == 'structured'),
            )
        )
    )
    assert query.query['filter2'] == dct  # pyright: ignore [reportTypedDictNotRequiredAccess]
    count, _ = query.get_scanner_data()
    assert count > 0
