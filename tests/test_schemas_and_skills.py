"""CI-facing checks: JSON Schema validity, example-objective conformance, skill
frontmatter integrity, and internal markdown-link resolution."""

import json
import re
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_json_schemas_are_valid_draft2020(self):
        for rel in ("objective.schema.json", "recovery/round_state.schema.json"):
            with self.subTest(schema=rel):
                schema = json.loads((ROOT / rel).read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)

    def test_example_objective_conforms_to_schema(self):
        schema = json.loads((ROOT / "objective.schema.json").read_text(encoding="utf-8"))
        obj = yaml.safe_load((ROOT / "objective.example.yaml").read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
        self.assertEqual(errors, [], msg="; ".join(e.message for e in errors))


class SkillFrontmatterTests(unittest.TestCase):
    def _frontmatter(self, skill_md: Path) -> dict:
        text = skill_md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(m, f"{skill_md} has no YAML frontmatter")
        return yaml.safe_load(m.group(1)) or {}

    def test_every_skill_name_matches_its_directory(self):
        # Recurse: skills live under skills/original/ and skills/iterated/, not flat.
        skill_files = sorted((ROOT / "skills").rglob("SKILL.md"))
        self.assertGreaterEqual(len(skill_files), 10, "expected the skills library to be discovered")
        for skill_md in skill_files:
            with self.subTest(skill=skill_md.parent.name):
                fm = self._frontmatter(skill_md)
                self.assertEqual(
                    fm.get("name"),
                    skill_md.parent.name,
                    f"{skill_md}: name != directory",
                )
                self.assertTrue(fm.get("description"), f"{skill_md}: missing description")


class InternalLinkTests(unittest.TestCase):
    _LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)]+)\)")

    def test_relative_links_resolve(self):
        for rel in ("README.md", "skills/index.md"):
            md = ROOT / rel
            for target in self._LINK_RE.findall(md.read_text(encoding="utf-8")):
                path = target.split("#", 1)[0].strip()
                if not path:
                    continue
                with self.subTest(source=rel, link=path):
                    self.assertTrue((md.parent / path).exists(), f"{rel}: broken link -> {path}")


if __name__ == "__main__":
    unittest.main()
