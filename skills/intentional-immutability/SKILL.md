---
name: intentional-immutability
description: Use when Python code mutates shared dicts, lists, or dataclasses across pipeline stages. Apply Rust's "Aliasing XOR Mutability" principle using frozen dataclasses, tuples, and dataclasses.replace.
---

# Intentional immutability & The Ownership Law

Rust's borrow checker is built on one invariant:
> **Aliasing XOR Mutability:** You can have many shared readers (`&T`), OR one exclusive writer (`&mut T`). Never both.

Python does not have a borrow checker to enforce this at compile time, but
the architectural bug is identical: **when multiple references to a mutable
object exist, a mutation anywhere corrupts state everywhere.**

## Use this skill when

- A pipeline function returns the same object it received and callers rely on
  that side effect.
- A module-level list or dict is shared or used as a default (`setdefault("topics", SHARED)`).
- Tests fail intermittently depending on test execution order.
- Two async tasks or workers see each other's in-place updates.

## Do not use this skill when

- You are accumulating into a private, local list inside a function. That is fine.
- The object is a performance-sensitive buffer and copying would degrade throughput.
- You would wrap every primitive in a frozen wrapper.

## The Principle: Keep Mutation Private, Share Immutably

1. **Shared data across boundaries must be immutable:**
   Use `@dataclass(frozen=True)` and `tuple[str, ...]`.
2. **Transformations return a new object:**
   Use `dataclasses.replace`.
3. **Local mutation is permitted only if strictly private:**
   Building a temporary list inside a function before converting it to a tuple
   is completely sound—because no alias exists yet!

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


def tag_topics(article: Article) -> Article:
    # Private mutation: ok because topics is local and unshared
    local_tags = ["news"]
    if "bike" in article.body.lower():
        local_tags.append("transportation")
    local_tags.append("ingested")
    # Published as immutable tuple:
    return replace(article, topics=tuple(local_tags))


def enrich(article: Article) -> Article:
    for stage in (count_words, detect_language, tag_topics):
        article = stage(article)
    return article
```

Now, no caller can mutate an article out from underneath another worker.
Tests can reuse fixtures without fear of mutation leaks.

## Fun Fact: Python's built-in borrow checker
Did you know Python has a built-in borrow checker at runtime?
If you create a `memoryview(bytearray(b"abc"))`, trying to mutate or resize the
bytearray while the view exists raises:
`BufferError: Existing exports of data: object cannot be re-allocated`.
Python core developers had to invent a borrow check to prevent memory corruption!

## Review checklist

- Does a function mutate an argument that another part of the system might hold?
- Is there a mutable default or a module-level collection?
- Did you use `tuple` instead of `list` for published collections?

## In this repo

- Problem: `src/ingest/before/pipeline.py`
- Solution: `src/ingest/after/pipeline.py`
- Tests: `tests/test_before_pipeline.py`, `tests/test_after_pipeline.py`
- Invalid type check: `typecheck/invalid/mutate_frozen_article.py`
