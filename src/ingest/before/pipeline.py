"""In-place enrichment. Shared mutable defaults leak across articles."""

from __future__ import annotations

from typing import Any

SHARED_TOPICS: list[str] = ["news"]


def enrich(article: dict[str, Any]) -> dict[str, Any]:
    """Mutates *article* and may mutate the process-wide SHARED_TOPICS list."""
    article["word_count"] = len(article.get("body", "").split())
    topics = article.setdefault("topics", SHARED_TOPICS)
    body = article.get("body", "").lower()
    if "bike" in body and "transportation" not in topics:
        topics.append("transportation")
    if "ingested" not in topics:
        topics.append("ingested")
    article["language"] = "en"
    return article
