# Stealing Good Ideas from Rust

Companion repository for a 40-minute talk at Alamo Python (Geekdom, November 16):

**Python patterns for reliability in the age of AI coding agents.**

You do not need to write Rust to think like a Rust developer. And when AI
writes your Python, you can give it mechanical compiler guardrails.

This repo contains a self-contained teaching app, a 34-slide deck (HTML and PPTX),
a timed speaker script, and five portable agent skills. Zero cloud, zero network.

## What you will find

| Path | Purpose |
|---|---|
| `src/ingest/before/` | Realistic backend code with subtle design bugs |
| `src/ingest/after/` | The same service refactored with the four patterns |
| `tests/` | 31 automated tests encoding both bugs and fixes |
| `typecheck/` | What Pyright catches (typestates, NewType, assert_never) |
| `skills/` | Five reusable agent skills (`SKILL.md`) |
| `prompts/` | Prompts for reproducing the agent demo |
| `examples/agent-demo/` | Prepared naive vs skilled AI reviews |
| `presentation/slides.html` | 34-slide interactive HTML deck (styled after Alamo Python flyer) |
| `presentation/stealing-good-ideas-from-rust.pptx` | 16:9 Google Slides ready deck with full speaker notes |
| `presentation/SCRIPT.md` | Full 40-minute conversational speaker script |
| `presentation/PRESENTER.md` | Stage cheat-sheet with timing and demo commands |
| `docs/agent-guidance.md` | Repository-wide agent instructions |

## The Four Architectural Patterns

1. **Explicit Error Boundaries:** Model expected failures as `Ok | Err` values.
   Stop returning `None` that means both 404 and timeout.
2. **Typestates & Method Gating:** `Pending.start() -> Processing`, `Processing.finish() -> Completed | Failed`.
   Calling `.finish()` on a `Pending` job does not compile.
3. **Compiler Contracts:**
   - Zero-cost `NewType` (`JobId`, `Url`) stops argument transposition.
   - `assert_never` turns Python `match` into an exhaustive compiler check.
4. **The Ownership Law (Aliasing XOR Mutability):** Multiple shared readers OR
   one exclusive writer, never both. Immutable published dataclasses and private
   local mutation prevent leaked state across pipeline stages.

## The AI Punchline: The Compiler as the Agent's Leash

When you prompt an AI coding agent on loose Python (dicts, mutable lists, ambiguous `None`),
it hallucinates invalid states and swaps string arguments.
When you give it typestates, `NewType`, and `assert_never`, **the type checker acts as a
mechanical leash.** Pyright fails on invalid calls, and the agent self-corrects before
opening the pull request.

## Setup

Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cd thinking-in-rust-writing-in-python
uv sync --group dev
uv run pytest
uv run ruff check .
uv run pyright
```

## Demo commands

The catalog is in-memory. Four URLs exist:

- `https://news.example/ok`
- `https://news.example/missing`
- `https://news.example/empty-title`
- `https://news.example/timeout`

```bash
# 1. Explicit Errors
uv run python -m ingest demo --mode before --url https://news.example/timeout
uv run python -m ingest demo --mode after --url https://news.example/timeout

# 2. Typestate compile-time check
uv run pyright -p typecheck/invalid typecheck/invalid/cannot_finish_pending_job.py

# 3. NewType argument swap check
uv run pyright -p typecheck/invalid typecheck/invalid/swapped_newtype_arguments.py

# 4. Ownership / Pipeline isolation
uv run python -m ingest pipeline --mode before
uv run python -m ingest pipeline --mode after
```

## Agent skills

Portable `SKILL.md` files compatible with Claude Code, Cursor, Codex, and Hermes:

- `skills/explicit-error-handling/`
- `skills/model-valid-states/`
- `skills/type-driven-contracts/`
- `skills/intentional-immutability/`
- `skills/python-design-review/`

## Talk materials

- **Google Slides:** Import `presentation/stealing-good-ideas-from-rust.pptx` into Google Drive.
- **Local Browser:** Open `presentation/slides.html`. Keys: Arrow keys, `N` (notes), `F` (fullscreen).

## License

MIT.
