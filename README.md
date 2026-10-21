# autopilot-skill

`/autopilot` is a Claude Code skill that runs a project from start to finish while I'm away. I answer questions at the start, then Claude Code writes a plan to disk, backs things up, builds in small tested steps without asking me anything, and hands back a tested result with a report. It is meant for projects where I want to spend as little time as possible and still get something that works.

It came out of an Android TV project where Claude Code rewrote a TV's home screen over several sessions. That project is in `examples/tv-debloat/`.

## Install

```
mkdir -p ~/.claude/skills/autopilot
cp skill/autopilot/SKILL.md ~/.claude/skills/autopilot/SKILL.md
```

## Use

Inside Claude Code:

```
/autopilot <describe the project>
/autopilot resume
```

The skill only runs when I type it (`disable-model-invocation: true`).

## What the model is responsible for

Every time the skill runs, Claude Code does the work:

1. **Interview.** It detects what it can, then asks me about the goal, what must keep working, my exact preferences, limits, and anything that needs a human (logins, button presses).
2. **Plan.** It writes `PLAN.md` in a fixed structure, shows me a summary, and gives me a `/goal` message to paste that spells out the approved actions and the off-limits list.
3. **Baseline and backup.** It snapshots the current state and writes a `restore.sh` with `--dry-run`.
4. **Build.** It works in small batches, debugs from logs before changing anything, and undoes and moves on after three failed attempts at the same problem.
5. **Report.** It writes `REPORT.md` with the results, what is still broken, and what I have to check by hand.

## What does not rely on the model

- The tests, commands and measurements the skill requires (test suite, `dumpsys` numbers, screenshot hash comparisons) produce output that is saved in `change_log.md`.
- The approved and off-limits actions are written into my `/goal` message, so Claude Code's own permission check reads them from me, not from a file the model wrote.
- `restore.sh --dry-run` and a harmless real undo test are required before any real change.
- `test_skill.py` checks the skill file's structure with plain Python, and runs the example run's real `restore.sh --dry-run` against a fake `adb` that fails the test if it is ever called.

## Limits

- The skill is instructions, so the model can still misread them. That is why it requires evidence for every test and a report that lists failures.
- The example run came before the skill. The skill was written from it, so the example shows the pattern but is not a run of `/autopilot` itself. See `LOG.md`.
- It needs a Claude Code version with `/goal` and auto mode for fully unattended work.

## Tests

```
python3 -m unittest
```
