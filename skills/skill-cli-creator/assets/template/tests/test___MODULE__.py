import json
import subprocess
import sys
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "scripts" / "__SKILL__"


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)


class CliContract(unittest.TestCase):
    def test_version_matches_doctor(self):
        version = run("--version")
        self.assertEqual(version.returncode, 0)
        name, number = version.stdout.split()
        self.assertEqual(name, "__SKILL__")
        doctor = run("--json", "doctor")
        self.assertEqual(doctor.returncode, 0)
        payload = json.loads(doctor.stdout)
        self.assertEqual((payload["ok"], payload["command"], payload["version"]), (True, "doctor", number))

    def test_invalid_arguments_use_the_error_shape(self):
        out = run("--json", "no-such-command")
        self.assertEqual(out.returncode, 2)
        payload = json.loads(out.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "invalid-arguments")


if __name__ == "__main__":
    unittest.main()
