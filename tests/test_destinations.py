"""Offline tests for production destinations: standalone default and client projects."""
import argparse
import contextlib
import importlib.util
import io
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import videos  # noqa: E402
import workspace  # noqa: E402

spec = importlib.util.spec_from_file_location("storyboard", ROOT / ".claude/skills/storyboard/scripts/storyboard.py")
storyboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storyboard)


def png(path, width, height):
    path.parent.mkdir(parents=True, exist_ok=True)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunk = b"IHDR" + ihdr
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(ihdr)) + chunk + struct.pack(">I", zlib.crc32(chunk)))


def run(module, argv):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.main(argv) if module is videos else None
    return code, output.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.tmp = Path(scratch.name)
        self.workshop = self.tmp / "workshop"
        self.workshop.mkdir()
        patches = [
            mock.patch.multiple(workspace, ROOT=self.workshop, VIDEOS=self.workshop / "videos",
                                WORK=self.workshop / ".work", REGISTRY=self.workshop / "projects.local.json"),
            mock.patch.multiple(videos, ROOT=self.workshop, VIDEOS=self.workshop / "videos",
                                CSV_PATH=self.workshop / "videos.csv"),
            mock.patch.object(storyboard, "VIDEOS", self.workshop / "videos"),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.client = self.tmp / "My Client"
        docs = self.client / "Docs"
        docs.mkdir(parents=True)
        self.manifest = {
            "schema_version": 1, "name": "Client", "slug": "client", "root": "..",
            "references": ["Docs/refs"],
            "records": {"state": "Docs/state.json"},
            "layout": {"default": "Videos/Storyboard/{production}", "clips": "Videos/Production/{production}/clips",
                       "final": "Videos"},
            "deliverables": {"planning": {"exclusive": True, "items": [
                {"id": "storyboard", "role": "plan", "glob": "storyboard*.png", "min": 1, "max": 2},
                {"id": "keyframes", "role": "keyframes", "pattern": "shot{nn}.png", "per_shot": True, "size": [1920, 1080]},
                {"id": "prompts", "role": "plan", "glob": "*.txt", "min": 1, "max": 1}]}},
        }
        (docs / "video-factory.json").write_text(json.dumps(self.manifest), encoding="utf-8")


class DestinationTests(Base):
    def test_standalone_default_keeps_numbered_layout(self):
        code, out = run(videos, ["new", "My promo", "--tipo", "edicion", "--formato", "16:9"])
        vid = out.strip()
        folder = self.workshop / "videos" / vid
        self.assertEqual(sorted(p.name for p in folder.iterdir()), sorted(workspace.ROLES.values()))
        row = videos.read_rows()[0]
        self.assertEqual((row["carpeta"], row["proyecto"]), (f"videos/{vid}", ""))
        production = videos.open_production(argparse.Namespace(project=None, out=None, role=[], refs=None,
                                                                deliverables=None), "promo")
        self.assertEqual(production.work, folder / "00_plan")
        self.assertEqual(production.href(folder / "02_keyframes/01.png", production.work), "../02_keyframes/01.png")

    def test_client_layout_alias_and_nested_manifest(self):
        (self.workshop / "projects.local.json").write_text(json.dumps({"client": str(self.client)}), encoding="utf-8")
        production = workspace.client("client", "Intro Teaser")
        self.assertEqual(production.id, "client/intro-teaser")
        self.assertEqual(production.dirs["plan"], self.client / "Videos/Storyboard/intro-teaser")
        self.assertEqual(production.dirs["clips"], self.client / "Videos/Production/intro-teaser/clips")
        self.assertEqual(production.dirs["final"], self.client / "Videos")
        self.assertEqual(production.references, [self.client / "Docs/refs"])
        self.assertEqual(production.work, self.workshop / ".work/client/intro-teaser")

    def test_explicit_values_take_precedence(self):
        saved = workspace.client(self.client, "intro", {"roles": {"audio": "Audio/{production}"}, "references": ["A"]})
        saved.save_overrides()
        later = workspace.client(self.client, "intro", {"roles": {"clips": "Clips"}})
        self.assertEqual(later.dirs["audio"], self.client / "Audio/intro")  # kept from creation
        self.assertEqual(later.dirs["clips"], self.client / "Clips")  # this command
        self.assertEqual(later.references, [self.client / "A"])
        moved = workspace.client(self.client, "other", {"out": "Elsewhere", "roles": {"final": "Out"}})
        self.assertEqual({p for r, p in moved.dirs.items() if r != "final"}, {self.client / "Elsewhere"})
        self.assertEqual(moved.dirs["final"], self.client / "Out")

    def test_deliverable_check_reports_counts_sizes_and_extras(self):
        production = workspace.client(self.client, "intro")
        plan = production.dirs["plan"]
        png(plan / "storyboard.png", 1182, 1330)
        (plan / "animation-prompts.txt").write_text("prompts", encoding="utf-8")
        png(plan / "shot01.png", 1920, 1080)
        png(plan / "shot02.png", 1280, 720)
        report = workspace.check(production, shots=3)
        self.assertIn(("MISSING", "planning/keyframes: 2/3 present; missing shot03.png"), report)
        self.assertIn(("SIZE", "planning/keyframes: shot02.png is 1280x720, expected 1920x1080"), report)
        self.assertEqual([s for s, m in report if "storyboard" in m or "prompts" in m], ["OK", "OK"])
        (plan / "notes.md").write_text("extra", encoding="utf-8")
        (plan / "second.txt").write_text("extra", encoding="utf-8")
        statuses = [s for s, _ in workspace.check(production, shots=2)]
        self.assertEqual(statuses.count("EXTRA"), 2)  # a second TXT and an undeclared file

    def test_client_production_cli_creates_only_plan(self):
        code, out = run(videos, ["new", "intro", "--project", str(self.client), "--tipo", "ia-storyboard"])
        self.assertEqual(out.strip(), "client/intro")
        self.assertEqual([p.relative_to(self.client).as_posix() for p in self.client.rglob("*") if p.is_dir()],
                         ["Docs", "Videos", "Videos/Storyboard", "Videos/Storyboard/intro"])
        row = videos.read_rows()[0]
        self.assertEqual(Path(row["proyecto"]).name, "video-factory.json")
        code, out = run(videos, ["paths", "client/intro"])
        self.assertEqual(json.loads(out)["dirs"]["clips"], str(self.client / "Videos/Production/intro/clips"))
        code, out = run(videos, ["clean", "client/intro", "--yes"])  # nothing final yet: nothing removed
        self.assertEqual(code, 1)
        self.assertTrue((self.client / "Videos/Storyboard/intro").is_dir())
        with self.assertRaises(SystemExit):  # client-only flags need --project
            run(videos, ["new", "x", "--refs", "A"])

    def test_storyboard_working_files_stay_in_workshop(self):
        production = workspace.client(self.client, "intro")
        png(production.dirs["keyframes"] / "shot01.png", 1920, 1080)
        args = dict(project=str(self.client), out=None, role=[], refs=None, deliverables=None)
        with contextlib.redirect_stdout(io.StringIO()):
            storyboard.cmd_init(argparse.Namespace(id="intro", title="Intro", format="16:9", **args))
        source = production.work / "storyboard.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["shots"] = [{"technique": {"name": "Static"}, "keyframe": "Videos/Storyboard/intro/shot01.png"}]
        source.write_text(json.dumps(data), encoding="utf-8")
        before = sorted(self.client.rglob("*"))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            storyboard.cmd_build(argparse.Namespace(id="intro", **args))
        self.assertEqual(sorted(self.client.rglob("*")), before)
        self.assertTrue(output.getvalue().startswith("file:"))
        built = (production.work / "storyboard.data.js").read_text(encoding="utf-8")
        relative = Path(workspace.os.path.relpath(production.dirs["keyframes"] / "shot01.png", production.work)).as_posix()
        self.assertIn(f'"keyframe": "{relative}"', built)


class CleanupTests(Base):
    def write(self, path, text="x"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def storyboard(self, production, shots):
        self.write(production.work / "storyboard.json", json.dumps({"shots": shots}))

    def test_finished_standalone_keeps_final_version_only(self):
        code, out = run(videos, ["new", "promo"])
        production = videos.open_production(argparse.Namespace(project=None, out=None, role=[], refs=None,
                                                                deliverables=None), out.strip())
        folder = production.base
        keep = [self.write(folder / "final/final.mp4"), self.write(folder / "final/cover.png"),
                self.write(folder / "02_keyframes/01.png"), self.write(folder / "03_clips/01.mp4"),
                self.write(folder / "00_plan/borradores/02.mp4")]
        gone = [self.write(folder / "02_keyframes/01_old.png"), self.write(folder / "03_clips/01_take2.mp4"),
                self.write(folder / "01_referencias/hero.png"), self.write(folder / "04_audio/music.wav"),
                self.write(folder / "05_montaje/project/index.html"), self.write(folder / "00_plan/storyboard.html")]
        self.storyboard(production, [{"keyframe": "02_keyframes/01.png", "clip": "03_clips/01.mp4"},
                                     {"clip": "00_plan/borradores/02.mp4"}])
        code, out = run(videos, ["clean", production.id])
        self.assertTrue(all(p.exists() for p in keep + gone))  # dry run
        run(videos, ["clean", production.id, "--yes"])
        self.assertTrue(all(p.exists() for p in keep))
        self.assertFalse(any(p.exists() for p in gone))
        self.assertTrue((folder / "00_plan/storyboard.json").exists())
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["00_plan", "02_keyframes", "03_clips", "final"])
        self.assertEqual(videos.read_rows()[0]["estado"], "limpiado")

    def test_keep_and_drop_adjust_the_final_version(self):
        code, out = run(videos, ["new", "tutorial"])
        vid = out.strip()
        folder = self.workshop / "videos" / vid
        light = self.write(folder / "final/tutorial-v2-x.mp4")
        old = [self.write(folder / "final/tutorial-v1-x.mp4"), self.write(folder / "final/tutorial-v2.mp4")]
        burst = self.write(folder / "05_montaje/burst_approved.mp4")
        render = self.write(folder / "05_montaje/preview.mp4")
        self.storyboard(videos.open_production(argparse.Namespace(project=None, out=None, role=[], refs=None,
                                                                   deliverables=None), vid), [])
        run(videos, ["clean", vid, "--keep", "05_montaje/burst_approved.mp4",
                     "--drop", "final/tutorial-v1-x.mp4", "--drop", "final/tutorial-v2.mp4", "--yes"])
        self.assertTrue(light.exists() and burst.exists())
        self.assertFalse(any(p.exists() for p in old + [render]))

    def test_without_storyboard_every_keyframe_and_clip_is_kept(self):
        production = workspace.standalone("2026-01-01_edit", self.workshop / "videos/2026-01-01_edit")
        clip = self.write(production.dirs["clips"] / "take.mp4")
        self.write(production.dirs["final"] / "final.mp4")
        render = self.write(production.dirs["assembly"] / "render.mp4")
        remove, kept, notes = workspace.cleanup_plan(production)
        self.assertEqual(remove, [render])
        self.assertIn(clip, kept)
        self.assertTrue(notes)

    def test_client_cleanup_touches_only_production_folders(self):
        production = workspace.client(self.client, "intro")
        plan = production.dirs["plan"]
        shared = [self.write(self.client / "Docs/refs/hero.png"), self.write(self.client / "Videos/other.mp4"),
                  self.write(self.client / "Videos/Storyboard/teaser/storyboard.png"),
                  self.write(self.client / "Docs/state.json")]
        keep = [self.write(plan / "storyboard.png"), self.write(plan / "animation-prompts.txt"),
                self.write(plan / "shot01.png"), self.write(self.client / "Videos/Production/intro/clips/01.mp4")]
        gone = [self.write(plan / "storyboard_v1_rejected.png.bak"), self.write(plan / "notes.md"),
                self.write(self.client / "Videos/Production/intro/clips/01_old.mp4"),
                self.write(self.client / "Videos/Production/intro/edit/render.mp4")]
        self.storyboard(production, [{"keyframe": "Videos/Storyboard/intro/shot01.png",
                                      "clip": "Videos/Production/intro/clips/01.mp4"}])
        self.write(production.work / "storyboard.html")
        remove, kept, notes = workspace.cleanup_plan(production)
        workspace.apply_cleanup(production, remove)
        self.assertTrue(all(p.exists() for p in shared + keep))
        self.assertFalse(any(p.exists() for p in gone))
        self.assertFalse((self.client / "Videos/Production/intro/edit").exists())
        self.assertEqual([p.name for p in production.work.iterdir()], ["storyboard.json"])


if __name__ == "__main__":
    unittest.main()
