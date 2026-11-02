"""Collect evidence, measure historical risk and request a cited Muse report."""
import time
from datetime import datetime, timezone

from .config import require_muse
from .data import live_inputs
from .metrics import historical_metrics
from .muse import synthesize
from .validation import validate_citations


def research(ticker: str, question: str, discovery_created_at: str | None = None) -> dict:
    started = time.monotonic()
    require_muse()  # Fail before fetching data if no Muse key is available.
    prices, fundamentals, news, warnings = live_inputs(ticker)
    metrics = historical_metrics(prices)
    age = (datetime.now(timezone.utc).date() - prices.index[-1].date()).days
    if age > 5:
        warnings.append(f"Price history is stale: last bar is {age} calendar days old.")
    now = datetime.now(timezone.utc).isoformat()
    evidence = [
        {"id": "M1", "kind": "market", "title": "Completed daily adjusted closes and computed historical risk",
         "data": metrics, "url": f"https://finance.yahoo.com/quote/{ticker}/history/",
         "publisher": "Yahoo Finance via yfinance", "retrieved_at": now},
        {"id": "F1", "kind": "fundamentals", "title": "Company fundamentals (provider snapshot; reporting period unverified)",
         "data": fundamentals, "url": f"https://finance.yahoo.com/quote/{ticker}/key-statistics/",
         "publisher": "Yahoo Finance via yfinance", "retrieved_at": now},
        *[{"id": f"N{i}", "kind": "news", "retrieved_at": now, **article} for i, article in enumerate(news, 1)],
    ]
    if discovery_created_at:
        from .discovery import research_context
        context = research_context(ticker, discovery_created_at)
        if context:
            evidence.extend(context)
        else:
            warnings.append("The selected market-radar snapshot expired or changed. This report uses stock-specific evidence only; rescan to restore the economic context.")
    result, inference = synthesize(question, evidence)
    validate_citations(result, evidence)
    return {
        "ticker": ticker, "question": question, "mode": "live", "created_at": now,
        "company": fundamentals["company"], "currency": fundamentals["currency"],
        "metrics": metrics,
        "price_history": [{"date": index.date().isoformat(), "close": round(float(value), 4)} for index, value in prices.items()],
        "evidence": evidence, "research": result.model_dump(), "inference": inference,
        "quality": {
            "citation_id_coverage_pct": 100, "citation_support_verified": False,
            "news_count": len(news), "warnings": warnings,
            "limitations": [
                "Citation IDs are validated; source truth and claim entailment are not automatically verified.",
                "Daily adjusted closes exclude today's session. Fundamentals are current snapshots, not point-in-time filings.",
                "Yahoo ticker news may include broad or unrelated stories; relevance is assessed by Muse.",
                "Historical risk is descriptive, not a price forecast or calibrated probability.",
            ],
        },
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "disclaimer": "Educational research only. Not investment advice.",
    }
