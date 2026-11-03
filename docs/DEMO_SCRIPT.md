# Three-minute demo script

Record the real Muse-backed workflow in at most 180 seconds. The opening shows a
saved scheduled scan, followed by one explicitly requested live stock investigation.
Keep keys, System Properties and account/billing screens out of the recording.

| Time | Screen | Narration / caption |
| --- | --- | --- |
| 0:00-0:09 | Saved radar and last-scan time | Muse scans broad economic and business news every two hours. Opening the page reads the saved top ten and makes no model call. |
| 0:09-0:18 | Stock cards, reasons, risks and citations | Discovery begins with news across industries, without a fixed stock watchlist. Companies and quotes are verified before final selection. |
| 0:18-0:26 | Radar coverage and source method | Nine configured feeds provide broad coverage, not every internet story. All collected recent headlines are reviewed in batches. Prices are saved snapshots. |
| 0:26-0:33 | Select a card; research form | I built scheduled discovery, Muse integration, cited reports and validation on an earlier data-fetching foundation. Selection fills the form; Investigate is a separate action. |
| 0:33-1:15 | Explicit Investigate request and research brief | One real Muse call reasons over stock-specific evidence and original radar sources. Missing evidence remains visible; no canned report is substituted. |
| 1:15-1:31 | Follow a claim to evidence | Inspect numeric data and linked sources. R-prefixed IDs carry original radar evidence into research. Checked citation IDs do not establish factual truth. |
| 1:31-1:48 | Findings and counterpoints | Compare the narrative with opposing evidence. Report ticker-news and radar-headline counts separately, including any missing ticker news. |
| 1:48-2:05 | Risk and unanswered questions | Historical volatility and drawdown describe the observed window, not a forecast. No trades or promised returns. |
| 2:05-2:19 | Research method and Muse metadata | Show the actual model ID and token usage. Credentials stay on the server. |
| 2:19-2:31 | Export JSON | Export the findings, original evidence, risk calculations, gaps and inference metadata together. |
| 2:31-2:46 | New scheduling code | Explain the two-hour due check, atomic publication and last-good-list retention on failure. Tests cover schedule, persistence and citation failures. |
| 2:46-2:55 | Return to product | Discover, question, inspect. Build for Your World. Prior work is acknowledged; educational research only. |

## Reproduce the recording

1. Run `python main.py` with `MUSE_API_KEY` configured.
2. Allow the first scheduled scan to finish. The radar must have a fresh real list
   before recording; the recorder does not force a scan or invent candidates.
3. Install optional recording tools if needed: `python -m pip install playwright`
   and `python -m playwright install chromium`.
4. Run `python scripts/record_demo.py`. It records the first selected stock and one
   real Muse investigation, including original-source handoff and a JSON download.
5. Inspect `artifacts/recording-receipt.json`, measure the video duration and review
   playback. Upload only through a hosting service authorized by the builder.

The recorder preserves the previous video/report/receipt in ignored
`artifacts/previous-demo/`. The current draft is `artifacts/marketmind-demo.webm`,
with captions and no audio narration. The current version is 175.60 seconds; full
local playback and 13 sampled-frame checks passed. See `submission/VERIFICATION.md`
for evidence and tested feature coverage. Public hosting and signed-out playback checks
remain pending. Do not describe a local video as a submitted or publicly accessible demo.
