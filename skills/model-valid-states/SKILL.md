---
name: model-valid-states
description: Use when a Python object uses status strings plus optional fields, and invalid combinations are representable (completed without a result, failed without an error). Replace them with tagged unions so each state carries only the data that state needs.
---

# Model valid states

If a `status: str` field and two optional fields can describe an impossible
situation, someone will eventually persist that situation.

## Use this skill when

- You see `status` / `state` / `kind` as a string or enum **plus** several
  `X | None` fields that are only meaningful for some statuses.
- Callers write `if job.result is None` after already checking
  `job.status == "completed"`.
- Magic strings (`"pending"`, `"done"`, `"complete"`, `"COMPLETED"`) have
  already drifted.

## Do not use this skill when

- There is only one state and a couple of required fields.
- You would create a class per JSON key in a throwaway parser.
- The domain really does have optional data that is independent of state.

Python dataclasses will not stop you from writing a bad union. Pyright will
flag `job.article` on a `Pending` job **if the object is typed as `Pending`**,
not if it has been widened to `object`.

## Pattern

Replace:

```python
@dataclass
class Job:
    status: str
    result: dict | None
    error: str | None
```

with one frozen dataclass per state:

```python
@dataclass(frozen=True)
class Pending:
    job_id: str
    url: str

@dataclass(frozen=True)
class Processing:
    job_id: str
    url: str

@dataclass(frozen=True)
class Completed:
    job_id: str
    article: Article

@dataclass(frozen=True)
class Failed:
    job_id: str
    error: IngestError

type Job = Pending | Processing | Completed | Failed
```

Transitions return a *new* state. They do not mutate fields in place.

```python
def finish(job: Processing, result: Result[Article, IngestError]) -> Completed | Failed:
    match result:
        case Ok(value):
            return Completed(job_id=job.job_id, article=value)
        case Err(error):
            return Failed(job_id=job.job_id, error=error)
```

A completed job without an article cannot be constructed. A failed job without
an error cannot be constructed.

## Review checklist

- Can you construct a completed-without-result object in one line?
- Do transitions keep stale fields from a previous state?
- Is `match` exhaustive for the states you actually handle?
- Are you using this to model *domain* states, not every boolean flag?

## In this repo

- Problem: `src/ingest/before/jobs.py`
- Solution: `src/ingest/after/jobs.py`
- Invalid example Pyright should catch: `typecheck/invalid/pending_has_no_article.py`
