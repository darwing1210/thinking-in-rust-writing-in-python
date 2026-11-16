 # Speaker script — Stealing good ideas from Rust

**Event:** Alamo Python, Geekdom, November 16
**Length:** ~40 minutes of talking
**Deck:** `slides.html` (34 slides)
**Repo root:** one folder up from this file

How to read this script:

- Normal text is what you say.
- *Italic text* is for you only. Don't read it out loud.
- **[cut]** means: skip this part if you are running late.
- The words are simple on purpose. Say them your own way. If you forget a
  sentence, just say the idea. Nobody has the script but you.

---

## 0:00–5:00 — Intro
### Slides 1–7

### Slide 1 — Title
*Take one breath. Look at the room. Smile.*

Hi everyone. Thanks for coming out on a Monday.

The talk is called **Stealing good ideas from Rust**. And the important word
there is *ideas*. We are not here to rewrite anything in Rust. We are going
to keep writing Python. We're just going to take some good habits from Rust
and bring them home.

You don't need to know Rust for this. I'll show you a few lines, and I'll
explain every one of them.

### Slide 2 — About me
*30 seconds. Keep it light.*

Quick intro. I'm Darwing. I came down from Austin tonight, where I work at
Handraise.

Handraise is a platform for media monitoring and narrative intelligence.
In plain English: we help teams see what people — and AI systems — are
saying about a brand.

I've been writing Python for work since 2016. And these days I review a lot
of Python that an AI wrote. Some of it is great. Some of it made me want to
make this talk.

I also write Rust at work, which I'll explain at the end.

### Slide 3 — Get the code

*20 seconds. Let people scan. Don't rush this one.*

Before we start: if you want to follow along, scan this QR code.
Everything I show tonight is in this repo. The slides, the full script,
every demo, and the agent skills. It's all MIT, and it runs without
internet.

*Wait a few seconds. Watch for phones going down.*

Got it? Okay. Let's go.

### Slide 4 — Who this is for

This talk is for people who write Python at work. APIs, background jobs,
data pipelines. That kind of thing.

It's also for anyone who ever wrote `return None` and thought, "eh, the
next person will figure it out."

And it's for anyone who asked an AI to write some code, and the code
worked… but something still felt wrong about it.

*Raise your own hand.* Quick question: who here has shipped Python code
that an AI wrote, at least partly, in the last six months?

*Look around. Nod. Don't count.*

Yeah. Me too. So this talk is for all of us.

### Slide 5 — The plan

Three parts.

First, a short story about Rust. Then four habits. Then the AI part and a
real Rust example from work.

We'll use one small app the whole night. It fetches news, checks it, tags it,
and keeps track of a job.

### Slide 6 — The main idea

The point is simple. You do not need to write Rust to use the good parts.
And if AI is writing your Python, you can teach it those parts too.

### Slide 7 — Disclaimer

*Forty seconds. Smile. Then move on.*

Quick disclaimer, because the flyer has a crab on it.

These are not really "Rust patterns." They are old, good design habits.
Give your errors a name. Don't let an object be in a state that makes no
sense. Don't share a list and then act surprised when it changes. You can
do all of this in Python, Go, TypeScript, Java, anything.

Rust just doesn't let you forget them. That's why it's a good teacher.

---

## 5:00–9:30 — A short story: Rust's playroom rules
### Slides 8–13 — Story: Rust's playroom rules
*This is a story. Slow down. Point at the pictures. Have fun with it.*

### Slide 8 — Rust's playroom rules

Ferris is our strict babysitter. Leo and Mia are the kids. Rust starts with
one simple idea: the babysitter checks before the door opens.

### Slide 9 — Rule 1: Every toy has one owner

Leo has a red truck. He gives it to Mia. He doesn't copy it. He doesn't
keep a secret copy. He just hands it over.

*Point at the code label.*

In Rust, a variable is the owner. `let leo = Truck`. `let mia = leo`. The
truck moves to Mia. That's ownership.

### Slide 10 — Rule 2: Look together, color alone

Many kids can look at the book at the same time. But if someone wants to
color, only one kid can do it.

In Rust, `&` means many readers. `&mut` means one writer. Never both.

### Slide 11 — Rule 3: Open the box before you eat

If something might be missing, Rust puts it in an Option box. If an errand
can fail, it comes back in a Result box. You open the box before you use
what's inside.

### Slide 12 — Rule 4: Badges, not family trees

Ferris also hands out badges, not family trees. A pigeon, an airplane, and a
kid with cardboard wings can all share the same badge.

