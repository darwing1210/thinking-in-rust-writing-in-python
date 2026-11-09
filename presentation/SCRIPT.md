# Speaker script — Stealing good ideas from Rust

**Event:** Alamo Python, Geekdom, November 16
**Length:** ~40 minutes
**Deck:** `slides.html` (23 slides)
**Repo root:** one directory up from this file

Spoken text is in roman. Stage directions are in *italics*. Do not read
the italics. Cut anything marked **[cut]** if you run long. Talk like you
are explaining this to a coworker at the whiteboard — conversational,
punchy, but technically grounded.

---

## 0:00–5:00 — Introduction & Disclaimer
### Slides 1–5

### Slide 1 — Title
*Lights. One breath.*

Good evening. The flyer says **Stealing good ideas from Rust**. Under that:
**Python patterns for reliability**.

Promise up front: you do not need to know Rust. You will see about four
lines of it. If you forget those on the way to the garage, you still got
the talk.

We are stealing *ideas*. We keep writing Python.

### Slide 2 — Who this is for

This is for people who write Python at work. APIs, jobs, pipelines.

It is also for anyone who has returned `None` and hoped the next person
would know why.

And it is for anyone who pasted a function into ChatGPT or Claude, got code
that ran, and still felt weird about it.

*Hands.* Who here has shipped Python that an AI wrote at least part of,
in the last six months?

*Nod. Do not count.*

Yeah. That is this room.

### Slide 3 — Forty minutes

Four architectural habits. Then we teach them to AI. Then questions.

1. Explicit Errors: Name the failure. Don’t shrug with `None`.
2. Typestates: Gate methods by lifecycle state.
3. Compiler Contracts: Zero-cost `NewType` and `assert_never`.
4. The Ownership Law: Aliasing XOR Mutability.
5. The AI Sandbox: The compiler as the agent's mechanical leash.

Same tiny app the whole night: we fetch an article, check it, tag it, and
track a job. No network. Four fake URLs. After the meetup you can run every
demo with `uv run python -m ingest`.

### Slide 4 — The point

*Read it. Then say it again in your own words.*

You don’t need to write Rust. You can still steal the good parts. And if
AI is writing your Python, you can teach it those parts too.

Why the second sentence matters: the AI copies whatever is already in the
file. If the file says `return None`, you get more `return None`. If the
file has strict compiler contracts, the AI gets instant feedback when it
hallucinates.

Honesty, three times tonight: **Python will not stop you.** A type checker
can nag. Frozen objects slow you down. None of that is Rust’s compiler.
We are making the next person less likely to mess it up. That next person
might be an AI.

### Slide 5 — Disclaimer

*Forty seconds. Smile. Then move.*

Quick disclaimer, because the flyer has a crab on it.

These are not “Rust patterns.” They’re old design habits. Name the
failure. Don’t let a job be done and empty. Don’t share a list and then
act surprised. Python can do that. So can Go, TypeScript, Java, whatever
you already write.

Rust just makes them hard to ignore. That’s why it’s a useful teacher tonight.
Nobody here is being asked to rewrite their app.

One more reason this matters: AI copies the project in front of it. If
the repo has clear habits, the model writes clearer code. If the repo
shrugs, the model shrugs too.

---

## 5:00–12:00 — Pattern 1: Explicit Error Boundaries
### Slides 6–10
*If only one demo works, it is this one.*

### Slide 6 — The shrug

You have written this function.

It fetches an article. Sometimes the article is gone. Sometimes the other
side times out. Sometimes the title is blank.

You want three different next steps: retry the timeout, record the miss,
send the blank title somewhere to die.

Here is the version most of us ship.

*Let them read. Count to four.*

Missing and timeout both come back as `None`. Blank title raises. The
signature says “dict or None.” That is a shrug. The next function cannot
tell a 404 from a blip.

*Hands, optional.* Who has spent twenty minutes asking “was it gone, or
did the vendor hiccup?”

### Slide 7 — What Rust does

Rust’s idea, in English: **don’t hide a failure. Hand it back.**

Not a crash. Not a missing object. A value the next line has to look at.

That type is called `Result`. It is either `Ok` with the article, or `Err`
with a reason.

