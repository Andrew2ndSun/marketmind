# MarketMind

Explainable stock research powered exclusively by Muse models through Meta Model API.
Start with the market radar: Muse connects current economic/business headlines to
10 stocks drawn from live market screens. Select one, or enter your own ticker, then
inspect cited findings and counterpoints, review historical risk,
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
provider fallbacks, or fixed demo reports. Every successful research request calls Muse. Discovery uses its own Muse call,
shared across page loads through a 15-minute in-memory cache.
Yahoo Finance via yfinance supplies financial evidence, not model inference.

An optional local `.env` can define the same variables; process variables take precedence.
Restart the server after changing its configuration.

## Source layout

```text
marketmind/
  app.py          FastAPI routes and dashboard serving
  config.py       Muse model and server-side key settings
  data.py         Yahoo prices, fundamentals, and ticker news
  discovery_data.py  Activity screens, sector metadata and economic RSS feeds
  discovery.py    Validated 10-stock Muse selection, cache and source handoff
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
| GET | `/api/discovery` | Cached 10-stock market radar with themes and sources |

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
invalid output, provider errors, removed routes, news formats, and historical risk math.

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

The home page scans automatically. It combines up to 30 US-listed equity candidates
from Yahoo most-active, gainer and decliner screens with dated headlines from CNBC
markets/economy, BBC business and Federal Reserve feeds. Headlines and quotes older
than seven days are excluded. Sector/industry metadata comes from Yahoo snapshots.
Muse selects exactly 10 distinct symbols from the real pool and explains possible
industry links and risks. Each selection must cite its own quote and a headline.
These are attention-based research candidates, not predicted winners or a complete
market ranking. Economic connections are hypotheses, not verified price catalysts.

A card's Research button fills the question and symbol; Investigate remains a separate
user action. While the originating scan is available, its original headline and quote
sources are included in deep research with R-prefixed IDs. Expired/replaced context
produces an explicit warning. Muse-generated radar claims are not recycled as evidence.

`GET /api/discovery?refresh=true` requests a new scan, with a one-minute refresh
cooldown. Normal scans are cached 15 minutes per server process; restarting clears
the cache. A second in-flight scan returns 503. Missing data or invalid model output
never produces a canned top-ten list, and manual ticker research remains available.

The optional request field `discovery_created_at` identifies a selected server-side
scan. Clients do not submit arbitrary source payloads. Quotes may be delayed and
sources can be incomplete. No full news articles are downloaded.
