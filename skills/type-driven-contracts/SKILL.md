---
name: type-driven-contracts
description: Use when domain IDs (user_id, article_id) are raw strings that can be accidentally swapped, or when pattern matching on unions needs compile-time exhaustiveness checking via assert_never.
---

# Type-driven contracts (NewType & assert_never)

Two subtle but devastating bugs plague Python codebases:
1. **Argument transposition:** Swapping two `str` or `int` parameters (`def link(user_id: str, article_id: str)`). Tests pass because both are strings.
2. **Silent fallthrough in match:** Adding a new union variant and forgetting to handle it in downstream match statements. Python returns `None` silently.

Rust solves both at compile time. Modern Python can too.

## Pattern 1: Zero-Cost NewTypes

Use `typing.NewType` to make identifiers distinct at type-check time with **zero runtime cost**:

```python
from typing import NewType

JobId = NewType("JobId", str)
Url = NewType("Url", str)
ArticleId = NewType("ArticleId", str)
```

At runtime, `JobId("123")` is literally the string `"123"`. There is no wrapper object, no memory overhead, and no boxing.

At static analysis time:
```python
def fetch(url: Url, job_id: JobId) -> None: ...

# If an AI agent or developer swaps them:
fetch(my_job_id, my_url)
# Pyright ERROR: Argument of type "JobId" cannot be assigned to parameter "url: Url"
```

## Pattern 2: Compile-Time Exhaustiveness (`assert_never`)

Python's `match/case` does not enforce exhaustiveness by default.
To get Rust's compiler guarantee, add `case _ as unreachable: assert_never(unreachable)`:

```python
from typing import assert_never

def inspect_job(job: Job) -> str:
    match job:
        case Pending(job_id, _):
            return f"pending:{job_id}"
        case Processing(job_id, _):
            return f"running:{job_id}"
        case Completed(job_id, _):
            return f"done:{job_id}"
        case Failed(job_id, _):
            return f"failed:{job_id}"
        case _ as unreachable:
            assert_never(unreachable)
```

Now, if a developer or agent adds `type Job = ... | Cancelled` next month:
**Pyright fails across the entire codebase wherever `assert_never` was placed.**
You cannot deploy with an unhandled state.

## Review checklist

- Are raw strings used for distinct domain identifiers (IDs, URLs, keys)?
- Does pattern matching on closed unions end with `assert_never`?
- Did you avoid creating heavyweight wrapper classes when `NewType` suffices?

## In this repo

- Types: `src/ingest/after/types.py`
- Exhaustive match: `src/ingest/after/jobs.py` (`describe()`)
- Invalid type checks:
  - `typecheck/invalid/swapped_newtype_arguments.py`
  - `typecheck/invalid/non_exhaustive_match.py`
