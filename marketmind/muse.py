"""Muse-only inference through Meta's official HTTP API."""
import json

import httpx

from .config import MUSE_BASE_URL, require_muse
from .errors import SynthesisError
from .prompts import SYSTEM_PROMPT
from .schemas import Synthesis
from .validation import validate_citations


def synthesize(question: str, evidence: list[dict]) -> tuple[Synthesis, dict]:
    settings = require_muse()
    try:
        # Fixed destination and no redirects: keys never route to another provider.
        with httpx.Client(timeout=60, follow_redirects=False) as client:
            response = client.post(
                f"{MUSE_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.api_key}"},
                json={
                    "model": settings.model,
                    "max_completion_tokens": 8192,
                    "reasoning_effort": "low",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT.replace("{schema}", json.dumps(Synthesis.model_json_schema()))},
                        {"role": "user", "content": json.dumps({"question": question, "evidence": evidence})},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()
        if payload["choices"][0].get("finish_reason") != "stop":
            raise ValueError("Muse did not complete the research report.")
        result = Synthesis.model_validate_json(payload["choices"][0]["message"]["content"])
        validate_citations(result, evidence)
        usage = payload.get("usage") or {}
        return result, {
            "provider": "meta-model-api", "model": settings.model,
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
        }
    except Exception as exc:
        # Suppress response bodies, which can contain provider internals or prompts.
        raise SynthesisError("Muse inference failed or returned invalid cited JSON. Check your Muse credentials and model, then retry.") from exc
