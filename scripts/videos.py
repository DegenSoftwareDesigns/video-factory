#!/usr/bin/env python3
"""Video folders and the videos.csv learning log.

Standalone (default): every video lives in videos/<YYYY-MM-DD>_<name>/ with numbered subfolders.
Client project: --project points to a project that keeps its own folders, references and
deliverables (see docs/client-projects.md and scripts/workspace.py). Either way the production has
one row in videos.csv (project root). The CSV uses ';' and UTF-8 with BOM so it opens cleanly in Excel.

Usage:
  videos.py new "<name>" [--tipo T] [--intencion "..."] [--formato 9:16] [destination]
  videos.py list
  videos.py show <id>
  videos.py paths <id> [destination]   # JSON: role folders, references, records, deliverables
  videos.py check <id> [--stage S] [--shots N] [destination]   # deliverables present on disk
  videos.py update <id> [--estado E] [--nota N] [--intencion ...] [--formato ...] [--duracion S]
                        [--herramientas ...] [--funciono ...] [--mejorar ...] [--tipo ...]
  videos.py learnings [--tipo T]       # past notes to read before starting a new video
  videos.py clean <id> [--yes] [--keep PATH] [--drop FILE] [destination]   # dry run unless --yes; keeps the final video,
                                       # deliverables, final-version images/clips, storyboard.json

destination: --project P [--out DIR] [--role ROLE=PATH] [--refs PATH] [--deliverables FILE];
standalone new accepts --out DIR instead of videos/.
<id> can be the full id or any unique part of it; client productions use <project>/<name>.
"""
import argparse
import csv
import datetime
import json
import sys

import workspace
from workspace import ROOT, VIDEOS, slugify  # noqa: F401  (slugify stays importable from here)

CSV_PATH = ROOT / "videos.csv"
FIELDS = ["id", "fecha", "nombre", "tipo", "intencion", "formato", "duracion_s", "herramientas",
          "estado", "nota", "que_funciono", "que_mejorar", "carpeta", "proyecto"]
ESTADOS = ["en-curso", "terminado", "descartado", "limpiado"]
TIPOS = ["ia-storyboard", "edicion", "shorts", "explainer", "motion-graphics", "otro"]


def read_rows():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def write_rows(rows):
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def matching(rows, key):
    return [r for r in rows if r["id"] == key] or [r for r in rows if key in r["id"]]


def find(rows, key):
    matches = matching(rows, key)
    if len(matches) != 1:
        sys.exit(f"'{key}' coincide con {len(matches)} vídeos: {[r['id'] for r in matches]}")
    return matches[0]


def folder_of(row):
    return ROOT / row["carpeta"] if row.get("carpeta") else VIDEOS / row["id"]


