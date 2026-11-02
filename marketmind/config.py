"""Muse configuration. No alternate providers or endpoint overrides."""
import os
from dataclasses import dataclass, field

from .errors import ResearchUnavailable

MUSE_BASE_URL = "https://api.meta.ai/v1"
DEFAULT_MODEL = "muse-spark-1.3"


def load_windows_environment() -> None:
    """Read saved Muse variables when a terminal predates the Windows change."""
    if os.name != "nt":
        return
    import winreg

    locations = (
        (winreg.HKEY_CURRENT_USER, r"Environment"),
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
    )
    for name in ("MUSE_API_KEY", "MODEL_API_KEY", "MUSE_MODEL"):
        if os.getenv(name):
            continue
        for hive, path in locations:
            try:
                with winreg.OpenKey(hive, path) as key:
                    value, _ = winreg.QueryValueEx(key, name)
                if isinstance(value, str) and value.strip():
                    os.environ[name] = value.strip()
                    break
            except OSError:
                continue


@dataclass(frozen=True)
class MuseSettings:
    model: str
    api_key: str = field(repr=False)


def muse_settings() -> MuseSettings:
    model = os.getenv("MUSE_MODEL", DEFAULT_MODEL).strip()
    if not model.startswith("muse-"):
        raise ResearchUnavailable("MUSE_MODEL must identify a Muse model supported by Meta's chat-completions API.")
    return MuseSettings(
        model=model,
        api_key=(os.getenv("MUSE_API_KEY") or os.getenv("MODEL_API_KEY") or "").strip(),
    )


def require_muse() -> MuseSettings:
    settings = muse_settings()
    if not settings.api_key:
        raise ResearchUnavailable("Set MUSE_API_KEY or MODEL_API_KEY in the server environment before running research.")
    return settings
