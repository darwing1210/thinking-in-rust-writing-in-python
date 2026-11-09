# Presenter guide

Event: Alamo Python, Geekdom, November 16. Duration: 40 minutes. Deck: `slides.html`.
Script: `SCRIPT.md`. Code: `src/ingest/before` vs `src/ingest/after`.

## Before the talk

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run pyright
uv run pyright --project typecheck/invalid   # expected to fail with 8 errors
```

Open `presentation/slides.html` in a browser (or upload `stealing-good-ideas-from-rust.pptx` to Google Slides).
Press `N` once so you know where notes live, then hide them.
Have a terminal tab ready in the repo root.

If wifi dies, skip live agents. Use `examples/agent-demo/`.

## Timing

| Min | Section | Slides | Demo |
|---:|---|---|---|
| 0–5 | Intro + disclaimer | 1–5 | none |
| 5–12 | Explicit Errors | 6–10 | `ingest demo` timeout before/after |
| 12–20 | Typestates & Lifecycle Gating | 11–14 | `cannot_finish_pending_job.py` |
| 20–26 | Compiler Contracts | 15–16 | `NewType` & `assert_never` checks |
| 26–32 | Ownership: Aliasing XOR Mutability | 17–19 | `ingest pipeline` before/after |
| 32–37 | The AI Sandbox | 20–21 | read naive vs skilled reviews |
| 37–40 | Takeaways, Q&A | 22–23 | repo URL |

## Demo commands (expected output)

Working directory: repo root. `PYTHONPATH` is set by `uv run`.

### 1. Explicit Errors: Timeout before vs after

```bash
uv run python -m ingest demo --mode before --url https://news.example/timeout
```

```
returned: None
note: None means missing OR timeout. The caller cannot tell.
```

```bash
uv run python -m ingest demo --mode after --url https://news.example/timeout
```

```
retryable: timed out fetching https://news.example/timeout
```

### 2. Typestates: Compile-time method gating

```bash
uv run pyright typecheck/invalid/cannot_finish_pending_job.py
```

```
error: Cannot access attribute "finish" for class "Pending"
  Attribute "finish" is unknown
```

### 3. Compiler Contracts: Swapped IDs & Non-exhaustive Match

```bash
uv run pyright typecheck/invalid/swapped_newtype_arguments.py
```

```
error: Argument of type "Url" cannot be assigned to parameter "job_id" of type "JobId"
```

```bash
uv run pyright typecheck/invalid/non_exhaustive_match.py
```

```
error: Argument of type "Processing" cannot be assigned to parameter "arg" of type "Never"
```

### 4. Ownership: Leaked shared list before vs after

```bash
uv run python -m ingest pipeline --mode before
```

Second article topics include `transportation`. Note line says inherited.

```bash
uv run python -m ingest pipeline --mode after
```

First topics include `transportation`. Second topics do not.

## If a demo fails

Do not debug live past 20 seconds. The script already describes the output.
The tests encode the same facts: `tests/test_cli.py`.

## After the talk

Point people at the README setup block and the five skill folders.
The takeaway is not "rewrite your codebase tonight." It is "steal one
pattern, and put it in a skill so the agent steals it too."
