from __future__ import annotations

from ingest.before.jobs import Job


def test_completed_job_can_omit_result() -> None:
    job = Job(job_id="job-1", url="https://news.example/ok")
    job.complete(None)
    assert job.status == "completed"
    assert job.result is None


def test_failed_job_can_omit_error() -> None:
    job = Job(job_id="job-1", url="https://news.example/ok")
    job.fail()
    assert job.status == "failed"
    assert job.error is None


def test_completed_job_can_still_carry_a_stale_error() -> None:
    job = Job(job_id="job-1", url="https://news.example/ok")
    job.fail("boom")
    job.complete({"title": "ok"})
    assert job.status == "completed"
    assert job.error == "boom"
