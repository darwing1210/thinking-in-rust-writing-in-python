"""The 'after' codebase: same behavior, explicit contracts."""

from ingest.after.errors import IngestError, NotFound, Retryable, ValidationFailed
from ingest.after.ingest import ingest
from ingest.after.jobs import Completed, Failed, Job, Pending, Processing, finish, start
from ingest.after.pipeline import Article, enrich
from ingest.after.result import Err, Ok, Result

__all__ = [
    "Article",
    "Completed",
    "Err",
    "Failed",
    "IngestError",
    "Job",
    "NotFound",
    "Ok",
    "Pending",
    "Processing",
    "Result",
    "Retryable",
    "ValidationFailed",
    "enrich",
    "finish",
    "ingest",
    "start",
]
