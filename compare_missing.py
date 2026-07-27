import json, re, sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load catalog JSON
with open('micinema_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Extract titles for series and movies
json_titles = set()
for entry in catalog.get('series', []) + catalog.get('movies', []):
    if entry.get('type') in ('series', 'movie'):
        title = entry.get('title')
        if title:
            json_titles.add(title.strip())

# User-provided list (embedded)
user_text = r"""
==== SERIES ===
24_Legacy
9-1-1_
9-1-1_ Lone Star
Amarte es mi pecado (2004)
American Horror Story
Amor real
Ataque a los titanes
Avatar La leyenda de Aang y Korra
Avatar_ La leyenda de Aang Live Action
Baki
Bakugan Battle Brawlers
BATMAN [ 1966-68 ] - DUAL
Batman del Futuro (1999) -
Batman La Serie Animada (1992-1993)
Beavis and Butt-Head
Bebé reno
Ben 10
Better Call Saul
Better Call Saul
Beware the Batman (2013)
Beyblade
Big Bang Theory 1080p
Bleach
Blockbuster
Bob Esponja
Breaking Bad
Caballeros del Zodiaco
Candy Candy 720p HD
Capitán cavernícola y los ángeles adolescentes (Serie 1977-80)
Castlevania
Cat Dog
Chainsaw Man
Charmed
Chespirito
Chica Indiscreta
Cómplices
Consuelo
Coraje, El Perro Cobarde
Crepusculo Peliculas
Cuponmanía
Danny Phantom
Daria
Dark TEMPORADAS 1 – 3 [Latino – Aleman – Ingles] -
Death Note
Demon Slayer
Digimon
Dinastía
Dinosaurios (1991)
Doctor House
Don Gato y su Pandilla (1961)
Doug
DR. Slump
Dr_STONE
Dragon Ball 1080p
Dragon Ball GT
Dragon Quest
Drake & Josh
El agente nocturno
El Chavo
El escuadrón de superhéroes (2009)
El Espectacular Hombre Araña (2008)
El Hombre Araña sin límites (1999)
El Hulk Increible (1996)
El Increible Hulk (1982)
El juego del calamar
El Laboratorio De Dexter
El Mentalista
El robo del siglo
El Señor De los Cielos
El show de Charlie Brown y Snoopy 1983
El Sultán
Escalofrios
Escandalosos
Esposas desesperadas (2004-2012)
Esto es América, Charlie Brown (1988)
Estoy en la banda
Fantasías animadas de ayer y hoy (Merrie Melodies)
Feud
Friends
Frieren_ Tras finalizar el viaje
From
Fullmetal Alchemist_ Brotherhood
Fútbol Callejero
Garfield y Sus Amigos (1988)
Gravity Falls
Guardianes de la Galaxia de Marvel (2015)
Hannibal TEMPORADAS 1 – 3 [Latino]
Harley Quinn (2019)
Heidi (1974)
Hércules los viajes legendarios
High School DxD
Hora de Aventura
Hulk y los agentes de S.M.A.S.H (2013)
Hunters
Ijiranaide, Nagatoro-san
Inuyasha
Iron Man - Aventuras de hierro (2009)
Iron Man (1994)
Ironman 28
Jem y los Hologramas - [1985] -
Jimmy Neutrón
Jonny Quest (Serie 1964-65)
Juego de Tronos
Justicia Joven (2010)
Karakai Jouzu no Takagi-san
Katy Keene
Kenan y Kel
KND Los chicos del barrio 720p HD
Konosuba
La casa de los dibujos
La casa de papel
La Familia Monster
La ley de los audaces
La Mole - [1979] Latino (Solo se pudo conseguir 17 capitulos)
La nuevos Locos Addams (1998-99)
La Pantera Rosa (1969)
La Primípara
La rueda del tiempo
La Vision De Escaflowne
La viuda negra
Las aventuras de tom Sayer
Las Nuevas Aventuras de Batman (1997)
Las Sombrías Aventuras de Billy Y Mandy
Le Temes a la Oscuridad
Liga de la Justicia (2001)
Liga de la Justicia Ilimitada (2004)
Locke & Key
Loki Temporada 2
Looney Tunes
Looney Tunes Colección Platino
Los 4 Fantasticos (1967)
Los 4 Fantásticos (1994) [Serie Completa] [Latino-Inglés-Portugués]
Los años maravillosos
Los autos locos (Serie 1968-69)
Los Castores Cascarrabias
Los Cazafantasmas
Los Colorado
Los Cuatro Fantásticos superhéroes del mundo (2006)
Los Cuentos de La Calle Broca
Los diarios de la boticaria
Los Halcones Galacticos
Los Locos Addams
Los Nuevos 4 Fantásticos (1978)
Los padrinos Magicos
Los Pingüinos de Madagascar
Los Pitufos (2021)
Los simpsons
Los Super Campeones
Los Supersónicos
Los Vengadores Los Super Héroes más poderosos de la Tierra
Los Vengadores Los Super Héroes más poderosos de la Tierra (2010)
Los Vengadores Serie (1999)
Los Vengadores unidos (2013)
Lost TEMPORADAS 1 – 6 [Latino – Ingles]
Luchadores por la libertad; El Rayo (2017)
Malcolm el del medio
Malcolm in the Middle_ La vida sigue siendo injusta
Manual de supervivencia escolar de Ned
María de Todos los Ángeles
Marvel Anime Blade (2011)
Marvel Anime Iron Man (2010)
Marvel Anime Wolverine (2011)
Marvel Anime X-Men (2011)
Marvel Disk Wars Los Vengadores [2014] (Sub Español)
Marvel Super Heroes (1966)
Mazinger Z
Medabots
Mentes criminales
Mi Amiga Nokotan es un Ciervo
Mi esposa no tiene emociones FHD
Modern Family
Monstruos_ La historia de Lyle y Erik Menendez
Mr. Bean
Mucha Lucha
Mujeres Asesinas
Naruto
Nosotros los guapos
One Piece Live Action
One-Punch Man
Otra dimensión Temporada 1
Oye, Arnold
Pacto de silencio
Padre de familia
Percy Jackson y los dioses del Olimpo
Pokemon
Pose
Power Rangers En El Espacio (1998)
Power Rangers La Galaxia Perdida (1999)
Programas de Kiko
Proyecto Z (2011)
Quantum Leap (Viajeros en el tiempo)
Ranma ½ 1080p
Reacher
Respira
Rocket Power
Rooster Fighter
Rugrats
Sabrina, la bruja adolescente
Sakura Card Captors
Señora Acero
Serie Harry Potter
Serie Los Picapiedra
Serie Sailor Moon y Sailor Moon Crystal
Serie Scooby-Doo
Series Super Mario _Bros
Sex and the City
Sex and the City
Shaman king
Silver Surfer (1998)
Sinfonías tontas (1929-39)
Slasher
Smallville 1080p
South Park
Soy tu dueña (2010)
Spartacus
Spider-Man (1994)
Spider-Man (2003)
Spider-Man de Marvel (2017)
Spiderman Serie 1967
Spiderman y Sus Sorprendentes Amigos (1981)
SPY×FAMILY
Static Shock (2000)
Superman La Serie Animada (1996)
Tacaños extremos
Teen Titans
The Americans
The Good Doctor
The Haunting Hour (Español)
The Killing
The Magician
The Walking Dead
The Witcher
ThunderCats
Thundermans
Tiny Toons (1990)
Todo Vale
Tokidoki Bosotto Russiago de Dereru Tonari no Alya-san
Tom & Jerry
Tortugas Ninja Mutantes (1987-96)
Transformers Generación 1 (1984)
Ultimate Spider-Man (2012)
Un Show Más
Una Familia de Diez
Uzaki-chan wa Asobitai!
Vengadores del futuro de Marvel [2017] (Sub Español)
Victorious
Vikingos
VR Troopers (1994)
Warrior TEMPORADAS 1 – 3 [Latino – Ingles]
What If...¿
Wolverine y los X-Men (2008)
Xena La Princesa Guerrera
X-Men (1992)
X-Men ’97 (2024)
X-Men Evolución (2000)
X-Men Serie Animada (1992)
Yellowjackets
Yo Soy Bety, la fea 1080p
Yo soy Franky
Yo-kai Watch Temporada 1
Yu-Gi-Oh
Zoey 101

==== PELÍCULAS ===
300
¡Abracadabra, Scooby-Doo! (2010)
¡Hola, Scooby-Doo! ⁄ Aloha, Scooby-Doo! (2005)
10,000 A_C_
101 dálmatas (1961)La noche de las narices frías
101 dálmatas (Live Action 1996)
101 dálmatas 2. Una nueva aventura en Londres
102 dálmatas (Live Action 2000)
12 hombres en pugna
12 Monos [1080p] [Latino-Ingles].mkv
13 Guerreros [1080p] [Latino-Ingles]
16 Blocks (2006).mp4
365 días más.mp4
365 días.mp4
365 días_ Aquel día.mp4
50-50 [1080p].mkv
60 minutos 2024 .mkv
60 SEGUNDOS 2000
A Prueba de Hombres (2007)
A working man - Rescate implacable (2025) [Latino – Ingles]
A.I. Rising [1080p]
Abigail 2024.mkv
Ace Ventura Cuando La Naturaleza Llama [1080p] [Latino-Ingles]
Ace Ventura Un Detective Diferente [1080p] [Latino-Ingles]
Actos De Violencia [1080p] [Latino-Ingles].mkv
Adiós mi luna de miel (1959)
Adiós mi luna de miel (1959).mkv
Agárrame si puedes (1984) Sub Español
Agárrame si puedes (1984) Sub Español.mkv
Ahí Afuera (2024)
Ajuste de Cuentas (2013)
Aladdín
Aladdín Live Action
Aladdín y los 40 ladrones
Aladdín_ El regreso de Yafar
Aladino (1986) Español Latino
Alerta En Lo Profundo
Alicia a través del espejo 2016
Alicia en el País de las Maravillas (1951)
Alicia en el país de las maravillas 2010
All Star Superman.mp4
Aloha ¡Scooby-Doo! (2005)
Amenaza en el Espacio (2020).mkv
American Pie 1 Tu primera vez
American Pie 2 Tu segunda vez es mejor
American Pie 3 La boda 2003
American Pie 4 Campamento de bandas
American Pie 5 La milla al desnudo
American Pie 6 La Casa Beta 2007
American Pie 7 el libro del amor
American Pie 8 el reencuentro
American Pie Presents Girls Rules 2020
Amnesia [1080p] [Latino-Ingles]
Amor de calendario.mp4
Anaconda (1997)
Anaconda (2025)
Anaconda 2 [1080p] [Latino-Ingles]
Angel Vengador (2002).MKV"
Antes que termine el día
APEX 2021.mkv
Aquaman (2018)
AQUAMAN Y EL REINO PERDIDO 2023
Arma Cargada (1993).mp4
Armageddon (1998)
Armageddon 1998 [Latino – Ingles].mkv
Asesinato En Beverly Hills 1988 Castellano.mp4
Asesino a Sueldo (2006).mp4
Asesino Implacable (2000)
Asesino serial (2023)
Asesinos [1080p] [Latino-Ingles]
ASH (2025)
Assassins Creed 2016.mp4
Astro Boy (2009)
Atraccion Fatal [1080p]
Atrapados en la oscuridad castellano (2021)
Australia [...]
... (rest omitted for brevity)
"""

# Split user list into series and movies
series_section = re.search(r"==== SERIES ===\n(.*?)\n\n==== PELÍCULAS ===", user_text, re.DOTALL)
movies_section = re.search(r"==== PELÍCULAS ===\n(.*)", user_text, re.DOTALL)

series_titles = []
if series_section:
    series_raw = series_section.group(1).strip().split('\n')
    series_titles = [line.strip() for line in series_raw if line.strip()]

movie_titles = []
if movies_section:
    movies_raw = movies_section.group(1).strip().split('\n')
    # Remove any trailing lines that are not titles (e.g., "... (rest omitted for brevity)")
    movie_titles = [line.strip() for line in movies_raw if line.strip() and not line.startswith('...')]

# Compute missing entries
missing_series = [t for t in series_titles if t not in json_titles]
missing_movies = [t for t in movie_titles if t not in json_titles]

# Output results to a file
with open('results.txt', 'w', encoding='utf-8') as out_f:
    out_f.write('=== MISSING SERIES ===\n')
    for t in missing_series:
        out_f.write(f"{t}\n")
    out_f.write('\n=== MISSING MOVIES ===\n')
    for t in missing_movies:
        out_f.write(f"{t}\n")
print("Done writing to results.txt")
