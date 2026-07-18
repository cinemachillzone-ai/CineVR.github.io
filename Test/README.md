# Test — verificación V3 (lado Yuta) · NO toca nada vivo

Paquete de verificación generado por el **lado Yuta** con **datos reales de este repo**
(los primeros 160 títulos con póster en `Backup/`). Todo vive bajo `Test/`; **no se modificó
ningún archivo vivo** (`JSON_UnityVR.json`, atlases A–G, `Backup/`, etc. quedan intactos).

## Qué hay aquí

### `atlas/` — atlas nuevo 16×10 (PC + Quest)
- `A.png` — **2048×2048, grid 16×10 (160 celdas)** — el nuevo formato.
- `AQuest.png` — **1024×1024** (mitad, para VRAM de Quest).
- `atlas_manifest.json` — `id → posterCell` de cada uno de los 160 (para cross-check).
- Generado desde los pósters actuales de `Backup/` (128×256) → celda `128×204.8` con `fit:cover`.
  **Ojo:** el paso de 16×8 → 16×10 recorta un poco arriba/abajo (celda más baja que el póster 1:2).
  Confirmame si ese recorte te sirve o preferís otra relación de celda.

### `Backup/` — muestra de póster a **256×512**
- 12 pósters de ejemplo re-escalados a 256×512 (hoy están a 128×256).
- ⚠️ **Son ×2 del original** (no hay fuente de más resolución de nuestro lado: la **clave TMDB
  está de tu lado**). Para 256×512 con calidad real hay que **re-descargar de TMDB**. Esto es
  solo para verificar el **formato/resolución de destino**, no la calidad final.

### `json/` — JSON V3 (nuestro sistema de 3 salidas), coherente con el atlas
- `out-api.json` — **con `links`** (id → URL del CDN). Lo lee la API desde GitHub.
- `out-unity.json` — **sin URLs**. Lo lee el Udon. Campos V3 completos (cast/director/recommended/
  saga vacíos: los llena **TMDB**; `saga` es manual).
- `out-quest.json` — = Unity con `\uXXXX` (metadata sin caracteres especiales).
- 160 items, `posterAtlas="A"`, `posterCell=0..159` (coinciden con `atlas/A.png` y el manifest).

### `catalogV3.js`
El normalizador (cero deps) que produce las 3 salidas, por si querés inspeccionarlo o re-correrlo.

## Qué te pido verificar

1. ¿`out-unity.json` calza **exacto** con tu parser (`CinemaCatalogManager`) — nombres/tipos/orden?
2. ¿El atlas `A.png` (16×10) + `AQuest.png` cargan bien en el mundo (PC y Quest)?
3. ¿El **recorte** de celda 16×10 sobre pósters 1:2 es aceptable, o ajustamos la relación?
4. ¿La resolución **256×512** de `Backup/` es la correcta para la vista de detalle?
5. ¿Falta algún campo que el Udon lea?

> Demo de campos V3 "llenos" (saga Marvel, `seasons[]`, kanji) está en el repo **MemoriaIA → `Test/`**.

— **Claude Code (Opus 4.8) — lado Yuta**
