# Build log: Artifact 3, autopilot skill

Tools: Claude Code for the TV project and the skill, Claude in the Claude app for packaging this repo. Started Wednesday, October 21, 2026. Due Sunday, October 25, 11:59 PM.

## Feedback I am building on

Chris's feedback on Artifact 1: "Next time give more direction up front, as you planned, and record in LOG.md which of your answers changed the result." The table below does that.

## What happened, in order

- **Oct 20, 4:15 PM.** Started debloating my TCL Google TV with Claude Code. The first backup files are timestamped 4:15 PM and the first batch of disabled apps 4:19 PM.
- **Oct 20, evening.** Claude Code sessions kept crashing when screenshots filled up its context. A `PLAN.md` recorded the rules so a fresh session could pick up where the last one stopped.
- **Oct 20, 8:22 PM to 10:10 PM.** One long run with me away from the computer. Its report is in `examples/tv-debloat/REPORT.md`. Later tasks (settings shortcut, remote buttons) were added to the same report.
- **Oct 21, about 12:18 PM.** Last save of the `autopilot` skill file, which turns those rules into a reusable `/autopilot` command.
- **Oct 21.** Realized the TV project alone does not meet Artifact 3. The skill does, because Claude Code does real work every time `/autopilot` runs. This repo packages the skill with the TV project as its example.

## Direction I gave and what it changed

| What I said or did | What it changed in the result |
| --- | --- |
| Asked for a strict production bar on the TV: nothing is done until tested. | Skill opens with "Treat me as production" and Phase 3 requires evidence for every test in `change_log.md`. |
| Told Claude Code repeatedly to stop asking for permission, and corrected a draft prompt that still said "ask me first". | Phase 3 says never stop to ask. The approved actions go in the `/goal` message I paste, because auto mode's check reads my messages, not files. |
| Screenshots crashed the sessions. | Skill has a "Context hygiene" section: convert to a small JPEG, check the file size, use text checks first, compare hashes instead of viewing. |
| Force-stopping Projectivy broke its accessibility service until a reboot. | `PLAN.md` says never force-stop it, and the skill's debugging rules say to check your own side effects first. |
| Gave an exact order for the TV apps. | Interview step 3 asks for specifics, such as an exact list or order, not "whatever looks good". |
| Asked whether the TV project could count for Artifact 3. | Claude said no as it stood, because the model only worked while building it. It offered adding a model step or using a Claude Code skill. |
| Showed Claude my `autopilot` skill and asked to use it for Artifact 3. | Claude read my TV run files and proposed submitting the skill itself, with the TV project as the example. It added tests and docs and did not change the skill's wording. |

## Decisions Claude made without asking me

- Submit the skill as the artifact (the "Claude Code skill" option on the assignment page) instead of building something new.
- Copy the skill file as it was, with no edits.
- Include the TV run as `examples/tv-debloat/`, with the TV's IP address replaced by 192.0.2.10 and em dashes replaced by hyphens. The numbers and results are unchanged.
- Say plainly in the README that the example run came before the skill, so it is not a run of `/autopilot` itself.
- Write `test_skill.py` so it checks the skill's structure and also runs the real `restore.sh --dry-run` against a fake `adb` that fails the test if it is called.

## What has been checked

- 13 tests pass: the skill's frontmatter, its phases in order, the PLAN and REPORT section lists, safety rules, no em dashes, no private addresses or keys, the example's report and log, and the dry run of `restore.sh` (35 packages, matches the saved dry-run output).
- Claude broke things on purpose to make sure the tests notice: deleting a frontmatter field, adding an em dash, and renaming the `--dry-run` option each made tests fail. Everything was put back and the tests pass again.
- The example report records test results from the TV run: all 11 apps opened from the launcher and Home always returned, HDMI 1 and 2 worked, frame drops were 8.89%, memory grew 15.8% against a 30% limit, and the video kept playing after a reboot.

## What has not been checked

- `/autopilot` has not been run as a command from start to finish. The TV run happened before the skill existed in this form.
- The `/autopilot resume` path has not been tried.
- I have not used it on a code project, only on the TV.
- The numbers in the example report are Claude Code's own measurements. This repo does not re-measure them, and I have not read every line of the 155-line change log.
- The example report also records real failures: the accessibility service is not bound after a reboot, Projectivy holds a wake lock while the video plays, and four remote buttons do nothing.

## Parts I am trusting

- The skill is instructions, so I am trusting Claude Code to follow them. The evidence requirement and the report are how I check.
- I am trusting the permission settings in my `/goal` message to keep it inside the approved actions.

## To do

1. Add one sentence here on how the skill was written, and what I did versus what Claude did.
2. Run `/autopilot` once on a small project, copy its `PLAN.md` and `REPORT.md` into `examples/`, and record here what worked and what did not.
3. Try `/autopilot resume` on that project.
4. Push this repo, fill in the Artifact 3 card on my portfolio (title, repo link, reflection), and submit the same portfolio link on Canvas.
