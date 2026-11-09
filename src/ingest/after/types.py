"""Zero-cost semantic types. Prevents accidental argument swapping."""

from __future__ import annotations

from typing import NewType

JobId = NewType("JobId", str)
Url = NewType("Url", str)
ArticleId = NewType("ArticleId", str)
