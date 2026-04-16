const fs = require('fs');
const path = 'c:/Users/Carmesi/Documents/Github/Cine.github.io/Cine/micinema_catalog.json';

const catalog = JSON.parse(fs.readFileSync(path, 'utf8'));

function fixId(id, prefix) {
  if (id && id.startsWith(prefix)) {
    const num = parseInt(id.substring(prefix.length), 10);
    if (!isNaN(num)) {
      return prefix + num.toString().padStart(3, '0');
    }
  }
  return id;
}

// Fix Movies
catalog.movies.forEach(m => {
  m.id = fixId(m.id, 'movie_');
  if (m.episodes) {
    m.episodes.forEach(e => {
      e.slotId = fixId(e.slotId, 'ep_');
    });
  }
});

// Fix Series
if (catalog.series) {
  catalog.series.forEach(s => {
    s.id = fixId(s.id, 'series_'); // Assuming series might have it too
    if (s.episodes) {
      s.episodes.forEach(e => {
        e.slotId = fixId(e.slotId, 'ep_');
      });
    }
  });
}

fs.writeFileSync(path, JSON.stringify(catalog, null, 2));
console.log('Padding unificado a 3 dígitos con éxito.');
