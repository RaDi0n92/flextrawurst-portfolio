# Cómo contribuir

## Camino más corto

1. Abre un issue con la plantilla **Nuevo término**.
2. Introduce la forma bruta exacta. No la corrijas.
3. Separa quien presenta, posible autor e incertidumbre.
4. Añade fecha, contexto, formulación exacta y una fuente publicable.
5. Explica el término en alemán, inglés o español. Se aceptan más idiomas.
6. Indica expresamente lo que el término no significa.
7. Envía un pull request con un archivo en `data/proposals/`.

## Campos mínimos

- `id`
- `raw_form`
- `submitted_by`
- `authorship_status`
- `first_seen`
- `exact_input`
- `source_ref`
- `definitions`
- `status: submitted`

## Qué ocurre después

Las comprobaciones técnicas validan esquema, IDs, fuentes, fechas y secretos accidentales. Después puede revisarse la procedencia. Solo Daniel puede cambiar un elemento del registro oficial a `accepted` y crear el registro de decisión correspondiente.

## Correcciones

No sustituyas silenciosamente la procedencia antigua. Presenta un evento nuevo con `event_type: correction` y referencia el evento incorrecto.

## Traducciones

Traduce explicaciones, límites y ejemplos. Conserva la forma bruta. Una forma nueva en otro idioma es una propuesta separada, no una traducción ordinaria.

## Derechos

Al contribuir confirmas que puedes publicar el material bajo las licencias del repositorio. No envíes conversaciones completas de terceros, libros, artículos ni mensajes privados sin permiso.
