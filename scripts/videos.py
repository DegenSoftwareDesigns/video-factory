#!/usr/bin/env python3
"""Video folders and the videos.csv learning log.

Every video lives in videos/<YYYY-MM-DD>_<name>/ with numbered subfolders, and has one row in
videos.csv (project root). The CSV uses ';' and UTF-8 with BOM so it opens cleanly in Excel.

Usage:
  videos.py new "<name>" [--tipo T] [--intencion "..."] [--formato 9:16]
  videos.py list
  videos.py show <id>
  videos.py update <id> [--estado E] [--nota N] [--intencion ...] [--formato ...] [--duracion S]
                        [--herramientas ...] [--funciono ...] [--mejorar ...] [--tipo ...]
  videos.py learnings [--tipo T]       # past notes to read before starting a new video
  videos.py clean <id> [--yes]         # dry run unless --yes: keeps only final/

<id> can be the full folder name or any unique part of it.
"""
import argparse
import csv
import datetime
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS = ROOT / "videos"
CSV_PATH = ROOT / "videos.csv"
FIELDS = ["id", "fecha", "nombre", "tipo", "intencion", "formato", "duracion_s", "herramientas",
          "estado", "nota", "que_funciono", "que_mejorar", "carpeta"]
SUBFOLDERS = ["00_plan", "01_referencias", "02_keyframes", "03_clips", "04_audio", "05_montaje", "final"]
ESTADOS = ["en-curso", "terminado", "descartado", "limpiado"]
TIPOS = ["ia-storyboard", "edicion", "shorts", "explainer", "motion-graphics", "otro"]


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


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


def find(rows, key):
    matches = [r for r in rows if r["id"] == key] or [r for r in rows if key in r["id"]]
    if len(matches) != 1:
        sys.exit(f"'{key}' coincide con {len(matches)} vídeos: {[r['id'] for r in matches]}")
    return matches[0]


def folder_size(path):
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def cmd_new(a):
    slug = slugify(a.nombre)
    if not slug:
        sys.exit("El nombre no puede quedar vacío.")
    today = datetime.date.today().isoformat()
    vid = f"{today}_{slug}"
    folder = VIDEOS / vid
    if folder.exists():
        sys.exit(f"Ya existe: {folder}")
    for sub in SUBFOLDERS:
        (folder / sub).mkdir(parents=True)
    rows = read_rows()
    rows.append({"id": vid, "fecha": today, "nombre": a.nombre, "tipo": a.tipo, "intencion": a.intencion,
                 "formato": a.formato, "estado": "en-curso", "carpeta": f"videos/{vid}"})
    write_rows(rows)
    print(vid)


def cmd_list(a):
    rows = read_rows()
    if not rows:
        print("Sin vídeos todavía.")
        return
    for r in rows:
        folder = VIDEOS / r["id"]
        size = human(folder_size(folder)) if folder.exists() else "-"
        nota = f"nota {r['nota']}" if r.get("nota") else "sin nota"
        print(f"{r['id']}\t{r['estado']}\t{r['tipo'] or '-'}\t{nota}\t{size}")


def cmd_show(a):
    r = find(read_rows(), a.id)
    for k in FIELDS:
        print(f"{k}: {r.get(k, '')}")
    folder = VIDEOS / r["id"]
    if folder.exists():
        for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
            print(f"  {sub.name}/ {human(folder_size(sub))}")


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


def cmd_clean(a):
    rows = read_rows()
    r = find(rows, a.id)
    folder = VIDEOS / r["id"]
    final = folder / "final"
    if not final.exists() or not any(final.iterdir()):
        sys.exit(f"{final} está vacía: no hay resultado que conservar, no limpio nada.")
    # The plan is a few KB and records the decisions, so it is kept next to the result.
    plan = folder / "00_plan" / "storyboard.json"
    targets = [p for p in folder.iterdir() if p.name != "final"]
    freed = sum(folder_size(p) if p.is_dir() else p.stat().st_size for p in targets)
    print(f"Se conserva: final/ ({human(folder_size(final))})" + (" + storyboard.json" if plan.exists() else ""))
    for p in targets:
        print(f"Se borra:    {p.name}{'/' if p.is_dir() else ''} ({human(folder_size(p) if p.is_dir() else p.stat().st_size)})")
    print(f"Espacio liberado: {human(freed)}")
    if not a.yes:
        print("Simulación. Repite con --yes para borrar.")
        return
    if plan.exists():
        shutil.copy2(plan, final / "storyboard.json")
    for p in targets:
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    r["estado"] = "limpiado"
    write_rows(rows)
    print("Limpieza hecha.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("nombre")
    n.add_argument("--tipo", default="", choices=TIPOS + [""])
    n.add_argument("--intencion", default="")
    n.add_argument("--formato", default="")
    sub.add_parser("list")
    s = sub.add_parser("show")
    s.add_argument("id")
    u = sub.add_parser("update")
    u.add_argument("id")
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
    a = p.parse_args()
    {"new": cmd_new, "list": cmd_list, "show": cmd_show, "update": cmd_update,
     "learnings": cmd_learnings, "clean": cmd_clean}[a.cmd](a)


if __name__ == "__main__":
    main()
