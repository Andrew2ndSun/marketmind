# Original-contribution disclosure

Prepared during the event on November 2, 2026. The prior foundation existed before
this hackathon. This map describes work from this conversation; it is not a fabricated
pre-event commit history, and deleting old files does not make inherited work new.

| Files / feature | Provenance | How to present it |
| --- | --- | --- |
| marketmind/data.py price-history helpers | Adapted from earlier stock-research code | Inherited data-fetching foundation, not an event invention. |
| marketmind/data.py news normalization and evidence snapshots | Event integration with existing Yahoo data tooling | Show how excerpts enter the new evidence trail, acknowledging Yahoo/yfinance. |
| marketmind/metrics.py | Event extraction/integration of standard financial formulas | New research presentation and validation; no claim that volatility/drawdown formulas are novel. |
| marketmind/muse.py, config.py, prompts.py | Event Muse integration | Official Muse-only API, server-side Windows key loading, bounded structured synthesis. |
| marketmind/schemas.py, validation.py, errors.py | Event research-contract implementation | Required citations, schema validation and rejection of invalid report output. |
| marketmind/research.py | Event research workflow | Evidence packaging, risk context, conflict/unknown sections, honest quality metadata. |
| marketmind/app.py | Event-focused API built on prior FastAPI experience | New research-only routes, not the inherited trading platform. |
| marketmind/web/ | Event dashboard | Question form, linked findings, counterpoints, chart, unknowns, export. |
| tests/ | Event-focused regression suite | Offline invented fixtures only; no fixed product report masquerading as Muse. |
| docs/, submission/, CI and preflight | Submission preparation | Audit trail, reproducibility, demo plan and explicit pending gates. |

The earlier platform contained trading/allocations, strategy validation, paper snapshots,
other provider clients and old reports. Those were removed and must not appear in the
demo as new event work. The new app does not place orders or establish profitable trades.

## Track confirmation

The builder confirmed on November 2, 2026 that organizers accepted this project as
an **Indie Developer** candidate, not a startup. The team is solo: Andrew2ndSun is
the sole contributor and representative. This records the builder's account; no
independent written organizer decision was inspected. Retain any organizer message
with the submission records. The adapted foundation remains disclosed regardless
of acceptance, and the demo must still distinguish the new event contributions.

## Evidence limits

A new local Git repository only records work from now forward. It cannot establish
when inherited code was originally written. Preserve truthful dates and original
history if it is available; do not backdate commits or invent authorship.
