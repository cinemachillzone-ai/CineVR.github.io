const axios = require('axios');
const fs = require('fs');

// =========================================================================
// CONFIGURACIÓN PARA GITHUB ACTIONS 
// =========================================================================

// Obtenemos los secretos desde las Variables de Entorno
const BUNNY_API_KEY = process.env.BUNNY_API_KEY;
const BUNNY_LIBRARY_ID = process.env.BUNNY_LIBRARY_ID;

// Puesto que GitHub Actions clona tu repo, el JSON ya lo tenemos localmente 
const CATALOG_PATH = './micinema_catalog.json';
const MAX_CONCURRENCY = 3; 

// Verificamos que los secretos se hayan inyectado correctamente
if (!BUNNY_API_KEY || !BUNNY_LIBRARY_ID) {
    console.error("❌ ERROR CRÍTICO: No se encontraron los secretos o no están configurados correctamente.");
    console.error("Asegúrate de tener BUNNY_API_KEY y BUNNY_LIBRARY_ID guardados en Settings > Secrets de Github.");
    process.exit(1); 
}

const api = axios.create({
    baseURL: `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}`,
    headers: {
        'AccessKey': BUNNY_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// =========================================================================
// FUNCIONES DE CONTROL
// =========================================================================

async function getExistingVideos() {
    console.log("🔍 Consultando videos existentes en Bunny Stream...");
    let existingTitles = new Set();
    let page = 1;
    let hasMore = true;

    while (hasMore) {
        try {
            const { data } = await api.get(`/videos?page=${page}&itemsPerPage=1000`);
            const items = data.items || [];
            
            items.forEach(video => {
                existingTitles.add(video.title);
            });

            if (items.length < 1000) {
                hasMore = false; 
            } else {
                page++;
            }
        } catch (error) {
            console.error("❌ Error de comunicación con Bunny al listar videos:", error.message);
            throw error;
        }
    }
    
    console.log(`✅ ¡Encontrados ${existingTitles.size} videos ya en la CDN!`);
    return existingTitles;
}

async function processConcurrently(items, concurrency, asyncFn) {
    const results = [];
    const executing = [];
    
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        const p = Promise.resolve().then(() => asyncFn(item, i, items.length));
        results.push(p);

        if (concurrency <= items.length) {
            const e = p.then(() => executing.splice(executing.indexOf(e), 1));
            executing.push(e);
            if (executing.length >= concurrency) {
                await Promise.race(executing);
            }
        }
    }
    return Promise.all(results);
}

// =========================================================================
// RUTINA CENTRAL 
// =========================================================================
async function runMigration() {
    console.log("🚀 Iniciando automatización con GitHub Actions...");

    let catalog;
    try {
        const rawData = fs.readFileSync(CATALOG_PATH, 'utf-8');
        catalog = JSON.parse(rawData);
    } catch (e) {
        console.error("❌ No se pudo leer el archivo micinema_catalog.json", e.message);
        process.exit(1);
    }
    
    let itemsToProcess = catalog.movies || [];
    if (catalog.series) itemsToProcess = itemsToProcess.concat(catalog.series);

    console.log(`✅ Catálogo cargado: ${itemsToProcess.length} elementos (películas/series).`);

    const existingTitles = await getExistingVideos();

    console.log(`\n⚙️ Analizando subidas con prevención de duplicados (MÁXIMO ${MAX_CONCURRENCY})...\n`);
    
    let report = {
        success: [],
        failed: [],
        skipped: 0
    };

    const processMovie = async (movie, index, total) => {
        const title = movie.title || `Video_${index}`;
        
        let videoUrl = null;
        if (movie.links) {
            videoUrl = movie.links.default || movie.links.language_Spanish || movie.links.language_English;
        }

        if (!videoUrl || videoUrl.length < 10) {
            console.log(`[${index + 1}/${total}] ⚠️ Omitido "${title}": No tiene enlace de video válido.`);
            report.skipped++;
            return;
        }

        // VERIFICACIÓN CLAVE: prevenir doble coste
        if (existingTitles.has(title)) {
            console.log(`[${index + 1}/${total}] ⏩ OK: "${title}" ya existe en el servidor Stream.`);
            report.skipped++;
            return; // Nos lo saltamos sin coste.
        }

        try {
            // Mandamos la orden
            const response = await api.post('/videos/fetch', {
                url: videoUrl,
                title: title
            });

            console.log(`[${index + 1}/${total}] ✅ "${title}" procesado correctamente. Bunny ID: ${response.data.id}`);
            report.success.push(title);

        } catch (error) {
            const errMsg = error.response?.data?.Message || error.message;
            console.error(`[${index + 1}/${total}] ❌ Falló "${title}": ${errMsg}`);
            // Guardamos el error pero el script NO se crashea
            report.failed.push({ title, reason: errMsg });
        }
    };

    // Lanzar todo en la cola manejable
    await processConcurrently(itemsToProcess, MAX_CONCURRENCY, processMovie);

    // ============================================
    // REPORTE FINAL EN CONSOLA (Para los logs de GitHub Actions)
    // ============================================
    console.log("\n============================================\n");
    console.log("📊 REPORTE FINAL DE LA EJECUCIÓN:");
    console.log(`⏩ Omitidos (Ya existían o sin link): ${report.skipped}`);
    console.log(`✅ Transferidos con éxito: ${report.success.length}`);
    console.log(`❌ Errores: ${report.failed.length}`);
    
    if (report.failed.length > 0) {
        console.log("\n⚠️ Lista de Errores:");
        report.failed.forEach(f => console.log(`   - ${f.title} (${f.reason})`));
        // Opcional: si quieres que el Github Action salga como "Errored" si hubo fallas:
        // process.exit(1); 
    }
    
    console.log("\n============================================\n");
    console.log("🎉 Run terminado.");
}

runMigration();
