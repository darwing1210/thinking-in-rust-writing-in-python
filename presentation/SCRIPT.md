# Speaker script — Thinking in Rust, Writing in Python

**Event:** PySanAntonio
**Length:** ~40 minutes
**Deck:** `slides.html` (20 slides)
**Repo root:** one directory up from this file

How to use this: the spoken text is in roman. Stage directions, timing, and
demo cues are in *italics*. Do not read the italics. If you run long, cut
the sentences marked **[cut]**. Target pace is conversational, about 130
words per minute, with pauses on code slides.

---

## 0:00–4:00 — Introduction
### Slides 1–4

### Slide 1 — Title
*Lights, title slide. Stand still for one breath.*

Good evening. The talk is called **Thinking in Rust, Writing in Python**.
The subtitle is the part I actually care about: **safer Python design
patterns in the age of AI coding agents**.

I am going to make you a promise up front. You do not need to know Rust.
You do not need to install Rust. You will see maybe four lines of Rust the
entire night, and if you forget them on the way to the parking lot, you
still got the talk.

We are going to steal *ideas*, not syntax.

### Slide 2 — Who this is for

If you write Python services — ingestion jobs, workers, HTTP handlers —
this is for you. If you have ever returned `None` and hoped the caller
would know what it meant, this is for you. If you have pasted a function
into ChatGPT or Claude or Codex and gotten back something that *ran* and
still made you nervous, this is definitely for you.

*Audience ping.* Quick show of hands: who has shipped Python that an AI
agent wrote at least part of, in the last six months?

*Look around. Nod. Do not count.*

Yeah. That is the room.

### Slide 3 — What we will do in 40 minutes

Here is the map. Three patterns, one agent section, then questions.

1. Explicit errors — Rust's `Result`, in Python.
2. Valid states — making illegal combinations unconstructable.
3. Intentional immutability — mutation you can see.
4. How to pack those into agent skills so the machine does not "helpfully"
   put the bugs back.

Each pattern uses the same toy service: an **article ingestion** pipeline.
Fetch a story by URL, validate it, enrich it, track a background job. No
network. Four fake URLs. You can run every demo from the repo after this
with `uv run python -m ingest`.

### Slide 4 — The sentence on the tin

*Read it, then paraphrase. Do not rush.*

You don't need to write Rust to think like a Rust developer. And when AI
writes your Python, you can teach it to apply those same principles.

That second sentence is why this is not a 2018 types talk with extra
slides. Agents copy the patterns they can see. If the pattern in the file
is `return None`, you will get more `return None`. If the pattern is a
tagged error, you will get tagged errors — *if you bother to write that
down as a skill*.

One more honesty check, because I will say it three times tonight: **Python
is not going to stop you.** Pyright will nag you. Frozen dataclasses will
slow you down. `match` will look exhaustive until you add a new variant and
forget a branch. None of that is `rustc`. We are buying clarity and a
better default for the next author, who may not be human.

---

## 4:00–12:00 — Explicit errors
### Slides 5–9
*If you have only one demo that works, it is this one.*

### Slide 5 — The Python problem

Let me start with a function you have written.

*Do not click yet. Talk to the room.*

An ingest function. It hits a catalog. Sometimes the article is not there.
Sometimes the upstream times out. Sometimes the payload has a blank title.
You would like the caller to retry the timeout, record the miss, and send
the blank title to a dead-letter queue.

Here is the version in `src/ingest/before/errors.py`.

*Click. Let them read. Count to four.*

```python
def ingest(url: str) -> dict | None:
    try:
        raw = fetch_raw(url)
    except SourceTimeout:
        return None
    if raw is None:
        return None
    ...
    if not article["title"]:
        raise ValueError("title is required")
    return article
```

Three outcomes, two channels. Missing and timeout are both `None`.
Validation is an exception. The type says `dict | None`. That type is a
lie about the domain.

*Audience ping.* Who has paged on a `None` and then spent twenty minutes
asking "was it gone, or did the vendor hiccup?"

*Pause.* That is not a typing problem. That is a contract problem.

### Slide 6 — Rust inspiration, four lines

Rust's move, in plain language: **an expected failure is a value.**

Not a traceback. Not a missing object. A value the caller has to look at.

The type is `Result<T, E>`. It is either `Ok` with a `T`, or `Err` with an
`E`. If you forget to handle it, the compiler yells.

*Click the four lines. Do not teach lifetimes.*

```rust
fn ingest(url: &str) -> Result<Article, IngestError> { ... }
```

That is the whole souvenir. Forget `mut`, forget the borrow checker.
Remember: **the failure has a type, and it comes back in the return
position.**

Python cannot force you to handle it. We can still put the failure in the
return position.

### Slide 7 — Python `Ok` and `Err`

