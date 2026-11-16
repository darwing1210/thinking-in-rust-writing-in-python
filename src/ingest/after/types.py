"""Zero-cost semantic types. Prevents accidental argument swapping.

A NewType is a label, not a check: ``Url("not a url")`` type-checks fine.
Check raw input once at the edge with ``parse_url``; trust ``Url`` after that.
"""

from __future__ import annotations

from typing import NewType
from urllib.parse import urlsplit

from ingest.after.errors import ValidationFailed
from ingest.after.result import Err, Ok, Result

JobId = NewType("JobId", str)
Url = NewType("Url", str)
ArticleId = NewType("ArticleId", str)


def parse_url(raw: str) -> Result[Url, ValidationFailed]:
    """Check raw input once, at the edge. Inside the app, a Url is trusted."""
    parts = urlsplit(raw.strip())
    if parts.scheme not in ("http", "https"):
        return Err(ValidationFailed(("url",)))
    if not parts.netloc:
        return Err(ValidationFailed(("url",)))
    return Ok(Url(raw.strip()))
