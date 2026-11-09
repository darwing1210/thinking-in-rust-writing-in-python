"""Pending jobs do not have an article. Pyright should flag this access."""

from ingest.after.jobs import Pending
from ingest.after.types import JobId, Url

job = Pending(job_id=JobId("job-1"), url=Url("https://news.example/ok"))
print(job.article)
