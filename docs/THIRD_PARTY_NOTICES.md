# Third-party components and data

MarketMind installs these dependencies; their source is not vendored into this project:

| Component | Purpose | Upstream |
| --- | --- | --- |
| httpx | Muse HTTPS requests | https://github.com/encode/httpx |
| python-dotenv | Optional local environment loading | https://github.com/theskumar/python-dotenv |
| yfinance | Yahoo financial data adapter | https://github.com/ranaroussi/yfinance |
| pandas / NumPy | Time series and risk calculations | https://pandas.pydata.org / https://numpy.org |
| FastAPI / Pydantic | API and validated research schema | https://fastapi.tiangolo.com / https://docs.pydantic.dev |
| Uvicorn | Local HTTP server | https://www.uvicorn.org |

Consult each installed distribution's license and upstream notices before redistribution.
Dependency licenses do not grant rights to unrelated market data, news or model outputs.

Meta Model API supplies Muse inference under the account's applicable terms. Yahoo
Finance supplies prices, provider snapshots and headline excerpts through yfinance.
Source links and provenance are included in reports; citation does not establish a
right to redistribute the underlying data. Do not commit bulk market/news dumps to
the public repository. Tests use invented data written for this project.

The dashboard uses local HTML/CSS/JavaScript and system fonts; no third-party logo,
photo, music or downloaded visual asset is included. Contributor ownership, use of
prior code, and any chosen open-source license require the builder's confirmation.
A public-repository requirement does not by itself select a source-code license.
