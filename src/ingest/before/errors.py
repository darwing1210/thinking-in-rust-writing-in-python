"""Ambiguous failure contract: None, exceptions, and missing data collide."""

from __future__ import annotations

from typing import Any

from ingest.catalog import SourceTimeout, fetch_raw


def ingest(url: str) -> dict[str, Any] | None:
    """Fetch and validate an article.

    Returns a dict on success.
    Returns None if the article is missing *or* the source timed out.
    Raises ValueError if the payload is invalid.

    Callers cannot tell a 404 from a blip.
    """
    try:
        raw = fetch_raw(url)
    except SourceTimeout:
        return None
    if raw is None:
        return None

    article = {
        "url": raw.url,
        "title": raw.title.strip(),
        "body": raw.body,
        "source": raw.source,
    }
    if not article["title"]:
        raise ValueError("title is required")
    return article
