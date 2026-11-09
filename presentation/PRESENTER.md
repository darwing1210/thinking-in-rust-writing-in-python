# Presenter guide

Event: PySanAntonio. Duration: 40 minutes. Deck: `slides.html`.
Script: `SCRIPT.md`. Code: `src/ingest/before` vs `src/ingest/after`.

## Before the talk

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run pyright
uv run pyright --project typecheck/invalid   # expected to fail
```

Open `presentation/slides.html` in a browser. Press `N` once so you know
where notes live, then hide them. Have a terminal tab in the repo root.

If wifi dies, skip live agents. Use `examples/agent-demo/`.

## Timing

| Min | Section | Slides | Demo |
|---:|---|---|---|
| 0–4 | Intro | 1–4 | none |
| 4–12 | Explicit errors | 5–9 | `ingest demo` timeout before/after |
| 12–21 | Valid states | 10–13 | `ingest jobs` missing before/after |
| 21–27 | Immutability | 14–16 | `ingest pipeline` before/after |
| 27–36 | Agents + skills | 17–18 | read naive vs skilled reviews |
| 36–40 | Takeaways, Q&A | 19–20 | repo URL |

## Demo commands (expected output)

Working directory: repo root. `PYTHONPATH` is set by `uv run`.

### Pattern 1 — timeout

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

Also useful, if there is time:

```bash
uv run python -m ingest demo --mode after --url https://news.example/missing
uv run python -m ingest demo --mode after --url https://news.example/empty-title
uv run python -m ingest demo --mode after --url https://news.example/ok
```

### Pattern 2 — completed without a result

```bash
uv run python -m ingest jobs --mode before --url https://news.example/missing
```

JSON with `"status": "completed"` and `"result": null`.

```bash
uv run python -m ingest jobs --mode after --url https://news.example/missing
```

Starts with `Failed`.

### Pattern 3 — shared topics

```bash
uv run python -m ingest pipeline --mode before
```

Second article topics include `transportation`. Note line says inherited.

```bash
uv run python -m ingest pipeline --mode after
```

First topics include `transportation`. Second topics do not.

### Types (optional, 30 seconds)

```bash
uv run pyright typecheck/invalid/pending_has_no_article.py
```

Expect an error: `Pending` has no attribute `article`.

## If a demo fails

Do not debug live past 20 seconds. The script already describes the output.
The tests encode the same facts: `tests/test_cli.py`.

## After the talk

Point people at the README setup block and the four skill folders.
The takeaway is not "rewrite your codebase tonight." It is "steal one
pattern, and put it in a skill so the agent steals it too."
