from __future__ import annotations

from collections.abc import Iterator

import pytest

from ingest.before.pipeline import SHARED_TOPICS, enrich


@pytest.fixture(autouse=True)
def reset_shared_topics() -> Iterator[None]:
    original = list(SHARED_TOPICS)
    SHARED_TOPICS.clear()
    SHARED_TOPICS.extend(["news"])
    yield
    SHARED_TOPICS.clear()
    SHARED_TOPICS.extend(original)


def test_enrich_mutates_the_input_dict() -> None:
    article = {"title": "Hi", "body": "hello world"}
    out = enrich(article)
    assert out is article
    assert article["word_count"] == 2


def test_second_article_inherits_topics_from_the_first() -> None:
    bike = {"title": "Bike lanes", "body": "New bike lanes downtown."}
    weather = {"title": "Weather", "body": "Sunshine through Thursday."}

    enrich(bike)
    enrich(weather)

    assert "transportation" in weather["topics"]
    assert weather["topics"] is SHARED_TOPICS
    assert bike["topics"] is weather["topics"]