*Four lines. Do not teach the rest of Rust.*

Rust makes you handle it. Python will not. We can still hand the failure
back.

### Slide 8 — Two little classes

This is the entire “framework.” Two frozen classes and a nickname.

`Ok` means it worked. `Err` means it didn’t. Then give the failures names:
not found, bad fields, try again later.

The next function uses `match` — the same `match` Python already has:

- it worked → save
- not found → record a miss
- bad fields → record invalid
- try again → schedule a retry

You can hear the on-call rotation in that. Retry is not a comment. It is
a branch.

### Slide 9 — Demo

*Terminal. Do not narrate typing.*

Before:

```bash
uv run python -m ingest demo --mode before --url https://news.example/timeout
```

You should see `None`, and a note that None means missing *or* timeout.

After:

```bash
uv run python -m ingest demo --mode after --url https://news.example/timeout
```

You should see `retryable:`.

Same catalog. Same timeout. Now you can tell them apart.

### Slide 10 — When not to bother

Use this when “it failed” is not enough. When someone has to retry, skip,
or give up. When you talk to the network.

Skip it when you actually have a bug — just raise. Skip it if the team
already has one clear exception style. Skip it for a script you will
delete on Friday.

Please do not add a Result library. Two classes is enough.

---

## 12:00–20:00 — Pattern 2: Typestates & Lifecycle Gating
### Slides 11–14

### Slide 11 — The form with extra boxes

Second function you have written: a job.

Status is a string: "pending", "processing", "completed", "failed".

Result might be there. Error might be there.

And look at the methods: `.complete()` and `.fail()`.
What stops someone from calling `job.complete()` before the job was even started?
Nothing! You have to write `if self.status != "running": raise InvalidStateError`.
That is a runtime check. It only blows up when the user clicks the button.

### Slide 12 — The Typestate Pattern

In Rust, they use something called **Typestates**.
Instead of one big mutable object with a status flag, each state is its
own type.

And state transitions consume the old state: `fn start(self) -> Processing`.
Methods only exist where they make sense!
A `Pending` job has a `.start()` method. It does NOT have a `.finish()` method.
You cannot finish a job that hasn't started, because that method literally
does not exist.

### Slide 13 — Typestates in Python

In Python:

`Pending` has `def start(self) -> Processing: ...`
`Processing` has `def finish(self, res) -> Completed | Failed: ...`

`Completed` holds an `Article`. `Failed` holds an `IngestError`.

A completed job without an article cannot be built.
And calling `pending.finish(...)`?
It is not an `if/raise` check at runtime.

### Slide 14 — Pyright catches it at compile time

*Show the slide / terminal demo.*

```bash
uv run pyright typecheck/invalid/cannot_finish_pending_job.py
```

`Cannot access attribute "finish" for class "Pending"`.

The compiler stops it before the code ever runs.
If a junior engineer or an AI agent hallucinates calling `.finish()` on a
pending job, Pyright rejects it on the spot.

---

## 20:00–26:00 — Pattern 3: Compiler Contracts (NewType & assert_never)
### Slides 15–16

### Slide 15 — Two quiet killers

Two bugs that pass unit tests and blow up production:

**1. Swapped arguments:** Look at `def fetch(url: str, job_id: str): ...`
Someone calls `fetch(my_job_id, my_url)`.
Both are strings! Pyright says: looks good. Tests pass. Production corrupts.

**2. Silent match fallthrough:** You write a `match job:` statement.
Next month someone adds `Cancelled` to the `Job` union.
What does Python do? It silently skips the unhandled case and returns `None`!

### Slide 16 — NewType & assert_never

Rust fixes both at compile time. Here is how Python does it:

**1. Zero-cost `NewType`:**
```python
JobId = NewType("JobId", str)
Url = NewType("Url", str)
```
At runtime: literally just strings. Zero performance cost, zero memory overhead.
At static type check: swapping them fails the build immediately!

**2. Exhaustiveness with `assert_never`:**
At the end of your `match`, add:
```python
case _ as unreachable:
    assert_never(unreachable)
```
If anyone adds `Cancelled` to `Job` anywhere in the codebase, Pyright breaks
across CI until every `match` handles it.
Now Python's `match` has the same exhaustiveness guarantee as Rust's compiler.

