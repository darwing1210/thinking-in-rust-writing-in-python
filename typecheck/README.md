# Type-check examples

`typecheck/valid/` is included in the Pyright project and must stay clean.

`typecheck/invalid/` is excluded from the default Pyright run. These files
exist to show what the type checker *can* catch after the refactor — not to
pretend Python has Rust's compiler.

```bash
uv run pyright            # valid examples + src + tests
uv run pyright --project typecheck/invalid
```

The second command is expected to report errors, including:

| File | What Pyright should complain about |
|---|---|
| `pending_has_no_article.py` | `Pending` has no attribute `article` |
| `result_is_not_article.py` | `Ok \| Err` has no attribute `title` |
| `mutate_frozen_article.py` | `tuple` has no `append` |

This is the honest version of "make invalid states hard to represent" in Python:
the type checker helps *if you run it*. Runtime will still explode if you ignore it.
