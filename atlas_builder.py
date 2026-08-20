#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
atlas_builder.py — compone y parchea los atlas de posters de CineVR.

Geometria (set PNG, el que lee el mundo segun atlasInfo):
    hoja PC    2048x2048  ->  16 col x 10 filas, celda 128 x 204.8
    hoja Quest 1024x1024  ->  16 col x 10 filas, celda  64 x 102.4

La posicion de cada titulo la manda el JSON del catalogo: campos `atlas` (A..E) y
`gridIndex` (0..159). NUNCA se reordenan: son append-only. Ver
RFD_Yuta_Atlas_Posters_2026-08-20.md.

Modos:
    verify                 lista las celdas que el JSON declara y estan vacias
    patch  <id> <archivo>  pega UNA celda sobre la hoja existente y no toca el resto
    build  <dir_posters>   compone las hojas enteras desde cero (DESTRUCTIVO: cambia
                           encuadre y color de todo, usar solo si se regenera todo el arte)

Uso:
    python atlas_builder.py verify
    python atlas_builder.py patch movie_603 /ruta/poster.png
    python atlas_builder.py build ./fuentes --dry-run
"""

import argparse
import json
import os
import sys

from PIL import Image, ImageStat

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(ROOT, "JSON_UnityVR.json")
COLS, ROWS = 16, 10
PC_SIZE, QUEST_SIZE = 2048, 2048        # hoja PC cuadrada
QUEST_SHEET = 1024
# Recorte: el arte del atlas es mas cerrado que el poster de ficha 1:2. Se recorta
# desde arriba, que es como esta hecho el set actual (medido sobre A.png).
CROP_ANCHOR = 0.0                        # 0.0 = pegado al borde superior


def cell_box(index, sheet_size):
    cw = sheet_size / COLS
    chh = sheet_size / ROWS
    col, row = index % COLS, index // COLS
    return (int(round(col * cw)), int(round(row * chh)),
            int(round((col + 1) * cw)), int(round((row + 1) * chh)))


def load_catalog():
    with open(CATALOG, encoding="utf-8") as fh:
        return json.load(fh)


def fit_cell(poster, size):
    """Escala el poster al ancho de la celda y recorta el alto sobrante desde CROP_ANCHOR."""
    target_w, target_h = size
    w, h = poster.size
    scale = target_w / w
    new_h = int(round(h * scale))
    img = poster.resize((target_w, new_h), Image.LANCZOS)
    if new_h <= target_h:
        canvas = Image.new("RGB", size, (0, 0, 0))
        canvas.paste(img, (0, (target_h - new_h) // 2))
        return canvas
    top = int(round((new_h - target_h) * CROP_ANCHOR))
    return img.crop((0, top, target_w, top + target_h))


def is_empty(sheet, index, sheet_size):
    x0, y0, x1, y1 = cell_box(index, sheet_size)
    st = ImageStat.Stat(sheet.crop((x0 + 6, y0 + 6, x1 - 6, y1 - 6)).convert("RGB"))
    return max(st.stddev) < 8


def cmd_verify(_args):
    cat = load_catalog()
    sheets = {}
    faltan = []
    for item in cat["movies"]:
        key, idx = item["atlas"], item["gridIndex"]
        path = os.path.join(ROOT, key + ".png")
        if key not in sheets:
            if not os.path.exists(path):
                print("FALTA LA HOJA:", path)
                sheets[key] = None
                continue
            sheets[key] = Image.open(path).convert("RGB")
        if sheets[key] is None:
            continue
        if is_empty(sheets[key], idx, sheets[key].size[0]):
            faltan.append((key, idx, item["id"], item["title"]))
    print("celdas declaradas en el JSON y vacias en el atlas: %d de %d"
          % (len(faltan), len(cat["movies"])))
    for key, idx, mid, title in faltan:
        hero = os.path.join(ROOT, "Backup", mid + ".png")
        print("   %s[%3d]  %-12s  hero:%-6s  %s"
              % (key, idx, mid, "ok" if os.path.exists(hero) else "FALTA", title[:48]))
    return 1 if faltan else 0


def cmd_patch(args):
    cat = load_catalog()
    item = next((m for m in cat["movies"] if m["id"] == args.movie_id), None)
    if item is None:
        sys.exit("ese id no esta en el catalogo: " + args.movie_id)
    key, idx = item["atlas"], item["gridIndex"]
    poster = Image.open(args.poster).convert("RGB")

    for sheet_name, size in ((key + ".png", PC_SIZE), (key + "Quest.png", QUEST_SHEET)):
        path = os.path.join(ROOT, sheet_name)
        if not os.path.exists(path):
            print("no existe, se salta:", sheet_name)
            continue
        # Se trabaja en el modo nativo de la hoja: convertirla entera a RGB volveria
        # opacas las celdas vacias de las hojas RGBA y reescribiria pixeles que no
        # tocan a este parche.
        sheet = Image.open(path)
        if sheet.size[0] != size:
            print("OJO: %s mide %s, se usa su tamano real" % (sheet_name, sheet.size))
        x0, y0, x1, y1 = cell_box(idx, sheet.size[0])
        celda = fit_cell(poster, (x1 - x0, y1 - y0))
        if sheet.mode == "RGBA":
            celda = celda.convert("RGBA")
        sheet.paste(celda, (x0, y0))
        if not args.dry_run:
            sheet.save(path, "PNG", optimize=True)
        print("%s  %s[%d]  celda %dx%d  %s"
              % (sheet_name, key, idx, x1 - x0, y1 - y0,
                 "(dry-run)" if args.dry_run else "escrito"))
    return 0


def cmd_build(args):
    cat = load_catalog()
    by_sheet = {}
    for item in cat["movies"]:
        by_sheet.setdefault(item["atlas"], []).append(item)
    for key, items in sorted(by_sheet.items()):
        for sheet_name, size in ((key + ".png", PC_SIZE), (key + "Quest.png", QUEST_SHEET)):
            sheet = Image.new("RGB", (size, size), (0, 0, 0))
            puestos = 0
            for item in items:
                src = os.path.join(args.sources, item["id"] + ".png")
                if not os.path.exists(src):
                    continue
                x0, y0, x1, y1 = cell_box(item["gridIndex"], size)
                sheet.paste(fit_cell(Image.open(src).convert("RGB"), (x1 - x0, y1 - y0)), (x0, y0))
                puestos += 1
            out = os.path.join(ROOT, sheet_name)
            if not args.dry_run:
                sheet.save(out, "PNG", optimize=True)
            print("%s  %d/%d celdas  %s" % (sheet_name, puestos, len(items),
                                            "(dry-run)" if args.dry_run else "escrito"))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("verify", help="lista celdas declaradas y vacias").set_defaults(fn=cmd_verify)

    p = sub.add_parser("patch", help="pega una sola celda sin tocar el resto de la hoja")
    p.add_argument("movie_id")
    p.add_argument("poster")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_patch)

    p = sub.add_parser("build", help="compone las hojas enteras (DESTRUCTIVO)")
    p.add_argument("sources", help="carpeta con {id}.png")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_build)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
