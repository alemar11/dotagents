import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
CLI = SKILL / "scripts" / "skill-cli-creator"


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)


def payload(out):
    return json.loads(out.stdout)


class TemplateAndCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def new(self, name="release-notes"):
        out = run("--json", "new", name, "--into", str(self.root), "--description", 'Read "notes". Use when asked.')
        self.assertEqual(out.returncode, 0, out.stdout)
        return self.root / name

    def test_a_new_skill_passes_the_check_and_its_own_tests(self):
        skill = self.new()
        self.assertTrue((skill / "scripts" / "release-notes").stat().st_mode & stat.S_IXUSR)
        self.assertTrue((skill / "tests" / "test_release_notes.py").is_file())
        checked = run("--json", "check", str(skill))
        self.assertEqual(checked.returncode, 0, checked.stdout)
        self.assertTrue(all(c["ok"] for c in payload(checked)["checks"]))
        tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                               cwd=skill, capture_output=True, text=True)
        self.assertEqual(tests.returncode, 0, tests.stderr)

    def test_check_names_each_violation(self):
        skill = self.new()
        artifact = skill / "scripts" / "release-notes"
        artifact.write_text(artifact.read_text().replace('version=f"{PROG} {VERSION}"', 'version=VERSION'))
        (skill / "references" / "cli.md").unlink()
        out = run("--json", "check", str(skill))
        self.assertEqual(out.returncode, 1)
        result = payload(out)
        self.assertEqual(result["error"]["code"], "standard-violations")
        failed = {c["id"] for c in result["checks"] if not c["ok"]}
        # The removed cli.md also breaks SKILL.md's link to it.
        self.assertEqual(failed, {"file:references/cli.md", "links", "version", "doctor"})

    def test_new_refuses_a_bad_name_and_an_existing_target(self):
        out = run("--json", "new", "Bad_Name", "--into", str(self.root), "--description", "x")
        self.assertEqual((out.returncode, payload(out)["error"]["code"]), (2, "invalid-name"))
        self.new()
        out = run("--json", "new", "release-notes", "--into", str(self.root), "--description", "x")
        self.assertEqual((out.returncode, payload(out)["error"]["code"]), (1, "target-exists"))


class OwnContract(unittest.TestCase):
    def test_this_skill_follows_its_own_standard(self):
        out = run("--json", "check", str(SKILL))
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_invalid_arguments_use_the_error_shape(self):
        out = run("--json", "nope")
        self.assertEqual(out.returncode, 2)
        self.assertEqual(payload(out)["error"]["code"], "invalid-arguments")


if __name__ == "__main__":
    unittest.main()
