# Agent skills

Four portable `SKILL.md` files. They are the talk's payload for people who
will never write Rust and will still let an agent touch their Python.

| Skill | Use when |
|---|---|
| `explicit-error-handling` | `None` or mixed exceptions hide expected failures |
| `model-valid-states` | Status strings plus optional fields allow nonsense |
| `intentional-immutability` | Pipeline stages mutate shared dicts/lists |
| `python-design-review` | You want a review that can say "do not gold-plate" |

## Install

Copy a skill folder into the tool's skills directory, or point the tool at
this `skills/` tree.

Examples:

- Claude Code: `.claude/skills/<name>/SKILL.md`
- Codex: `.agents/skills/<name>/SKILL.md` (also read `docs/agent-guidance.md`)
- Cursor: project rules or a skills folder, depending on version
- Hermes: profile `skills/`

The markdown is the skill. There is no extra runtime.

## Repo-wide instructions

See `docs/agent-guidance.md`. Rename or copy it to `AGENTS.md` at the repo
root if your tool loads that filename automatically.
