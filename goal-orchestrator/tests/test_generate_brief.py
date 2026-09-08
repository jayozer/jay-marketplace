from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_brief  # noqa: E402
from generate_brief import generate_brief as build_brief  # noqa: E402

GENERATE_BRIEF = ROOT / "scripts" / "generate_brief.py"

PYPROJECT = '[project]\nname = "pyname"\ndescription = "Py description."\n'
PACKAGE_JSON = '{"name": "jsname", "description": "JS description.", "dependencies": {"react": "^18"}}\n'


class SourcePrecedenceTests(unittest.TestCase):
    def test_readme_name_and_description_win_over_pyproject(self) -> None:
        if generate_brief.tomllib is None:
            self.skipTest("tomllib is unavailable on this Python")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# ReadmeName\n\nReadme description here.\n", encoding="utf-8"
            )
            (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
            brief = build_brief(root)

        self.assertIn("**Name:** ReadmeName", brief)
        self.assertIn("**Description:** Readme description here.", brief)
        self.assertNotIn("pyname", brief)
        self.assertNotIn("Py description.", brief)

    def test_readme_values_win_over_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# ReadmeName\n\nReadme description here.\n", encoding="utf-8"
            )
            (root / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
            brief = build_brief(root)

        self.assertIn("**Name:** ReadmeName", brief)
        self.assertIn("**Description:** Readme description here.", brief)
        self.assertNotIn("jsname", brief)
        # Tech stack is still unioned from every source.
        self.assertIn("React", brief)

    def test_pyproject_fills_in_when_readme_has_no_values(self) -> None:
        if generate_brief.tomllib is None:
            self.skipTest("tomllib is unavailable on this Python")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # A README with no top-level heading yields neither name nor description.
            (root / "README.md").write_text("Just some notes.\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
            brief = build_brief(root)

        self.assertIn("**Name:** pyname", brief)
        self.assertIn("**Description:** Py description.", brief)

    def test_pyproject_fills_in_when_readme_is_absent(self) -> None:
        if generate_brief.tomllib is None:
            self.skipTest("tomllib is unavailable on this Python")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
            brief = build_brief(root)

        self.assertIn("**Name:** pyname", brief)
        self.assertIn("**Description:** Py description.", brief)


class ScopeWordingTests(unittest.TestCase):
    def test_docstring_and_help_describe_the_draft_scaffold_scope(self) -> None:
        self.assertIn("draft scaffold", generate_brief.__doc__)
        self.assertIn("README.md, package.json, and pyproject.toml only", generate_brief.__doc__)
        self.assertIn(
            "does not inspect git state, AGENTS.md, or verification scripts",
            generate_brief.__doc__,
        )

        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "COLUMNS": "400"}
        result = subprocess.run(
            [sys.executable, str(GENERATE_BRIEF), "--help"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("draft scaffold", result.stdout)
        self.assertIn("README.md, package.json, and pyproject.toml only", result.stdout)
        self.assertIn(
            "does not inspect git state, AGENTS.md, or verification scripts",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
