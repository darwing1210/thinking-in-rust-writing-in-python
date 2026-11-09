# Agent guidance

This repository teaches three Python design patterns inspired by Rust.
It is not a Rust tutorial and it is not a framework.

Copy this file to `AGENTS.md` at the repo root if your coding agent loads
that filename automatically.

## Default behavior

- Prefer the smallest change that removes a class of bugs.
- Keep expected failures visible in return types.
- Keep domain states as tagged unions, not status strings plus optional fields.
- Mutate on purpose, locally. Do not share mutable defaults.
- Do not introduce a Result monad library, a DI container, or extra runtime
  dependencies.

## Languages and tools

- Python 3.12+.
- Tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Types: `uv run pyright`
- Demo: `uv run python -m ingest --help`

## Skills

Read these before refactoring `src/ingest/before/`:

- `skills/python-design-review/SKILL.md`
- `skills/explicit-error-handling/SKILL.md`
- `skills/model-valid-states/SKILL.md`
- `skills/intentional-immutability/SKILL.md`

## Honesty about Python

Pyright is not rustc. Ignoring a type error still runs. Frozen dataclasses
can be bypassed. These patterns pay off when humans and agents *follow*
them, not because the language enforces them.

## Do not

- Rewrite `ingest.before` in place unless a prompt says so. The talk compares
  before and after.
- Add network calls, databases, or cloud clients.
- "Improve" the teaching bugs in `before/` — they are intentional.
