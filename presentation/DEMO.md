# Demo sheet

Keep this open in a second terminal.

## Before the talk

```bash
cd ~/code/thinking-in-rust-writing-in-python
uv sync --group dev
```

Open these files in a tab before you start:
- `presentation/SCRIPT.md`
- `presentation/PRESENTER.md`
- `examples/agent-demo/naive-review.md`
- `examples/agent-demo/skilled-review.md`

## Demo 1 — timeout before vs after

```bash
uv run python -m ingest demo --mode before --url https://news.example/timeout
uv run python -m ingest demo --mode after --url https://news.example/timeout
```

Say: "Before: we can't tell what happened. After: we can."

## Demo 2 — Pyright catches the bad state

```bash
uv run pyright -p typecheck/invalid typecheck/invalid/cannot_finish_pending_job.py
```

Say: "The compiler catches it before runtime."

## Demo 3 — pipeline before vs after

```bash
uv run python -m ingest pipeline --mode before
uv run python -m ingest pipeline --mode after
```

Say: "The after version doesn't leak tags across articles."

## Demo 4 — naive vs skilled review

Read 2 lines from `naive-review.md`, then 2 lines from `skilled-review.md`.
Then rerun Demo 2 once.

Say: "The agent gets better when the code is clearer."

## If something breaks

- Don't debug live for more than 20 seconds.
- Say the expected line from the slide and move on.
- If the terminal is weird, just use the slide and keep talking.