**[cut]** If we're short on time, skip this page.

### Slide 13 — The babysitter checks first

Ferris checks the rules before the door opens. That's the compiler. It feels
strict at first, but once the program runs, nobody is slowing you down.

Python can have that too. It's called Pyright. The only problem is: it only
shows up if you invite it.

### Slide 14 — `None` means two things

The same function can fail in three different ways. But the code returns
`None` for two of them, and an exception for the third. The next function
cannot tell which is which.

### Slide 15 — What Rust does

Rust's answer is simple: don't hide the failure. Return it.
Remember the errand box from the story? That's `Result`.

Strict Pyright already gives you part of this with `Article | None`: it
forces you to check for `None` before you use the value.

### Slide 16 — Two little classes

Two frozen classes. One for success, one for failure. Then a `match` with
four branches. That's the whole pattern.

### Slide 17 — Demo

*Switch to the terminal.*

Before:
```bash
uv run python -m ingest demo --mode before --url https://news.example/timeout
```
`None`.

After:
```bash
uv run python -m ingest demo --mode after --url https://news.example/timeout
```
`retryable`.

### Slide 18 — When it's worth it

Use this when "it failed" isn't enough information. Skip it when it's just a
bug or a tiny script you will delete on Friday.

### Slide 19 — The form with extra boxes

Jobs with a status string and two optional fields look simple, but they let
you call methods out of order.

### Slide 20 — The Typestate pattern

Rust fixes this by making each state its own type. A method only exists
where it makes sense.

### Slide 21 — Typestates in Python

`Pending` has `start()`. `Processing` has `finish()`. The old value still
exists in Python, but the invalid method is gone.

### Slide 22 — Pyright catches it

```bash
uv run pyright -p typecheck/invalid typecheck/invalid/cannot_finish_pending_job.py
```
Pyright stops the bad call before runtime.

### Slide 23 — Two quiet bugs

Swapped strings and forgotten match cases both pass tests and still break
production.

### Slide 24 — `NewType` and `assert_never`

`NewType` stops swapped IDs. `assert_never` makes forgotten cases break the
build.

### Slide 25 — A type is a label

Okay, now an important catch. Somebody always asks this, so let's say it
first.

*Left side.*

`Url("not a url")`. Pyright is happy with this. `JobId(some_url)`. Also
happy. A `NewType` is just a label. It doesn't check anything. It trusts
you.

But data from outside your app shouldn't be trusted. HTTP requests, files,
messages from a queue.

*Right side.*

So the rule is: **check once at the edge, then trust the type inside.**

Here's a small function from the repo. `parse_url` takes a raw string. If
it doesn't look like a real web address, it returns an error. If it does,
it returns a `Url`. After that point, the rest of the app can trust it.

**[cut]** For HTTP and JSON, Pydantic is great for this job. Use it at the
edges. Inside the app, small frozen dataclasses are enough.

---

## 24:00–30:30 — Habit 4: One writer or many readers
### Slides 26–29

### Slide 26 — The weather story

Third function: adding topic tags to an article.

There's a list at the top of the file. `SHARED_TOPICS`, with just "news"
in it.

The first article is about new bike lanes. So we add "transportation."
Makes sense.

The second article is the weather forecast.

*Pause.*

And the weather comes out tagged "transportation."

Why? Look at `setdefault`. It didn't copy the list. It gave both articles
the *same* list. So when we added "transportation" for the first article,
we added it to that shared list. And every article after that gets it too,
until the process restarts.

I think most of us have lost an afternoon to a bug like this.

### Slide 27 — Back to the playroom

So how does Rust prevent this? Let's go back to the playroom. These are
the real error messages Ferris gives you.

*Left side.*

Remember Leo and the truck? Here, `topics` owns the list. Then
`let a = topics` gives it to `a`. In Python, that would just give the same
list a second name. In Rust, the list *moves*. Now `a` is the owner. And
when we try to use `topics` again — Leo trying to drive the truck — Rust
says no. "Borrow of moved value."

*Right side.*

And remember looking and coloring? Here I lend the list to `reader`. That's
looking. Then I try to push a new tag while `reader` is still looking at
it. That's coloring while someone else is looking. Rust says no. "Cannot
borrow as mutable because it is also borrowed as immutable."

And you might have heard about lifetimes. That's just Ferris checking that
nobody keeps a borrowed toy after the owner goes home. The closest thing in
Python is a `with` block. The file is open inside the block, and it's
closed after. That's all we need about lifetimes tonight.

