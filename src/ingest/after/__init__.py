"""The 'after' codebase: explicit contracts, typestates, and intentional immutability."""

from ingest.after.errors import IngestError, NotFound, Retryable, ValidationFailed
from ingest.after.ingest import ingest
from ingest.after.jobs import (
    Completed,
    Failed,
    Job,
    Pending,
    Processing,
    describe,
    finish,
    start,
)
from ingest.after.pipeline import Article, enrich
from ingest.after.result import Err, Ok, Result
from ingest.after.types import ArticleId, JobId, Url, parse_url

__all__ = [
    "Article",
    "ArticleId",
    "Completed",
    "Err",
    "Failed",
    "IngestError",
    "Job",
    "JobId",
    "NotFound",
    "Ok",
    "Pending",
    "Processing",
    "Result",
    "Retryable",
    "Url",
    "ValidationFailed",
    "describe",
    "enrich",
    "finish",
    "ingest",
    "parse_url",
    "start",
]
