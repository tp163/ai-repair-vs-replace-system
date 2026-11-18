"""Document chunker for technical smartphone datasheets and service manuals.

Reads markdown files in data/datasheets/ and produces structured semantic chunks
with rich metadata (brand, model, variant, source URL, date verified, component category).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

COMPONENT_KEYWORDS = {
    "safety": ("safety", "hazard", "warning", "precaution", "disclaimer"),
    "screen": ("display", "screen", "glass", "oled", "amoled", "digitizer"),
    "battery": ("battery", "power", "mah", "voltage", "pull-tab"),
    "charging": ("charging", "port", "usb", "lightning", "daughterboard", "sub-pba", "dock", "flex"),
    "thermal": ("thermal", "cooling", "vapor chamber"),
}

# A URL is preserved as provenance, but the application has not checked that
# each individual claim is supported by that page. Keep this distinction
# explicit in every retrieved citation until the corpus has been audited.
SOURCE_VERIFICATION_STATUS = "linked_unverified"
MAX_PASSAGE_CHARS = 700


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return cleaned.strip("_")


def _detect_component(section_title: str, text: str) -> str:
    title_lower = section_title.lower()
    for comp, keywords in COMPONENT_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            return comp
    text_lower = text[:200].lower()
    for comp, keywords in COMPONENT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return comp
    return "general"


def _safe_source_url(value: str) -> str:
    value = value.strip()
    try:
        parsed = urlsplit(value)
    except ValueError:
        return ""
    return value if parsed.scheme == "https" and parsed.netloc else ""


def _split_passages(text: str, max_chars: int = MAX_PASSAGE_CHARS) -> list[str]:
    """Split section text into small, readable passages without losing lines."""
    passages: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        passage = "\n".join(current).strip()
        if passage:
            passages.append(passage)
        current = []
        current_len = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        # Each Markdown list item is usually one independently sourced fact.
        # Keep it as its own passage instead of bundling unrelated claims.
        if line.startswith(("- ", "* ")):
            flush()
        # Long single-line claims are split at word boundaries.
        pieces: list[str] = []
        while len(line) > max_chars:
            split_at = line.rfind(" ", 0, max_chars + 1)
            if split_at < 1:
                split_at = max_chars
            pieces.append(line[:split_at].strip())
            line = line[split_at:].strip()
        if line:
            pieces.append(line)

        for piece in pieces:
            if current and current_len + len(piece) + 1 > max_chars:
                flush()
            current.append(piece)
            current_len += len(piece) + (1 if current_len else 0)
    flush()
    return passages


def _source_citation(brand: str, model: str, section: str, source: dict[str, str], date_verified: str) -> str:
    parts = [f"{brand} {model}".strip(), section]
    if source.get("doc"):
        parts.append(source["doc"])
    citation = " | ".join(part for part in parts if part)
    if date_verified:
        citation += f" (dataset date: {date_verified})"
    return citation


def parse_datasheet(file_path: Path) -> list[dict[str, Any]]:
    """Parse a single datasheet markdown file into structured component chunks."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    brand = ""
    model = ""
    variant = ""
    model_ids = ""
    source_title = ""
    source_url = ""
    date_verified = ""
    ip_rating = ""

    # Parse header metadata
    for line in lines:
        if line.startswith("**Brand:**"):
            brand = line.replace("**Brand:**", "").strip()
        elif line.startswith("**Model:**"):
            model = line.replace("**Model:**", "").strip()
        elif line.startswith("**Variant:**"):
            variant = line.replace("**Variant:**", "").strip()
        elif line.startswith("**Model Identifiers:**"):
            model_ids = line.replace("**Model Identifiers:**", "").strip()
        elif line.startswith("**Source Title:**"):
            source_title = line.replace("**Source Title:**", "").strip()
        elif line.startswith("**Source URL:**"):
            source_url = line.replace("**Source URL:**", "").strip()
        elif line.startswith("**Date Verified:**"):
            date_verified = line.replace("**Date Verified:**", "").strip()
        elif line.startswith("**Ingress Protection:**"):
            ip_rating = line.replace("**Ingress Protection:**", "").strip()

    source_url = _safe_source_url(source_url)

    # Split into sections by '## '. Inline source metadata belongs to the
    # section that follows it and overrides the document-level fallback.
    sections = re.split(r"\n##\s+", content)
    chunks: list[dict[str, Any]] = []

    # Intro section
    intro_text = sections[0].strip()
    if intro_text:
        overview_sources = [{
            "doc": source_title or "Source not specified",
            "source_url": source_url,
            "verification_status": SOURCE_VERIFICATION_STATUS,
            "scope": "document",
        }]
        for passage_index, passage in enumerate(_split_passages(intro_text), start=1):
            chunks.append({
                "chunk_id": f"{_slugify(model or file_path.stem)}#overview-p{passage_index:02d}",
                "brand": brand,
                "model": model,
                "variant": variant,
                "model_identifiers": model_ids,
                "section": "Device Overview & Specifications",
                "component": "overview",
                "text": passage,
                "source_title": source_title or "Official Service Manual",
                "source_url": source_url,
                "sources": overview_sources,
                "source_verification_status": SOURCE_VERIFICATION_STATUS,
                "date_verified": date_verified,
                "file_name": file_path.name,
                "ip_rating": ip_rating,
            })

    # Numbered component sections
    for sec in sections[1:]:
        sec_lines = sec.strip().splitlines()
        if not sec_lines:
            continue
        section_title = sec_lines[0].strip()
        section_sources: list[dict[str, str]] = []
        pending_source_title = ""
        body_lines = []
        for line in sec_lines[1:]:
            stripped = line.strip()
            if stripped.startswith("- Source:"):
                pending_source_title = stripped.removeprefix("- Source:").strip()
            elif stripped.startswith("- Reference:"):
                section_sources.append({
                    "doc": pending_source_title or source_title,
                    "source_url": _safe_source_url(stripped.removeprefix("- Reference:").strip()),
                })
                pending_source_title = ""
            else:
                body_lines.append(line)
        if pending_source_title:
            section_sources.append({"doc": pending_source_title, "source_url": ""})
        section_body = "\n".join(body_lines).strip()
        if not section_body:
            continue
        if not section_sources:
            section_sources = [{"doc": source_title, "source_url": source_url}]
        section_sources = [
            {**source, "verification_status": SOURCE_VERIFICATION_STATUS, "scope": "section"}
            for source in section_sources
        ]
        primary_source = section_sources[0]

        component = _detect_component(section_title, section_body)
        base_chunk_id = f"{_slugify(model or file_path.stem)}#{_slugify(section_title)}"

        for passage_index, passage in enumerate(_split_passages(section_body), start=1):
            passage_sources = [
                {
                    **source,
                    "citation": _source_citation(brand, model, section_title, source, date_verified),
                    "date_verified": date_verified,
                }
                for source in section_sources
            ]
            chunks.append({
                "chunk_id": f"{base_chunk_id}#p{passage_index:02d}",
                "brand": brand,
                "model": model,
                "variant": variant,
                "model_identifiers": model_ids,
                "section": section_title,
                "component": component,
                "text": passage,
                "source_title": primary_source["doc"],
                "source_url": primary_source["source_url"],
                "sources": passage_sources,
                "date_verified": date_verified,
                "source_verification_status": SOURCE_VERIFICATION_STATUS,
                "file_name": file_path.name,
                "ip_rating": ip_rating,
            })

    return chunks


def load_all_chunks(datasheets_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """Load and chunk all markdown datasheets in the datasheets directory."""
    if datasheets_dir is None:
        datasheets_dir = Path(__file__).resolve().parent.parent.parent / "data" / "datasheets"
    else:
        datasheets_dir = Path(datasheets_dir)

    if not datasheets_dir.exists():
        return []

    all_chunks: list[dict[str, Any]] = []
    for file_path in sorted(datasheets_dir.glob("*.md")):
        chunks = parse_datasheet(file_path)
        all_chunks.extend(chunks)

    return all_chunks
