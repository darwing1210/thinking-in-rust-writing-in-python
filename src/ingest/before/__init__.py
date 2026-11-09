"""The 'before' codebase: it works, and it hides several design bugs."""

from ingest.before.errors import ingest
from ingest.before.jobs import Job
from ingest.before.pipeline import SHARED_TOPICS, enrich

__all__ = ["Job", "SHARED_TOPICS", "enrich", "ingest"]
