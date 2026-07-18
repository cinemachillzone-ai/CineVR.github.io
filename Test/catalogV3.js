// catalog-v3/catalogV3.js — normalizador JSON V3 (CommonJS, cero deps, PURO).
//
// CONTRATO REAL extraído del parser (CinemaCatalogManager.ParseCatalog), no de los
// docs. Donde docs y código no coincidían, MANDA el código. Case-sensitive.
// Fuente: MemoriaIA/Intercomunicador/Para_Yuta/2026-07-17_contrato-json-v3-y-almacenamiento.md
//
// Se conecta al commitCatalog VIVO del NAS: pasar cada item por normalizeItemV3()
// antes de escribir. Aquí NO se toca disco ni red.
//
// OJO — el Udon NO lee: `poster`, `mainGenre`, `links`, `master_url`, `videoUrl`.
// El idioma NO va en el JSON (el mundo arma {API}/{id}/{idioma}?key=… en runtime).
// Por eso este normalizador NO genera esos campos.

// ---------- helpers ----------
function asArray(v) {
  if (Array.isArray(v)) return v.filter(x => x != null).map(String);
  if (typeof v === 'string' && v.trim()) return v.split(',').map(s => s.trim()).filter(Boolean);
  return [];
}
function asInt(v, def) { const n = parseInt(v, 10); return Number.isFinite(n) ? n : def; }
function asStr(v, def = '') { return v == null ? def : String(v); }
function asBool(v, def = true) { return v == null ? def : Boolean(v); }

function normType(t) {
  const s = String(t ?? 'movie').toLowerCase();
  if (s === 'series' || s === 'serie') return 'series';
  return 'movie'; // cualquier otro valor → movie (como el parser)
}

// ---------- seasons ----------
function normEpisode(ep = {}) {
  return {
    id: asStr(ep.id),
    title: asStr(ep.title, 'Sin título'),
    slotId: asStr(ep.slotId ?? ep.slot ?? '')   // lo que SE REPRODUCE (ep_001); sin él no reproduce
  };
}
function normSeasons(item) {
  // Preferencia: seasons[]. Fallback: episodes[] plano = 1 temporada.
  if (Array.isArray(item.seasons)) {
    return item.seasons.map((s, i) => ({
      season: asInt(s.season, i + 1),
      episodes: Array.isArray(s.episodes) ? s.episodes.map(normEpisode) : []
    }));
  }
  if (Array.isArray(item.episodes)) {
    return [{ season: 1, episodes: item.episodes.map(normEpisode) }];
  }
  return [];
}

// ---------- item ----------
/** COPIA del item con la forma V3 real. No muta. Idempotente. */
function normalizeItemV3(item = {}) {
  const type = normType(item.type ?? item.contentType);
  const out = {
    id: asStr(item.id),
    title: asStr(item.title, 'Sin título'),
    description: asStr(item.description),
    type,
    section: asStr(item.section, 'catalog').toLowerCase(),
    addedAt: asStr(item.addedAt ?? item.createdAt),
    year: asInt(item.year, 0),
    releaseDate: asStr(item.releaseDate),
    duration: asStr(item.duration),                 // STRING (texto), no segundos
    rating: asStr(item.rating),
    genres: asArray(item.genres),
    languages: asArray(item.languages ?? item.language),
    quality: asStr(item.quality ?? item.calidad, 'None'),
    enabled: asBool(item.enabled, true),
    cast: asArray(item.cast ?? item.actors),
    director: asStr(item.director),
    recommended: asStr(item.recommended ?? item.score), // STRING, no número
    saga: asStr(item.saga),                          // "" si ausente/null
    posterAtlas: asStr(item.posterAtlas ?? item.atlas),
    posterCell: asInt(item.posterCell ?? item.gridIndex, -1)
  };
  // hero* opcionales → fallback al póster.
  out.heroAtlas = item.heroAtlas != null ? asStr(item.heroAtlas) : out.posterAtlas;
  out.heroCell = item.heroCell != null ? asInt(item.heroCell, out.posterCell) : out.posterCell;
  // seasons solo para series.
  if (type === 'series') out.seasons = normSeasons(item);
  return out;
}

// ---------- sagas[] (tabla raíz) ----------
function normalizeSaga(s = {}) {
  return { name: asStr(s.name), cell: asInt(s.cell, -1) };  // cell en AtlasSaga 8×8 (0–63)
}

