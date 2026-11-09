"""Lexical TF-IDF document retriever for smartphone technical datasheets.

Implements metadata filtering with fail-closed model gating, TF-IDF cosine similarity,
and section-level source metadata (direct URLs and checked dates where supplied).
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .chunker import load_all_chunks

COMPONENT_MAP = {
    "cracked_screen": "screen",
    "screen": "screen",
    "battery": "battery",
    "charging": "charging",
    "liquid_damage": "safety",
    "safety": "safety",
    "overheating": "battery",
    "performance": "general",
}


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    """Term frequency with log normalization."""
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {word: count / total for word, count in counts.items()}


def _normalize_label(value: str) -> str:
    """Normalize punctuation and spacing without discarding variant tokens."""
    value = value.casefold().strip()
    value = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", " ", value)
    return " ".join(re.findall(r"[a-z0-9]+", value))


def _matches_model_strictly(
    target_brand: str,
    target_model: str,
    chunk_brand: str,
    chunk_model: str,
    model_identifiers: str = "",
) -> bool:
    """Match a complete device name or identifier; never use substring matches."""
    target_brand_norm = _normalize_label(target_brand)
    chunk_brand_norm = _normalize_label(chunk_brand)
    target_norm = _normalize_label(target_model)
    chunk_norm = _normalize_label(chunk_model)
    if not target_brand_norm or target_brand_norm != chunk_brand_norm or not target_norm:
        return False

    # The brand is supplied separately by the form, but tolerate it repeated in
    # the model field. Preserve every remaining token (Pro, mini, 4G, 5G, etc.).
    if target_norm.startswith(target_brand_norm + " "):
        target_norm = target_norm[len(target_brand_norm):].strip()
    if target_norm == chunk_norm:
        return True

    identifiers = {
        _normalize_label(identifier)
        for identifier in re.split(r"[,;/|]", model_identifiers)
        if identifier.strip()
    }
    return target_norm in identifiers


class LexicalTFIDFVectorStore:
    """In-memory Lexical TF-IDF vector index with strict fail-closed metadata gating."""

    def __init__(self, chunks: list[dict[str, Any]] | None = None) -> None:
        self.chunks: list[dict[str, Any]] = chunks or []
        self.doc_count = len(self.chunks)
        self.idf: dict[str, float] = {}
        self.doc_vectors: list[dict[str, float]] = []
        if self.chunks:
            self._index_chunks()

    def _index_chunks(self) -> None:
        df: Counter[str] = Counter()
        tokenized_docs: list[list[str]] = []

        for chunk in self.chunks:
            combined_text = f"{chunk.get('section', '')} {chunk.get('component', '')} {chunk.get('text', '')}"
            tokens = _tokenize(combined_text)
            tokenized_docs.append(tokens)
            df.update(set(tokens))

        self.doc_count = len(self.chunks)
        self.idf = {word: math.log((self.doc_count + 1) / (count + 1)) + 1.0 for word, count in df.items()}

        self.doc_vectors = []
        for tokens in tokenized_docs:
            tf = _compute_tf(tokens)
            vec = {w: tf[w] * self.idf.get(w, 1.0) for w in tf}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self.doc_vectors.append({w: v / norm for w, v in vec.items()})

    def search(
        self,
        query: str,
        brand: str = "",
        model: str = "",
        component: str = "",
        top_k: int = 2,
        min_score: float = 0.05,
    ) -> list[dict[str, Any]]:
        if not self.chunks or not brand.strip() or not model.strip():
            # Fail closed: never return generic chunks without a validated model target
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        q_tf = _compute_tf(query_tokens)
        q_vec = {w: q_tf[w] * self.idf.get(w, 1.0) for w in q_tf}
        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0
        q_unit = {w: v / q_norm for w, v in q_vec.items()}

        target_comp = COMPONENT_MAP.get(component.strip().lower(), component.strip().lower())

        results = []
        for idx, chunk in enumerate(self.chunks):
            chunk_brand = chunk.get("brand", "").lower()
            chunk_model = chunk.get("model", "")
            chunk_comp = chunk.get("component", "").lower()

            # Strict brand and complete model-name gating.
            if not _matches_model_strictly(
                brand, model, chunk_brand, chunk_model,
                chunk.get("model_identifiers", ""),
            ):
                continue

            # 3. TF-IDF Cosine Similarity
            doc_vec = self.doc_vectors[idx]
            sim = sum(q_unit[w] * doc_vec.get(w, 0.0) for w in q_unit)

            # 4. Component Relevance Boost
            boost = 1.0
            if target_comp and target_comp == chunk_comp:
                boost *= 1.4

            score = min(round(sim * boost, 4), 1.0)
            if score >= min_score:
                item = dict(chunk)
                item["score"] = score
                # Section-level source provenance (parsed from that section).
                source_title = chunk.get("source_title", "")
                source_url = chunk.get("source_url", "")
                date_verified = chunk.get("date_verified", "")
                section_title = chunk.get("section", "")
                item["citation"] = f"{chunk.get('brand', '')} {chunk.get('model', '')} — {section_title}"
                if source_title:
                    item["citation"] += f" — {source_title}"
                if date_verified:
                    item["citation"] += f" (checked {date_verified})"
                item["source_url"] = source_url
                item["sources"] = chunk.get("sources", [{
                    "doc": source_title,
                    "source_url": source_url,
                }])
                results.append(item)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


_GLOBAL_STORE: LexicalTFIDFVectorStore | None = None


def get_vector_store(datasheets_dir: Path | str | None = None) -> LexicalTFIDFVectorStore:
    """Retrieve or initialize the vector store. Custom paths create an isolated instance."""
    global _GLOBAL_STORE
    if datasheets_dir is not None:
        chunks = load_all_chunks(datasheets_dir)
        return LexicalTFIDFVectorStore(chunks)

    if _GLOBAL_STORE is None:
        chunks = load_all_chunks()
        _GLOBAL_STORE = LexicalTFIDFVectorStore(chunks)
    return _GLOBAL_STORE


def query_datasheet_rag(
    brand: str,
    model: str,
    query: str,
    component: str = "",
    top_k: int = 2,
    datasheets_dir: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Query technical datasheets and return matched excerpts with source metadata."""
    store = get_vector_store(datasheets_dir)
    return store.search(
        query=query,
        brand=brand,
        model=model,
        component=component,
        top_k=top_k,
    )
