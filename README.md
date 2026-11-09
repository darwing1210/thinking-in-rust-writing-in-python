# Thinking in Rust, Writing in Python

Companion repository for a 40-minute PySanAntonio talk:

**Safer Python design patterns in the age of AI coding agents.**

You do not need to write Rust to think like a Rust developer. And when AI
writes your Python, you can teach it to apply those same principles.

This repo is a teaching app, a slide deck, a speaker script, and four
portable agent skills. There is no network and no cloud.

## What you will find

| Path | Purpose |
|---|---|
| `src/ingest/before/` | Realistic code with three design bugs |
| `src/ingest/after/` | The same service after the three patterns |
| `tests/` | Behavior of both sides, including the bugs |
| `typecheck/` | What Pyright can and cannot catch |
| `skills/` | Reusable agent skills (`SKILL.md`) |
| `prompts/` | Prompts for reproducing the agent demo |
| `examples/agent-demo/` | Prepared naive vs skilled reviews |
| `presentation/slides.html` | ~20-slide deck |
| `presentation/SCRIPT.md` | Full 40-minute speaker script |
| `presentation/PRESENTER.md` | Demo commands and timing |
| `docs/agent-guidance.md` | Repository-wide agent instructions |

## The three patterns

1. **Explicit error handling** — expected failures as `Ok | Err` values,
   not `None` that means both 404 and timeout.
2. **Valid states** — `Pending | Processing | Completed | Failed` instead of
   a status string plus optional fields.
3. **Intentional immutability** — frozen `Article`, tuples, `replace()`,
   so enrichment cannot leak tags across articles.

Python does not give you Rust's compile-time guarantees. Pyright helps if
you run it. Exceptions and mutation remain the right tool in many places.

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
uv run python -m ingest demo --mode before --url https://news.example/timeout
uv run python -m ingest demo --mode after --url https://news.example/timeout

uv run python -m ingest jobs --mode before --url https://news.example/missing
uv run python -m ingest jobs --mode after --url https://news.example/missing

uv run python -m ingest pipeline --mode before
uv run python -m ingest pipeline --mode after
```

`before` timeout prints `None` (same as missing). `after` prints `retryable:`.

## Agent skills

Portable `SKILL.md` files, compatible with Claude Code, Codex, Cursor, and
similar tools that load a skill directory:

- `skills/explicit-error-handling/`
- `skills/model-valid-states/`
- `skills/intentional-immutability/`
- `skills/python-design-review/`

Point the tool at `skills/` or copy a skill folder into its skills path.
Repository-wide guidance: `docs/agent-guidance.md`.

Prepared (non-live) agent comparison: `examples/agent-demo/`.

## Talk materials

Open `presentation/slides.html` in a browser.

- Arrow keys / space: next and previous
- `Home` / `End`: first / last
- `N`: speaker notes
- `F`: fullscreen
- Slide index is stored in `localStorage`

Follow `presentation/SCRIPT.md` while presenting. Demo cues match
`presentation/PRESENTER.md`.

## License

MIT. The article texts are invented; they are not real news.
