# Verification record - November 2, 2026

## Verified locally

- Offline application regression suite: **10 tests passed**.
- Muse-only routing and credential handling, invalid JSON/citations/truncation,
  redirect refusal, API validation, risk math and news envelope behavior are tested.
- Staged-source whitespace check passed.
- Source key-pattern scan found no matching key-like values. This limited scan is
  not a guarantee; actual keys remain in the server environment, not the source.
- Real captioned demo recorded from the working app: **175.56 seconds** (2:55.56).
- Real inference: `muse-spark-1.3`, `meta-model-api`, 834 input / 1,841 output tokens.
- The recording run had **zero usable news excerpts**; the video and report make
  that limitation explicit and do not claim news-based causal attribution.
- Sample frames at 0:05, 1:20 and 2:36 were visually inspected for product content,
  evidence visibility, readable captions and real source-code presentation.
- Local video: `artifacts/marketmind-demo.webm`; no audio narration.
- `artifacts/` is ignored by Git. Demo reports and video are excluded from the
  reviewable source archive.

## Prepared, not externally verified

The source was published to https://github.com/Andrew2ndSun/marketmind using local
Git after the connector reported insufficient write permissions. Public visibility
and an unauthenticated README download were verified. Source, contribution disclosure,
configuration examples and tests are included; recordings and local exports are excluded.

The initial app source commit is fda90276092f4e4a92b196046cdd6f5c1f6cfefb. The offline
GitHub Actions workflow has started; consult the repository Actions page for current
hosted results. Local application tests passed. No CV submission is claimed.

The captioned demo is a local draft: check its full playback and add narration if
desired before hosting it. No public video URL or signed-out access has been verified.

The builder confirmed a solo Indie Developer entry, with Andrew2ndSun as contributor
and representative, and reports organizer acceptance of the adapted foundation.
Ownership/data rights, official rule acceptance, individually claimed credits and
final platform submission still require participant confirmation. A successful API call does not prove free credits applied.

Run `python scripts/check_submission.py --run-tests --output artifacts/preflight.json`
for remaining gates. Read docs/HACKATHON_AUDIT.md and ORIGINAL_CONTRIBUTIONS.md before
submission. Do not label this project fully compliant until pending items are resolved.

## Market-radar verification

The discovery feature was added after the original recording. The combined offline
suite now has **23 passing tests**. A live Muse scan selected 10 stocks from 30 valid
Yahoo activity candidates and 26 recent headlines, with no source warnings. Browser
checks passed at desktop and mobile widths for all ten cards, citations, cache refresh,
no automatic research on selection, and explicit manual research handoff. New tests
verify original-source transfer and expired-context warnings. The original recording
does not yet demonstrate the radar.
