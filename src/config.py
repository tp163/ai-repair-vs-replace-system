"""Central configuration for the multi-agent phone recommendation system.

Everything the user needs to tweak lives here. No secrets should be hard-coded;
copy .env.example to .env or set environment variables instead.
"""
import os

# ---------------------------------------------------------------------------
# LLM provider
# ---------------------------------------------------------------------------
# "ollama"  -> talk to a local Ollama instance (free, runs on your machine)
# "demo"    -> no LLM at all; agents fall back to template-based logic.
#              Use this to run the pipeline before installing Ollama.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "demo")

# Ollama speaks an OpenAI-compatible API on this endpoint.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Optional: any OpenAI-compatible cloud API (Kimi, OpenAI, ...). Left empty,
# the system never touches the network for LLM calls.
OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPAT_BASE_URL", "")
OPENAI_COMPAT_API_KEY = os.getenv("OPENAI_COMPAT_API_KEY", "")
OPENAI_COMPAT_MODEL = os.getenv("OPENAI_COMPAT_MODEL", "")

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
# Point this at your own dataset file (JSON list of phone objects, or CSV with
# the same column names). See data/phones_placeholder.json for the schema.
DATA_PATH = os.getenv("PHONE_DATA_PATH", "data/phones_placeholder.json")
REPAIR_COST_DATA_PATH = os.getenv("REPAIR_COST_DATA_PATH", "data/repair_costs.json")

# ---------------------------------------------------------------------------
# Market research
# ---------------------------------------------------------------------------
# The Market Research Agent first reads prices from the dataset, then
# optionally tries a free DuckDuckGo search to enrich/refresh them.
ENABLE_LIVE_SEARCH = os.getenv("ENABLE_LIVE_SEARCH", "false").lower() == "true"
LIVE_SEARCH_RESULTS = int(os.getenv("LIVE_SEARCH_RESULTS", "3"))

# ---------------------------------------------------------------------------
# Recommendation behaviour
# ---------------------------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", "3"))          # number of devices recommended
MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "10"))  # retrieval pool size
PRICE_OVER_BUDGET_TOLERANCE = 0.10            # allow 10% over budget, flagged
