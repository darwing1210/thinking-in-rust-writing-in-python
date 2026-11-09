# Agent skills

Five portable `SKILL.md` files. They are the talk's payload for people who
want to teach AI coding agents to write safer, reliable Python.

| Skill | Use when |
|---|---|
| `explicit-error-handling` | `None` or mixed exceptions hide expected failures |
| `model-valid-states` | Object lifecycles need typestates and method gating |
| `type-driven-contracts` | Domain IDs need `NewType` and match needs `assert_never` |
| `intentional-immutability` | Pipeline stages mutate shared state (Aliasing XOR Mutability) |
| `python-design-review` | You want a review that filters for simplicity and safety |

## Install

Copy a skill folder into the tool's skills directory, or point the tool at
this `skills/` tree.

Examples:

- Claude Code: `.claude/skills/<name>/SKILL.md`
- Codex: `.agents/skills/<name>/SKILL.md` (also read `docs/agent-guidance.md`)
- Cursor: project rules or `.cursorrules`
- Hermes: profile `skills/`

The markdown is the skill. There is no extra runtime.

## Repo-wide instructions

See `docs/agent-guidance.md`. Rename or copy it to `AGENTS.md` at the repo
root if your tool loads that filename automatically.
