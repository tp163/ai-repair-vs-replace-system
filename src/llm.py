"""LLM access layer.

One small client for the whole system. Agents call ``chat()`` and never care
which provider answers. Providers, in priority order:

1. An OpenAI-compatible cloud endpoint (if OPENAI_COMPAT_BASE_URL is set)
2. Local Ollama (if reachable)
3. Demo mode: returns a deterministic stub so the pipeline always runs

The demo stub makes no network calls. It exists so the full multi-agent
workflow can be demonstrated on any machine, with Ollama added later.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error

from . import config


class DemoLLM:
    """Deterministic stand-in used when no real LLM is configured.

    Agents that need structured output parse JSON from ``stub_json``; agents
    that need free text get a templated sentence. This keeps the agent graph
    fully exercisable without any model installed.
    """

    name = "demo"

    def chat(self, system: str, user: str, temperature: float = 0.2,
             image_data_uri: str | None = None) -> str:
        return (
            "[demo-llm] No LLM configured. Set LLM_PROVIDER=ollama and start "
            "Ollama for full natural-language agent outputs."
        )

    def stub_json(self, payload: dict) -> str:
        return json.dumps(payload)


class OllamaLLM:
    """Minimal OpenAI-compatible chat client (works for Ollama and any
    OpenAI-compatible endpoint, including cloud APIs)."""

    name = "ollama/openai-compatible"

    def __init__(self, base_url: str, model: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def chat(self, system: str, user: str, temperature: float = 0.2,
             image_data_uri: str | None = None) -> str:
        content = [{"type": "text", "text": user}]
        if image_data_uri:
            content.append({"type": "image_url", "image_url": {"url": image_data_uri}})
        body = json.dumps({
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": content if image_data_uri else user},
            ],
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, KeyError, TimeoutError) as exc:
            raise RuntimeError(
                f"LLM request failed ({exc}). Is Ollama running? "
                f"Try: ollama serve && ollama pull {self.model}"
            ) from exc


def get_llm():
    """Return the best available LLM client."""
    if config.OPENAI_COMPAT_BASE_URL and config.OPENAI_COMPAT_MODEL:
        return OllamaLLM(
            config.OPENAI_COMPAT_BASE_URL,
            config.OPENAI_COMPAT_MODEL,
            config.OPENAI_COMPAT_API_KEY,
        )
    if config.LLM_PROVIDER == "ollama":
        return OllamaLLM(config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    return DemoLLM()
