# MarketMind submission copy - review before submitting

**Project:** MarketMind

**Problem statement:** Build for Your World

**Short description:** Muse-powered stock research that exposes evidence, counterarguments,
historical risk and unanswered questions rather than hiding uncertainty behind a ranking.

**Who benefits:** People investigating public equities who want to inspect a market narrative
without assembling a price chart, data snapshot and source trail by hand. User impact is
proposed; no controlled time-saving or financial-performance claim has been established.

**What it does:** The user asks about a ticker. MarketMind collects completed adjusted closes,
fundamentals and available news, computes historical risk, and asks Muse Spark 1.3 for a
structured cited research brief. The dashboard links findings to evidence, shows opposing
interpretations and gaps, and exports the report as JSON.

**Meta tooling:** Official Meta Model API, Muse-only inference, server-side credential loading,
bounded evidence prompts and structured synthesis. One synthesis request per investigation;
not autonomous multi-agent coordination. No partner inference is required.

**New event work:** Muse integration, structured evidence/citation contract, research API and
dashboard, counterpoints/unknowns, risk presentation, JSON export, focused regression tests
and submission preparation. Price-fetching helpers were adapted from an earlier prototype.
See docs/ORIGINAL_CONTRIBUTIONS.md. The builder reports organizer acceptance of this project in the Indie Developer track.

**Technical limits:** Citation-ID membership is validated, not factual entailment. Yahoo may
return no news. Fundamentals are unverified provider snapshots. Historical risk is not a
forecast. The tool does not execute trades or give personalized investment instructions.

**Track:** Indie Developer.

**Sole contributor and representative:** Andrew2ndSun (builder-provided GitHub identity).

**Public repository URL:** https://github.com/Andrew2ndSun/marketmind

**Three-minute video URL:** Hosting pending. A captioned 175.56-second local recording is available at artifacts/marketmind-demo.webm.

**Public product URL, if used:** Pending. A localhost URL is not reachable by remote judges.

**Submission status:** Not submitted. The representative must complete the CV submission
before November 4, 2026 at 6:00 PM Pacific / 9:00 PM Eastern and verify all links signed out.
