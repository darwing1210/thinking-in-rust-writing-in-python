---
name: python-design-review
description: Use when reviewing or refactoring Python for maintainability. Look for ambiguous None/exception contracts, invalid representable states, and accidental shared mutation. Prefer the smallest change that removes a real class of bugs. Do not overengineer.
---

# Python design review

Review the code as if the next author is an AI agent who will copy whatever
pattern is already there.

This skill is a filter, not a mandate to apply every Rust-inspired pattern.

## Process

1. Describe the behavior in one paragraph. If you cannot, the types are lying.
2. List expected failures. For each: is it `None`, an exception, a log line, or
   a value? If two failures share a path, flag it.
3. List domain states. For each optional field, ask "when is this allowed to be
   missing?" If the answer is "when status is X", flag it.
4. Trace mutation. If a helper mutates an argument that other stages still
   hold, flag it.
5. Propose the *smallest* pattern that removes the bug class:
   - ambiguous failures → `skills/explicit-error-handling`
   - illegal field combinations → `skills/model-valid-states`
   - shared in-place updates → `skills/intentional-immutability`
6. State the trade-off in one sentence. If the pattern adds types without
   removing a bug class, do not apply it.

## What "better" is not

- More protocols, more ABCs, more `typing.NewType` for every string.
- A Result wrapper around functions that cannot fail.
- Replacing a perfectly good exception with a Result because a blog post did.
- Rewriting working code during a one-line bug fix.

## Checks to run after a refactor

```bash
uv run pytest
uv run ruff check .
uv run pyright
```

Passing tests are necessary and not sufficient. Ask:

- Can a new caller misuse the function without noticing?
- Did the diff make the happy path harder to read?
- Would you still want this code if the AI agent that wrote it left the team?

## In this repo

Start from `src/ingest/before/` and compare with `src/ingest/after/`.
Prepared agent outputs live in `examples/agent-demo/`.
