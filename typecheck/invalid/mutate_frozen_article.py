"""Frozen Article.topics is a tuple. In-place append should fail."""

from ingest.after.pipeline import Article

article = Article(
    url="https://news.example/ok",
    title="Hello",
    body="Hello world",
    source="example-news",
)
article.topics.append("news")
