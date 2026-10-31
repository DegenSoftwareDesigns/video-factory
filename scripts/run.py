#!/usr/bin/env python3
"""Run a command with the provider keys of whoever the work is for.

Keys come from the client project's .env (manifest "env", default .env at the project root) or,
for standalone work, the workshop's .env (scripts/workspace.py env_file). They override the
inherited environment, so each project's generations are billed to, and counted against, its own
accounts. Only key names are ever printed, never values.

Usage:
  run.py [--project P] --list           # which keys the command would receive
  run.py [--project P] [--] <command> [args...]
"""
import argparse
import os
import shutil
import subprocess
import sys

import workspace


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", default=os.environ.get("VIDEO_FACTORY_PROJECT") or None,
                        help="client project folder, manifest or alias; defaults to $VIDEO_FACTORY_PROJECT, "
                             "without one the workshop's .env is used")
    parser.add_argument("--list", action="store_true", help="print the .env used and its key names, then exit")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command

    try:
        path = workspace.env_file(args.project)
    except workspace.WorkspaceError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    keys = workspace.read_env(path) if path.is_file() else {}
    if args.list:
        print(path if path.is_file() else f"{path} (missing)")
        for name in sorted(keys):
            print(f"  {name}")
        return 0
    if not command:
        parser.error("give a command to run, or --list")
    if not path.is_file():
        print(f"WARNING: no {path}; the command uses the inherited environment, so its usage is not "
              f"billed to this project.", file=sys.stderr)

    executable = shutil.which(command[0]) or command[0]  # PATHEXT lookup for .cmd/.exe on Windows
    return subprocess.run([executable, *command[1:]], env={**os.environ, **keys}).returncode


if __name__ == "__main__":
    sys.exit(main())
