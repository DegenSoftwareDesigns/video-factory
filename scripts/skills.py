#!/usr/bin/env python3
"""Install project skills from exact Git commits; never execute upstream installers.

    python scripts/skills.py install [--source hyperframes] [--target claude|codex|both]
    python scripts/skills.py status [--target claude|codex|both]
    python scripts/skills.py fetch [--source hyperframes]
    python scripts/skills.py digest [--source hyperframes]

An existing installation must match the locked payload. Local changes and .env files
are preserved: mismatches stop installation instead of overwriting a working skill.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
IGNORED = {".git", ".cache", "__pycache__", "node_modules", ".DS_Store"}


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes {root}: {relative}")
    return path


def load_lock(root=ROOT):
    lock = json.loads((root / "skills.lock.json").read_text(encoding="utf-8"))
    if lock.get("schema_version") != 1:
        raise ValueError("Unsupported skills.lock.json schema")
    names, ids = set(), set()
    for source in lock["sources"]:
        if not re.fullmatch(r"[a-z0-9-]+", source["id"]) or source["id"] in ids:
            raise ValueError("Invalid or duplicate source id")
        ids.add(source["id"])
        if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+\.git", source["repository"]):
            raise ValueError("Expected an HTTPS GitHub repository")
        if not re.fullmatch(r"[0-9a-f]{40}", source["commit"]):
            raise ValueError("Every source must pin a full commit SHA")
        for skill in source["skills"]:
            name = skill["name"]
            if not re.fullmatch(r"[a-z0-9-]+", name) or name in names or name == "storyboard":
                raise ValueError(f"Invalid or duplicate external skill: {name}")
            names.add(name)
            if not re.fullmatch(r"[0-9a-f]{64}", skill.get("tree_sha256", "")):
                raise ValueError(f"Expected a SHA-256 payload hash: {name}")
            for relative in [skill["path"], *skill.get("exclude", [])]:
                if PurePosixPath(relative).is_absolute() or ".." in PurePosixPath(relative).parts or "\\" in relative or ":" in relative:
                    raise ValueError(f"Invalid source path: {relative}")
    return lock


def git(*args, cwd=None):
    result = subprocess.run(["git", "-c", f"core.hooksPath={os.devnull}", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def source_checkout(source, root=ROOT):
    """Sparse, detached checkout in an ignored cache; no user checkout is touched."""
    checkout = contained(root, f".cache/skill-sources/{source['id']}/{source['commit']}")
    checkout.parent.mkdir(parents=True, exist_ok=True)
    if not checkout.exists():
        checkout.mkdir()
        git("init", "--quiet", str(checkout))
        git("remote", "add", "origin", source["repository"], cwd=checkout)
        git("config", "remote.origin.promisor", "true", cwd=checkout)
        git("config", "remote.origin.partialclonefilter", "blob:none", cwd=checkout)
    if git("remote", "get-url", "origin", cwd=checkout) != source["repository"]:
        raise ValueError(f"Unexpected remote in {checkout}")
    try:
        git("cat-file", "-e", f"{source['commit']}^{{commit}}", cwd=checkout)
    except subprocess.CalledProcessError:
        print(f"Fetching {source['id']} at {source['commit'][:12]}", flush=True)
        git("-c", "core.autocrlf=false", "fetch", "--quiet", "--depth=1", "--filter=blob:none", "origin", source["commit"], cwd=checkout)
    if git("status", "--porcelain", cwd=checkout):
        raise ValueError(f"Source cache has local changes: {checkout}")
    paths = [skill["path"] for skill in source["skills"]]
    if "." in paths:
        git("sparse-checkout", "disable", cwd=checkout)
    else:
        git("sparse-checkout", "set", "--cone", *paths, cwd=checkout)
    git("-c", "core.autocrlf=false", "checkout", "--quiet", "--detach", source["commit"], cwd=checkout)
    if git("rev-parse", "HEAD", cwd=checkout) != source["commit"]:
        raise ValueError("Checkout did not resolve to the locked commit")
    return checkout


def payload_files(folder, excluded=()):
    for path in sorted(folder.rglob("*"), key=lambda item: item.relative_to(folder).as_posix()):
        relative = path.relative_to(folder)
        if any(part in IGNORED for part in relative.parts):
            continue
        if any(relative == Path(item) or Path(item) in relative.parents for item in excluded):
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example") or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported in skill payloads: {path}")
        if path.is_file():
            yield relative, path


def tree_digest(folder, excluded=()):
    digest = hashlib.sha256()
    for relative, path in payload_files(folder, excluded):
        data = path.read_bytes()
        try:
            data.decode("utf-8")
            if b"\0" not in data:
                data = data.replace(b"\r\n", b"\n")
        except UnicodeDecodeError:
            pass
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def install_payload(source, destination, skill):
    expected = skill["tree_sha256"]
    if not (source / "SKILL.md").is_file() or tree_digest(source, skill.get("exclude", [])) != expected:
        raise ValueError(f"Upstream payload does not match the lock: {skill['name']}")
    if destination.exists():
        if tree_digest(destination, skill.get("exclude", [])) != expected:
            raise ValueError(f"Local changes/version mismatch in {destination}; preserved. Back up and move this folder before reinstalling.")
        print(f"OK      {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Inherit the destination parent's ACL. Windows TemporaryDirectory uses a
    # private ACL which would survive rename and lock other team accounts out.
    staged = destination.parent / f".install-{uuid.uuid4().hex}"
    staged.mkdir()
    try:
        for relative, path in payload_files(source, skill.get("exclude", [])):
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        staged.rename(destination)
    finally:
        if staged.exists():
            contained(destination.parent, staged.name)
            shutil.rmtree(staged)
    print(f"ADDED   {destination}")


def target_directories(target, root=ROOT):
    choices = {"claude": root / ".claude/skills", "codex": root / ".agents/skills"}
    return list(choices.values()) if target == "both" else [choices[target]]


def run(args, root=ROOT):
    lock = load_lock(root)
    sources = [source for source in lock["sources"] if not args.source or source["id"] == args.source]
    if not sources:
        raise ValueError(f"Unknown source: {args.source}")
    failures = 0
    for source in sources:
        checkout = source_checkout(source, root) if args.command in {"fetch", "install", "digest"} else None
        if args.command == "fetch":
            print(checkout)
            continue
        for skill in source["skills"]:
            if args.command == "digest":
                print(f"{skill['name']} {tree_digest(contained(checkout, skill['path']), skill.get('exclude', []))}")
                continue
            for directory in target_directories(args.target, root):
                destination = contained(root, directory.relative_to(root) / skill["name"])
                if args.command == "status":
                    state = "MISSING" if not (destination / "SKILL.md").is_file() else "UNLOCKED" if "tree_sha256" not in skill else "OK" if tree_digest(destination, skill.get("exclude", [])) == skill["tree_sha256"] else "CHANGED"
                    print(f"{state:8} {directory.parent.name}/{skill['name']} ({source['commit'][:12]})")
                    failures += state != "OK"
                else:
                    install_payload(contained(checkout, skill["path"]), destination, skill)
    if args.command in {"install", "status"} and not args.source:
        own = root / ".claude/skills/storyboard"
        # Claude keeps the versioned copy. Codex receives a normal copy, avoiding Windows symlink privileges.
        for directory in target_directories(args.target, root):
            if directory == own.parent:
                continue
            destination = contained(root, directory.relative_to(root) / "storyboard")
            if args.command == "status":
                state = "MISSING" if not (destination / "SKILL.md").is_file() else "OK" if tree_digest(destination) == tree_digest(own) else "CHANGED"
                print(f"{state:8} {directory.parent.name}/storyboard (project-owned)")
                failures += state != "OK"
            else:
                install_payload(own, destination, {"name": "storyboard", "tree_sha256": tree_digest(own)})
    return int(bool(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["status", "fetch", "install", "digest"])
    parser.add_argument("--source", help="Only one source id from skills.lock.json")
    parser.add_argument("--target", choices=["claude", "codex", "both"], default="claude")
    try:
        return run(parser.parse_args())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr.strip(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
