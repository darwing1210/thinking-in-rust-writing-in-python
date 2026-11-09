"""Pending jobs do not have an article. Pyright should flag this access."""

from ingest.after.jobs import Pending

job = Pending(job_id="job-1", url="https://news.example/ok")
print(job.article)
