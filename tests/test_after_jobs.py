from __future__ import annotations

from ingest.after.errors import NotFound
from ingest.after.jobs import Completed, Failed, Pending, finish, start
from ingest.after.pipeline import Article
from ingest.after.result import Err, Ok


def test_start_returns_processing() -> None:
    pending = Pending(job_id="job-1", url="https://news.example/ok")
    processing = start(pending)
    assert processing.job_id == "job-1"
    assert processing.url == pending.url


def test_finish_ok_requires_an_article() -> None:
    processing = start(Pending(job_id="job-1", url="https://news.example/ok"))
    article = Article(
        url="https://news.example/ok",
        title="City council approves downtown bike lanes",
        body="The council voted.",
        source="example-news",
    )
    finished = finish(processing, Ok(article))
    assert isinstance(finished, Completed)
    assert finished.article.title.startswith("City council")


def test_finish_err_requires_an_error() -> None:
    processing = start(Pending(job_id="job-1", url="https://news.example/missing"))
    finished = finish(processing, Err(NotFound(url="https://news.example/missing")))
    assert isinstance(finished, Failed)
    assert isinstance(finished.error, NotFound)
    assert finished.error.url.endswith("missing")
