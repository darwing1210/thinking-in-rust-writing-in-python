"""In-memory source catalog. No network, no cloud, no fixtures to download."""

from __future__ import annotations

from dataclasses import dataclass

OK_URL = "https://news.example/ok"
MISSING_URL = "https://news.example/missing"
EMPTY_TITLE_URL = "https://news.example/empty-title"
TIMEOUT_URL = "https://news.example/timeout"


@dataclass(frozen=True)
class RawArticle:
    url: str
    title: str
    body: str
    source: str


class SourceTimeout(Exception):
    """Simulated retryable upstream failure."""


_ARTICLES: dict[str, RawArticle] = {
    OK_URL: RawArticle(
        url=OK_URL,
        title="City council approves downtown bike lanes",
        body=(
            "The council voted 8-1 to add protected bike lanes on Main Street. "
            "Construction starts in March."
        ),
        source="example-news",
    ),
    EMPTY_TITLE_URL: RawArticle(
        url=EMPTY_TITLE_URL,
        title="  ",
        body="A wire story arrived without a usable title.",
        source="example-news",
    ),
}


def fetch_raw(url: str) -> RawArticle | None:
    """Return a raw article, None if missing, or raise SourceTimeout."""
    if url == TIMEOUT_URL:
        raise SourceTimeout(f"timed out fetching {url}")
    return _ARTICLES.get(url)
