# Agent demo (prepared, not live)

Live coding agents are not deterministic. This folder is the version of the
demo you can show even if wifi dies.

| Path | What it is |
|---|---|
| `original.md` | The three bugs, quoted from `src/ingest/before/` |
| `naive-review.md` | Typical review **without** the design skills |
| `skilled-review.md` | Review **with** the four skills |
| `naive-refactor.py` | A "typed, logged, professional" rewrite that keeps the bugs |

The intended after-code is `src/ingest/after/`. That is the skilled refactor.

Talk flow:

1. Show `src/ingest/before/errors.py` returning `None` for two failures.
2. Read two or three sentences from `naive-review.md`.
3. Read the corresponding sentences from `skilled-review.md`.
4. Run `python -m ingest demo --mode before --url https://news.example/timeout`
   and the after equivalent.
5. Ask the room: which diff would you want an agent to copy next week?
