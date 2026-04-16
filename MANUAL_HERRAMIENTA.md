# 📘 Manual de Uso: MiCinema Catalog Tool

Esta guía explica detalladamente cómo utilizar la herramienta de gestión de catálogo para MiCinema.

## 🚀 Inicio Rápido
1. Abre la aplicación **MiCinema Tool**.
2. Ve a **Configuración** (icono de engranaje ⚙️).
3. Selecciona la carpeta donde tienes tu archivo `micinema_catalog.json`.

## ✍️ Gestión de Contenido
### Agregar una nueva Película o Serie
1. Haz clic en el botón **"+ Agregar Nuevo"** en la esquina superior derecha.
2. Completa los campos obligatorios:
   - **Título**: Nombre completo de la obra.
   - **ID**: Identificador único (ej: `M-154`).
   - **Géneros**: Selecciona varios si es necesario.
   - **Año**: Fecha de estreno.
   - **Rating**: La clasificación (G, PG, R, etc.).
3. **Poster**: Haz clic para subir la imagen del poster.
   - *Nota*: La aplicación se encargará automáticamente de redimensionarla y colocarla en el Atlas correspondiente.
4. Haz clic en **"Guardar"**.

### Editar Contenido Existente
Simplemente busca el título en la lista o en la cuadrícula y haz clic sobre él para abrir el formulario de edición.

## 🖼️ Sistema de Atlases (Imágenes)
La herramienta organiza los posters en imágenes de 2048x2048 llamadas "Atlases".
- Cada Atlas puede contener hasta **128 posters** (en una cuadrícula de 16x8).
- Al agregar contenido, la herramienta asigna automáticamente el siguiente espacio libre.
- **Backups**: Cada poster que subas se guarda individualmente en una carpeta oculta llamada `Backup`. Esto permite que si reinstalas la herramienta o mueves archivos, puedas reconstruir los Atlases sin perder calidad.

## 🔍 Filtros y Vistas
- **Búsqueda Directa**: Usa la barra superior para buscar por título.
- **Filtros Avanzados**: Puedes filtrar por Género, Año, Estado (Estreno/Catálogo) o Rating.
- **Vistas**: 
  - **Tabla**: Mejor para buscar IDs específicos o ver detalles técnicos. 
  - **Cuadrícula (Netflix Style)**: Mejor para ver cómo se verán los posters en el mundo de VRChat.

## ⚠️ Consejos Importantes
> [!IMPORTANT]
> **No borres la carpeta 'Backup'**: Si borras los archivos individuales de la carpeta Backup, no podrás usar la función de "Reconstruir Atlases" si tus imágenes principales se corrompen.

> [!TIP]
> **IDs de Reproducción**: Asegúrate de que el link de reproducción sea compatible con los reproductores de VRChat (ej: links directos .mp4, Youtube, etc.).

---
*Para soporte técnico, contacta con la administración de MiCinema.*
