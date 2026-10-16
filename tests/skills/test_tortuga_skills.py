"""Offline checks for project skills and real synthetic contract executions."""
import ast
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
NAMES = ("tortuga-research", "tortuga-implement", "tortuga-review")

class SkillContracts(unittest.TestCase):
    def test_frontmatter(self):
        for name in NAMES:
            with self.subTest(skill=name):
                text = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertTrue(text.startswith("---\n"))
                header, body = text[4:].split("\n---\n", 1)
                self.assertIn("name: " + name, header)
                match = re.search(r"^description: (.+)$", header, re.M)
                assert match is not None
                desc = match.group(1)
                self.assertLessEqual(len(desc), 60)
                self.assertTrue(desc.endswith("."))
                for key in ("version:", "author:", "license:", "platforms:", "metadata:"):
                    self.assertIn(key, header)
                for section in ("When to Use", "Procedure", "Pitfalls", "Verification"):
                    self.assertIn("## " + section, body)
                for token in ("/home/", "/Data/", "~/.claude", "skills_invoked.txt"):
                    self.assertNotIn(token, text)
                match = re.search(r"related_skills: \[(.*?)\]", header)
                assert match is not None
                related = match.group(1).split(", ")
                for sibling in related:
                    self.assertTrue((ROOT / "skills" / sibling / "SKILL.md").is_file())

    def test_local_references(self):
        for name in NAMES:
            base = ROOT / "skills" / name
            text = (base / "SKILL.md").read_text()
            for ref in re.findall(r"`(references/[^`]+)`", text):
                self.assertTrue((base / ref).is_file(), ref)

    def test_runner_and_scope_gates(self):
        text = (ROOT / "skills/tortuga-implement/SKILL.md").read_text()
        for term in ("FULL agreed suite", "Commit/push/PR", "Retry/recovery", "quota/429", "timeout", "not prerequisites"):
            self.assertIn(term, text)
        text = (ROOT / "skills/tortuga-review/SKILL.md").read_text()
        for term in ("REQUEST_CHANGES", "self-review", "Stale hashes", "human acceptance"):
            self.assertIn(term, text)

    def test_fixture_syntax(self):
        for path in (ROOT / "experiments/t_95b161ac").rglob("*.py"):
            ast.parse(path.read_text(), filename=str(path))

    def test_known_defect_detected(self):
        result = subprocess.run([sys.executable, "-B", "experiments/t_95b161ac/test_quantity.py", "--variant", "baseline"], cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL: test_reject_bool", result.stderr)
        self.assertIn("Ran 9 tests", result.stderr)
        self.assertIn("FAILED (failures=1)", result.stderr)
        self.assertNotIn("ERROR:", result.stderr)

    def test_fixed_full_suite_twice(self):
        outcomes = []
        for _ in range(2):
            result = subprocess.run([sys.executable, "-B", "experiments/t_95b161ac/test_quantity.py", "--variant", "fixed"], cwd=ROOT, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Ran 9 tests", result.stderr)
            self.assertNotIn("skipped", result.stderr)
            outcomes.append([line for line in result.stderr.splitlines() if line.startswith("test_")])
        self.assertEqual(outcomes[0], outcomes[1])

if __name__ == "__main__":
    unittest.main()