---

## 26:00–32:00 — Pattern 4: The Ownership Law (Aliasing XOR Mutability)
### Slides 17–19

### Slide 17 — The weather story

Third function: enrichment. Adding topics to an article.

There is a module list `SHARED_TOPICS = ["news"]`.
First article is bike lanes, so we append `transportation`.
Second article is the weather.

The weather story comes out tagged transportation.
Why? Because `setdefault` shared the list. Mutating it in place affected
every future article in the process.

### Slide 18 — Aliasing XOR Mutability

Rust’s entire borrow checker is based on one invariant:
> **You can have many shared readers, OR one exclusive writer. Never both.**

If multiple parts of your application hold references to the same object,
**none of them may mutate it in place**.

*Fun fact:* Did you know Python has a borrow checker?
If you create a `memoryview` on a bytearray, and try to resize the bytearray
while the view is open, Python raises:
`BufferError: Existing exports of data: object cannot be re-allocated`.
Python's core team literally implemented a borrow check to prevent memory bugs!

### Slide 19 — Solution & Demo

The Python rule:
1. Data passed across boundaries must be immutable (`@dataclass(frozen=True)`, `tuple`).
2. Private mutation inside a function is fine—because no alias exists yet!
3. Transformations return a new copy with `replace()`.

```bash
uv run python -m ingest pipeline --mode before  # leaked tags!
uv run python -m ingest pipeline --mode after   # isolated!
```

---

## 32:00–37:00 — The AI Sandbox: The Compiler as the Agent's Leash
### Slides 20–21

### Slide 20 — Why this matters in 2026

Here is the punchline of the talk.

When you ask an AI coding agent to work on sloppy Python—loose dicts, mutable
lists, ambiguous `None`, raw strings:
- The AI hallucinates invalid states.
- It swaps string IDs.
- It forgets match branches.
- The happy-path tests pass, and production quietly degrades.

When you give the AI:
- Typestates (it can't call invalid methods),
- `NewType` (it can't swap arguments),
- `assert_never` (it can't miss cases),
- Frozen dataclasses (it can't mutate shared state),

**The type checker becomes a mechanical leash.**
The AI runs `pyright`, sees 3 errors where it violated domain constraints,
and self-corrects *before* opening the PR.
Strict types are no longer about human ego—they are how we make AI coding safe.

### Slide 21 — Five skills in the repo

A skill is a markdown file the agent reads first. Five ship in this repo:
- `skills/explicit-error-handling`
- `skills/model-valid-states`
- `skills/type-driven-contracts`
- `skills/intentional-immutability`
- `skills/python-design-review`

Portable across Claude Code, Codex, Cursor, and Hermes.

---

## 37:00–40:00 — Steal this & Close
### Slides 22–23

### Slide 22 — Five habits for this week

Not next quarter. Pick one function this week:

1. Return failures as values. Stop returning `None` for two different problems.
2. Typestates: Gate methods on state dataclasses so illegal calls don't type-check.
3. Zero-cost IDs: Wrap raw strings with `NewType` to stop argument swapping.
4. Compile-time exhaustiveness: End closed matches with `assert_never`.
5. Aliasing XOR Mutability: Private mutation ok; shared mutation forbidden.

### Slide 23 — Close

Better Python is not more code. It’s clearer decisions — and giving our
AI agents the mechanical guardrails to write safe software.

The repo is `thinking-in-rust-writing-in-python`. Slides, script, skills,
and the little ingest app. MIT. No cloud.

I will take questions.

*Stop. Water. Hands.*

---

## Question Bank

- **Isn't NewType just a type alias?** No. A type alias `UserId = str` lets you
  pass any string. `NewType("UserId", str)` creates a distinct type that
  requires explicit casting, catching swapped arguments.
- **Does `assert_never` cost anything at runtime?** No. At runtime, if you ever
  hit that branch, it raises `AssertionError`. But Pyright guarantees at
  type-check time that the line is unreachable.
- **Why not use Pydantic for everything?** Pydantic is great for HTTP request/response
  validation. But inside your core domain, frozen dataclasses with `NewType`
  have zero overhead and no dependency weight.
