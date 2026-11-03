# Third-party components and data

MarketMind installs these dependencies; their source is not vendored into this project:

| Component | Purpose | Upstream |
| --- | --- | --- |
| httpx | Muse and public RSS HTTPS requests | https://github.com/encode/httpx |
| python-dotenv | Optional local environment loading | https://github.com/theskumar/python-dotenv |
| yfinance | Yahoo company lookup, quotes and financial evidence | https://github.com/ranaroussi/yfinance |
| pandas / NumPy | Time series and risk calculations | https://pandas.pydata.org / https://numpy.org |
| FastAPI / Pydantic | API and validated research schema | https://fastapi.tiangolo.com / https://docs.pydantic.dev |
| Uvicorn | Local HTTP server | https://www.uvicorn.org |

Consult each installed distribution's license and upstream notices before redistribution.
Dependency licenses do not grant rights to unrelated market data, news or model outputs.

Meta Model API supplies Muse inference under the account's applicable terms. Yahoo
Finance supplies prices, provider snapshots and headline excerpts through yfinance.
The scheduled discovery feature reads these public RSS feeds, using headlines and
short publisher excerpts rather than full articles:

| Publisher | Feeds used |
| --- | --- |
| CNBC | Markets, economy, world, finance, technology and energy |
| BBC | Business and technology |
| Federal Reserve | Press releases |

The exact nine feed URLs are defined in `marketmind/discovery_data.py`. Every recent
dated item returned by those feeds is eligible for review; this is not a licensed
complete-market news service. Company names/tickers and fresh quotes are checked
through Yahoo before selection. Saved snapshots remain in ignored `.cache/`; videos,
receipts and exported reports remain in ignored `artifacts/`.

Source links and provenance are included in reports; citation does not establish a
right to redistribute the underlying data. Do not commit bulk market/news dumps to
the public repository. Tests use invented data written for this project.

The dashboard uses local HTML/CSS/JavaScript and system fonts; no third-party logo,
photo, music or downloaded visual asset is included. Contributor ownership, use of
prior code, and any chosen open-source license require the builder's confirmation.
A public-repository requirement does not by itself select a source-code license.

Optional demo tooling uses Playwright, Chromium and its bundled FFmpeg to record and
inspect the local UI. These are development tools and are not vendored into the source
archive. The generated walkthrough uses real product screens and text captions, with
no music or audio narration. Review upstream licenses and applicable data/model terms
before redistributing source, reports or video.
