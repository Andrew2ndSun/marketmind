# MarketMind

Explainable stock research powered exclusively by Muse models through Meta Model API.
Start with the market radar: Muse connects current economic/business headlines to
10 stocks discovered from broad news coverage across industries, refreshed every two
hours in the background. Select one, or enter your own ticker, then inspect cited
findings and counterpoints, review historical risk,
and export the full evidence-backed report as JSON.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

Open http://127.0.0.1:8000. The entry point reads `MUSE_API_KEY` from your current process
or saved Windows User/Machine environment variables. `MODEL_API_KEY` is also supported.
Keys are never copied into project files or sent to the browser.

For other platforms, export `MUSE_API_KEY` and run:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The default model is `muse-spark-1.3`; optionally set `MUSE_MODEL` to another Muse
text model supported by chat completions. The endpoint is fixed to
`https://api.meta.ai/v1/chat/completions`. There are no alternate inference providers,
provider fallbacks, or fixed demo reports. Every successful research request calls Muse. Discovery runs every two hours in the
background, using Muse for news-led company
discovery and final selection. Its saved result is shared across page loads and restarts.
Yahoo Finance via yfinance supplies financial evidence, not model inference.

An optional local `.env` can define the same variables; process variables take precedence.
Restart the server after changing its configuration.

## Source layout

```text
marketmind/
  app.py          FastAPI routes and dashboard serving
  config.py       Muse model and server-side key settings
  data.py         Yahoo prices, fundamentals, and ticker news
  discovery_data.py  Broad news feeds and company/quote verification
  discovery.py    News-led Muse discovery, selection and source handoff
  discovery_store.py  Durable snapshots and two-hour background schedule
  metrics.py      Historical returns, volatility, and drawdown
  muse.py         Direct HTTP calls to the official Muse API
  prompts.py      Evidence-constrained research instructions
  research.py     Evidence collection and research orchestration
  schemas.py      Validated report structure
  validation.py   Citation-ID validation
  errors.py       Safe workflow errors
  web/            HTML, CSS, and browser JavaScript
tests/            Offline test data and regression suite
main.py           Server entry point, .env and saved Windows environment loading
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health |
| GET | `/api/research/status` | Muse configuration presence, without secrets |
| POST | `/api/research` | Live financial evidence plus cited Muse research |
| GET | `/api/discovery` | Read-only saved 10-stock radar, age and schedule status |

Request example:

```json
{
  "ticker": "AMD",
  "question": "What does recent evidence suggest about this stock, and what challenges that story?"
}
```

Interactive API documentation: http://127.0.0.1:8000/docs.
Missing credentials or insufficient price history return 503. Muse failures,
truncated replies, malformed JSON, and invalid citation IDs return 502.
A configured status does not guarantee model access or provider availability.

## Verify

```powershell
python -m unittest discover -s tests -v
```

Tests use mocked HTTP and invented data confined to `tests/`; they make no live API
calls. They cover the full API pipeline, official endpoint restriction, key handling,
invalid output, provider errors, removed routes, news formats, historical risk math,
full-headline batch coverage, symbol verification, durable scheduling, read-only page
loads, failed-update retention and original-source handoff. The suite has 31 tests.

## Limits

Daily adjusted closes exclude today's session, including after market close. Risk
metrics describe the collected historical window; they do not forecast prices or
returns. News and fundamentals can be unavailable and are flagged in the report.
Citation IDs are checked, but source truth and factual support are not automatically
verified. This local demo has no public authentication or rate limiting.

Educational research only. Not investment advice.

See [HACKATHON.md](HACKATHON.md) for the presentation and prior-work disclosure.

## Hackathon submission readiness

See [the participant-guide audit](docs/HACKATHON_AUDIT.md),
[original contributions](docs/ORIGINAL_CONTRIBUTIONS.md), and
[three-minute demo script](docs/DEMO_SCRIPT.md).
Run `python scripts/check_submission.py` for explicit remaining submission gates.
A local working app is not a completed hackathon submission.

## Market radar

The server scans in the background at startup if no recent result exists, then every
two hours after a successful scan. Opening the page never starts a scan. The page
reads the saved list immediately and checks for updates every minute; Reload saved
list only fetches the saved result. On a fresh installation the page shows a pending
message while the first background scan runs. Manual ticker research stays available.

Discovery starts from news, with no fixed stock watchlist or activity screener. It
reads every dated item from the last seven days in nine configured feeds: CNBC
markets, economy, world, finance, technology and energy; BBC business and technology;
and Federal Reserve press releases. Duplicate stories are removed. Muse reviews all
collected headlines in batches of 80 and proposes news-linked companies, including
possible indirect macroeconomic effects. Company search and fresh equity quotes
independently verify the proposed symbols. Muse then selects exactly ten verified
stocks, each with its own quote citation, a headline citation, a reason and a risk.
The demo focuses on US-listed equities and ADRs. Feed coverage is broad but does not
include every market story or full articles. No fixed first-30 candidate list is used.

Results are atomically saved to ignored `.cache/market-radar/latest.json`, so restarts
reuse a recent list. A failed scan preserves the previous list, displays an overdue
indicator and retries after 15 minutes. The two-hour interval is checked every 30
seconds while the server is running. This demo uses one server process; run one
Uvicorn worker. When the server is stopped no job runs; restart catches up if due.

A card's Research button fills the question and symbol; Investigate remains a separate
user action. The optional `discovery_created_at` request field identifies the saved
scan. Its original headline and quote evidence can be included in deep research with
R-prefixed IDs while it remains the latest scan and is less than 24 hours old.
Replaced/expired context produces an explicit warning. Generated radar claims are
never reused as evidence. Quotes shown on cards are saved at scan time and may be
delayed; they do not update live. These candidates are research starting points,
not buy recommendations or predicted winners. Economic connections are hypotheses.

## Demo and source package

The captioned local walkthrough is `artifacts/marketmind-demo.webm`. It demonstrates
the saved news radar, explicit Muse research, citations, counterpoints, risk, export
and new event code. `submission/VERIFICATION.md` records its measured duration and
evidence. Optional recording instructions are in `docs/DEMO_SCRIPT.md`. Videos, saved
news/quotes and exported reports remain ignored by Git. The review archive
`artifacts/MarketMind-source-review.zip` contains tracked source only.

The entry is solo, Indie Developer, with Andrew2ndSun as representative. Public video
hosting, rights confirmation, official rules acceptance and CV submission remain
participant actions; they are not established by a successful local demonstration.