This is the entire "framework" in the repo. Two frozen dataclasses and a
type alias. `src/ingest/after/result.py`.

```python
@dataclass(frozen=True)
class Ok[T]:
    value: T

@dataclass(frozen=True)
class Err[E]:
    error: E

type Result[T, E] = Ok[T] | Err[E]
```

Then the errors get names.

```python
@dataclass(frozen=True)
class NotFound:
    url: str

@dataclass(frozen=True)
class ValidationFailed:
    fields: tuple[str, ...]

@dataclass(frozen=True)
class Retryable:
    reason: str
```

`ingest` now returns
`Result[Article, NotFound | ValidationFailed | Retryable]`.

And the caller, in 3.10+ `match`:

```python
match ingest(url):
    case Ok(article):
        save(article)
    case Err(NotFound()):
        record_miss()
    case Err(ValidationFailed(fields)):
        record_invalid(fields)
    case Err(Retryable()):
        schedule_retry()
```

Read that out loud. You can hear the operations team in it. Retry is not a
comment. It is a branch.

### Slide 8 — Demo: timeout before vs after

*Terminal. Repo root. Do not narrate typing.*

Before:

```bash
uv run python -m ingest demo --mode before --url https://news.example/timeout
```

*Expected:*

```
returned: None
note: None means missing OR timeout. The caller cannot tell.
```

After:

```bash
uv run python -m ingest demo --mode after --url https://news.example/timeout
```

*Expected:*

```
retryable: timed out fetching https://news.example/timeout
```

Same catalog. Same timeout. Different contract.

**[cut if behind]** If you have thirty seconds, run missing and empty-title
on `--mode after` so they see `not_found:` and `validation_failed:`.

The tests in `tests/test_before_errors.py` encode the bug on purpose:
`test_missing_and_timeout_are_indistinguishable`. I want you to keep tests
like that when you teach. A green suite that cannot tell 404 from timeout
is how the bug survives code review.

### Slide 9 — Trade-offs

When this is worth it:

- More than one expected failure.
- Callers have to *choose* (retry, skip, dead-letter).
- The function is on a boundary: HTTP, disk, vendor, queue.

When it is not:

- The failure is a bug. Raise. Do not Result-wrap `KeyError` you caused.
- One exception type is already the house style and everyone catches it at
  the edge.
- A 40-line script you will delete on Friday.

**[cut]** A Result library, `.and_then()` chains, custom monad syntax —
that is how this pattern gets a bad reputation in Python. Two dataclasses
is enough.

Python limitation, said slowly: if you write `ingest(url).value` without
matching, Pyright *might* complain, and the interpreter *will still run
until it blows up*. This is design, plus optional static analysis. It is
not memory safety.

---

## 12:00–21:00 — Valid states
### Slides 10–13

### Slide 10 — Optional fields as a bug farm

Second function you have written: a job record.

```python
@dataclass
class Job:
    job_id: str
    url: str
    status: str = "pending"
    result: dict | None = None
    error: str | None = None
```

Four statuses, two optional blobs. How many combinations exist? Status has
at least four values; result is present or not; error is present or not.
That is a lot of boxes. The domain only wanted four.

The illegal ones show up in production as:

- `status="completed"` and `result is None`
- `status="failed"` and `error is None`
- `status="completed"` *and* a leftover `error` from the last retry

`src/ingest/before/jobs.py` will happily do all three. `complete(None)` is
a legal call. `fail("boom")` then `complete(article)` leaves `error="boom"`
on a completed job.

*Audience ping.* Who has written `if job.status == "completed" and job.result:`
and hated themselves?

That `and job.result` is the type system leaking into an `if`.

### Slide 11 — Make invalid states hard to represent

Rust people repeat this sentence until it is a tattoo: **make invalid
states hard to represent.**

In Rust that is often an enum. One variant per state. Each variant holds
only the data that state needs. There is no `result: Option` hanging off
the whole job.

Python's closest everyday tool is: frozen dataclasses plus a union plus
`match`. Algebraic data types without the vocabulary.

You already know the pieces. `int | str` is a union. A dataclass is a
product of fields. Put them together and you get "this *or* that, and if
it is this, these fields exist."

### Slide 12 — Jobs as a tagged union

`src/ingest/after/jobs.py`:

```python
@dataclass(frozen=True)
class Pending:
    job_id: str
    url: str

@dataclass(frozen=True)
class Completed:
    job_id: str
    article: Article

@dataclass(frozen=True)
class Failed:
    job_id: str
    error: IngestError

type Job = Pending | Processing | Completed | Failed
```

A completed job without an article is not a missing field. It is a call
that does not type-check, and a constructor you cannot write without
passing an `Article`.

