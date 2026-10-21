"""Checks for the autopilot skill and the example run it came from. Standard library only."""
import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skill" / "autopilot" / "SKILL.md"
EXAMPLE = ROOT / "examples" / "tv-debloat"


def split_skill():
    text = SKILL.read_text()
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    assert match, "SKILL.md must start with a frontmatter block"
    meta = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    return meta, match.group(2)


def text_files():
    skip = {".git", "__pycache__"}
    for path in ROOT.rglob("*"):
        if path.is_file() and not (set(path.parts) & skip) and path.suffix not in {".png", ".mp4", ".webp"}:
            yield path


class SkillFileTests(unittest.TestCase):
    def test_frontmatter(self):
        meta, _ = split_skill()
        self.assertEqual(meta["name"], "autopilot")
        self.assertTrue(0 < len(meta["description"]) <= 1024)
        self.assertEqual(meta["disable-model-invocation"], "true")  # only runs when I type /autopilot
        self.assertIn("argument-hint", meta)

    def test_uses_the_arguments_placeholder(self):
        _, body = split_skill()
        self.assertIn("$ARGUMENTS", body)

    def test_phases_exist_in_order(self):
        _, body = split_skill()
        headings = re.findall(r"^## (.+)$", body, re.M)
        wanted = ["Resuming", "Files", "Phase 1", "PLAN.md structure", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
        positions = []
        for name in wanted:
            hits = [i for i, h in enumerate(headings) if h.startswith(name)]
            self.assertTrue(hits, f"missing section: {name}")
            positions.append(hits[0])
        self.assertEqual(positions, sorted(positions))

    def test_plan_structure_lists_every_section_in_order(self):
        _, body = split_skill()
        block = body.split("## PLAN.md structure", 1)[1].split("## Phase 2", 1)[0]
        names = ["Where things stand", "Done means", "My preferences", "Approved", "Off limits",
                 "How to work", "Steps", "Test plan", "Check by hand", "Goal message"]
        last = -1
        for name in names:
            index = block.find(f"**{name}")
            self.assertGreater(index, last, f"PLAN section out of order or missing: {name}")
            last = index

    def test_report_structure_lists_every_section(self):
        _, body = split_skill()
        block = body.split("## Phase 5", 1)[1]
        for name in ["Read this first", "What changed", "Test results", "Check by hand",
                     "Still broken", "Where everything is", "What could undo this later"]:
            self.assertIn(name, block)

    def test_safety_rules_are_present(self):
        _, body = split_skill()
        for rule in ["Three-strike rule", "Never push to main", "Stop and wait only if",
                     "cold-start", "--dry-run", "under 3,500 characters"]:
            self.assertIn(rule, body)


class RepoHygieneTests(unittest.TestCase):
    def test_no_em_dashes_anywhere(self):
        for path in text_files():
            self.assertNotIn("\u2014", path.read_text(errors="ignore"), str(path))

    def test_no_private_addresses_or_keys(self):
        for path in text_files():
            if path.name == "test_skill.py":
                continue
            content = path.read_text(errors="ignore")
            self.assertIsNone(re.search(r"\b192\.168\.\d+\.\d+\b", content), str(path))
            self.assertIsNone(re.search(r"(api[_-]?key|secret|token)\s*[=:]\s*\S{12,}", content, re.I), str(path))


class ExampleRunTests(unittest.TestCase):
    """The TV project came first and the skill was written from it, so these check what that run produced."""

    def test_plan_is_marked_as_source_of_truth(self):
        plan = (EXAMPLE / "PLAN.md").read_text()
        self.assertIn("Re-read this file after every compaction", plan)
        self.assertIn("## Steps", plan)
        self.assertIn("DONE", plan)

    def test_report_has_a_test_table_with_pass_and_fail(self):
        report = (EXAMPLE / "REPORT.md").read_text()
        self.assertIn("## Read this first", report)
        rows = [line for line in report.splitlines() if line.startswith("|") and ("PASS" in line or "FAIL" in line)]
        self.assertGreaterEqual(len(rows), 10)
        self.assertTrue(any("FAIL" in row for row in rows), "the report should show failures honestly")

    def test_change_log_has_timestamps(self):
        log = (EXAMPLE / "change_log.txt").read_text()
        self.assertGreaterEqual(len(re.findall(r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) \w{3} +\d+ \d\d:\d\d:\d\d", log)), 10)

    def test_restore_script_dry_run_changes_nothing(self):
        """Runs the real restore.sh with --dry-run and a fake adb that fails the test if it is ever called."""
        script = EXAMPLE / "restore.sh"
        listed = re.findall(r'^\s*"([A-Za-z0-9_.]+)"\s*$', script.read_text(), re.M)
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "adb"
            fake.write_text("#!/bin/bash\necho ADB WAS CALLED >&2\nexit 99\n")
            fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}"}
            result = subprocess.run(["bash", str(script), "--dry-run"], capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("ADB WAS CALLED", result.stderr + result.stdout)
        self.assertIn("Dry run finished", result.stdout)
        enabled = re.findall(r"pm enable --user 0 (\S+)", result.stdout)
        self.assertEqual(len(enabled), len(listed))
        self.assertEqual(sorted(enabled), sorted(listed))
        self.assertEqual(len(enabled), 35)  # the report says 35 packages were disabled

    def test_saved_dry_run_output_matches_a_fresh_one(self):
        saved = (EXAMPLE / "restore_dryrun.txt").read_text()
        fresh = subprocess.run(["bash", str(EXAMPLE / "restore.sh"), "--dry-run"], capture_output=True, text=True, timeout=30).stdout
        self.assertEqual([l.strip() for l in saved.splitlines() if l.strip()],
                         [l.strip() for l in fresh.splitlines() if l.strip()])


if __name__ == "__main__":
    unittest.main()
