#!/usr/bin/env python3
"""Build the visual storyboard of a video in its working folder.

Standalone productions keep it in videos/<id>/00_plan/ (create the folder first with
scripts/videos.py new "<name>"). Client productions (--project) keep these working files in the
workshop's ignored .work/<project>/<name>/ folder, so the client folder only receives its
declared deliverables.

Usage:
  storyboard.py init <id> --title "Title" [--format 16:9] [--project P]
      Creates storyboard.json in the production's working folder.
  storyboard.py build <id> [--project P]
      Resolves every Melies technique ref in storyboard.json (name, url, preview video, still),
      writes storyboard.data.js and refreshes storyboard.html from the skill template.
      Prints the preview URL (preview server for videos/, file URL otherwise) and the file path.

storyboard.json is the source of truth. Shots reference techniques as "<category>/<slug>",
e.g. "camera-movement/dolly-in" (find them with melies.py search/list). "keyframe" and "clip"
paths are relative to the production base (the video folder, or the client project root), e.g.
"02_keyframes/01.png", "Videos/Storyboard/intro/shot01.png", or full http(s) URLs (stock
previews). An optional per-shot "clip_label" replaces the "Clip generado" caption,
e.g. "Draft with real footage" or "Stock preview".
<id> can be the full folder name or any unique part of it; see scripts/videos.py paths.
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melies  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "templates" / "storyboard.html"
SHOT_CACHE = SKILL / ".cache" / "shots.json"
ROOT = SKILL.parent.parent.parent  # .claude/skills/storyboard -> project root
sys.path.insert(0, str(ROOT / "scripts"))
import videos  # noqa: E402
import workspace  # noqa: E402

VIDEOS = workspace.VIDEOS
SERVER = "http://localhost:8765"  # "storyboards" preview server in .claude/launch.json serves videos/
STATUSES = {"propuesto", "aprobado", "cambiar"}


def load_cache():
    if SHOT_CACHE.exists():
        return json.loads(SHOT_CACHE.read_text(encoding="utf-8"))
    return {}


def resolve(ref, cache):
    if ref not in cache:
        info = melies.shot(ref)
        cache[ref] = {k: info.get(k) for k in ("name", "category", "slug", "url", "preview", "still")}
    return dict(cache[ref])


def cmd_init(args):
    production = videos.open_production(args, args.id)
    if production.mode == "standalone" and not production.base.is_dir():
        sys.exit(f"No existe {production.base}. Crea el vídeo con scripts/videos.py new \"<nombre>\".")
    plan = production.work
    plan.mkdir(parents=True, exist_ok=True)
    if (plan / "storyboard.json").exists():
        sys.exit(f"Ya existe: {plan / 'storyboard.json'}")
    skeleton = {
        "title": args.title,
        "format": args.format,
        "phase": 1,
        "version": 1,
        "idea": "",
        "look": "",
        "notes": "",
        "shots": [],
    }
    (plan / "storyboard.json").write_text(json.dumps(skeleton, ensure_ascii=False, indent=2), encoding="utf-8")
    print(plan / "storyboard.json")


def cmd_build(args):
    production = videos.open_production(args, args.id)
    folder, plan = production.base, production.work
    src = plan / "storyboard.json"
    if not src.exists():
        sys.exit(f"No existe {src}. Créalo con: storyboard.py init {production.name} --title ...")
    data = json.loads(src.read_text(encoding="utf-8"))
    cache = load_cache()
    warnings = []

    for i, shot in enumerate(data.get("shots", []), 1):
        ref = shot.get("technique")
        if isinstance(ref, str):
            try:
                shot["technique"] = resolve(ref, cache)
            except Exception as exc:  # unknown slug or network error: keep the ref visible
                warnings.append(f"plano {i}: no se pudo resolver '{ref}' ({exc})")
                shot["technique"] = {"name": ref, "url": f"{melies.BASE}/{ref}"}
        for alt in shot.get("alternatives", []):
            aref = alt.get("technique")
            if isinstance(aref, str):
                try:
                    alt.update(resolve(aref, cache))
                except Exception as exc:
                    warnings.append(f"plano {i}: alternativa '{aref}' no resuelta ({exc})")
                    alt["name"] = aref
        if shot.get("status", "propuesto") not in STATUSES:
            warnings.append(f"plano {i}: status '{shot.get('status')}' no es {sorted(STATUSES)}")
        for key in ("keyframe", "clip"):
            if shot.get(key):
                if shot[key].startswith(("http://", "https://")):  # e.g. a stock preview, played from its CDN
                    continue
                target = folder / shot[key]
                if not target.exists():
                    warnings.append(f"plano {i}: falta el archivo {shot[key]}")
                shot[key] = production.href(target, plan)  # the page lives in the working folder

    SHOT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SHOT_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    data["updated"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    (plan / "storyboard.data.js").write_text(f"window.STORYBOARD = {payload};\n", encoding="utf-8")
    shutil.copyfile(TEMPLATE, plan / "storyboard.html")

    for w in warnings:
        print("AVISO:", w)
    page = plan / "storyboard.html"
    try:
        print(f"{SERVER}/{plan.relative_to(VIDEOS).as_posix()}/storyboard.html")
    except ValueError:  # outside videos/: open the file directly, it needs no server
        print(page.resolve().as_uri())
    print(page)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("id")
    p_init.add_argument("--title", required=True)
    p_init.add_argument("--format", default="16:9")
    workspace.add_arguments(p_init)
    p_build = sub.add_parser("build")
    p_build.add_argument("id")
    workspace.add_arguments(p_build)
    args = parser.parse_args()
    {"init": cmd_init, "build": cmd_build}[args.cmd](args)


if __name__ == "__main__":
    main()
