# Original (the teaching bugs)

From `src/ingest/before/errors.py`:

- `ingest()` returns `None` on missing **and** on timeout.
- Invalid title raises `ValueError`.
- Callers cannot tell a 404 from a blip.

From `src/ingest/before/jobs.py`:

- `status` is a string.
- `complete(None)` is legal.
- `fail()` then `complete(...)` leaves a stale `error`.

From `src/ingest/before/pipeline.py`:

- `SHARED_TOPICS` is a module-level list.
- `setdefault("topics", SHARED_TOPICS)` aliases that list into every article
  that did not pass its own topics.
- Enriching a bike-lane story makes a later weather story look like
  transportation coverage.
