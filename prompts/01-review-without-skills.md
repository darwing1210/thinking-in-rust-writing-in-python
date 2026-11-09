# Review the article ingestion service

You are reviewing `src/ingest/before/` in this repository.

The service fetches an article by URL, validates it, enriches metadata, and
tracks a background job.

Please:

1. Identify bugs, API issues, and maintainability problems.
2. Propose a refactor.
3. Do not look at `src/ingest/after/`, `skills/`, or `examples/`.

Keep the proposal practical. We still need the same behaviors:

- success
- missing article
- invalid title
- upstream timeout
- enrichment (word count, language, topics)
- job lifecycle pending → processing → completed/failed