Transitions return a new object. They do not flip a string:

```python
def finish(job: Processing, result: Result[Article, IngestError]) -> Completed | Failed:
    match result:
        case Ok(value):
            return Completed(job_id=job.job_id, article=value)
        case Err(error):
            return Failed(job_id=job.job_id, error=error)
```

*Demo.*

```bash
uv run python -m ingest jobs --mode before --url https://news.example/missing
```

You should see `"status": "completed"` and `"result": null`. The miss was
turned into a successful empty job. That is a paging story.

```bash
uv run python -m ingest jobs --mode after --url https://news.example/missing
```

`Failed` with a `NotFound`. The state and the error arrived together.

**[cut]** Optional Pyright demo:

```bash
uv run pyright --project typecheck/invalid
```

`Pending` has no attribute `article`. That is the whole point. The file is
in `typecheck/invalid/` so the default `pyright` run on the repo stays
green. Teaching repos should show both.

### Slide 13 — Trade-offs

Worth it when the object is a lifecycle: jobs, orders, payments,
connections, anything with "you may not read field X yet."

Not worth it when optional really means optional — a middle name, a
nickname, a nullable column that is independent of state.

Also not worth it as a gold-plating exercise: a class per JSON key in a
one-off parser.

Exhaustiveness: `match` in Python is not checked the way Rust `match` is,
unless you use a type checker and a plugin or you keep the union small and
the tests honest. I still want the union. The `if status ==` soup is worse.

---

## 21:00–27:00 — Intentional immutability
### Slides 14–16

### Slide 14 — The shared list

Third function. Enrichment. Word count, language, topics.

`src/ingest/before/pipeline.py` has a classic:

```python
SHARED_TOPICS: list[str] = ["news"]

def enrich(article: dict) -> dict:
    topics = article.setdefault("topics", SHARED_TOPICS)
    if "bike" in body:
        topics.append("transportation")
    topics.append("ingested")
    return article
```

Two articles go through. The first is about bike lanes. The second is the
weather. The weather story comes out tagged `transportation`.

Why? `setdefault` on a missing key does not copy. It aliases the module
list. `append` is process-wide.

This is the bug that fails depending on test order. This is the bug that
shows up when you add concurrency. This is the bug an agent will recreate
if the surrounding code mutates dicts in place, because mutating dicts in
place looks like Python.

*Audience ping.* Who has had a test pass alone and fail in CI because a
list leaked? *Hands. Grin. Move.*

### Slide 15 — Immutable by default, without the borrow checker

Rust bindings are immutable unless you write `mut`. The borrow checker is
the famous part. The boring part is more useful to us: **if something
changes, you can see the assignment.**

We are not doing ownership tonight. We are doing frozen dataclasses,
tuples instead of lists, and `dataclasses.replace`.

```python
@dataclass(frozen=True)
class Article:
    ...
    topics: tuple[str, ...] = ()

def tag_topics(article: Article) -> Article:
    topics = ["news"]
    if "bike" in article.body.lower():
        topics.append("transportation")
    return replace(article, topics=tuple(topics))
```

Local mutation of a *new* list is fine. Sharing that list is not.

`enrich` is a fold:

```python
def enrich(article: Article) -> Article:
    for stage in (count_words, detect_language, tag_topics):
        article = stage(article)
    return article
```

Each stage is a function from Article to Article. The original object the
caller held is still the original object. Tests become easy: you keep the
input fixture.

### Slide 16 — Demo and trade-offs

```bash
uv run python -m ingest pipeline --mode before
```

Second topics include `transportation`. The note admits the leak.

```bash
uv run python -m ingest pipeline --mode after
```

First has `transportation`. Second does not.

When to freeze:

- Values that cross a boundary: queue payload, domain entity, cache key.
- Pipelines with more than one stage.
- Anything you might put in a set or use as a dict key later.

When not to:

- A local accumulator. Just use a list.
- A buffer you cannot afford to copy. Mutation is the feature.
- Freezing every `int` in a frozen wrapper because a slide said
  "immutability."

Python limitation: `frozen=True` is a speed bump. `object.__setattr__`
still exists. Tuples can contain lists if you put lists in them. We used
`tuple[str, ...]` on purpose.

---

## 27:00–36:00 — Agents, skills, demonstration
### Slides 17–18

### Slide 17 — Agents copy what they can see

Here is the uncomfortable part. If you paste `src/ingest/before/` into an
agent and say "review this," you often get a review that is *correct* and
still useless.

I did not want that part of the talk to depend on wifi or on the model's
mood. So the repo has a prepared demo in `examples/agent-demo/`.

The naive review, condensed:

- Add a `TypedDict`.
- Log the timeout.
- Catch `Exception`.
- Make an `Enum` for status.
- Keep returning `None`.

