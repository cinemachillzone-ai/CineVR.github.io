# -*- coding: utf-8 -*-
"""
Genera los creativos de relleno "ESPACIO DISPONIBLE" del cine.

POR QUÉ EXISTE ESTE FICHERO
El AdManager pide SIEMPRE todas las URLs de sus arrays de atlas, existan o no. Cuando falta una
imagen, cada jugador se come un 404 con reintentos en cada arranque — y el aviso queda enterrado
entre el resto del log. Con las plantillas puestas, una ranura sin vender enseña un cartel que
invita a anunciarse en vez de un hueco negro.

El generador original se escribió en agosto y se perdió. Éste lo reconstruye a partir del arte que
sí sobrevivió (ads/atlas/pc/0.png y ads/pause/pc/0.png), midiendo sus colores y su composición.

QUÉ GENERA

    ads/atlas/pc/N.png      2048x2048   grilla 4x2 de celdas verticales (512x1024)
    ads/atlas/quest/N.png   1024x1024   la misma grilla, mitad de lado
    ads/pause/pc/N.png      1024x512    cartel horizontal suelto
    ads/pause/quest/N.png    512x256    ídem, mitad

Uso:
    python Herramientas/generar_plantillas_publicidad.py            (lo que falta)
    python Herramientas/generar_plantillas_publicidad.py --todo     (rehace también lo que hay)

Las medidas van en proporción al lienzo, así que PC y Quest salen idénticos y basta cambiar un
número para añadir un tamaño nuevo.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paleta del cine — los mismos tokens que CineVRMenuGenerator.cs
FONDO   = (10, 4, 7)        # #0A0407
VINO    = (19, 5, 11)       # #13050B  el tono que domina el arte existente
ROSA    = (255, 45, 120)    # #FF2D78
ROSA_CL = (255, 120, 175)   # #FF78AF
BLANCO  = (255, 255, 255)
GRIS    = (170, 165, 168)

F_BOLD  = 'C:/Windows/Fonts/arialbd.ttf'
F_REG   = 'C:/Windows/Fonts/arial.ttf'


def fuente(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def texto_espaciado(d, xy, txt, font, fill, tracking, centro_x=None):
    """Dibuja con espaciado entre letras. Pillow no lo trae, y sin tracking los rótulos
    en mayúsculas del cine pierden el aire que los hace legibles de lejos."""
    anchos = [d.textlength(c, font=font) for c in txt]
    total = sum(anchos) + tracking * (len(txt) - 1)
    x = (centro_x - total / 2) if centro_x is not None else xy[0]
    y = xy[1]
    for c, w in zip(txt, anchos):
        d.text((x, y), c, font=font, fill=fill)
        x += w + tracking
    return total


def fondo_celda(w, h):
    """Fondo vino con un halo rosado al centro, como el arte original."""
    im = Image.new('RGB', (w, h), FONDO)
    px = im.load()
    cx, cy = w / 2.0, h * 0.42
    rad = max(w, h) * 0.55
    for y in range(h):
        dy = (y - cy) / rad
        for x in range(w):
            dx = (x - cx) / rad
            d2 = dx * dx + dy * dy
            if d2 >= 1.0:
                px[x, y] = VINO if ((x + y) % 97 == 0) else FONDO
                continue
            f = (1.0 - d2) ** 2
            px[x, y] = (
                int(FONDO[0] + (VINO[0] - FONDO[0] + 26) * f),
                int(FONDO[1] + (VINO[1] - FONDO[1] + 6) * f),
                int(FONDO[2] + (VINO[2] - FONDO[2] + 14) * f),
            )
    return im


def marco(d, w, h, g):
    """Esquinas blancas gruesas + dos filetes rosas verticales. Es la firma visual del cartel:
    lee como 'marco de foto vacío', que es justo el mensaje."""
    m = int(w * 0.035)
    largo_x, largo_y = int(w * 0.22), int(h * 0.10)
    # filetes rosas a los lados
    d.rectangle([m, m, m + g, h - m], fill=ROSA)
    d.rectangle([w - m - g, m, w - m, h - m], fill=ROSA)
    # esquinas blancas: dos brazos por esquina (uno horizontal, otro vertical)
    def barra(x0, y0, x1, y1):
        d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=BLANCO)

    for (ex, ey, sx, sy) in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        barra(ex, ey, ex + sx * largo_x, ey + sy * g * 2)   # brazo horizontal
        barra(ex, ey, ex + sx * g * 2, ey + sy * largo_y)   # brazo vertical


def pildora(d, cx, cy, w, h, lineas, font):
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2, fill=ROSA)
    n = len(lineas)
    alto = font.size * 1.18
    y0 = cy - (alto * n) / 2 + (alto - font.size) / 2 - font.size * 0.09
    for i, l in enumerate(lineas):
        d.text((cx, y0 + i * alto), l, font=font, fill=(10, 4, 7), anchor='ma')


def cartel(w, h, vertical):
    """Un creativo completo. `vertical` cambia la composición: en el atlas las celdas son altas
    y estrechas, y ahí el reclamo va en dos líneas y arriba; en el cartel de pausa cabe centrado."""
    im = fondo_celda(w, h)
    d = ImageDraw.Draw(im)
    g = max(2, int(w * 0.006))
    marco(d, w, h, g)

    # LA ESCALA ES SIEMPRE LA ALTURA, nunca el ancho. El tamaño de una tipografía se mide en
    # altura, así que escalar por el ancho hacía que el cartel horizontal (1024x512) saliera al
    # doble y los textos se montaran unos sobre otros. Las proporciones salen de medir el arte
    # que ya existía.
    f_top = fuente(F_BOLD, int(h * (0.026 if vertical else 0.050)))
    f_big = fuente(F_BOLD, int(h * (0.052 if vertical else 0.120)))
    f_pil = fuente(F_BOLD, int(h * (0.030 if vertical else 0.065)))
    f_pie = fuente(F_REG,  int(h * (0.016 if vertical else 0.038)))

    cx = w / 2
    if vertical:
        y = h * 0.265
        texto_espaciado(d, (0, y), 'TU MARCA AQUI', f_top, ROSA_CL, h * 0.010, centro_x=cx)
        y += f_top.size * 1.75
        d.text((cx, y), 'ESPACIO', font=f_big, fill=BLANCO, anchor='ma')
        d.text((cx, y + f_big.size * 1.10), 'DISPONIBLE', font=f_big, fill=BLANCO, anchor='ma')
        pildora(d, cx, y + f_big.size * 3.15, w * 0.68, f_pil.size * 3.0,
                ['COMPRA TU', 'ANUNCIO YA'], f_pil)
        texto_espaciado(d, (0, h * 0.862), 'CINE CHILL ZONE  ·  VRCHAT', f_pie, GRIS,
                        h * 0.006, centro_x=cx)
    else:
        texto_espaciado(d, (0, h * 0.055), 'TU MARCA AQUI', f_top, ROSA_CL, h * 0.020, centro_x=cx)
        y = h * 0.175
        d.text((cx, y), 'ESPACIO', font=f_big, fill=BLANCO, anchor='ma')
        d.text((cx, y + f_big.size * 1.12), 'DISPONIBLE', font=f_big, fill=BLANCO, anchor='ma')
        pildora(d, cx, h * 0.715, w * 0.64, f_pil.size * 1.85, ['COMPRA TU ANUNCIO YA'], f_pil)
        texto_espaciado(d, (0, h * 0.862), 'CINE CHILL ZONE  ·  VRCHAT', f_pie, GRIS,
                        h * 0.010, centro_x=cx)
    return im


def atlas(lado):
    """Grilla 4x2 de celdas verticales, que es lo que declara el manifiesto (grid 4x2)."""
    cw, ch = lado // 4, lado // 2
    hoja = Image.new('RGB', (lado, lado), FONDO)
    celda = cartel(cw, ch, vertical=True)
    for fila in range(2):
        for col in range(4):
            hoja.paste(celda, (col * cw, fila * ch))
    return hoja


def guardar(im, rel, rehacer):
    p = os.path.join(RAIZ, rel)
    if os.path.exists(p) and not rehacer:
        print('  (ya existe, se respeta)  ' + rel)
        return False
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p, 'PNG', optimize=True)
    print('  generado  %-28s %sx%s  %d KB' % (rel, im.size[0], im.size[1], os.path.getsize(p) // 1024))
    return True


def main():
    rehacer = '--todo' in sys.argv
    n = 0

    print('Atlas de corte (grilla 4x2):')
    n += guardar(atlas(2048), 'ads/atlas/pc/1.png', rehacer)
    n += guardar(atlas(1024), 'ads/atlas/quest/1.png', rehacer)

    print('Carteles de pausa (3..15; 0-2 ya existen):')
    pc = cartel(1024, 512, vertical=False)
    qu = cartel(512, 256, vertical=False)
    for i in range(3, 16):
        n += guardar(pc, 'ads/pause/pc/%d.png' % i, rehacer)
        n += guardar(qu, 'ads/pause/quest/%d.png' % i, rehacer)

    print()
    print('%d imagenes escritas.' % n)
    print('Recuerda: el manifiesto (ads/manifest.json) es quien decide cuantas ranuras se usan.')
    print('Estas plantillas solo evitan el hueco cuando una ranura no esta vendida.')


if __name__ == '__main__':
    main()
