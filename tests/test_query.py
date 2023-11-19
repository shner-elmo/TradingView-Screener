import pytest

from tradingview_screener.query import Query


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
    assert q.query['markets'] == markets