That is `examples/agent-demo/naive-review.md`, and the code it implies is
`naive-refactor.py`. It looks more professional. The three bug classes are
still there. Logging a timeout that you still return as `None` does not
give the caller a retry branch. An Enum plus `result: ArticleDict | None`
still lets you complete without a result.

*Let that sit.*

Agents are not bad at Python. They are extremely good at completing the
pattern in front of them. "Make it typed" is a pattern. "Make the illegal
state unconstructable" is a different pattern, and it is not the default.

### Slide 18 — Skills are how we change the default

A skill is a markdown file the agent is told to read *before* it reviews.
Four of them ship in this repo:

- `skills/explicit-error-handling`
- `skills/model-valid-states`
- `skills/intentional-immutability`
- `skills/python-design-review` — the filter that says *do not gold-plate*

They are ordinary `SKILL.md` files. Claude Code, Codex, Cursor, and most
other coding agents will take a folder of these. `docs/agent-guidance.md`
is the repo-wide version.

The skilled review, condensed, from `examples/agent-demo/skilled-review.md`:

1. `None` means two things — use `Result` with named errors.
2. Status plus optional fields — use a tagged union.
3. Shared list — freeze `Article`, return `replace(...)`.
4. Trade-off sentence on each. No Result library.

That is the same agent, same code, different instructions.

Live, if you want to try this after the meetup: `prompts/01-review-without-skills.md`
versus `prompts/02-review-with-skills.md`. Tonight we trust the prepared
files, because I like finishing on time.

How to evaluate the diff — this is the takeaway for agents:

- Did tests pass? Necessary, not sufficient. The before-suite *also* passes.
- Can a new caller misuse the function without noticing?
- Did we add types that do not remove a bug class?
- Would I want the next agent to copy this?

If the skilled refactor is `src/ingest/after/`, you can grade it with:

```bash
uv run pytest
uv run ruff check .
uv run pyright
```

Green is the floor. The ceiling is whether `timeout` is a value.

---

## 36:00–40:00 — Takeaways and questions
### Slides 19–20

### Slide 19 — What I want you to steal

You should be able to do these six things. Not next quarter. This week,
on one function.

1. Spot a `None` that means two things.
2. Put expected failures in the return type when callers have to choose.
3. Replace status-plus-optionals with a union of dataclasses.
4. Make mutation obvious: new object, `replace`, tuples.
5. Write one `SKILL.md` so your agent has a chance of doing 2–4.
6. Judge AI output on maintainability, not on "it ran."

You do not need all three patterns on every file. You need the one that
matches the bug you are actually shipping.

### Slide 20 — Close

Better Python is not more code, more abstractions, or another language.

It is better design decisions — and teaching our AI coding agents to make
those decisions with us.

The repo is `thinking-in-rust-writing-in-python`. Slides, script, skills,
and the ingest app are all in there. MIT. No cloud.

I will take questions. If your question is "should I rewrite my monolith
tomorrow," the answer is no. Pick one boundary function. Give it a real
error type. Put four lines in a skill. See if the next agent PR is less
embarrassing.

*Stop. Water. Hands.*

---

## Question bank (if the room goes quiet)

- **Isn't this just typed Python?** Types are the notation. The design is
  "which values exist." You can add types and keep the illegal states.
- **Why not `raises` in the docstring?** Because agents and callers read
  signatures more than prose, and `None` is still one value.
- **Why not Pydantic?** Fine at the edge. Inside the domain I want boring
  dataclasses I can construct in tests without a context.
- **Does `match` exhaustiveness work?** Not like Rust. Keep the union
  small. Use Pyright. Add a test per variant.
- **Can I use `returns` / `result` on PyPI?** You can. I did not, on
  purpose. Two dataclasses survive a copy-paste into a skill.
- **What about asyncio / concurrency?** The shared-list bug gets worse.
  Frozen values get more valuable. The Result pattern is independent.

## Timing recovery

| You are here | Cut this |
|---|---|
| 6 min in and still on slide 4 | Skip the show of hands. Jump to slide 5. |
| Pattern 1 demo failed | Read the expected output from PRESENTER.md. Move. |
| 25 min in and still on jobs | Skip the Pyright extra. Do pipeline in one command. |
| 32 min in and no agent section | Skip naive-refactor.py. Read the two review summaries. |
| 38 min in | Go to slide 20. Take one question. |

## Repo paths you may want to open on the projector

- `src/ingest/before/errors.py`
- `src/ingest/after/ingest.py`
- `src/ingest/after/jobs.py`
- `src/ingest/before/pipeline.py`
- `examples/agent-demo/naive-review.md`
- `examples/agent-demo/skilled-review.md`
- `skills/python-design-review/SKILL.md`
