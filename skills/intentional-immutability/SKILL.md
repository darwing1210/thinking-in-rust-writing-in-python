---
name: intentional-immutability
description: Use when Python code mutates shared dicts, lists, or dataclasses across pipeline stages and callers cannot tell what changed. Prefer frozen dataclasses, tuples, and dataclasses.replace. Do not freeze everything in the process.
---

# Intentional immutability

Rust defaults to immutable bindings because mutation plus sharing is where
action-at-a-distance comes from. Python defaults the other way. You do not
need a borrow checker to make mutation *obvious*.

## Use this skill when

- A pipeline function returns the same object it received and callers rely on
  that side effect.
- A module-level list or dict is used as a default (`setdefault("topics", SHARED)`).
- Tests fail depending on order because one case mutates a shared fixture.
- Two workers or two requests might see each other's in-place updates.

## Do not use this skill when

- You are accumulating into a local list inside a function. That is fine.
- The object is a performance-sensitive buffer and copying would be the bug.
- You would wrap every `int` in a frozen dataclass.

Frozen dataclasses are a *convention plus Pyright*, not a guarantee. Anyone
can drop `frozen=True`. Anyone can use `object.__setattr__`. The win is that
ordinary code cannot shrug and append.

## Pattern

```python
@dataclass(frozen=True)
class Article:
    url: str
    title: str
    body: str
    source: str
    word_count: int = 0
    topics: tuple[str, ...] = ()
    language: str = "und"


def count_words(article: Article) -> Article:
    return replace(article, word_count=len(article.body.split()))


def enrich(article: Article) -> Article:
    for stage in (count_words, detect_language, tag_topics):
        article = stage(article)
    return article
```

Each stage takes an article and returns an article. The original is unchanged.
Two enrichments cannot share a topics list because topics is a tuple created
per call.

## Review checklist

- Does a function mutate an argument *and* return it?
- Is there a mutable default or a module-level collection used as a default?
- Would `replace` make the test simpler because you can keep the input fixture?
- Are you freezing objects that are genuine accumulators?

## In this repo

- Problem: `src/ingest/before/pipeline.py`
- Solution: `src/ingest/after/pipeline.py`
- Tests: `tests/test_before_pipeline.py`, `tests/test_after_pipeline.py`
