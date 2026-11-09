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
        chunks.append({
            "chunk_id": f"{_slugify(model or file_path.stem)}#overview",
            "brand": brand,
            "model": model,
            "variant": variant,
            "model_identifiers": model_ids,
            "section": "Device Overview & Specifications",
            "component": "overview",
            "text": intro_text,
            "source_title": source_title or "Official Service Manual",
            "source_url": source_url,
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
        primary_source = section_sources[0]

        component = _detect_component(section_title, section_body)
        chunk_id = f"{_slugify(model or file_path.stem)}#{_slugify(section_title)}"

        chunks.append({
            "chunk_id": chunk_id,
            "brand": brand,
            "model": model,
            "variant": variant,
            "model_identifiers": model_ids,
            "section": section_title,
            "component": component,
            "text": section_body,
            "source_title": primary_source["doc"],
            "source_url": primary_source["source_url"],
            "sources": section_sources,
            "date_verified": date_verified,
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
