"""Job states as a typestate machine.

Methods only exist in states where they are valid.
Transitions return new types.
Exhaustiveness is verified via assert_never.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import assert_never

from ingest.after.errors import IngestError
from ingest.after.pipeline import Article
from ingest.after.result import Err, Ok, Result
from ingest.after.types import JobId, Url


@dataclass(frozen=True)
class Pending:
    job_id: JobId
    url: Url

    def start(self) -> Processing:
        """Transitions to Processing. .finish() does not exist in Pending."""
        return Processing(job_id=self.job_id, url=self.url)


@dataclass(frozen=True)
class Processing:
    job_id: JobId
    url: Url

    def finish(self, result: Result[Article, IngestError]) -> Completed | Failed:
        """Transitions to Completed or Failed depending on result."""
        match result:
            case Ok(value):
                return Completed(job_id=self.job_id, article=value)
            case Err(error):
                return Failed(job_id=self.job_id, error=error)


@dataclass(frozen=True)
class Completed:
    job_id: JobId
    article: Article


@dataclass(frozen=True)
class Failed:
    job_id: JobId
    error: IngestError


type Job = Pending | Processing | Completed | Failed


def start(job: Pending) -> Processing:
    return job.start()


def finish(job: Processing, result: Result[Article, IngestError]) -> Completed | Failed:
    return job.finish(result)


def describe(job: Job) -> str:
    """Exhaustive status inspect verified by Pyright via assert_never."""
    match job:
        case Pending(job_id, _):
            return f"pending:{job_id}"
        case Processing(job_id, _):
            return f"processing:{job_id}"
        case Completed(job_id, article):
            return f"completed:{job_id}:{article.title}"
        case Failed(job_id, error):
            return f"failed:{job_id}:{type(error).__name__}"
        case _ as unreachable:
            assert_never(unreachable)
