"""Expected ingest failures, modeled as data rather than control flow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NotFound:
    url: str


@dataclass(frozen=True)
class ValidationFailed:
    fields: tuple[str, ...]


@dataclass(frozen=True)
class Retryable:
    reason: str


type IngestError = NotFound | ValidationFailed | Retryable
