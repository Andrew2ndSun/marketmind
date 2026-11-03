"""Broad economic/business RSS collection and news-led company verification."""
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

FEEDS = (
    ("CNBC markets", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
    ("CNBC economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"),
    ("CNBC world", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362"),
    ("CNBC finance", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"),
    ("CNBC technology", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910"),
    ("CNBC energy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19836768"),
    ("BBC technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
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
    return sorted(records, key=lambda item: item["published_at"], reverse=True)


def fetch_headlines(feed: tuple[str, str], now: datetime) -> list[dict]:
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        response = client.get(feed[1])
        response.raise_for_status()
        if len(response.content) > 2_000_000:
            raise ValueError("RSS feed exceeds collection limit")
        return parse_feed(response.content, feed[0], now)


def collect_news() -> tuple[list[dict], list[str]]:
    """Read every recent item in the configured feeds, without a stock watchlist."""
    now = datetime.now(timezone.utc)
    warnings, stories = [], []
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = [(feed[0], pool.submit(fetch_headlines, feed, now)) for feed in FEEDS]
        for name, future in jobs:
            try:
                items = future.result()
                if not items:
                    warnings.append(f"No headlines within seven days from {name}.")
                stories.extend(items)
            except Exception:
                warnings.append(f"Headline feed unavailable: {name}.")
    headlines, seen = [], set()
    for story in sorted(stories, key=lambda item: item["published_at"], reverse=True):
        key = story["title"].strip().casefold()
        if story["url"] in seen or key in seen:
            continue
        seen.update((story["url"], key))
        headlines.append(story)
    if not headlines:
        raise ResearchUnavailable("No recent market or economic headlines are available.")
    return headlines, warnings


def resolve_company(proposal: dict) -> dict | None:
    """Verify a Muse-proposed symbol against company search and a fresh equity quote."""
    try:
        matches = yf.Search(proposal["company"], max_results=8, news_count=0, timeout=15).quotes
        ticker = proposal["ticker"]
        if not any(q.get("symbol") == ticker and q.get("quoteType") == "EQUITY" for q in matches):
            return None
        info = yf.Ticker(ticker).get_info() or {}
        if info.get("symbol") != ticker or info.get("quoteType") != "EQUITY":
            return None
        price = number(info.get("regularMarketPrice"))
        change = number(info.get("regularMarketChangePercent"))
        stamp = number(info.get("regularMarketTime"))
        if price is None or price <= 0 or change is None or stamp is None:
            return None
        observed = datetime.fromtimestamp(stamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        if not now - timedelta(days=7) <= observed <= now + timedelta(minutes=10):
            return None
        return {"ticker": ticker, "company": str(info.get("longName") or info.get("shortName") or proposal["company"])[:160],
                "price": price, "change_pct": round(change, 2), "currency": info.get("currency"),
                "volume": number(info.get("regularMarketVolume")), "quote_at": observed.isoformat(),
                "sector": info.get("sector"), "industry": info.get("industry"),
                "news_evidence_ids": proposal["evidence_ids"]}
    except Exception:
        return None


def resolve_candidates(proposals: list[dict]) -> tuple[list[dict], list[str]]:
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(resolve_company, proposals))
    candidates, seen = [], set()
    for item in results:
        if item and item["ticker"] not in seen:
            seen.add(item["ticker"])
            candidates.append(item)
    if len(candidates) < 10:
        raise ResearchUnavailable("Fewer than 10 news-linked companies could be verified; keeping the previous scan.")
    warnings = []
    rejected = len(proposals) - len(candidates)
    if rejected:
        warnings.append(f"Excluded {rejected} proposed companies without unique verified fresh equity data.")
    return candidates, warnings
