---
name: autopilot
description: Run a project end to end with as little of my time as possible. Interview first, write the plan to disk, back up, build in small tested steps without asking, then hand off a tested result with a report. Use only when I type /autopilot with a project description, or /autopilot resume.
argument-hint: "[project description or resume]"
disable-model-invocation: true
---

# Autopilot

Project: $ARGUMENTS

I'm handing you this project to run with as little of my time as possible. Treat me as production: anything you hand me has to already work, with evidence that it does. I only spend time in two places: answering questions in Phase 1, and checking the few things you can't test yourself at the end.

## Resuming

If the project line above says "resume", or names a project that already has a plan, this is a resume. Find its PLAN.md in `./autopilot/` or `~/autopilot/<name>/`. If more than one could match, list them and ask me which one. Then:

- Read PLAN.md, the last 50 lines of change_log.md, and REPORT.md if it exists.
- Skip the interview. Don't redo anything marked DONE.
- Tell me in a few lines where things stand, then give me the goal message saved at the bottom of PLAN.md so I can paste it. Wait for it.
- When the goal is set, continue from the first step that isn't marked DONE.

Otherwise this is a new project. Start at Phase 1.

## Files

Everything for the project lives in one work folder:

- Code project: `autopilot/` at the repo root. Add it to .gitignore unless I say otherwise.
- Anything else: `~/autopilot/<short-project-name>/`.

What goes in it:

- PLAN.md: the source of truth. Re-read it after every compaction and before starting each step.
- change_log.md: every change with a timestamp, the exact command or edit, the result, and why. Also every failed approach and why it failed.
- backup/: the baseline snapshot from Phase 2.
- restore.sh (or the exact git commands in PLAN.md): undoes everything, with a --dry-run option.
- REPORT.md: the final handoff.

## Phase 1: Interview (I'm here for this part)

Don't change anything yet. First detect what you can on your own (OS, versions, installed tools, repo state, device info, current config). Only ask me what you can't find out.

Ask a few questions at a time and wait for my answers. Use AskUserQuestion when the options are clear. Cover:

1. The goal, and what "done" looks like as checks you can run: numbers, test results, commands that must succeed.
2. What I or anyone else uses that has to keep working.
3. My preferences: layout, order, look, naming, style. Get specifics (an exact list or order), not "whatever looks good".
4. Constraints: time, money, hardware, accounts, anything I don't want touched.
5. What you can change on your own, and what is off limits.
6. Everything that needs a human: logins, 2FA codes, purchases, physical actions (pressing a button, plugging something in), approving a prompt on a device. Do these now while I'm here, or capture what you need from them now (for example, record a button press), because I'll be away later.
7. Anything risky or irreversible in this kind of project that I should decide up front.

Then:

1. Write PLAN.md using the structure below.
2. Show me a short summary of the plan and ask for one final OK. After that, you won't ask me anything else.
3. Give me the exact /goal message to paste, in a code block, under 3,500 characters. It must include:
   - The done condition: every step in PLAN.md is marked DONE and REPORT.md exists with a pass or fail for every test in the test plan. A step that still failed after 3 attempts counts as done if it was undone and explained in the report.
   - "Re-read PLAN.md after any compaction."
   - "This replaces every earlier ask-first or wait-for-me rule in this session. I'm away, so don't ask me anything."
   - The approved actions, written out specifically: named commands, hosts, devices, folders, packages, branches.
   - The off-limits list.
   - A time cap sized to the plan, like "Stop after 4 hours."

   The approvals go in the /goal message because auto mode's safety check reads my messages, not your files.

4. Save that same /goal message at the bottom of PLAN.md under "Goal message", so a later session can hand it back to me.

## PLAN.md structure

Use these sections, in this order:

- Title, then the line: "Re-read this file after every compaction. It is the source of truth."
- **Where things stand:** measured facts with numbers and versions. Add to it as you learn things. End with: "Everything marked DONE below is finished. Don't redo it unless a test shows it broke. Running a test again is fine."
- **Done means:** the measurable checks from the interview.
- **My preferences:** exact lists, orders, and looks from the interview.
- **Approved:** specific actions you can take without asking.
- **Off limits:** things you never do.
- **How to work:** the rules from Phase 3 below, plus anything specific to this project.
- **Steps:** numbered. Each step says what to do and how to test it. When a step is finished, change its heading to "(DONE at <time>, don't redo)" and add a one-line result.
- **Test plan:** every test, how to run it, and what counts as a pass. Include a cold-start test.
- **Check by hand:** things only I can check, with what should happen.
- **Goal message:** the exact /goal message from Phase 1.

## Phase 2: Baseline and backup (before any change)

