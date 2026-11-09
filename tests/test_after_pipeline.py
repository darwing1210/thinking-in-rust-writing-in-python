from __future__ import annotations

from ingest.after.pipeline import Article, enrich


def test_enrich_returns_a_new_article() -> None:
    original = Article(
        url="https://news.example/ok",
        title="City council approves downtown bike lanes",
        body="The council voted 8-1 to add protected bike lanes on Main Street.",
        source="example-news",
    )
    enriched = enrich(original)
    assert enriched is not original
    assert original.word_count == 0
    assert enriched.word_count == len(original.body.split())
    assert original.topics == ()
    assert "transportation" in enriched.topics
    assert "local-government" in enriched.topics


def test_two_articles_do_not_share_topics() -> None:
    bike = enrich(
        Article(
            url="https://news.example/ok",
            title="Bike lanes",
            body="New bike lanes downtown.",
            source="example-news",
        )
    )
    weather = enrich(
        Article(
            url="https://news.example/other",
            title="Weather outlook",
            body="Sunshine through Thursday.",
            source="example-news",
        )
    )
    assert "transportation" in bike.topics
    assert "transportation" not in weather.topics
    assert bike.topics != weather.topics
