# Type-check examples

`typecheck/valid/` is included in the Pyright project and must stay clean.

`typecheck/invalid/` is excluded from the default Pyright run. These files
exist to show what the type checker *can* catch when you borrow Rust's
guarantees:

```bash
uv run pyright                              # valid examples + src + tests (clean)
uv run pyright --project typecheck/invalid  # expected to report 7 errors
```

The second command reports compile-time errors:

| File | Pattern | What Pyright complains about |
|---|---|---|
| `pending_has_no_article.py` | State modeling | `Pending` has no attribute `article` |
| `cannot_finish_pending_job.py` | Typestates | `Pending` has no method `.finish()` (must `.start()` first) |
| `swapped_newtype_arguments.py` | NewTypes | `Url` is not assignable to parameter `job_id: JobId` |
| `non_exhaustive_match.py` | Exhaustiveness | `Processing` is unhandled before `assert_never` |
| `result_is_not_article.py` | Result union | `Ok \| Err` has no attribute `title` without checking |
| `mutate_frozen_article.py` | Immutability | `tuple` has no attribute `append` |

This is the mechanical core of the talk:
- Typestates gate methods by state.
- `assert_never` makes pattern matching exhaustive across the codebase.
- `NewType` stops argument swapping with zero runtime cost.
- Immutability prevents action-at-a-distance side effects.

When an AI coding agent works in this environment, Pyright acts as its
mechanical guardrail: if the agent hallucinates an invalid state or misses
a branch, the compiler catches it immediately.
