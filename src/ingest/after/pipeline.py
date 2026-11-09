"""Enrichment as a sequence of transformations. No shared mutable state."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Article:
    url: str
    title: str
    body: str
    source: str
    word_count: int = 0
    topics: tuple[str, ...] = ()
    language: str = "und"


def count_words(article: Article) -> Article:
    return replace(article, word_count=len(article.body.split()))


def detect_language(article: Article) -> Article:
    return replace(article, language="en")


def tag_topics(article: Article) -> Article:
    topics = ["news"]
    body = article.body.lower()
    if "council" in body or "voted" in body:
        topics.append("local-government")
    if "bike" in body:
        topics.append("transportation")
    topics.append("ingested")
    return replace(article, topics=tuple(topics))


def enrich(article: Article) -> Article:
    for stage in (count_words, detect_language, tag_topics):
        article = stage(article)
    return article
