"""Yahoo Finance price history, fundamentals and ticker news."""
import logging
import math
from urllib.parse import urlparse
import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)

def _spot_price(ticker: str) -> float | None:
    """Current spot price from fast_info — different API path than history()."""
    try:
        fi = yf.Ticker(ticker).fast_info
        p  = getattr(fi, "last_price", None) or getattr(fi, "regularMarketPrice", None)
        return float(p) if p else None
    except Exception:
        return None

def _history(ticker: str, lookback_days: int) -> pd.DataFrame:
    """Shared history fetch with split-repair enabled."""
    return yf.Ticker(ticker).history(
        period=f"{lookback_days}d",
        auto_adjust=True,
        repair=True,
    )

def fetch_price_history(ticker: str, lookback_days: int = 120) -> pd.Series:
    """Daily adjusted close prices, sorted ascending. Returns empty Series on failure."""
    try:
        df = _history(ticker, lookback_days)
        if df.empty or "Close" not in df.columns:
            return pd.Series(dtype=float)
        s = df["Close"].dropna()
        s.index = pd.to_datetime(s.index).tz_localize(None)
        s = s.sort_index()
        today = pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()
        s = s.loc[s.index < today]

        # Cross-check last close against fast_info spot price.
        # If they differ by more than 3× either way, the history is likely wrong
        # (stale split adjustment or wrong security).
        spot = _spot_price(ticker)
        if spot and spot > 0 and not s.empty:
            ratio = float(s.iloc[-1]) / spot
            if not (0.33 <= ratio <= 3.0):
                log.warning(
                    "price_history %s: last close $%.2f vs spot $%.2f (ratio %.2f) — "
                    "possible split-adjustment error; returning empty",
                    ticker, float(s.iloc[-1]), spot, ratio,
                )
                return pd.Series(dtype=float)
        return s
    except Exception as exc:
        log.warning("price_history %s: %s", ticker, exc)
        return pd.Series(dtype=float)

def safe_url(value):
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    return value if parsed.scheme in ("http", "https") and parsed.hostname else None

def normalize_news(articles):
    """Accept both modern yfinance content envelopes and legacy article records."""
    records, seen = [], set()
    for article in articles or []:
        content = article.get("content") or article
        title = content.get("title")
        link = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
        url = safe_url(link.get("url") if isinstance(link, dict) else link)
        url = url or safe_url(content.get("link"))
        if not title or not url or url in seen:
            continue
        seen.add(url)
        provider = content.get("provider") or {}
        records.append({
            "title": str(title)[:500], "url": url,
            "publisher": str(provider.get("displayName") or content.get("publisher") or "Unknown")[:120],
            "published_at": content.get("pubDate") or content.get("providerPublishTime"),
            "excerpt": str(content.get("summary") or "")[:1800],
        })
        if len(records) == 8:
            break
    return records

def live_inputs(ticker):
    prices = fetch_price_history(ticker, 365)
    warnings = []
    security = yf.Ticker(ticker)
    try:
        info = security.info or {}
    except Exception:
        info = {}
        warnings.append("Fundamentals unavailable from Yahoo Finance.")
    fundamentals = {"company": info.get("shortName") or ticker, "currency": info.get("currency"),
                    "trailing_pe": info.get("trailingPE"), "revenue_growth": info.get("revenueGrowth"),
                    "debt_to_equity": info.get("debtToEquity")}
    for key, value in fundamentals.items():
        if isinstance(value, float) and not math.isfinite(value):
            fundamentals[key] = None
    try:
        news = normalize_news(security.news)
    except Exception:
        news = []
    if not news:
        warnings.append("No usable ticker news returned. A price move's cause cannot be established.")
    return prices, fundamentals, news, warnings
