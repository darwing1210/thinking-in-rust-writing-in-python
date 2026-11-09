"""Job states as a tagged union. Invalid combinations cannot be constructed."""

from __future__ import annotations

from dataclasses import dataclass

from ingest.after.errors import IngestError
from ingest.after.pipeline import Article
from ingest.after.result import Err, Ok, Result


@dataclass(frozen=True)
class Pending:
    job_id: str
    url: str


@dataclass(frozen=True)
class Processing:
    job_id: str
    url: str


@dataclass(frozen=True)
class Completed:
    job_id: str
    article: Article


@dataclass(frozen=True)
class Failed:
    job_id: str
    error: IngestError


type Job = Pending | Processing | Completed | Failed


def start(job: Pending) -> Processing:
    return Processing(job_id=job.job_id, url=job.url)


def finish(job: Processing, result: Result[Article, IngestError]) -> Completed | Failed:
    match result:
        case Ok(value):
            return Completed(job_id=job.job_id, article=value)
        case Err(error):
            return Failed(job_id=job.job_id, error=error)
