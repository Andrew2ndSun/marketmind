# MarketMind - Meta Global AI Developer Hackathon

**Theme:** Build for Your World. **Track:** Indie Developer.
**Solo contributor and representative:** Andrew2ndSun.
The builder reports that organizers accepted this project for the indie track.

## The problem

A stock chart shows what moved; one headline can create false confidence about why.
MarketMind helps users inspect a narrative through cited market observations,
counterarguments, historical risk, and unanswered questions.

## Three-minute walkthrough

1. Open the local dashboard with your Windows `MUSE_API_KEY` configured.
2. Ask: "What could explain AMD's recent movement, and what challenges that story?"
3. Show the research brief and follow a citation into the evidence trail.
4. Compare supporting findings with counterpoints. Explain the limits of causal claims.
5. Show historical volatility/drawdown and the unanswered questions.
6. Export the JSON and show the Muse model ID and usage metadata.

Every report uses live financial inputs and a real Muse API request. If news is
missing, explain that gap; the model must not invent a news-based catalyst.

## Implementation

A bounded pipeline collects completed daily adjusted closes, fundamentals, and up
to eight deduplicated ticker news excerpts from Yahoo Finance. It computes descriptive
historical risk, then calls a Muse model at Meta's official chat-completions endpoint.
The response must match the structured report schema and use supplied evidence IDs.
Malformed, truncated, or invalidly cited responses fail explicitly. There is no model
provider fallback and no fixed narrative substituted for a Muse response.

The UI links claims to sources, presents counterarguments and unknowns, and exports
complete evidence and model metadata. This is a research pipeline; it does not execute
trades or claim an independently verified causal explanation.

## Prior-work disclosure

The earlier stock-research prototype supplied the foundation and initial
market-data integration. Hackathon work introduced the MarketMind experience, cited
structured synthesis, counterpoints and uncertainty, historical risk presentation,
Muse Model API integration, JSON export, and focused reliability tests.

This repository has since been reduced to the MarketMind application. Legacy trading,
allocation, backtesting, paper tracking, other model integrations, capstone documents,
and historical output artifacts were removed. Disclose the prior foundation in any
submission and check reuse rules against the organizer's final official rules.

## Verification and limits

Run `python -m unittest discover -s tests -v`. Offline tests check software behavior;
they do not establish investment performance, factual accuracy, or model quality.
Citation-ID coverage is a linkage check, not an entailment or truth score. Fundamentals
are current provider snapshots with unverified reporting periods, not point-in-time
filings. Headline excerpts are not full-article verification. Historical daily-close
risk can miss intraday losses and does not bound future outcomes.

API references: [Meta quickstart](https://dev.meta.ai/docs/quickstart) and
[chat completions](https://dev.meta.ai/docs/protocols/chat-completions).

No submission or public deployment is performed by this project.

## Participant-guide readiness

The detailed [audit](docs/HACKATHON_AUDIT.md) is the submission source of truth.
Read the [file-level contribution map](docs/ORIGINAL_CONTRIBUTIONS.md) before recording
or submitting. Organizer acceptance as an Indie Developer candidate was confirmed by
the builder; the earlier foundation and new event work remain explicitly distinguished.

Prepared CV wording is in [submission/DRAFT.md](submission/DRAFT.md). Record verified
team, link and eligibility details in `submission/project.json`, then run:

```powershell
python scripts/check_submission.py --run-tests --output artifacts/preflight.json
```

Exit code 2 means submission gates remain pending. Do not treat local test success as
proof of public access, personal eligibility, accepted rules, claimed credits or submission.

The [timed script](docs/DEMO_SCRIPT.md) describes the three-minute walkthrough.
`scripts/record_demo.py` can record a real captioned walkthrough of a running local
app when the optional Playwright package/browser are available. It never mocks the
model response and fails if the live request cannot complete its recording segment.
Generated videos/reports are saved in ignored `artifacts/`, not in the public source.

The deadline in the supplied guide is November 4, 2026 at 6:00 PM Pacific / 9:00 PM
Eastern. The representative must submit once on CV and verify all public links.
