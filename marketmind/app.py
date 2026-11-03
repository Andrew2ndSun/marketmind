"""MarketMind's API and same-origin web dashboard."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .config import muse_settings
from .errors import ResearchUnavailable, SynthesisError
from .research import research
from .discovery import scan_market

WEB_DIR = Path(__file__).parent / "web"


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticker: str = Field(min_length=1, max_length=12, pattern=r"^[A-Z0-9^][A-Z0-9.^=-]*$")
    question: str = Field(
        default="What does the recent evidence say about this stock's movement and risks?",
        min_length=8, max_length=1200,
    )

    discovery_created_at: str | None = Field(default=None, max_length=64)

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value):
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("question", mode="before")
    @classmethod
    def normalize_question(cls, value):
        return value.strip() if isinstance(value, str) else value


@asynccontextmanager
async def lifespan(app):
    from .discovery_store import start_scheduler
    stop, worker = start_scheduler()
    try:
        yield
    finally:
        stop.set()
        worker.join(timeout=0.1)


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(title="MarketMind | Muse Stock Research", version="4.1.0", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index():
        return (WEB_DIR / "index.html").read_text(encoding="utf-8")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "marketmind"}

    @app.get("/api/research/status")
    def status():
        try:
            settings = muse_settings()
        except ResearchUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc
        return {"live_configured": bool(settings.api_key), "model": settings.model,
                "provider": "meta-model-api"}

    @app.get("/api/discovery")
    def discover():
        try:
            return scan_market()
        except ResearchUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc
        except SynthesisError as exc:
            raise HTTPException(502, str(exc)) from exc

    @app.post("/api/research")
    def investigate(request: ResearchRequest):
        try:
            return research(request.ticker, request.question, discovery_created_at=request.discovery_created_at)
        except ResearchUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc
        except SynthesisError as exc:
            raise HTTPException(502, str(exc)) from exc

    return app


app = create_app()