// ---------- validación ----------
const ID_RE = /^(movie|series|ep)_\d{3,}$/;
function validateV3(item = {}) {
  const errors = [];
  if (!item.id) errors.push('falta id (llave inmutable)');
  else if (!ID_RE.test(item.id)) errors.push(`id "${item.id}" sin prefijo válido (movie_/series_/ep_ + ≥3 dígitos)`);
  if (typeof item.recommended !== 'string') errors.push('recommended debe ser string');
  if (item.type === 'series') {
    if (!Array.isArray(item.seasons) || item.seasons.length === 0) errors.push('serie sin seasons[]');
    else for (const s of item.seasons)
      for (const ep of (s.episodes || []))
        if (!ep.slotId) errors.push(`episodio "${ep.id || ep.title}" sin slotId (no se reproduce)`);
  }
  const cell = item.posterCell;
  if (cell != null && cell !== -1 && (cell < 0 || cell > 159)) errors.push(`posterCell ${cell} fuera de 0–159`);
  return { ok: errors.length === 0, errors };
}

// ---------- catálogo completo ----------
/** Normaliza { movies, series, sagas } (o array plano → movies). Reporta issues. */
function normalizeCatalogV3(catalog) {
  const flat = Array.isArray(catalog);
  const movies = (flat ? catalog : (catalog.movies || [])).map(normalizeItemV3);
  const series = (flat ? [] : (catalog.series || [])).map(normalizeItemV3);
  const sagas = (flat ? [] : (catalog.sagas || [])).map(normalizeSaga);

  const all = [...movies, ...series];
  const issues = [];
  all.forEach((it, i) => { const v = validateV3(it); if (!v.ok) issues.push({ id: it.id || `#${i}`, errors: v.errors }); });

  // Cruce: todo item.saga no vacío debe tener entrada en sagas[].
  const sagaNames = new Set(sagas.map(s => s.name));
  for (const it of all)
    if (it.saga && !sagaNames.has(it.saga)) issues.push({ id: it.id, errors: [`saga "${it.saga}" sin entrada en sagas[]`] });

  const out = flat ? movies : { ...catalog, movies, series, sagas };
  return { out, count: all.length, sagas: sagas.length, issues };
}

// ---------- sistema de 3 salidas (el que ya manejamos) ----------
// Un MASTER (con links) → 3 artefactos:
//   1) JSON-API   : master normalizado CON links (lo lee la API desde GitHub).
//   2) JSON-Unity : sin URLs (lo lee el Udon).
//   3) JSON-Quest : = Unity, serializado con \uXXXX (sin caracteres especiales).

/** Links de vídeo por idioma para el JSON-API. Mantiene `?key=` (parte del contrato). */
function normalizeLinks(item) {
  const raw = item.links;
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
    const out = {};
    for (const k of ['default', 'Spanish', 'English']) if (raw[k]) out[k] = String(raw[k]);
    return out;
  }
  const legacy = item.videoUrl || item.master || item.master_url;
  return legacy ? { default: String(legacy) } : {};
}

/** Item del JSON-API = campos Unity + links. */
function toApiItem(item) {
  return { ...normalizeItemV3(item), links: normalizeLinks(item) };
}

/** Serializa a JSON con TODO no-ASCII escapado a uXXXX (salida Quest). */
function serializeAsciiSafe(obj) {
  const BS = String.fromCharCode(92);
  const s = JSON.stringify(obj, null, 2);
  let r = '';
  for (let i = 0; i < s.length; i++) {
    const code = s.charCodeAt(i);
    if (code > 127) r += BS + 'u' + ('000' + code.toString(16)).slice(-4);
    else r += s[i];
  }
  return r;
}

/**
 * Desde un MASTER { movies, series, sagas } produce las 3 salidas.
 * @returns {{ api:object, unity:object, questString:string, issues:Array }}
 */
function buildOutputs(master) {
  const flat = Array.isArray(master);
  const rawMovies = flat ? master : (master.movies || []);
  const rawSeries = flat ? [] : (master.series || []);
  const rawSagas = flat ? [] : (master.sagas || []);

  const sagas = rawSagas.map(normalizeSaga);
  const api = { movies: rawMovies.map(toApiItem), series: rawSeries.map(toApiItem), sagas };
  const unity = { movies: rawMovies.map(normalizeItemV3), series: rawSeries.map(normalizeItemV3), sagas };
  const questString = serializeAsciiSafe(unity);

  const { issues } = normalizeCatalogV3(master);
  return { api, unity, questString, issues };
}

module.exports = {
  normalizeItemV3, normalizeSaga, normSeasons, validateV3, normalizeCatalogV3, normType,
  normalizeLinks, toApiItem, serializeAsciiSafe, buildOutputs
};
