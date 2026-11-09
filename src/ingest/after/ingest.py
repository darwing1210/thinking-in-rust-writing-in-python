"""Explicit ingest: success and each expected failure are distinct values."""

from __future__ import annotations

from ingest.after.errors import NotFound, Retryable, ValidationFailed
from ingest.after.pipeline import Article
from ingest.after.result import Err, Ok, Result
from ingest.catalog import SourceTimeout, fetch_raw


def ingest(url: str) -> Result[Article, NotFound | ValidationFailed | Retryable]:
    try:
        raw = fetch_raw(url)
    except SourceTimeout as exc:
        return Err(Retryable(reason=str(exc)))

    if raw is None:
        return Err(NotFound(url=url))

    missing: list[str] = []
    title = raw.title.strip()
    if not title:
        missing.append("title")
    if not raw.body.strip():
        missing.append("body")
    if missing:
        return Err(ValidationFailed(fields=tuple(missing)))

    return Ok(Article(url=raw.url, title=title, body=raw.body, source=raw.source))
