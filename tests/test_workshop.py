"""Offline tests for skill installation and the publication boundary."""
import argparse
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor
import skills

ROOT = Path(__file__).resolve().parents[1]


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("---\nname: demo\n---\nA skill.\n", encoding="utf-8")
        (self.source / "scripts").mkdir()
        (self.source / "scripts/tool.py").write_text("print('hello')\n", encoding="utf-8")
        self.destination = self.root / "installed/demo"
        self.skill = {"name": "demo", "path": ".", "tree_sha256": skills.tree_digest(self.source)}

    def install(self):
        with contextlib.redirect_stdout(io.StringIO()):
            skills.install_payload(self.source, self.destination, self.skill)

    def test_install_is_idempotent_and_preserves_credentials(self):
        (self.source / ".env").write_text("DO_NOT_COPY=private", encoding="utf-8")
        self.install()
        self.assertFalse((self.destination / ".env").exists())
        secret = self.destination / ".env"
        secret.write_text("KEEP_ME=private", encoding="utf-8")
        before = (self.destination / "SKILL.md").stat().st_mtime_ns
        self.install()
        self.assertEqual(secret.read_text(), "KEEP_ME=private")
        self.assertEqual((self.destination / "SKILL.md").stat().st_mtime_ns, before)

    def test_local_changes_are_never_overwritten(self):
        self.install()
        changed = self.destination / "scripts/tool.py"
        changed.write_text("my local work\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "preserved"):
            self.install()
        self.assertEqual(changed.read_text(), "my local work\n")

    def test_unexpected_upstream_content_is_rejected_before_install(self):
        (self.source / "scripts/tool.py").write_text("changed upstream", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.install()
        self.assertFalse(self.destination.exists())

    def test_digest_ignores_runtime_but_detects_extra_code(self):
        (self.source / ".cache").mkdir()
        (self.source / ".cache/data.json").write_text("{}", encoding="utf-8")
        self.assertEqual(skills.tree_digest(self.source), self.skill["tree_sha256"])
        (self.source / "extra.py").write_text("extra", encoding="utf-8")
        self.assertNotEqual(skills.tree_digest(self.source), self.skill["tree_sha256"])

    def test_hash_is_consistent_across_line_endings(self):
        original = skills.tree_digest(self.source)
        path = self.source / "SKILL.md"
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual(original, skills.tree_digest(self.source))

    def test_path_cannot_escape_destination(self):
        with self.assertRaises(ValueError):
            skills.contained(self.root, "../outside")

    def test_locked_skill_names_and_paths_are_validated(self):
        lock = skills.load_lock(ROOT)
        lock["sources"][0]["skills"][0]["path"] = "../outside"
        (self.root / "skills.lock.json").write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid source path"):
            skills.load_lock(self.root)

    def test_committed_lock_covers_every_expected_skill(self):
        lock = skills.load_lock(ROOT)
        self.assertEqual(len(lock["sources"]), 7)
        self.assertEqual(sum(len(source["skills"]) for source in lock["sources"]), 28)

    def test_both_agents_receive_skills_without_modifying_own_source(self):
        own = self.root / ".claude/skills/storyboard"
        own.mkdir(parents=True)
        (own / "SKILL.md").write_text("Own storyboard.\n", encoding="utf-8")
        source = {"id": "demo", "repository": "https://github.com/example/demo.git", "commit": "a" * 40,
                  "license": "MIT", "skills": [self.skill]}
        (self.root / "skills.lock.json").write_text(json.dumps({"schema_version": 1, "sources": [source]}), encoding="utf-8")
        with mock.patch.object(skills, "source_checkout", return_value=self.source), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(skills.run(argparse.Namespace(command="install", source=None, target="both"), self.root), 0)
            self.assertEqual(skills.run(argparse.Namespace(command="status", source=None, target="both"), self.root), 0)
        self.assertEqual((self.root / ".agents/skills/storyboard/SKILL.md").read_text(), own.joinpath("SKILL.md").read_text())


@unittest.skipUnless(shutil.which("git"), "Git required")
class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull}
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, env=self.env)
        shutil.copyfile(ROOT / ".gitignore", self.root / ".gitignore")

    def test_private_workspaces_ignored_and_small_examples_allowed(self):
        paths = ["videos/project/final.mp4", "videos.csv", "vendor/repo/.git/config", ".venv/runtime",
                 "marca-army/design.md", "marca-oscar-twitter/data.json", ".env", "nested/.env.production",
                 ".claude/launch.json", ".claude/skills/clipify/SKILL.md", ".agents/skills/clipify/SKILL.md",
                 ".claude/skills/storyboard/.cache/technical.json", "examples/demo/renders/final.mp4",
                 ".work/client/intro/storyboard.json", "projects.local.json",
                 ".claude/skills/storyboard/SKILL.md", "examples/demo/reference.webp", "examples/demo/index.html",
                 ".env.example", "nested/.env.example"]
        for relative in paths:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture", encoding="utf-8")
        result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=self.root,
                                env=self.env, capture_output=True, check=True, text=True)
        self.assertEqual(set(result.stdout.splitlines()), {".gitignore", ".env.example", "nested/.env.example",
                         ".claude/skills/storyboard/SKILL.md", "examples/demo/reference.webp", "examples/demo/index.html"})

    def test_publication_gate_catches_force_added_credentials(self):
        secret = self.root / ".env"
        secret.write_text("FAKE=fixture", encoding="utf-8")
        subprocess.run(["git", "add", "--force", ".env"], cwd=self.root, env=self.env, check=True)
        output = io.StringIO()
        with mock.patch.dict(os.environ, self.env), contextlib.redirect_stdout(output):
            self.assertEqual(doctor.publication_check(self.root), 1)
        self.assertIn("Credential file included: .env", output.getvalue())
        self.assertNotIn("FAKE=fixture", output.getvalue())

    def test_large_example_fails_budget(self):
        asset = self.root / "examples/demo/reference.webp"
        asset.parent.mkdir(parents=True)
        with asset.open("wb") as stream:
            stream.truncate(5 * 1024 * 1024 + 1)
        with mock.patch.dict(os.environ, self.env), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(doctor.publication_check(self.root), 1)


if __name__ == "__main__":
    unittest.main()
