# autopilot-skill

A Claude Code skill I wrote, `/autopilot`, plus the first real project it was based on. Built for TCSS 490 Artifact 3.

## Layout

- `skill/autopilot/SKILL.md` is the skill itself. Copy that folder to `~/.claude/skills/autopilot/` to install it.
- `examples/tv-debloat/` holds the plan, log, report and restore script from the Android TV project the skill was written from. The TV's IP address is replaced with 192.0.2.10 and em dashes are replaced with hyphens.
- `test_skill.py` checks the skill file and the example run with plain Python. Run `python3 -m unittest`.
- `LOG.md` is the log of plans and changes.

## Rules for working in this repo

- Standard library only. Add a test for every change to the skill's structure.
- Never put an IP address, token or key in this repo.
- No em dashes in any file.
- Keep LOG.md current: what I asked for, what changed, and which of my answers changed the result.
