"""Typical 'improvements' that keep the original design bugs.

This is not the recommended code. It is the naive-refactor exhibit:
types, logging, an Enum — and the same None, the same optional fields,
the same shared list.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import TypedDict

from ingest.catalog import SourceTimeout, fetch_raw

logger = logging.getLogger(__name__)

SHARED_TOPICS: list[str] = ["news"]


class ArticleDict(TypedDict, total=False):
    url: str
    title: str
    body: str
    source: str
    word_count: int
    topics: list[str]
    language: str


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def ingest(url: str) -> ArticleDict | None:
    try:
        raw = fetch_raw(url)
    except SourceTimeout:
        logger.exception("timeout fetching %s", url)
        return None
    except Exception:
        logger.exception("unexpected error fetching %s", url)
        return None
    if raw is None:
        return None
    article: ArticleDict = {
        "url": raw.url,
        "title": raw.title.strip(),
        "body": raw.body,
        "source": raw.source,
    }
    if not article["title"]:
        raise ValueError("title is required")
    return article


class Job:
    def __init__(self, job_id: str, url: str) -> None:
        self.job_id = job_id
        self.url = url
        self.status: JobStatus = JobStatus.PENDING
        self.result: ArticleDict | None = None
        self.error: str | None = None

    def complete(self, result: ArticleDict | None = None) -> None:
        self.status = JobStatus.COMPLETED
        self.result = result

    def fail(self, error: str | None = None) -> None:
        self.status = JobStatus.FAILED
        self.error = error


def enrich(article: ArticleDict) -> ArticleDict:
    article["word_count"] = len(article.get("body", "").split())
    topics = article.setdefault("topics", SHARED_TOPICS)
    body = article.get("body", "").lower()
    if "bike" in body and "transportation" not in topics:
        topics.append("transportation")
    if "ingested" not in topics:
        topics.append("ingested")
    article["language"] = "en"
    return article
