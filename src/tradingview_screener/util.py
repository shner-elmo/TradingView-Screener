from __future__ import annotations


# see issue: https://github.com/shner-elmo/TradingView-Screener/issues/12
def format_technical_rating(rating: float) -> str:
    if rating >= 0.5:
        return 'Strong Buy'
    elif rating >= 0.1:
        return 'Buy'
    elif rating >= -0.1:
        return 'Neutral'
    elif rating >= -0.5:
        return 'Sell'
    # elif x >= -0.1:
    else:
        return 'Strong Sell'
