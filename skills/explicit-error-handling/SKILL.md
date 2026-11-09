---
name: explicit-error-handling
description: Use when a Python function has expected failures (missing records, validation, retryable I/O) mixed with None, booleans, or exceptions. Model those failures as values with Ok/Err unions. Do not use this for true bugs or when a single exception type is already the project convention.
---

# Explicit error handling

Expected failures are part of the function contract. Hide them in `None`,
`False`, or a catch-all `except Exception`, and callers cannot tell a 404 from
a timeout from "I forgot to return".

## Use this skill when

- A function returns `T | None` and `None` means more than one thing.
- Validation errors are raised, but missing data is returned as `None`.
- Retryable I/O and permanent failures share the same return path.
- An agent is about to "fix" this by adding more `try/except` or more `Optional`.

## Do not use this skill when

- The failure is a programming bug (index out of range, invariant broken). Raise.
- The project already has a consistent exception hierarchy and catching it at
  the boundary is the convention.
- You would introduce a Result monad framework, `.and_then()` chains, or a
  third-party `result` library for a 30-line script.

Python will not refuse to compile if a caller ignores an `Err`. The value is
clarity plus what Pyright can flag **if you run it**.

## Pattern

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Ok[T]:
    value: T

@dataclass(frozen=True)
class Err[E]:
    error: E

type Result[T, E] = Ok[T] | Err[E]
```

Model *distinct* expected failures as distinct types, then union them:

```python
@dataclass(frozen=True)
class NotFound:
    url: str

@dataclass(frozen=True)
class ValidationFailed:
    fields: tuple[str, ...]

@dataclass(frozen=True)
class Retryable:
    reason: str

def ingest(url: str) -> Result[Article, NotFound | ValidationFailed | Retryable]:
    ...
```

Callers branch with `match`. Do not `.value` without checking.

```python
match ingest(url):
    case Ok(article):
        save(article)
    case Err(NotFound()):
        record_miss()
    case Err(ValidationFailed(fields)):
        record_invalid(fields)
    case Err(Retryable()):
        schedule_retry()
```

## Review checklist

- Can a caller distinguish retryable from permanent failures without reading
  log lines?
- Are unexpected bugs still exceptions?
- Is the error type specific enough that `match` is useful?
- Did you avoid wrapping *every* function in Result?

## In this repo

- Problem: `src/ingest/before/errors.py`
- Solution: `src/ingest/after/result.py`, `src/ingest/after/errors.py`,
  `src/ingest/after/ingest.py`
- Tests: `tests/test_before_errors.py`, `tests/test_after_ingest.py`