def display(path):
    """Path relative to the workshop when inside it, absolute otherwise."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def destination_overrides(args):
    overrides = workspace.overrides_from(args)
    if not args.project and set(overrides) - {"out"}:
        sys.exit("--role, --refs y --deliverables requieren --project.")
    return overrides


def open_production(args, key):
    """Resolve a production from explicit destination flags, its videos.csv row or videos/."""
    try:
        overrides = destination_overrides(args)
        if args.project:
            return workspace.client(args.project, key, overrides)
        matches = matching(read_rows(), key)
        if len(matches) > 1:
            sys.exit(f"'{key}' coincide con {len(matches)} vídeos: {[r['id'] for r in matches]}")
        if matches:
            row = matches[0]
            if row.get("proyecto"):
                return workspace.client(row["proyecto"], row["id"].split("/", 1)[-1])
            return workspace.standalone(row["id"], folder_of(row))
        folders = [p for p in VIDEOS.glob("*") if p.is_dir() and key in p.name]
        folders = [p for p in folders if p.name == key] or folders
        if len(folders) != 1:
            sys.exit(f"'{key}' coincide con {len(folders)} carpetas en videos/: {[p.name for p in folders]}. "
                     f"Crea el vídeo con scripts/videos.py new \"<nombre>\" o indica --project.")
        return workspace.standalone(folders[0].name, folders[0])
    except workspace.WorkspaceError as exc:
        sys.exit(str(exc))


def folder_size(path):
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def cmd_new(a):
    rows = read_rows()
    try:
        overrides = destination_overrides(a)
        if a.project:
            prod = workspace.client(a.project, a.nombre, overrides)
        else:
            prod = workspace.standalone_new(a.nombre, overrides.get("out"))
    except workspace.WorkspaceError as exc:
        sys.exit(str(exc))
    if any(r["id"] == prod.id for r in rows):
        sys.exit(f"Ya existe en videos.csv: {prod.id}")
    if prod.mode == "standalone":
        if prod.base.exists():
            sys.exit(f"Ya existe: {prod.base}")
        for folder in prod.dirs.values():
            folder.mkdir(parents=True)
        carpeta, proyecto = display(prod.base), ""
    else:
        # The client owns its folders: only the plan folder and the workshop's working folder are created.
        prod.dirs["plan"].mkdir(parents=True, exist_ok=True)
        prod.work.mkdir(parents=True, exist_ok=True)
        prod.save_overrides()
        carpeta, proyecto = str(prod.dirs["plan"]), str(prod.manifest or prod.base)
    today = datetime.date.today().isoformat()
    rows.append({"id": prod.id, "fecha": today, "nombre": a.nombre, "tipo": a.tipo, "intencion": a.intencion,
                 "formato": a.formato, "estado": "en-curso", "carpeta": carpeta, "proyecto": proyecto})
    write_rows(rows)
    print(prod.id)


def cmd_list(a):
    rows = read_rows()
    if not rows:
        print("Sin vídeos todavía.")
        return
    for r in rows:
        folder = folder_of(r)
        size = human(folder_size(folder)) if folder.exists() else "-"
        nota = f"nota {r['nota']}" if r.get("nota") else "sin nota"
        print(f"{r['id']}\t{r['estado']}\t{r['tipo'] or '-'}\t{nota}\t{size}")


def cmd_show(a):
    r = find(read_rows(), a.id)
    for k in FIELDS:
        print(f"{k}: {r.get(k) or ''}")
    folder = folder_of(r)
    if folder.exists() and not r.get("proyecto"):
        for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
            print(f"  {sub.name}/ {human(folder_size(sub))}")


def cmd_paths(a):
    print(json.dumps(open_production(a, a.id).describe(), ensure_ascii=False, indent=2))


def cmd_check(a):
    prod = open_production(a, a.id)
    try:
        report = workspace.check(prod, a.stage, a.shots)
    except workspace.WorkspaceError as exc:
        sys.exit(str(exc))
    if not report:
        print(f"{prod.id}: sin entregables declarados.")
        return 0
    for status, message in report:
        print(f"{status:8} {message}")
    problems = sum(status in ("MISSING", "EXTRA", "SIZE") for status, _ in report)
    print(f"{prod.id}: {'completo' if not problems else f'{problems} pendiente(s)'}")
    return int(bool(problems))


def cmd_update(a):
    rows = read_rows()
    r = find(rows, a.id)
    changes = {"estado": a.estado, "nota": a.nota, "intencion": a.intencion, "formato": a.formato,
               "duracion_s": a.duracion, "herramientas": a.herramientas, "que_funciono": a.funciono,
               "que_mejorar": a.mejorar, "tipo": a.tipo}
    for k, v in changes.items():
        if v is not None:
            r[k] = v
    write_rows(rows)
    print(f"Actualizado {r['id']}")
    if a.estado == "terminado":
        # Finished productions do not keep working files: show the cleanup for the user's approval.
        print()
        print("Limpieza pendiente (simulación):")
        if cleanup_report(open_production(a, r["id"])) is not None:
            print(f"Tras la aprobación del usuario: videos.py clean {r['id']} --yes")


def cmd_learnings(a):
    rows = [r for r in read_rows() if (r.get("que_funciono") or r.get("que_mejorar"))]
    if a.tipo:
        rows = [r for r in rows if r.get("tipo") == a.tipo]
    if not rows:
        print("Aún no hay aprendizajes registrados.")
        return
    for r in rows:
        print(f"- {r['id']} ({r.get('tipo') or '-'}, nota {r.get('nota') or '?'}): {r.get('intencion', '')}")
        if r.get("que_funciono"):
            print(f"    funcionó: {r['que_funciono']}")
        if r.get("que_mejorar"):
            print(f"    mejorar: {r['que_mejorar']}")


VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".mkv"}


def cleanup_report(prod, extra=(), drop=()):
    """Print what cleanup keeps and removes. Returns the files to remove, or None when unsafe."""
    final = prod.dirs["final"]
    declared = "final" in prod.deliverables
    finished = (not any(s == "MISSING" for s, _ in workspace.check(prod, "final")) if declared
                else final.is_dir() and any(p.is_file() for p in final.iterdir()))
    if not finished:
        print(f"{final} no tiene el resultado final: no hay nada que conservar, no limpio nada.")
        return None
    remove, kept, notes = workspace.cleanup_plan(prod, extra)
    # Final videos stay unless named with --drop: older versions and heavy masters.
    dropped = {p.resolve() for p in drop}
    kept = [p for p in kept if p.resolve() not in dropped]
    remove = sorted(set(remove) | set(drop))
    finals = [p for p in kept if within_final(prod, p) and p.suffix.lower() in VIDEO_SUFFIXES]
    if len(finals) > 1:
        notes.append(f"final has {len(finals)} videos; keep only the latest light version per format "
                     "and name older versions and masters with --drop")
    print(f"Se conserva ({human(sum(p.stat().st_size for p in kept))}): vídeo final, entregables, "
          f"imágenes y clips de la versión final, storyboard.json")
    for p in kept:
        print(f"  = {display(p)}")
    for note in notes:
        print(f"AVISO: {note}")
    by_folder = {}
    for p in remove:  # grouped by the first folder level inside each folder the production owns
        root = next(r for r in prod.owned if p == r or r in p.parents)
        rel = p.relative_to(root).parts
        by_folder.setdefault(root / rel[0] if len(rel) > 1 else root, []).append(p)
    for folder, files in sorted(by_folder.items()):
        size = human(sum(f.stat().st_size for f in files))
        names = ", ".join(f.name for f in files[:6]) + (f" y {len(files) - 6} más" if len(files) > 6 else "")
        print(f"Se borra:    {display(folder)}/ {len(files)} archivo(s), {size}: {names}")
    print(f"Espacio liberado: {human(sum(p.stat().st_size for p in remove))}")
    return remove


def within_final(prod, path):
    final = prod.dirs["final"].resolve()
    return final in path.resolve().parents


def cmd_clean(a):
    rows = read_rows()
    prod = open_production(a, a.id)
    extra = [prod.base / k for k in a.keep]
    drop = [prod.base / d for d in a.drop]
    missing = [str(k) for k in extra if not k.exists()] + [str(d) for d in drop if not d.is_file()]
    if missing:
        sys.exit(f"--keep/--drop no existe: {missing}")
    remove = cleanup_report(prod, extra, drop)
    if remove is None:
        return 1
    if not a.yes:
        print("Simulación. Repite con --yes para borrar.")
        return
    workspace.apply_cleanup(prod, remove)
    for r in rows:
        if r["id"] == prod.id:
            r["estado"] = "limpiado"
    write_rows(rows)
    print("Limpieza hecha.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("nombre")
    n.add_argument("--tipo", default="", choices=TIPOS + [""])
    n.add_argument("--intencion", default="")
    n.add_argument("--formato", default="")
    workspace.add_arguments(n)
    sub.add_parser("list")
    s = sub.add_parser("show")
    s.add_argument("id")
    pa = sub.add_parser("paths")
    pa.add_argument("id")
    workspace.add_arguments(pa)
    ch = sub.add_parser("check")
    ch.add_argument("id")
    ch.add_argument("--stage", help="deliverable stage to check, e.g. planning or final")
    ch.add_argument("--shots", type=int, help="number of shots, for per-shot deliverables")
    workspace.add_arguments(ch)
    u = sub.add_parser("update")
    u.add_argument("id")
    workspace.add_arguments(u)
    u.add_argument("--estado", choices=ESTADOS)
    u.add_argument("--nota", type=lambda v: str(max(1, min(10, int(v)))))
    u.add_argument("--tipo", choices=TIPOS)
    for flag in ("--intencion", "--formato", "--duracion", "--herramientas", "--funciono", "--mejorar"):
        u.add_argument(flag)
    l = sub.add_parser("learnings")
    l.add_argument("--tipo", choices=TIPOS)
    c = sub.add_parser("clean")
    c.add_argument("id")
    c.add_argument("--yes", action="store_true")
    c.add_argument("--keep", action="append", default=[], metavar="PATH",
                   help="another final-version file or folder to keep, relative to the production base")
    c.add_argument("--drop", action="append", default=[], metavar="FILE",
                   help="a superseded final version or heavy master to remove, relative to the production base")
    workspace.add_arguments(c)
    a = p.parse_args(argv)
    return {"new": cmd_new, "list": cmd_list, "show": cmd_show, "paths": cmd_paths, "check": cmd_check,
            "update": cmd_update, "learnings": cmd_learnings, "clean": cmd_clean}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
