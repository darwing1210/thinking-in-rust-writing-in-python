# Naive review (no design skills)

Prepared example of what a capable coding agent often produces when you only
ask "review this" and the surrounding code already uses dicts, None, and
status strings.

---

The ingestion function is a bit messy. I would:

1. Add type hints (`dict[str, Any] | None`) and a `TypedDict` for articles.
2. Log the exception on timeout so operators can see it.
3. Catch `Exception` around `fetch_raw` to make the function safer.
4. Replace status strings with an `Enum`.
5. Add `Optional` annotations on `Job.result` and `Job.error`.
6. Copy the topics list before appending, *or* document that `enrich`
   mutates in place.

Suggested signature:

```python
def ingest(url: str) -> ArticleDict | None:
    ...
```

This keeps the current contract (`None` means failure) and improves typing
and logging. Tests that assert `None` for both missing and timeout would
still pass.

I would not change the return type, because that would be a breaking change
for callers.

---

What this review optimized for: the code still runs, types look modern,
tests stay green.

What it missed: `None` still means two things, a completed job still need
not have a result, and a shared list can still leak across articles unless
the copy is done in every caller.
