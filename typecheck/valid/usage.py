"""These files are supposed to type-check cleanly under pyright --strict."""

from __future__ import annotations

from ingest.after.errors import NotFound, Retryable, ValidationFailed
from ingest.after.ingest import ingest
from ingest.after.jobs import Completed, Failed, Pending, describe
from ingest.after.pipeline import enrich
from ingest.after.result import Err, Ok
from ingest.after.types import JobId, Url
from ingest.catalog import OK_URL


def handle(url: str) -> str:
    match ingest(url):
        case Ok(article):
            enriched = enrich(article)
            return f"ok:{enriched.title}:{enriched.word_count}"
        case Err(error):
            match error:
                case NotFound(missing):
                    return f"not_found:{missing}"
                case ValidationFailed(fields):
                    return f"invalid:{','.join(fields)}"
                case Retryable(reason):
                    return f"retry:{reason}"


def run_job(url: str) -> Completed | Failed:
    # Typestate: Pending -> Processing -> Completed | Failed
    pending = Pending(job_id=JobId("job-1"), url=Url(url))
    processing = pending.start()
    return processing.finish(ingest(url))


def inspect_status(job: Pending | Completed | Failed) -> str:
    return describe(job)


def title_of(job: Completed) -> str:
    return job.article.title


def demo() -> str:
    return handle(OK_URL)
