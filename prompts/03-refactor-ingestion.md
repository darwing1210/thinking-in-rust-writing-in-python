# Refactor ingestion using the skills

Implement the review from `prompts/02-review-with-skills.md`.

Write the new code under `src/ingest/after/` if it does not already exist.
Do not "fix" the teaching bugs in `src/ingest/before/`.

After the refactor:

```bash
uv run pytest
uv run ruff check .
uv run pyright
```

Then run the demo commands in `presentation/PRESENTER.md` and confirm the
timeout path is distinguishable from not-found.
