# 📄 MiCinema Catalog Spec (V2)

Este documento define el esquema técnico del catálogo de MiCinema utilizado por la herramienta de gestión y el cargador en Unity/VRChat.

## 🏗️ Estructura de Raíz

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `catalogName` | String | Nombre identificativo del catálogo. |
| `version` | Integer | Versión del formato (Actual: `2`). |
| `schema` | String | Identificador del esquema para compatibilidad. |
| `atlasInfo` | Object | Configuración global de las cuadrículas de imagen. |
| `posterAtlases` | Array | Registro de texturas de posters disponibles. |
| `movies` | Array | Lista de objetos tipo Película. |
| `series` | Array | Lista de objetos tipo Serie. |

## 🖼️ Configuración de Atlases (`atlasInfo`)
Define cómo se dividen las texturas de 2048x2048.
- **`columns`**: Número de columnas (Default: `16`).
- **`rows`**: Número de filas (Default: `8`).
- **`cellCount`**: Capacidad total por imagen (16x8 = `128`).

## 🎬 Objeto Contenido (Movie/Series)

```json
{
  "id": "movie_001",
  "type": "movie",
  "title": "Ejemplo de Título",
  "description": "Breve sinopsis del contenido.",
  "year": 2024,
  "rating": "PG-13",
  "section": "catalog",
  "genres": ["Action", "Sci-Fi"],
  "languages": ["Spanish", "English"],
  "links": {
    "default": "URL_DE_VIDEO",
    "language_English": "URL_OPCIONAL_EN_INGLES"
  },
  "atlas": "A",
  "gridIndex": 0,
  "enabled": true,
  "addedAt": "ISO_TIMESTAMP",
  "addedBy": "Nombre_Operador"
}
```

### Campos Clave
- **`section`**: 
  - `catalog`: Contenido regular.
  - `recently_added`: Aparece en la sección de "Estrenos" con prioridad visual.
- **`atlas`**: La letra o clave de la textura donde está el poster (ej: `A`, `B`).
- **`gridIndex`**: La posición de la celda (0 a 127). La herramienta calcula automáticamente X e Y a partir de esto.

## 🗂️ Enumeraciones aceptadas

### Géneros
`Action`, `Adventure`, `Animation`, `Comedy`, `Crime`, `Documentary`, `Drama`, `Family`, `Fantasy`, `History`, `Horror`, `Music`, `Mystery`, `Romance`, `Sci-Fi`, `Thriller`, `War`, `Western`, `Cyberpunk`.

### Clasificaciones (Rating)
`G`, `PG`, `PG-13`, `R`, `TV-PG`, `TV-14`, `TV-MA`.

---
*Nota: Este esquema es estricto. Cualquier cambio fuera de este formato podría causar errores de lectura en el mundo de VRChat.*