### Slide 28 — One writer or many readers

*Point at the quote.*

So this is Rust's rule: many readers, or one writer. Never both. People
call it "aliasing XOR mutability." Aliasing means two names for the same
thing. XOR means one or the other, not both. But I like the short version
better: many readers, or one writer.

And our weather bug? That's two kids coloring the same page. Rust refuses
to compile it.

In Python, we follow the rule by hand. If more than one part of your
program can see an object, don't change it in place.

**[cut]** Fun fact. Python actually has one tiny version of this rule. If
you make a `memoryview` of a `bytearray`, and then you try to make the
bytearray bigger, Python raises a `BufferError`. It's not a real borrow
checker. It's just a counter of who is looking at the data. But it's the
same rule: while someone is reading, nobody resizes.

### Slide 29 — The fix and the demo

So here's the Python version of the rule.

One: data that leaves a function is frozen. A frozen dataclass, a tuple.

Two: changing data *inside* your function is totally fine. Nobody else can
see it yet. Here, `local_tags` is a normal list. I append to it. No problem.

Three: when you want a changed version, make a new copy with
`dataclasses.replace`.

*Terminal.*

```bash
uv run python -m ingest pipeline --mode before
```

The second article got "transportation." The shared list grew.

```bash
uv run python -m ingest pipeline --mode after
```

Now the second article only has "news" and "ingested." Each article has its
own tags.

---

## 30:30–35:30 — AI agents and the type checker
### Slides 30–31

### Slide 30 — The type checker keeps the agent on a leash

So, why do all of this in 2026? Here's my main point.

When you ask an AI agent to work on loose Python — dicts everywhere,
shared lists, `None` with two meanings, IDs that are just strings — it does
what we do. It invents states that shouldn't exist. It swaps the string
IDs. It forgets a case in the `match`. The happy-path tests pass. And
production slowly gets worse.

Now give the same agent typestates, `NewType`, `assert_never`, and frozen
data. It can still make the same mistakes. But now Pyright catches them.

You know a leash, like for a dog? The dog can still run around. But it
can't run into the street. That's what the type checker does for the
agent. The agent runs Pyright, sees three red errors, fixes them, and only
then opens the pull request.

*Proof. About two minutes. Open `examples/agent-demo/naive-review.md` and
`skilled-review.md` side by side. This is prepared output. No live model.*

Let me show you. Same agent, same prompt. Just "review this code."

Without any guidance, it says — *read it* — "I would not change the return
type, because that would be a breaking change for callers." It adds type
hints, it adds logging. It looks very professional. But `None` still means
two things, and the shared list still leaks.

With the skills, same code, it says: "`ingest()` collapses timeout and
missing into `None`. Use `Result`." It found the real problem.

*Switch to the terminal and run the typestate check again.*

```bash
uv run pyright -p typecheck/invalid typecheck/invalid/cannot_finish_pending_job.py
```

That red line is what the agent reads in its loop. It doesn't need to
understand your whole design. It just needs a clear error in the terminal.

### Slide 31 — Turn the leash on

So what do you actually do on Monday? Three small steps.

One. In `pyproject.toml`, turn on strict mode for Pyright. One line.

Two. Run `pyright` in CI, or in a pre-commit hook. If it's not in CI,
people stop listening to it. And agents do too.

Three. In your agent instructions, add one sentence: "Before you finish,
run Pyright and fix every error." That's it. That's the whole leash.

*Right side.*

And if you want to go further, the repo has five skills. A skill is just a
markdown file that the agent reads before it starts working. One for each
habit tonight, plus one for design reviews. They work with Claude Code,
Cursor, Codex, and Hermes. Copy them, change them, make them yours.

---

## 35:30–37:30 — When I really write Rust
### Slide 32

*Keep this personal. About 90 seconds.*

So after all this "you don't need Rust," I have to be honest. I do write
Rust. Here's where.

Remember, at Handraise we read a lot of news. A live stream of news
articles comes in all day, every day. And something has to catch it.

That's `hr-firehose`. It's a Rust service. It reads the stream, saves every
article to S3, and indexes it so we can search it. And it never stops. It
runs all day, all night. So it has to be fast, it has to use little memory,
and it has to be boring. Boring is the goal.

*Point at the code.*

