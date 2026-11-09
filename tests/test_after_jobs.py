from __future__ import annotations

from ingest.after.errors import NotFound
from ingest.after.jobs import Completed, Failed, Pending, describe, finish, start
from ingest.after.pipeline import Article
from ingest.after.result import Err, Ok
from ingest.after.types import JobId, Url


def test_start_returns_processing() -> None:
    pending = Pending(job_id=JobId("job-1"), url=Url("https://news.example/ok"))
    processing = pending.start()
    assert processing.job_id == "job-1"
    assert processing.url == pending.url
    # also test module-level function
    assert start(pending) == processing


def test_finish_ok_requires_an_article() -> None:
    pending = Pending(job_id=JobId("job-1"), url=Url("https://news.example/ok"))
    processing = pending.start()
    article = Article(
        url="https://news.example/ok",
        title="City council approves downtown bike lanes",
        body="The council voted.",
        source="example-news",
    )
    finished = processing.finish(Ok(article))
    assert isinstance(finished, Completed)
    assert finished.article.title.startswith("City council")
    assert finish(processing, Ok(article)) == finished


def test_finish_err_requires_an_error() -> None:
    pending = Pending(job_id=JobId("job-1"), url=Url("https://news.example/missing"))
    processing = pending.start()
    finished = processing.finish(Err(NotFound(url="https://news.example/missing")))
    assert isinstance(finished, Failed)
    assert isinstance(finished.error, NotFound)
    assert finished.error.url.endswith("missing")


def test_describe_is_exhaustive() -> None:
    pending = Pending(job_id=JobId("j1"), url=Url("https://news.example/ok"))
    processing = pending.start()
    article = Article(url="u", title="T", body="B", source="S")
    completed = processing.finish(Ok(article))
    failed = processing.finish(Err(NotFound(url="u")))

    assert describe(pending) == "pending:j1"
    assert describe(processing) == "processing:j1"
    assert describe(completed) == "completed:j1:T"
    assert describe(failed) == "failed:j1:NotFound"
