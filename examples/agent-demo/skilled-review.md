# Skilled review (with the design skills)

Prepared example of the same prompt after the agent is guided by the design skills.

---

Four bug *classes* eliminated through compiler-enforced design:

**1. Explicit errors.** `ingest()` collapses timeout and missing into `None`
and raises on validation. Use `Result[Article, NotFound | ValidationFailed | Retryable]`.
Callers must branch on `Ok` vs `Err` before reading the payload.

**2. Typestate machine & method gating.** `Job` status strings allow calling
`.complete()` on unstarted jobs, or leaving stale errors. Replace with
`Pending -> Processing -> Completed | Failed`. Methods are gated: `.start()`
only exists on `Pending`; `.finish()` only exists on `Processing`. Illegal
transitions do not typecheck.

**3. Type-driven contracts.** URLs and job IDs are raw strings vulnerable to
transposition. Use `Url = NewType('Url', str)` and `JobId = NewType('JobId', str)`.
In pattern matching, terminate with `case _ as unreachable: assert_never(unreachable)`
so adding future states breaks the build if unhandled.

**4. Intentional immutability (Aliasing XOR Mutability).** `SHARED_TOPICS` plus
`setdefault` leaks tags across articles. Make `Article` a frozen dataclass with
`topics: tuple[str, ...]`. Stages transform via `dataclasses.replace()`.

Trade-offs: more types to read; Pyright must run in CI; overkill for a 20-line
script. It is indispensable for services where AI agents or teams commit daily.

---

What this review achieved: the compiler acts as a mechanical leash. If the
next agent hallucinates an invalid transition or swaps an argument, Pyright
catches it before the PR is created.
