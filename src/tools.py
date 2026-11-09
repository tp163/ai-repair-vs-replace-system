"""External tools available to agents.

Currently a single free tool: DuckDuckGo web search (no API key needed).
The Market Research Agent uses it to enrich dataset prices with live
market signals. If the optional dependency or the network is unavailable,
agents degrade gracefully to dataset prices only.
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def web_search(query: str, max_results: int = 3) -> list[dict]:
    """Return [{'title','href','body'}] for a query, or [] on any failure."""
    try:
        from duckduckgo_search import DDGS  # optional dependency
    except ImportError:
        log.warning("duckduckgo-search not installed; live search disabled.")
        return []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {"title": r.get("title", ""), "href": r.get("href", ""),
             "body": r.get("body", "")}
            for r in results
        ]
    except Exception as exc:  # network errors, rate limits, ...
        log.warning("Live search failed (%s); using dataset prices only.", exc)
        return []
