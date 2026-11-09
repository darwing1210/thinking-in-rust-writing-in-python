"""Typestate pattern: .finish() does not exist on Pending jobs."""

from ingest.after.errors import NotFound
from ingest.after.jobs import Pending
from ingest.after.result import Err
from ingest.after.types import JobId, Url

job = Pending(job_id=JobId("job-1"), url=Url("https://news.example/ok"))
# Cannot finish a pending job before starting it!
job.finish(Err(NotFound(url="https://news.example/ok")))
