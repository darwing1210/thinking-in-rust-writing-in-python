# Skilled review (with the four design skills)

Prepared example of the same prompt after the agent is told to read
`python-design-review`, `explicit-error-handling`, `model-valid-states`,
and `intentional-immutability`.

---

Three bug *classes*, not three style nits.

**1. Explicit errors.** `ingest()` collapses timeout and missing into `None`
and raises on validation. Callers cannot choose "retry" vs "record a miss"
without re-fetching. Use `Result[Article, NotFound | ValidationFailed | Retryable]`.
Keep unexpected bugs as exceptions. Do not wrap `len()`.

**2. Valid states.** `Job` can be `completed` with `result is None`, and
`failed` then `completed` with a leftover error. Replace status + optional
fields with `Pending | Processing | Completed | Failed`. `Completed` requires
an `Article`. `Failed` requires an `IngestError`. Transitions return new
objects.

**3. Intentional immutability.** `SHARED_TOPICS` plus `setdefault` means the
second article inherits the first article's tags. Make `Article` a frozen
dataclass with `topics: tuple[str, ...]`. Enrichment uses `replace`.

Trade-offs: more types to read; Pyright only helps if we run it; this is
overkill for a one-off script. It is not overkill for a pipeline that
retries, bills, or pages on the wrong failure.

I would not add a Result library, an Enum for job status *in addition to*
the union, or extra logging as a substitute for a typed error.

---

What this review optimized for: the next agent cannot construct the illegal
states without noticing, and the timeout path is a value.
