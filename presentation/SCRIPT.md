# Speaker script — Stealing good ideas from Rust

**Event:** Alamo Python, Geekdom, November 16
**Length:** ~40 minutes
**Deck:** `slides.html` (21 slides)
**Repo root:** one directory up from this file

Spoken text is in roman. Stage directions are in *italics*. Do not read
the italics. Cut anything marked **[cut]** if you run long. Talk like you
are explaining this to a coworker at the whiteboard — not like a paper.

---

## 0:00–5:00 — Introduction
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

This is for people who write Python at work. APIs, jobs, scripts.

It is also for anyone who has returned `None` and hoped the next person
would know why.

And it is for anyone who pasted a function into ChatGPT, got code that
ran, and still felt weird about it.

*Hands.* Who here has shipped Python that an AI wrote at least part of,
in the last six months?

*Nod. Do not count.*

Yeah. That is this room.

### Slide 3 — Forty minutes

Three habits. Then we teach them to the AI. Then questions.

1. Name the failure. Don’t shrug with `None`.
2. Don’t let a job be “done” and empty.
3. Stop surprise edits when two functions share a list.
4. Write those habits down so the coding agent copies *those*, not the bugs.

Same tiny app the whole night: we fetch an article, check it, tag it, and
track a job. No network. Four fake URLs. After the meetup you can run every
demo with `uv run python -m ingest`.

### Slide 4 — The point

*Read it. Then say it again in your own words.*

You don’t need to write Rust. You can still steal the good parts. And if
AI is writing your Python, you can teach it those parts too.

Why the second sentence matters: the AI copies whatever is already in the
file. If the file says `return None`, you get more `return None`. If the
file names the failure, you get named failures — if you bother to write
that down.

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

Rust just nags you about them. That’s why it’s a useful teacher tonight.
Nobody here is being asked to rewrite their app.

One more reason this matters: AI copies the project in front of it. If
the repo has clear habits, the model writes clearer code. If the repo
shrugs, the model shrugs too. The patterns help you. They also help the
model.

---

## 5:00–12:00 — Name the failure
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

**[cut]** If you have thirty seconds, run missing and empty-title on
`--mode after` so they see `not_found:` and `validation_failed:`.

### Slide 10 — When not to bother

Use this when “it failed” is not enough. When someone has to retry, skip,
or give up. When you talk to the network.

Skip it when you actually have a bug — just raise. Skip it if the team
already has one clear exception style. Skip it for a script you will
delete on Friday.

**[cut]** Please do not add a Result library. Two classes is enough.

And Python still will not stop you. If you grab `.value` without looking,
the type checker *might* complain, and the program *will still run* until
it blows up. This is a habit, not a lock.

---

## 12:00–21:00 — Don’t let “done” be empty
### Slides 11–14

### Slide 11 — The form with extra boxes

Second function you have written: a job.

Status is a string. Result might be there. Error might be there.

That is a form with too many blank boxes. You can tick “completed” and
leave the result empty. You can tick “failed” and leave the error empty.
You can fail, then complete, and the old error is still sitting there.

Python will let you. Production will store it.

*Hands, optional.* Who has written `if job.status == "completed" and job.result:`
and hated the `and job.result` part?

That extra check is you not trusting your own object.

### Slide 12 — Rust’s sentence

Rust people repeat this until it is a tattoo: **if it shouldn’t happen,
don’t let the object exist.**

Pending is one shape. Running is another. Done always carries the article.
Failed always carries the reason.

You already write `int | str`. Same idea, for a job.

### Slide 13 — Four shapes

A completed job without an article is not a missing field. You cannot
build it. You have to pass an `Article`.

And we don’t flip a string on the same object. We return a *new* shape.

*Demo.*

```bash
uv run python -m ingest jobs --mode before --url https://news.example/missing
```

Status `"completed"`, result `null`. The miss became a successful empty
job. That is a paging story.

```bash
uv run python -m ingest jobs --mode after --url https://news.example/missing
```

`Failed`, with `NotFound`. The state and the reason arrived together.

**[cut]** Optional type-check:

```bash
uv run pyright --project typecheck/invalid
```

Pending has no `.article`. That is the point.

### Slide 14 — When not to bother

Use this for jobs, orders, payments — anything with a life cycle. Anything
where “you shouldn’t read that field yet.”

Skip it for a nickname that really is optional. Skip it for a one-off
parser you will throw away.

Python still will not yell like Rust if you forget a branch. Keep the list
of shapes small. Test each one.

---

## 21:00–27:00 — Stop surprise edits
### Slides 15–17

### Slide 15 — The weather story

Third function. We add word count, language, topics.

There is a module-level list called `SHARED_TOPICS`. First article is
about bike lanes, so we append `transportation`. Second article is the
weather.

The weather story comes out tagged transportation.

Why? We did not copy the list. We handed out the *same* list. `append`
is process-wide.

