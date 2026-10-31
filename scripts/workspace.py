#!/usr/bin/env python3
"""Where a production's files live: the standalone layout or a client project's own folders.

The methodology names roles (plan, references, keyframes, clips, audio, assembly, final); this
module maps each role to a folder. Two modes:

- Standalone (default): videos/<YYYY-MM-DD>_<name>/ with numbered subfolders, as before.
- Client project: a video-factory.json manifest inside the client project maps roles to its own
  folders and declares references, context documents, record files and deliverables.

Precedence, highest first: values given for this command (--out, --role, --refs, --deliverables),
values given when the production was created, the client manifest, the standalone defaults.
--out moves every role that is not named with --role. Relative paths resolve against the client
project root. Working files that are not deliverables (storyboard.json, the HTML board) stay in
the workshop's ignored .work/ folder for client productions.

Cleanup of a finished production keeps the final deliverables, the declared deliverables, the
keyframe images and clips that storyboard.json uses in the final version, and storyboard.json
itself. Everything else inside folders the production owns is removed: discarded or replaced takes,
drafts, audio, assembly projects and intermediate renders. A production owns its standalone folder,
or in a client project only the folders named after it ({production} in the layout) and its
working folder; shared client folders, references and the final folder are never touched.
"""
import datetime
import json
import os
import re
import struct
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS = ROOT / "videos"
WORK = ROOT / ".work"
REGISTRY = ROOT / "projects.local.json"
MANIFEST_NAME = "video-factory.json"
ROLES = {"plan": "00_plan", "references": "01_referencias", "keyframes": "02_keyframes", "clips": "03_clips",
         "audio": "04_audio", "assembly": "05_montaje", "final": "final"}
STANDALONE_DELIVERABLES = {"final": {"items": [
    {"id": "video", "role": "final", "glob": "*.mp4", "min": 1, "description": "final render"}]}}


class WorkspaceError(Exception):
    pass


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