This is real code from it, just trimmed. Look at the return type:
`Result` of an `Option`. Remember the playroom boxes? This is a box inside
a box. The call can fail, that's the `Result`. And even when it works,
maybe there are no new articles, that's the `Option`. And all those little
question marks? That's the `?` I told you Python doesn't have. Each one
passes the error up, with a message.

We also have a small Rust package called `handytools`, for cleaning up
URLs. Python calls it like any other import, thanks to PyO3.

But the API, the background jobs, the machine learning? All still Python.
Written with the habits from tonight.

So that's my rule. Use Rust where the code never stops and every
millisecond counts. Use Python everywhere else, and borrow Rust's good
ideas.

---

## 37:30–40:00 — Steal this, and close
### Slides 33–34

### Slide 33 — Six habits

Okay. Not next quarter. Pick *one* function this week, and try one of these.

1. Hand failures back as values. Stop using `None` for two different problems.
2. Typestates. Put each method only on the state where it makes sense.
3. Label your IDs with `NewType`, so you can't swap them.
4. Close every `match` with `assert_never`.
5. Check data at the edge. Then trust the type inside.
6. Many readers or one writer. Change local data freely. Don't change shared data.

### Slide 34 — Close

*Slow down here. This is the last thing they hear.*

Better Python isn't more code. It's clearer decisions. And today, those
clear decisions also give our AI agents the guardrails they need.

Everything is in the repo. Slides, this script, the skills, and the little
ingest app. It's MIT. No cloud. Scan the QR code, or the link is on the
slide.

Thank you. I'm happy to take questions.

*Stop. Drink some water. Wait for hands.*

---

## Timing check

If you are late, cut in this order:

| At slide | Cut |
|---:|---|
| 12 | Skip the traits page entirely |
| 18 | Shorten the trade-offs slide |
| 22 | Do not re-run Pyright twice |
| 27 | Skip the memoryview fun fact |
| 29 | Make the AI section very short |
| 31 | Keep the Rust story to 60 seconds |

## Question bank

Short answers. Say "good question" only if you mean it.

- **Isn't `NewType` just a type alias?**
  No. With an alias, `UserId = str`, any string is accepted. With
  `NewType("UserId", str)`, Pyright wants you to wrap it on purpose:
  `UserId(raw)`. That's what catches swapped arguments. When the code runs,
  `UserId(x)` just gives you `x` back.

- **Does `NewType` check the value?**
  No. It's a label, not a check. Check the data once at the edge, like the
  `parse_url` function, or with Pydantic. Then trust the type inside.

- **Does `assert_never` cost anything when the code runs?**
  Basically no. If the code ever reaches that line, it raises an error. But
  Pyright already checked that it can't be reached.

- **Why not use Pydantic for everything?**
  Pydantic is great at the edges: HTTP, JSON, config files. That's where
  you need to check data. Inside the app, the data is already checked, so
  small frozen dataclasses are enough. They're simpler and faster.

- **Can't I still call `.start()` twice on the same `Pending`?**
  Yes. Python can't move values like Rust. The old variable is still there.
  Typestates stop the *wrong* calls, like finishing before starting. They
  don't stop you from using an old value again. Rust stops both.

- **Why are some URLs still plain `str` in the `after/` code?**
  I used `NewType` in the job part, where IDs get swapped. `ingest(url: str)`
  is the edge, where raw input comes in. Using `parse_url` there is the
  natural next step.

- **Pyright or mypy?**
  Both work for these patterns. I use Pyright because it's fast and its
  strict mode is easy to turn on. Pick one and run it in CI. That matters
  more than which one.

- **Isn't this a lot of extra code?**
  A bit, yes. That's why I said: pick one function. Start with the function
  where a bug would hurt the most. Usually that's a network call or a job.

- **If I want Rust's safety, why not just use Rust?**
  Sometimes you should. I did, for our news firehose. But most teams can't
  rewrite their app. These habits give you a lot of the benefit for a much
  smaller cost.

---

## Words to practice

*Words in this script that are easy to trip on. Say them slowly once
before the talk.*

| Word | How to think of it |
|---|---|
| typestate | "type" + "state" — each state is its own type |
| exhaustive | "covers every case" |
| mutable / immutable | "can change" / "can't change" |
| borrow | "lend it for a while" — like a library book |
| babysitter | a person who watches kids while the parents are out |
| errand | a small job outside, like buying milk |
| trait | a skill a type has — Ferris's "badge" |
| aliasing | "two names for the same thing" |
| fingerprint | a short code that identifies something |
| guardrails | the metal rails on the side of a highway |
| leash | the strap you use to walk a dog |
