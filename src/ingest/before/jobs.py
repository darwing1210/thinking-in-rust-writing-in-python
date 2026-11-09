"""A job object that can represent impossible combinations of fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Job:
    job_id: str
    url: str
    status: str = "pending"
    result: dict[str, Any] | None = None
    error: str | None = None

    def start(self) -> None:
        self.status = "processing"

    def complete(self, result: dict[str, Any] | None = None) -> None:
        # Nothing stops us from marking the job completed without a result,
        # or leaving a previous error hanging around.
        self.status = "completed"
        self.result = result

    def fail(self, error: str | None = None) -> None:
        self.status = "failed"
        self.error = error