@dataclass
class Production:
    id: str
    name: str
    mode: str  # "standalone" or "client"
    base: Path  # storyboard.json keyframe/clip paths are relative to this folder
    work: Path  # storyboard.json and the HTML board
    dirs: dict
    references: list = field(default_factory=list)
    context: dict = field(default_factory=dict)
    records: dict = field(default_factory=dict)
    deliverables: dict = field(default_factory=dict)
    project: str = ""
    manifest: Path = None
    overrides: dict = field(default_factory=dict)
    owned: list = field(default_factory=list)  # folders cleanup may empty

    def href(self, target, start):
        """Link from one folder to a file, relative when both share a drive."""
        try:
            return Path(os.path.relpath(target, start)).as_posix()
        except ValueError:
            return Path(target).resolve().as_uri()

    def describe(self):
        return {
            "id": self.id, "name": self.name, "mode": self.mode, "project": self.project,
            "manifest": str(self.manifest) if self.manifest else None, "base": str(self.base),
            "work": str(self.work), "dirs": {role: str(path) for role, path in self.dirs.items()},
            "references": [str(p) for p in self.references],
            "context": {k: str(v) for k, v in self.context.items()},
            "records": {k: str(v) for k, v in self.records.items()},
            "deliverables": self.deliverables,
        }

    def save_overrides(self):
        """Keep the destination chosen at creation so later commands need not repeat the flags."""
        if self.mode != "client" or not self.overrides:
            return
        self.work.mkdir(parents=True, exist_ok=True)
        record = {"project": str(self.manifest or self.base), "overrides": self.overrides}
        (self.work / "production.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def add_arguments(parser):
    group = parser.add_argument_group("destination")
    group.add_argument("--project", default=os.environ.get("VIDEO_FACTORY_PROJECT") or None,
                       help="client project folder, its video-factory.json, or an alias in projects.local.json; "
                            "defaults to $VIDEO_FACTORY_PROJECT, which the plugin's vf commands set to the open project")
    group.add_argument("--out", help="output folder for this production; overrides the manifest and videos/")
    group.add_argument("--role", action="append", default=[], metavar="ROLE=PATH",
                       help=f"folder for one role ({', '.join(ROLES)}); repeatable")
    group.add_argument("--refs", action="append", metavar="PATH", help="reference file or folder; replaces the manifest list")
    group.add_argument("--deliverables", metavar="JSON_FILE", help="deliverables specification; replaces the manifest's")


def overrides_from(args):
    overrides = {}
    if getattr(args, "out", None):
        overrides["out"] = args.out
    roles = {}
    for item in getattr(args, "role", None) or []:
        role, sep, path = item.partition("=")
        if not sep or role not in ROLES or not path:
            raise WorkspaceError(f"--role expects ROLE=PATH with ROLE in {list(ROLES)}: {item}")
        roles[role] = path
    if roles:
        overrides["roles"] = roles
    if getattr(args, "refs", None):
        overrides["references"] = args.refs
    if getattr(args, "deliverables", None):
        overrides["deliverables"] = json.loads(Path(args.deliverables).read_text(encoding="utf-8"))
    return overrides


def merge(lower, higher):
    merged = {**lower, **higher}
    if "roles" in lower or "roles" in higher:
        merged["roles"] = {**lower.get("roles", {}), **higher.get("roles", {})}
    return merged


def locate(project):
    """Return the manifest file, or the project folder when it has none."""
    candidate = Path(project).expanduser()
    if not candidate.exists():
        aliases = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.is_file() else {}
        if project not in aliases:
            raise WorkspaceError(f"Project not found: '{project}' is neither a path nor an alias in {REGISTRY.name}")
        candidate = Path(aliases[project]).expanduser()
        if not candidate.exists():
            raise WorkspaceError(f"Alias '{project}' points to a missing path: {candidate}")
    if candidate.is_file():
        return candidate
    if (candidate / MANIFEST_NAME).is_file():
        return candidate / MANIFEST_NAME
    nested = sorted(candidate.glob(f"*/{MANIFEST_NAME}"))
    if len(nested) > 1:
        raise WorkspaceError(f"Several manifests in {candidate}: {[str(p) for p in nested]}; pass one with --project")
    return nested[0] if nested else candidate


def load_project(project):
    location = locate(project)
    if location.is_dir():
        return location, {}, None
    manifest = json.loads(location.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise WorkspaceError(f"{location}: unsupported schema_version {manifest.get('schema_version')!r}")
    return (location.parent / manifest.get("root", ".")).resolve(), manifest, location.resolve()


def client(project, name, overrides=None):
    root, manifest, manifest_path = load_project(project)
    slug = slugify(manifest.get("slug") or manifest.get("name") or root.name)
    production = slugify(name.replace("\\", "/").rsplit("/", 1)[-1])  # accepts the "<project>/<name>" id too
    if not production:
        raise WorkspaceError("The production name cannot be empty.")
    work = WORK / slug / production
    stored = work / "production.json"
    saved = json.loads(stored.read_text(encoding="utf-8")).get("overrides", {}) if stored.is_file() else {}
    effective = merge(saved, overrides or {})

    layout = dict(manifest.get("layout", {}))
    default = layout.pop("default", None)
    if "out" in effective:
        default, layout = effective["out"], {}
    if default is None:
        raise WorkspaceError(f"{manifest_path or root}: no layout.default in the manifest; pass --out")
    layout.update(effective.get("roles", {}))

    def place(template):
        return root / template.replace("{production}", production)

    def owned_root(template):
        parts = Path(template).parts
        for i, part in enumerate(parts):
            if "{production}" in part:
                return place(str(Path(*parts[:i + 1])))
        return None

    templates = {role: layout.get(role, default) for role in ROLES}
    owned = {owned_root(t) for t in templates.values()} - {None}

    return Production(
        id=f"{slug}/{production}", name=production, mode="client", base=root, work=work,
        dirs={role: place(t) for role, t in templates.items()},
        references=[place(p) for p in effective.get("references", manifest.get("references", []))],
        context={k: place(v) for k, v in manifest.get("context", {}).items()},
        records={k: place(v) for k, v in manifest.get("records", {}).items()},
        deliverables=effective.get("deliverables", manifest.get("deliverables", {})),
        project=manifest.get("name", root.name), manifest=manifest_path, overrides=effective,
        owned=sorted(owned) + [work],
    )


def standalone(vid, folder):
    dirs = {role: folder / sub for role, sub in ROLES.items()}
    return Production(id=vid, name=vid, mode="standalone", base=folder, work=dirs["plan"], dirs=dirs,
                      references=[dirs["references"]], deliverables=STANDALONE_DELIVERABLES, owned=[folder])


def standalone_new(name, out=None):
    slug = slugify(name)
    if not slug:
        raise WorkspaceError("The production name cannot be empty.")
    vid = f"{datetime.date.today().isoformat()}_{slug}"
    return standalone(vid, (ROOT / out / vid) if out else VIDEOS / vid)


def image_size(path):
    """(width, height) for PNG and JPEG files, None for other formats."""
    data = Path(path).read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            i += 2 + length
    return None


def pattern_regex(pattern):
    return re.compile(re.escape(pattern).replace(r"\{nn\}", r"\d{2}") + "$")


def item_files(production, item):
    """Files on disk that match one deliverable item."""
    folder = production.dirs[item["role"]]
    if not folder.is_dir():
        return []
    if "pattern" in item:
        regex = pattern_regex(item["pattern"])
        return sorted(p for p in folder.glob("*") if p.is_file() and regex.match(p.name))
    return sorted(p for p in folder.glob(item["glob"]) if p.is_file())


def check(production, stage=None, shots=None):
    """Compare files on disk with the declared deliverables. Returns [(status, message)]."""
    stages = production.deliverables
    if stage:
        if stage not in stages:
            raise WorkspaceError(f"No deliverables for stage '{stage}'; declared: {list(stages)}")
        stages = {stage: stages[stage]}
    report = []
    for name, spec in stages.items():
        claimed, folders = set(), set()
        for item in spec.get("items", []):
            folder = production.dirs[item["role"]]
            folders.add(folder)
            label = f"{name}/{item['id']}"
            present = item_files(production, item)
            if "pattern" in item:
                count = shots if item.get("per_shot") else item.get("count")
                if count is None:
                    report.append(("INFO", f"{label}: {len(present)} found; pass --shots to check the full set"))
                else:
                    expected = [folder / item["pattern"].format(nn=f"{i:02d}") for i in range(1, count + 1)]
                    missing = [p.name for p in expected if not p.is_file()]
                    found = count - len(missing)
                    report.append(("OK" if not missing else "MISSING",
                                   f"{label}: {found}/{count} present" + (f"; missing {', '.join(missing)}" if missing else "")))
            else:
                low, high = item.get("min", 1), item.get("max")
                ok = len(present) >= low and (high is None or len(present) <= high)
                bounds = f"{low}-{high}" if high is not None else f"at least {low}"
                report.append(("OK" if ok else ("MISSING" if len(present) < low else "EXTRA"),
                               f"{label}: {len(present)} file(s), expected {bounds} ({item['glob']} in {folder})"))
            claimed.update(present)
            if item.get("size"):
                for p in present:
                    size = image_size(p)
                    if size is None:
                        report.append(("INFO", f"{label}: size of {p.name} not verified"))
                    elif list(size) != list(item["size"]):
                        report.append(("SIZE", f"{label}: {p.name} is {size[0]}x{size[1]}, expected {item['size'][0]}x{item['size'][1]}"))
        if spec.get("exclusive"):
            for folder in sorted(folders):
                if folder.is_dir():
                    for p in sorted(folder.iterdir()):
                        if p.is_file() and not p.name.startswith(".") and p not in claimed:
                            report.append(("EXTRA", f"{name}: {p} is not a declared deliverable"))
    return report


def within(path, folder):
    return path == folder or folder in path.parents


def storyboards(production):
    """storyboard.json plus named variants such as intro_storyboard.json."""
    return sorted(production.work.glob("*storyboard.json")) if production.work.is_dir() else []


def used_media(production):
    """Keyframes and clips that the storyboards use, or None without a storyboard."""
    sources = storyboards(production)
    if not sources:
        return None
    used = set()
    for source in sources:
        for shot in json.loads(source.read_text(encoding="utf-8")).get("shots", []):
            for key in ("keyframe", "clip"):
                value = shot.get(key)
                if value and not value.startswith(("http://", "https://")):
                    used.add((production.base / value).resolve())
    return used


def cleanup_plan(production, extra=()):
    """(files to remove, files kept, notes) for a finished production.

    extra: further files or folders of the final version to keep, such as a clip
    assembled outside the storyboard.
    """
    keep = {p.resolve() for p in storyboards(production)}
    for spec in production.deliverables.values():
        keep.update(p.resolve() for item in spec.get("items", []) for p in item_files(production, item))
    final = production.dirs["final"].resolve()
    protected = [*production.context.values(), *production.records.values(), *extra]
    if production.mode == "client":  # client references are inputs; standalone ones were made for this video
        protected += production.references
    if any(final in root.resolve().parents for root in production.owned):
        # A shared final folder above the production's folders: keep only the files directly in it.
        keep.update(p.resolve() for p in final.glob("*") if p.is_file())
    else:
        protected.append(final)
    notes = []
    used = used_media(production)
    if used is None:
        notes.append("no storyboard.json: every keyframe and clip is kept")
        protected += [production.dirs["keyframes"], production.dirs["clips"]]
    else:
        keep.update(used)
    protected = [p.resolve() for p in protected]
    remove, kept = set(), set()
    for root in production.owned:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            real = p.resolve()
            (kept if real in keep or any(within(real, d) for d in protected) else remove).add(p)
    return sorted(remove), sorted(kept), notes


def apply_cleanup(production, remove):
    for p in remove:
        p.unlink()
    for root in production.owned:
        if not root.is_dir():
            continue
        for folder in sorted((d for d in root.rglob("*") if d.is_dir()), key=lambda d: len(d.parts), reverse=True):
            if not any(folder.iterdir()):
                folder.rmdir()
        if root != production.base and not any(root.iterdir()):
            root.rmdir()
