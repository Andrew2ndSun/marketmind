"""Descriptive risk calculations over completed daily adjusted closes."""
import math
import numpy as np
from .errors import ResearchUnavailable

def historical_metrics(prices):
    prices = prices.sort_index()
    if prices.index.has_duplicates:
        raise ResearchUnavailable("Duplicate price dates; cannot establish a reliable history.")
    values = prices.to_numpy(dtype=float)
    if len(values) < 30 or not np.isfinite(values).all() or (values <= 0).any():
        raise ResearchUnavailable("At least 30 finite, positive completed daily closes are required.")
    returns = prices.pct_change().dropna()
    return {
        "last_adjusted_close": round(float(values[-1]), 4),
        "last_bar_date": prices.index[-1].date().isoformat(),
        "bars": len(values),
        "one_day_return_pct": round(float(returns.iloc[-1]) * 100, 2),
        "twenty_session_return_pct": round((values[-1] / values[-21] - 1) * 100, 2),
        "annualized_volatility_pct": round(float(returns.std(ddof=1)) * math.sqrt(252) * 100, 2),
        "max_drawdown_pct": round(float((prices / prices.cummax() - 1).min()) * 100, 2),
        "window_start": prices.index[0].date().isoformat(),
    }
