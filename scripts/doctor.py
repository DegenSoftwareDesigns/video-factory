#!/usr/bin/env python3
"""Read-only environment checks and a Git publication inventory (filenames only)."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import skills

ROOT = Path(__file__).resolve().parent.parent


def publication_check(root=ROOT):
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, capture_output=True, check=True,
    )
    files = sorted(set(filter(None, result.stdout.decode("utf-8").split("\0"))))
    problems, total = [], 0
    private_roots = {"videos", "videos.csv", "vendor", ".venv", "node_modules", ".cache", "downloads", "brands", "marca-army", "marca-oscar-twitter"}
    for relative in files:
        path = root / relative
        if not path.is_file():
            continue
        size = path.stat().st_size
        total += size
        if Path(relative).parts[0] in private_roots:
            problems.append(f"Local workspace included: {relative}")
        if relative.startswith(".agents/skills/") or (relative.startswith(".claude/skills/") and not relative.startswith(".claude/skills/storyboard/")):
            problems.append(f"Installed dependency included: {relative}")
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            problems.append(f"Credential file included: {relative}")
        if path.suffix in {".pem", ".key"} or path.name.endswith(".local.json") or relative == ".claude/launch.json":
            problems.append(f"Private configuration included: {relative}")
        if path.suffix.lower() in {".mp4", ".mov", ".webm", ".wav", ".mp3", ".png", ".jpg", ".jpeg", ".webp", ".gif"} and not relative.startswith("examples/"):
            problems.append(f"Media outside examples/: {relative}")
        if size > 5 * 1024 * 1024:
            problems.append(f"Over the workshop's 5 MiB/file budget: {relative}")
    print(f"Git inventory: {len(files)} files, {total / 1024:.1f} KiB")
    for problem in problems:
        print(f"FAIL {problem}")
    return int(bool(problems))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", action="store_true", help="Check tracked + unignored files; requires git init")
    parser.add_argument("--target", choices=["claude", "codex", "both"], default="claude")
    args = parser.parse_args()
    if args.publication:
        try:
            return publication_check()
        except subprocess.CalledProcessError:
            print("Initialize a local Git repository first: git init")
            return 1
    failures = 0
    for name in ("git", "node", "npm", "ffmpeg", "ffprobe"):
        path = shutil.which(name)
        print(f"{'OK' if path else 'MISSING':8} {name}")
        failures += not bool(path)
    if shutil.which("node"):
        version = subprocess.check_output(["node", "--version"], text=True).strip()
        if int(version.lstrip("v").split(".")[0]) < 22:
            print(f"FAIL Node >=22 required, found {version}")
            failures += 1
    print(f"Python: {sys.version.split()[0]}")
    if sys.version_info < (3, 12):
        print("FAIL Python >=3.12 required; Python 3.12 is the tested profile")
        failures += 1
    cli = ROOT / "node_modules/hyperframes/package.json"
    expected = json.loads((ROOT / "package.json").read_text())["devDependencies"]["hyperframes"]
    actual = json.loads(cli.read_text())["version"] if cli.is_file() else None
    print(f"{'OK' if actual == expected else 'MISSING':8} HyperFrames CLI {expected} (npm ci)")
    failures += actual != expected
    failures += skills.run(argparse.Namespace(command="status", source=None, target=args.target))
    print(f"{'OK' if shutil.which('deno') else 'OPTIONAL':8} Deno (YouTube downloads)")
    print(f"{'OK' if shutil.which('heygen') else 'OPTIONAL':8} HeyGen CLI (catalogue/voice; each user signs in)")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