This is the bug that fails depending on test order. This is the bug that
gets worse with two requests at once. And it is the bug an AI will
recreate, because mutating dicts in place looks like “normal Python.”

*Hands, optional.* Who has had a test pass alone and fail in CI?

### Slide 16 — Copy, don’t poke

Rust’s boring idea: if something changes, you should see the assignment.

We are not doing the borrow checker tonight. We are doing: freeze the
article, keep topics as a tuple, return a new copy with `replace`.

Building a fresh list *inside* the function is fine. Sharing that list
with the next article is not.

Each step takes an article and returns an article. The original the caller
is holding is still the original. Tests get easier: you keep the input.

### Slide 17 — Demo

```bash
uv run python -m ingest pipeline --mode before
```

Second topics include transportation.

```bash
uv run python -m ingest pipeline --mode after
```

First has it. Second does not.

Freeze the values you pass around — queue payloads, domain objects. A
local list inside a function is still fine. A giant buffer you cannot
afford to copy? Mutation is the feature. Don’t freeze every integer
because a slide said so.

`frozen=True` is a speed bump, not a lock.

---

## 27:00–36:00 — Teach the AI
### Slides 18–19

### Slide 18 — It copies you

If you paste the “before” code into an AI and say “review this,” you often
get a review that is *correct* and still useless.

I did not want wifi to decide this section. The repo has a prepared demo.

Typical review, condensed:

- Add a TypedDict
- Log the timeout
- Catch Exception
- Make an Enum for status
- Keep returning `None`

It looks more professional. The three bugs are still there. A log line
does not give the next function a retry branch. An Enum plus “result might
be missing” still lets you complete with nothing.

The AI is not bad at Python. It is extremely good at finishing the pattern
in front of it. “Make it typed” is a pattern. “Don’t let done be empty” is
a different pattern, and it is not the default.

### Slide 19 — Write the habit down

A skill is a markdown file the agent is told to read *before* it reviews.
Four of them ship in the repo. Plain English:

- name the failure
- don’t allow empty “done”
- don’t share a list
- and don’t gold-plate

Same agent, same code, different instructions.

Live, after the meetup, you can try `prompts/01` versus `prompts/02`.
Tonight we use the prepared files, because I like finishing on time.

How to judge the diff:

- Did the tests pass? Necessary. Not enough. The *before* tests also pass.
- Can a new caller misuse this without noticing?
- Did we add types that don’t remove a real bug?
- Would I want the next AI to copy this?

Green tests are the floor. The ceiling is whether timeout is a named
thing, not a shrug.

---

## 36:00–40:00 — Steal this, then questions
### Slides 20–21

### Slide 20

Not next quarter. One function this week.

Notice a `None` that means two things.

Give those failures names, if someone has to choose what to do next.

Don’t let a job be “done” with nothing in it.

If you change data, return a new copy.

Write four lines in a `SKILL.md` so the AI does it too.

Don’t trust “it ran.” Ask if the next person can misuse it.

You do not need all three habits on every file. You need the one that
matches the bug you are actually shipping.

### Slide 21 — Close

Better Python is not more code. It’s clearer decisions — and teaching the
AI to make those with you.

The repo is `thinking-in-rust-writing-in-python`. Slides, script, skills,
and the little ingest app. MIT. No cloud.

I will take questions. If the question is “should I rewrite the whole app
tomorrow,” the answer is no. Pick one function. Give the failure a name.
Put four lines in a skill. See if the next AI pull request is less
embarrassing.

*Stop. Water. Hands.*

---

## If the room goes quiet

- **Isn’t this just types?** Types are spelling. The design is “which
  values are allowed to exist.” You can add types and keep the shrug.
- **Why not a docstring?** People and AIs read the signature more than
  the prose. `None` is still one value.
- **Why not Pydantic?** Fine at the edge. Inside, boring dataclasses you
  can build in a test without a ceremony.
- **Does match catch everything?** Not like Rust. Keep the list of shapes
  small. Add a test per shape.
- **Can I use a Result library?** You can. I didn’t, on purpose. Two
  classes survive a copy-paste into a skill.

## If you are running long

| You are here | Cut this |
|---|---|
| 6 min in, still on slide 4 | Skip the hands. Jump to slide 6. |
| Pattern 1 demo failed | Read the expected output. Move. |
| 25 min in, still on jobs | Skip the type-check extra. One pipeline command. |
| 32 min in, no AI section | Skip the naive file. Read the two review summaries. |
| 38 min in | Slide 21. One question. |

## Files to open on the projector if you want

- `src/ingest/before/errors.py`
- `src/ingest/after/ingest.py`
- `src/ingest/after/jobs.py`
- `src/ingest/before/pipeline.py`
- `examples/agent-demo/naive-review.md`
- `examples/agent-demo/skilled-review.md`
