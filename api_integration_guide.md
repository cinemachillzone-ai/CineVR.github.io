# Guía de Integración API - MiCinema Catalog v2

Esta documentación detalla los cambios estructurales realizados en el catálogo de MiCinema para soportar el nuevo Dashboard estilo Netflix y asegurar la compatibilidad con el prefab de Unity.

## 1. Esquema del Catálogo (v2)
**Schema ID:** `micinema.catalog.compat.v2`

El catálogo ahora utiliza una estructura de **Sincronización Bidireccional**. El Tool administrativo trabaja con un modelo unificado, pero exporta los datos divididos para optimizar la carga en Unity.

### Estructura de Raíz
```json
{
  "catalogName": "MiCinema New Catalog",
  "version": 2,
  "atlasInfo": {
    "columns": 16,
    "rows": 8,
    "cellCount": 128
  },
  "movies": [],
  "series": []
}
```

## 2. Cambios en el Modelo de Contenido
Cada item (película o serie) ahora incluye metadatos extendidos para filtrado avanzado:

*   **`type`**: `movie` o `series`. Determina en qué array se guarda el objeto.
*   **`section`**: 
    *   `recently_added`: Aparece en la fila de "Estrenos/Recomendados".
    *   `catalog`: Contenido estándar.
*   **`genres`**: Array de strings normalizados.
    *   *Importante:* Se ha añadido el género `Cyberpunk` a la lista oficial.
*   **`languages`**: Array con nombres completos (`Spanish`, `English`, `Japanese`, `Korean`).

## 3. Lógica de Enlaces y Episodios (Crítico)
Para simplificar la edición de múltiples idiomas y capítulos, el Tool utiliza un sistema de mapeo:

### En el Tool (`links`):
Se utiliza un objeto (Key-Value) para permitir ediciones rápidas.
```json
"links": {
  "default": "URL_PRINCIPAL",
  "language_Spanish_Cap_1": "URL_A",
  "language_English_Cap_1": "URL_B"
}
```

### Exportación para API/Unity (`episodes`):
Al guardar, el Tool genera automáticamente el array `episodes` que espera el prefab:
*   **ID**: Generado como `{movie_id}_{link_key}`.
*   **Title**: El Tool limpia el prefijo `language_` y reemplaza guiones por espacios (ej: "Spanish Cap 1").

## 4. Posicionamiento en el Atlas (Grid 16x8)
El sistema de posters ahora es estrictamente posicional para maximizar el rendimiento:
*   **`atlas`**: Letra del atlas (A, B, C...). Cada atlas soporta **128 items**.
*   **`gridIndex`**: Índice de 0 a 127.
*   **ID de Item**: Sigue el formato `{type}_{000}` (ej: `movie_042`).

> [!IMPORTANT]
> El Tool realiza un "Recalculate Indices" cada vez que se borra contenido, desplazando los items para que no queden huecos en el Atlas y los IDs se mantengan correlativos por fecha de adición.

## 5. Seguimiento de Actividad
Se han añadido campos de auditoría para el equipo de gestión:
*   **`addedAt`**: Timestamp ISO de creación.
*   **`addedBy`**: Nombre del operador que realizó la subida.

---
*Documentación generada para el equipo de desarrollo de API - MiCinema Tool 2026*
