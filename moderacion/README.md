# Moderación del sistema de recomendaciones

Dentro del cine hay un panel donde cualquier jugador puede escribir qué le gustaría ver. Es texto
libre y público, así que antes o después alguien lo usará para insultar. Esta carpeta es el freno.

## El archivo

`blacklist.json` — la lista de palabras que no pasan.

**La API lo relee sola cada 10 minutos.** Haces commit aquí y en diez minutos está funcionando. No
hay que desplegar nada, ni avisar a nadie, ni reiniciar el servidor.

## Cómo añadir una palabra

Abre `blacklist.json`, añade la palabra a `"palabras"`, guarda, commit. Eso es todo.

```json
"palabras": [
  "gilipollas",
  "la-palabra-nueva"     ← aquí
]
```

Escríbela **normal, en minúscula y sin adornos**. No hace falta añadir las variantes.

## Por qué no hacen falta las variantes

Antes de comparar, el texto del jugador se aplasta:

```
tildes fuera        PÜTO      → puto
números que imitan  p0t0, 4   → poto, a
letras repetidas    puuuuto   → puto
todo lo demás fuera p.u.t.o   → puto
                    p u t o   → puto
anchos completos    ｐｕｔｏ     → puto
alfabetos parecidos рutо (ruso) → puto
```

Todo eso acaba en la misma cadena, así que **una entrada cubre todas sus disfraces**. Está
comprobado: de trece formas distintas de escribir un insulto, las trece se detectan.

## Mínimo tres letras

Las palabras de una o dos letras se ignoran a propósito: aparecen dentro de demasiadas palabras
normales y bloquearían medio catálogo.

## Cuando el filtro bloquea una película de verdad

La búsqueda mira **dentro** de las palabras, así que `ass` bloquearía también *Kick-Ass*. Para eso
está la segunda lista:

```json
"permitidas": [
  "kick ass"
]
```

Lo que esté ahí se recorta del texto antes de comparar. Así **pedir la película funciona, pero
insultar usando el título como tapadera se sigue detectando**.

> Si alguien te dice que no puede pedir una peli concreta, casi seguro es esto. Añade el título a
> `permitidas` y en diez minutos funciona.

## Qué le pasa a quien lo intenta

No es sólo que el mensaje se descarte:

1. **Primer intento** — el mensaje se tira y queda anotado.
2. **Segundo intento** — se le cierra el sistema de recomendaciones **24 horas**. Puede seguir
   escribiendo y pulsando enviar; no llega nada.

Nunca se le dice por qué. Explicárselo sería enseñarle a esquivarlo.

Al reincidente grave se le puede bloquear de forma permanente: la lista de intentos está en
`/admin/recomendaciones?formato=sanciones` y de ahí se pasa a la lista negra de IPs, que no caduca.

## Lo que este filtro NO hace

Una lista de palabras no entiende lo que lee. **No detecta un insulto escrito con palabras
normales** ("ojalá te pase algo malo"), ni el acoso dirigido a una persona concreta por su nombre.

Por eso las recomendaciones **no llegan directamente a nadie**: pasan por una cola de revisión antes
de convertirse en lista de peticiones. El filtro quita el ruido evidente; el criterio lo sigue
poniendo una persona.
