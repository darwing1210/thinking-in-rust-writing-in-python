"""assert_never catches missing variants in pattern matching at type-check time."""

from typing import assert_never

from ingest.after.jobs import Completed, Failed, Job, Pending
from ingest.after.types import JobId, Url


def check_status(job: Job) -> str:
    # Bug: Forgot to handle Processing!
    match job:
        case Pending():
            return "pending"
        case Completed():
            return "completed"
        case Failed():
            return "failed"
        case _ as unreachable:
            # Pyright flags this because unreachable can still be Processing!
            assert_never(unreachable)


job: Job = Pending(job_id=JobId("j"), url=Url("u"))
print(check_status(job))
