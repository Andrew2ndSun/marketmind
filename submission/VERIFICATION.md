# Current verification record - November 2, 2026

This record describes the current scheduled news-led MarketMind workflow. Earlier
recordings and receipts are superseded and retained locally in ignored artifacts.

## Application and scheduled discovery

- **31 offline tests pass.** Coverage includes official Muse routing, key handling,
  schema/citation/truncation failures, numerical risk, full-headline batch coverage,
  company/quote verification, the two-hour schedule, durable results, concurrent-job
  prevention, read-only page requests, failed-update retention and source handoff.
- A real Muse scan reviewed **158 recent headlines**, independently verified **47
  companies**, and saved **10 stocks**. All nine configured feeds returned usable
  recent stories with no source warnings. The scan used three Muse calls.
- Desktop (1440px) and mobile (390px) checks passed: ten cards, no horizontal overflow,
  no JavaScript errors and no automatic research requests on selection. Page loading
  and saved-list reloading did not change the snapshot or trigger inference.
- A server restart reused the durable list without another model call. The server
  must remain running for scheduled updates; this demo supports one worker.
- Coverage is all recent items returned by the configured feeds, not every market
  story or every exchange. The equity focus is US listings and ADRs. Quotes are saved
  snapshots and may be delayed. Economic links are research hypotheses.

Evidence: ignored `artifacts/scheduled-radar-verification.json` and saved runtime data
in `.cache/market-radar/`. Cached news, quotes and reports are excluded from Git.

## Updated real demo

- Local video: `artifacts/marketmind-demo.webm`, **175.60 seconds** (2:55.60).
- Recorded November 2, 2026, Pacific time; captions only, with no audio narration.
- Full local browser playback passed. Thirteen timestamped frames were visually
  inspected across the complete presentation. No recording browser errors occurred.
- Shows the saved two-hour radar, broad news coverage and method, card selection,
  explicit live research, citations, original radar sources, counterpoints, historical
  risk, Muse metadata, JSON export, and new scheduling code with prior work disclosed.
- Exactly **one** investigation was explicitly requested, for **AAPL**.
- Real inference: `muse-spark-1.3`, `meta-model-api`,
  **1,427 input / 2,248 output tokens**.
- Research received **2 original radar headlines** and its own quote source.
  The provider returned **0 separate ticker-news excerpts**. The recording and report
  make that gap explicit; the original radar sources remain available for inspection.
- `artifacts/demo-report.json` is the actual downloaded research/evidence export.
- Receipt: `artifacts/recording-receipt.json`; sampled frames use
  `artifacts/demo-current-*.png`. Previous video/report/receipt: `artifacts/previous-demo/`.
- Video SHA-256: `80868a3f28faa09ec796b868b781e68efc08e2c84e1d7be11844f4c4863166d6`.

## Source publication and packaging

Public source: https://github.com/Andrew2ndSun/marketmind. Public visibility and an
unauthenticated README download were previously verified. The offline GitHub Actions
workflow for the scheduled-discovery implementation passed. Current source updates
and hosted check status are recorded by the latest repository commit/Actions run.

`artifacts/MarketMind-source-review.zip` is regenerated from tracked source. Its
commit, file count and SHA-256 are in `artifacts/source-package-receipt.json`.
It excludes credentials, runtime snapshots, generated reports and video.

The source secret-pattern check and whitespace check pass. Pattern scanning has
limits and does not establish rights, complete secret absence or platform compliance.

## Remaining participant actions

Public video hosting and signed-out playback are **pending**. No public product
hosting or CV submission is claimed. The entry is solo, Indie Developer, with
Andrew2ndSun as contributor/representative; organizer acceptance of the earlier
foundation is builder-reported. Rights confirmation, official rule acceptance,
individually claimed credits and final submission remain participant actions.
The initial idea suggestion from a classmate is acknowledged in the contribution map.

Run `python scripts/check_submission.py --run-tests --output artifacts/preflight.json`.
A passing local demo does not mean every submission gate is complete. The supplied
deadline is November 4, 2026 at 6:00 PM Pacific / 9:00 PM Eastern.
