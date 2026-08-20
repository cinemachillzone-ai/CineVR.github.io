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


# --------------------------------------------------------------------------
# Set JPEG 15x11 — el que lee hoy el prefab del mundo (contentAtlasColumns 15,
# contentAtlasRows 11). Mismo `atlas` + `gridIndex` del JSON que el set PNG: solo
# cambia la rejilla en la que se colocan. 15*11 = 165 huecos y el JSON reparte 160
# por hoja, asi que sobran 5 celdas al final de cada una.
# --------------------------------------------------------------------------
JPEG_COLS, JPEG_ROWS = 15, 11
JPEG_PC = (2040, 2024)          # celda 136 x 184
JPEG_QUEST = (1020, 1012)       # celda  68 x  92
JPEG_QUALITY = 92               # 4:4:4, sin submuestreo de croma


def jpeg_cell_box(index, sheet_size):
    cw = sheet_size[0] // JPEG_COLS
    chh = sheet_size[1] // JPEG_ROWS
    col, row = index % JPEG_COLS, index // JPEG_COLS
    return (col * cw, row * chh, (col + 1) * cw, (row + 1) * chh)


def cmd_jpegset(args):
    cat = load_catalog()
    by_sheet = {}
    for item in cat["movies"]:
        by_sheet.setdefault(item["atlas"], []).append(item)

    for key, items in sorted(by_sheet.items()):
        for suffix, size in ((".jpg", JPEG_PC), ("Quest.jpg", JPEG_QUEST)):
            sheet = Image.new("RGB", size, (0, 0, 0))
            puestos = 0
            for item in items:
                src = os.path.join(ROOT, "Backup", item["id"] + ".png")
                if not os.path.exists(src):
                    print("   sin hero, celda vacia:", item["id"])
                    continue
                if item["gridIndex"] >= JPEG_COLS * JPEG_ROWS:
                    print("   gridIndex fuera de la rejilla 15x11:", item["id"], item["gridIndex"])
                    continue
                x0, y0, x1, y1 = jpeg_cell_box(item["gridIndex"], size)
                with Image.open(src) as poster:
                    sheet.paste(fit_cell(poster.convert("RGB"), (x1 - x0, y1 - y0)), (x0, y0))
                puestos += 1
            out = os.path.join(ROOT, key + suffix)
            if not args.dry_run:
                sheet.save(out, "JPEG", quality=JPEG_QUALITY, subsampling=0, optimize=True)
            print("%-14s %d/%d celdas  %s" % (key + suffix, puestos, len(items),
                                              "(dry-run)" if args.dry_run else "escrito"))

    # AtlasSaga: el arte ya esta bien en PNG y su rejilla 8x8 no cambia entre sets;
    # solo hace falta la copia .jpg porque es la extension que pide el registry.
    for src_name, out_name, side in (("AtlasSaga.png", "AtlasSaga.jpg", 2048),
                                     ("AtlasSaga.png", "AtlasSagaQuest.jpg", 1024),
                                     ("AtlasSaga2.png", "AtlasSaga2.jpg", 2048),
                                     ("AtlasSaga2.png", "AtlasSaga2Quest.jpg", 1024)):
        src = os.path.join(ROOT, src_name)
        if not os.path.exists(src):
            print("no existe, se salta:", src_name)
            continue
        with Image.open(src) as im:
            im = im.convert("RGB")
            if im.size[0] != side:
                im = im.resize((side, side), Image.LANCZOS)
            if not args.dry_run:
                im.save(os.path.join(ROOT, out_name), "JPEG",
                        quality=JPEG_QUALITY, subsampling=0, optimize=True)
        print("%-14s desde %s  %s" % (out_name, src_name,
                                      "(dry-run)" if args.dry_run else "escrito"))
    return 0


def cmd_jpegverify(_args):
    """Comprueba el set JPEG con su propia rejilla: celda declarada == celda con arte."""
    cat = load_catalog()
    sheets, faltan = {}, []
    for item in cat["movies"]:
        key, idx = item["atlas"], item["gridIndex"]
        if key not in sheets:
            path = os.path.join(ROOT, key + ".jpg")
            sheets[key] = Image.open(path).convert("RGB") if os.path.exists(path) else None
            if sheets[key] is None:
                print("FALTA LA HOJA:", key + ".jpg")
        if sheets[key] is None:
            continue
        x0, y0, x1, y1 = jpeg_cell_box(idx, sheets[key].size)
        st = ImageStat.Stat(sheets[key].crop((x0 + 6, y0 + 6, x1 - 6, y1 - 6)))
        if max(st.stddev) < 8:
            faltan.append((key, idx, item["id"], item["title"]))
    print("set JPEG 15x11 — celdas declaradas y vacias: %d de %d"
          % (len(faltan), len(cat["movies"])))
    for f in faltan:
        print("   %s[%3d] %-12s %s" % (f[0], f[1], f[2], f[3][:48]))
    return 1 if faltan else 0


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

    p = sub.add_parser("jpegset", help="regenera el set JPEG 15x11 desde Backup/{id}.png")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_jpegset)

    sub.add_parser("jpegverify", help="verifica el set JPEG con rejilla 15x11") \
        .set_defaults(fn=cmd_jpegverify)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
