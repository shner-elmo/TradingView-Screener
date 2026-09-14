"""Query-copy regressions: no scanner requests are made."""
import pytest

from tradingview_screener.query import Query
from tradingview_screener.screeners import forex, options


@pytest.mark.parametrize('original', [forex(), options('NASDAQ:AAPL'), Query()])
def test_copy_preserves_endpoint_and_independent_nested_state(original):
    clone = original.copy()
    assert clone == original
    assert clone is not original
    assert clone.url == original.url
    original_range = original.query['range'][:]
    clone.offset(17).limit(31)
    assert original.query['range'] == original_range
    assert clone.query['range'] == [17, 31]
    original.query.setdefault('symbols', {})['tickers'] = ['NASDAQ:AAPL']
    independent = original.copy()
    independent.query['symbols']['tickers'].append('NASDAQ:MSFT')
    assert original.query['symbols']['tickers'] == ['NASDAQ:AAPL']
