# MarketMind

Explainable stock research powered exclusively by Muse models through Meta Model API.
Ask about a stock, inspect cited findings and counterpoints, review historical risk,
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
provider fallbacks, or fixed demo reports. Every successful research request calls Muse.
Yahoo Finance via yfinance supplies financial evidence, not model inference.

An optional local `.env` can define the same variables; process variables take precedence.
Restart the server after changing its configuration.

## Source layout

```text
marketmind/
  app.py          FastAPI routes and dashboard serving
  config.py       Muse model and server-side key settings
  data.py         Yahoo prices, fundamentals, and ticker news
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
