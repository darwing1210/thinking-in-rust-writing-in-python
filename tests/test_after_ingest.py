from __future__ import annotations

from ingest.after.errors import NotFound, Retryable, ValidationFailed
from ingest.after.ingest import ingest
from ingest.after.result import Err, Ok
from ingest.catalog import EMPTY_TITLE_URL, MISSING_URL, OK_URL, TIMEOUT_URL


def test_success_is_ok() -> None:
    result = ingest(OK_URL)
    assert isinstance(result, Ok)
    assert result.value.title.startswith("City council")


def test_missing_is_not_found() -> None:
    result = ingest(MISSING_URL)
    assert result == Err(NotFound(url=MISSING_URL))


def test_timeout_is_retryable() -> None:
    result = ingest(TIMEOUT_URL)
    assert isinstance(result, Err)
    assert isinstance(result.error, Retryable)


def test_invalid_title_is_validation_failed() -> None:
    result = ingest(EMPTY_TITLE_URL)
    assert result == Err(ValidationFailed(fields=("title",)))


def test_callers_can_branch_on_error_type() -> None:
    kinds: list[str] = []
    for url in (OK_URL, MISSING_URL, EMPTY_TITLE_URL, TIMEOUT_URL):
        match ingest(url):
            case Ok(_):
                kinds.append("ok")
            case Err(error):
                match error:
                    case NotFound():
                        kinds.append("not_found")
                    case ValidationFailed():
                        kinds.append("invalid")
                    case Retryable():
                        kinds.append("retry")
    assert kinds == ["ok", "not_found", "invalid", "retry"]
