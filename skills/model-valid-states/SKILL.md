---
name: model-valid-states
description: Use when a Python object uses status strings plus optional fields, and invalid combinations or lifecycle methods are representable. Replace them with typestates and tagged unions so methods only exist in valid states.
---

# Model valid states & Typestates

If a `status: str` field and optional fields can describe an impossible
situation, someone or an AI agent will eventually create that situation.
Furthermore, if an object exposes methods like `.complete()` or `.retry()`
before it has even been started, callers will call them.

## Use this skill when

- You see `status` / `state` / `kind` as a string or enum **plus** several
  `X | None` fields that are only meaningful for some statuses.
- Methods check `if self.status != "expected": raise InvalidStateError`.
- Callers write `if job.result is None` after already checking
  `job.status == "completed"`.

## Do not use this skill when

- There is only one state and a couple of required fields.
- You would create a class per JSON key in a throwaway parser.
- The domain really does have optional data that is independent of state.

## Pattern 1: Tagged Union of States

Replace a single blob with one frozen dataclass per state:

```python
@dataclass(frozen=True)
class Pending:
    job_id: JobId
    url: Url

@dataclass(frozen=True)
class Processing:
    job_id: JobId
    url: Url

@dataclass(frozen=True)
class Completed:
    job_id: JobId
    article: Article

@dataclass(frozen=True)
class Failed:
    job_id: JobId
    error: IngestError

type Job = Pending | Processing | Completed | Failed
```

## Pattern 2: Typestate (Method Gating)

Attach methods **only** to the states where they make sense.
Transitions return a *new* type:

```python
@dataclass(frozen=True)
class Pending:
    job_id: JobId
    url: Url

    def start(self) -> Processing:
        # Calling .finish() here is a static type error!
        return Processing(job_id=self.job_id, url=self.url)

@dataclass(frozen=True)
class Processing:
    job_id: JobId
    url: Url

    def finish(self, result: Result[Article, IngestError]) -> Completed | Failed:
        match result:
            case Ok(value):
                return Completed(job_id=self.job_id, article=value)
            case Err(error):
                return Failed(job_id=self.job_id, error=error)
```

Now:
- `pending.finish(...)` **does not compile** (AttributeError in Pyright).
- `completed.article` always exists.
- An AI coding agent cannot hallucinate illegal lifecycle transitions because
  Pyright rejects the code immediately.

## Review checklist

- Can you construct a completed-without-result object?
- Can you call a transition method on the wrong state?
- Do transitions return a new object instead of mutating in place?
- Is Pyright run in CI to enforce the typestate boundaries?

## In this repo

- Problem: `src/ingest/before/jobs.py`
- Solution: `src/ingest/after/jobs.py`
- Invalid type checks:
  - `typecheck/invalid/pending_has_no_article.py`
  - `typecheck/invalid/cannot_finish_pending_job.py`
