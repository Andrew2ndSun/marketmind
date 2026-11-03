# Participant-guide audit

Reviewed November 2, 2026 against the participant guide supplied by the builder.
This is an evidence inventory, not an organizer eligibility decision.

**Submission deadline: Wednesday, November 4, 2026, 6:00 PM Pacific / 9:00 PM Eastern.**
The guide's credit-claim deadline is the same. November 3 is the last full day
recommended for submission troubleshooting. Check Discord announcements for changes.

| Requirement | State | Evidence / remaining action |
| --- | --- | --- |
| One problem statement | Implemented | Build for Your World: discover news-linked stocks, then inspect equity narratives, counterarguments and historical risk. |
| Incorporate Meta models | Implemented and live-tested | Muse Spark 1.3, official Meta API only; no other model provider. |
| Public repository | Verified: source published and publicly readable | https://github.com/Andrew2ndSun/marketmind; private=false and unauthenticated README download returned HTTP 200. |
| Maximum four people; solo allowed | Builder confirmed | Indie Developer; Andrew2ndSun is the sole contributor and representative. |
| New work built during the event | Disclosure prepared; organizer acceptance reported by builder | See ORIGINAL_CONTRIBUTIONS.md. Builder confirmed organizers accepted this project as an indie candidate; no independent organizer record was inspected. |
| Clearly identify new code/features in demo | Recorded and locally checked | Scheduled discovery and Muse research are identified as event work; the earlier data-fetching foundation is explicitly acknowledged. |
| Legal/platform compliance and rights | Builder confirmation required | THIRD_PARTY_NOTICES.md identifies dependencies and data sources; ownership and redistribution permission are not established by a code scan. |
| Avoid banned generic projects | Scope documented; judges decide | Domain workflow combines computed risk with cited structured Muse synthesis; it has no medical/political/war features. Explain concrete differentiation rather than calling it generic RAG. |
| Three-minute video | Local captioned draft verified; hosting pending | Current 175.60-second captioned walkthrough covers the scheduled radar and real research; full local playback passed. Public hosting/playback remain pending. |
| Working demo | Locally verified | Two-hour saved radar, API, desktop/mobile UI and real Muse research tested; localhost is not a public product URL. |
| One CV submission per team | Pending | Representative submits repository/video links and lists every contributor on CV. |
| Links accessible to judges | Pending | Check repository and video while signed out, then repeat after submission. |
| Official rules accepted / entrant eligible | Builder confirmation required | Read/accept official rules in your participant account; this project cannot verify personal eligibility. |

## Community and credits

Discord introductions, announcements, questions and office hours are useful community
steps, not code requirements. Team formation is optional. Each participant must claim
their own Meta credits; **do not claim credits on another person's behalf**. Check your
own Billing page for applied credits and payment-method requirements. A successful API
call does not prove that free credits were applied. Partner credits are optional and
not guaranteed; this Muse-only build does not need partner inference.

The guide says weekday text office hours are 10-11 AM Eastern (7-8 AM Pacific).
For November 9 the closing ceremony is noon Eastern (9 AM Pacific). Community-vote
results are scheduled for November 16. Session attendance is not stated as mandatory.

## Judging preparation

| Rubric | Weight | What to demonstrate honestly |
| --- | --- | --- |
| Impact | 30% | Who needs the tool, the question it helps answer, and remaining evidence gaps. Do not claim measured time savings without a study. |
| Meta tooling | 25% | Actual Muse model ID, usage, bounded evidence prompt, and structured response. Scheduled news-discovery batches and final selection use Muse; each investigation adds one synthesis call. Page reads make no model calls. |
| Technical execution | 20% | News-led company verification, durable two-hour scheduling, retained results on failure, original-source handoff, historical risk and 31 offline tests. |
| Demo | 25% | Saved news radar, explicit live research, original-source inspection, counterpoints, uncertainty and JSON export within three minutes. |

The guide does not require every Meta model, every partner, or a bonus-prize entry.
This build does not claim the open-weight or Image/Wonder creative bonuses. X posting
for the viral bonus is optional and requires the builder's own authorized post/link.

## Final gate

Run `python scripts/check_submission.py`. Pending items must not be represented as
complete. Update submission/project.json only with verified facts. Do not publish
credentials, local account screenshots, provider billing details or bulk market data.

## Scheduled discovery coverage

The current workflow starts with all recent dated stories returned by nine configured
CNBC, BBC and Federal Reserve feeds. Muse reviews every collected headline in batches
of 80, proposes news-linked companies, then selects ten after independent company and
quote checks. There is no preset stock watchlist. Broad feed coverage is not a claim
to cover every internet article or every exchange; the demo focuses on US listings
and ADRs. Results are saved and refreshed every two hours while the server runs.

The front page reads the last successful list without inference. Loading/reloading
never forces a scan. Quotes are saved snapshots; an overdue list remains available
when an update fails. Selecting a card fills the form, and the user explicitly starts
the separate investigation. Only original sources, not generated radar claims, enter
that investigation. See README.md for startup, freshness and single-worker limits.