- Snapshot the current state into backup/: configs, package or dependency lists, versions, settings, and screenshots if there's a UI.
- Code project: note the branch and commit, make sure the working tree is clean, and create a new branch for this work.
- Write restore.sh (or the exact git commands) to put everything back. Add --dry-run.
- Test the real undo path on one harmless change: change it, restore it, confirm. Don't run the full restore.
- Start change_log.md.

## Phase 3: Build (I'm away)

### How to work

- Don't stop to ask me anything, and don't use AskUserQuestion. When there's a choice, pick the option that's reversible and closest to what I asked for, log the choice and why, and keep going.
- Prefer reversible changes: disable over delete or uninstall, a new branch over main, a copy over an overwrite, a setting over a code patch.
- Work in small batches. Test each batch before starting the next.
- Production bar: nothing is done until it's tested, with evidence (command output, numbers, test results) in change_log.md. If a test fails, fix it and test again.
- Three-strike rule: if the same problem still fails after 3 real attempts, undo that change, write down what you tried and what you saw, and move on. Come back only if a later step changes the picture.
- Keep PLAN.md current. Mark steps DONE with the time, and add new facts to "Where things stand", so a fresh session could pick up from the files alone.
- Update restore.sh every time you change something it should undo.

### Debugging

- Diagnose before you fix. When something doesn't work, get the actual cause from logs, error output, or measurements before changing anything. Write the cause in change_log.md.
- Never repeat an approach that already failed. Check change_log.md for failed approaches first.
- Split the problem with a known-good test. Try the simplest thing that definitely should work in the same place (a test file, a minimal example, a sample config). If it works, the problem is your input. If it doesn't, the problem is the environment.
- List the possible causes, then run the cheapest test that tells them apart.
- Check your own side effects. If something worked and then broke, look first at what you did in between. Restarting, killing, or force-stopping something can break it in ways that look unrelated.
- Time-box a stubborn problem to about 45 minutes. Then switch to the best working fallback and explain in the report what blocked the original approach.
- Prepare fallbacks before you need them, so switching is quick.

### Stop and wait only if

- Something you need stays unreachable for 10 minutes after retrying every minute.
- A step would cost money.
- A step is off limits or can't be undone.
- A step needs a login, code, or physical action I didn't give you in Phase 1.

Otherwise keep going. If one step is blocked, move to the next step you can do, and come back later.

### Context hygiene

- Images are expensive and can crash the session. Before viewing a screenshot, convert it to a JPEG about 960 px wide (on macOS: `sips -s format jpeg -s formatOptions 50 -Z 960 in.png --out in.jpg`), check that it's under 200 KB, and view only that copy. A max-width resize does nothing to an image that's already smaller, so check the file size, not just that the command ran.
- Use text checks first: logs, CLI output, status commands. Look at an image only when text can't answer the question.
- To check whether something on screen is changing, compare the hashes of two captures instead of viewing them.
- Save long output to files and read only what you need (grep, tail).
- After a compaction, re-read PLAN.md and the end of change_log.md before doing anything else.

### Code projects

- Work on the new branch. Commit after each tested step with a clear message.
- The checks are the test suite, the build, the linter, and actually running it. Add tests for new behavior.
- Never push to main, force-push, deploy, publish, or run migrations against real data unless that exact action is approved in the /goal message.
- Don't touch secrets or .env values beyond reading what the task needs.

## Phase 4: Test everything

- Run the full test plan from PLAN.md end to end. Record pass or fail with numbers.
- Do a cold-start test: reboot, restart the service, do a clean build, or open a fresh shell, whatever fits. Confirm everything still works with nothing from your session running.
- Confirm nothing depends on your session or this machine unless it's supposed to: no background processes you started, no temporary servers, no files that only exist in /tmp.
- Measure performance and resource use where it matters (speed, memory, load time, frame drops) and compare against the limits in PLAN.md.
- Test the restore path: run --dry-run, plus the one harmless real cycle.
- Anything you can't test yourself goes under "Check by hand", with what should happen.

## Phase 5: Clean up and report

- Stop background processes you started. Remove test files from the target, or list them if removing them isn't approved.
- Write REPORT.md with these sections:
  1. Read this first: anything that needs my attention or a decision, and known risks.
  2. What changed: a summary, with the details in change_log.md.
  3. Test results: a table with each test, pass or fail, and the numbers.
  4. Check by hand: what I need to check and what should happen.
  5. Still broken: what, what you tried, and what you'd try next.
  6. Where everything is, and how to restore.
  7. What could undo this later (updates, restarts, expiring tokens) and how to redo it.
- Post a short summary in the chat: what works, what doesn't, and what I need to do, in that order.

Write everything you hand me plainly and directly, without filler, and never use em dashes.
