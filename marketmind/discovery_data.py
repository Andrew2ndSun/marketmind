"""Live, bounded US-equity candidate pool and economic/business RSS headlines."""
import html
import math
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import httpx
import yfinance as yf

from .data import safe_url
from .errors import ResearchUnavailable

SCREENERS = ("most_actives", "day_gainers", "day_losers")
FEEDS = (
    ("CNBC markets", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
    ("CNBC economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"),
    ("BBC business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml"),
)


def number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def parse_feed(content: bytes, publisher: str, now: datetime) -> list[dict]:
    records = []
    for item in ET.fromstring(content).findall(".//item"):
        title, url = item.findtext("title"), safe_url(item.findtext("link"))
        try:
            published = parsedate_to_datetime(item.findtext("pubDate") or "")
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            published = published.astimezone(timezone.utc)
        except (ValueError, TypeError, OverflowError):
            continue
        if not title or not url or not now - timedelta(days=7) <= published <= now + timedelta(minutes=10):
            continue
        # Headlines and brief publisher excerpts only; never fetch full articles.
        excerpt = html.unescape(re.sub(r"<[^>]*>", " ", item.findtext("description") or ""))
        records.append({"title": html.unescape(title)[:400], "url": url,
                        "publisher": publisher, "published_at": published.isoformat(),
                        "excerpt": " ".join(excerpt.split())[:220]})
    return sorted(records, key=lambda item: item["published_at"], reverse=True)[:8]


def fetch_headlines(feed: tuple[str, str], now: datetime) -> list[dict]:
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        response = client.get(feed[1])
        response.raise_for_status()
        if len(response.content) > 2_000_000:
            raise ValueError("RSS feed exceeds collection limit")
        return parse_feed(response.content, feed[0], now)


def normalize_quotes(screens: list[tuple[str, list[dict]]], now: datetime) -> list[dict]:
    by_symbol = {}
    # Interleave feeds so one screener cannot fill the pool before another is seen.
    for position in range(25):
        for screen, rows in screens:
            if position >= len(rows):
                continue
            quote = rows[position]
            ticker = quote.get("symbol", "")
            if not re.fullmatch(r"[A-Z][A-Z0-9.=-]{0,11}", ticker) or quote.get("quoteType") != "EQUITY":
                continue
            if ticker in by_symbol:
                if screen not in by_symbol[ticker]["screeners"]:
                    by_symbol[ticker]["screeners"].append(screen)
                continue
            price = number(quote.get("regularMarketPrice"))
            change = number(quote.get("regularMarketChangePercent"))
            stamp = number(quote.get("regularMarketTime"))
            if price is None or price <= 0 or change is None or stamp is None:
                continue
            try:
                observed = datetime.fromtimestamp(stamp, tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                continue
            if not now - timedelta(days=7) <= observed <= now + timedelta(minutes=10):
                continue
            by_symbol[ticker] = {
                "ticker": ticker, "company": str(quote.get("shortName") or quote.get("longName") or ticker)[:160],
                "price": price, "change_pct": round(change, 2),
                "volume": number(quote.get("regularMarketVolume")), "currency": quote.get("currency"),
                "quote_at": observed.isoformat(), "screeners": [screen],
                "sector": quote.get("sector") or quote.get("sectorDisp"), "industry": quote.get("industry"),
            }
    return list(by_symbol.values())[:30]


def enrich_sector(candidate: dict) -> dict:
    candidate = dict(candidate)
    if not candidate["sector"] or not candidate["industry"]:
        try:
            info = yf.Ticker(candidate["ticker"]).get_info() or {}
            candidate["sector"] = info.get("sector") or candidate["sector"]
            candidate["industry"] = info.get("industry") or candidate["industry"]
        except Exception:
            pass
    return candidate


def collect_market() -> tuple[list[dict], list[dict], list[str]]:
    now = datetime.now(timezone.utc)
    warnings, screens, stories = [], [], []
    with ThreadPoolExecutor(max_workers=6) as pool:
        screen_jobs = [(name, pool.submit(yf.screen, name, count=25)) for name in SCREENERS]
        feed_jobs = [(feed[0], pool.submit(fetch_headlines, feed, now)) for feed in FEEDS]
        for name, future in screen_jobs:
            try:
                screens.append((name, (future.result() or {}).get("quotes", [])))
            except Exception:
                warnings.append(f"Yahoo screener unavailable: {name}.")
        for name, future in feed_jobs:
            try:
                items = future.result()
                if not items:
                    warnings.append(f"No headlines within seven days from {name}.")
                stories.extend(items)
            except Exception:
                warnings.append(f"Headline feed unavailable: {name}.")
        candidates = normalize_quotes(screens, now)
        if len(candidates) < 10:
            raise ResearchUnavailable("Fewer than 10 fresh stock candidates are available. Retry the market scan later.")
        candidates = list(pool.map(enrich_sector, candidates))
    headlines, seen = [], set()
    for story in stories:
        key = story["title"].strip().casefold()
        if story["url"] in seen or key in seen:
            continue
        seen.update((story["url"], key))
        headlines.append(story)
    if not headlines:
        raise ResearchUnavailable("No recent market or economic headlines are available. Retry the market scan later.")
    missing = sum(not candidate["sector"] for candidate in candidates)
    if missing:
        warnings.append(f"Sector metadata unavailable for {missing} candidates; industry links may be uncertain.")
    return candidates, headlines[:32], warnings
