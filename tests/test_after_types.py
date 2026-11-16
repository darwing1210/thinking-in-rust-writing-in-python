"""parse_url: NewType is a label, so the check happens once at the edge."""

from ingest.after import Err, Ok, Url, ValidationFailed, parse_url


def test_newtype_is_only_a_label() -> None:
    # Type-checks and runs. NewType does not validate anything.
    assert Url("not a url") == "not a url"


def test_parse_url_accepts_http_urls() -> None:
    assert parse_url("https://news.example/ok") == Ok(Url("https://news.example/ok"))


def test_parse_url_rejects_garbage() -> None:
    assert parse_url("not a url") == Err(ValidationFailed(fields=("url",)))
    assert parse_url("ftp://news.example/x") == Err(ValidationFailed(fields=("url",)))
