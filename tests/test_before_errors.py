from __future__ import annotations

import pytest

from ingest.before.errors import ingest
from ingest.catalog import EMPTY_TITLE_URL, MISSING_URL, OK_URL, TIMEOUT_URL


def test_success_returns_a_dict() -> None:
    article = ingest(OK_URL)
    assert article is not None
    assert article["title"].startswith("City council")


def test_missing_returns_none() -> None:
    assert ingest(MISSING_URL) is None


def test_timeout_also_returns_none() -> None:
    assert ingest(TIMEOUT_URL) is None


def test_missing_and_timeout_are_indistinguishable() -> None:
    assert ingest(MISSING_URL) == ingest(TIMEOUT_URL)


def test_invalid_title_raises() -> None:
    with pytest.raises(ValueError, match="title"):
        ingest(EMPTY_TITLE_URL)
