"""Run `python main.py` for the local MarketMind dashboard and API."""

from dotenv import load_dotenv
load_dotenv()

from marketmind.config import load_windows_environment  # noqa: E402
load_windows_environment()

from marketmind.app import app  # noqa: E402

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
