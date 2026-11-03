# MarketMind submission copy - review before submitting

**Project:** MarketMind

**Problem statement / theme:** Build for Your World

**Short description:** Muse-powered market discovery and explainable stock research.
A scheduled news scan surfaces ten stocks to investigate, with original sources,
counterarguments, historical risk and explicit uncertainty.

**Who benefits:** People researching public equities who want a starting point from
current news, then a way to challenge a market narrative with inspectable evidence.
No measured time-saving or financial-performance claim has been established.

**What it does:** Every two hours, a background job collects broad economic/business
news from nine configured feeds across industries. Muse reviews all recent collected
headlines and proposes companies without a fixed stock watchlist. Company search and
fresh equity quotes verify symbols; Muse then selects ten source-linked research
candidates with industry themes, reasons and risks. The front page reads the saved
list immediately, and successful results survive restarts. Failed updates retain the
previous list with an overdue indication.

A user selects a candidate or enters another ticker, then explicitly clicks
Investigate. MarketMind collects completed adjusted closes, fundamentals and available
ticker news, computes historical risk, and asks Muse Spark 1.3 for a structured cited
brief. Original radar sources can accompany the investigation. Findings, counterpoints,
unknowns and evidence are inspectable and exportable together as JSON.

**Meta tooling:** Official Meta Model API; Muse-only inference and server-side keys.
Scheduled scans use batched Muse news discovery and final selection. Each stock
investigation uses one additional synthesis call. Page loads and saved-list reloads
make no inference calls. This is a scheduled pipeline, not autonomous multi-agent
coordination, and does not require partner inference.

**New event work:** Scheduled news-led discovery, persistent two-hour updates,
company/quote validation, ten-stock radar, original-source handoff, Muse integration,
structured evidence/citation contract, research API/dashboard, counterpoints, risk
presentation, JSON export and failure-path regression tests. Price-fetching helpers
were adapted from an earlier prototype. See docs/ORIGINAL_CONTRIBUTIONS.md.
The builder reports organizer acceptance for the Indie Developer track.

**Technical limits:** Broad feed coverage is not an exhaustive scan of every market
story. The demo targets US-listed equities and ADRs. Saved quotes may be delayed.
The server must remain running for scheduled updates; this demo uses one worker.
Citation IDs are checked, not factual entailment. Yahoo ticker news can be absent;
provider fundamentals are not verified filings. Historical risk is not a forecast.
No trades or personalized investment instructions are provided.

**Track:** Indie Developer.

**Sole contributor and representative:** Andrew2ndSun.

**Idea acknowledgment:** A classmate suggested the initial stock-analysis idea;
MarketMind development and the contributor list remain solo.

**Public repository URL:** https://github.com/Andrew2ndSun/marketmind

**Three-minute video URL:** Hosting pending. The current captioned local draft is
artifacts/marketmind-demo.webm (175.60 seconds). It shows the scheduled radar and
one real Muse investigation. See project.json and VERIFICATION.md for verification.

**Public product URL, if used:** Pending. Localhost is not reachable by remote judges.

**Submission status:** Not submitted. The representative must submit through CV by
November 4, 2026 at 6:00 PM Pacific / 9:00 PM Eastern and verify public links signed out.
Rights confirmation and official rule acceptance remain participant actions.
