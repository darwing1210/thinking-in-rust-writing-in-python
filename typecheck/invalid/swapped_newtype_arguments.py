"""NewType prevents accidental argument transposition."""

from ingest.after.jobs import Pending
from ingest.after.types import JobId, Url

my_job_id = JobId("job-123")
my_url = Url("https://news.example/ok")

# Bug: swapped arguments! Passing (Url, JobId) where (JobId, Url) is required.
job = Pending(job_id=my_url, url=my_job_id)
