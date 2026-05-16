# Pestaña "Donaciones" — Greed Donation Machine

**Fecha:** 2026-05-16
**Estado:** Aprobado por el usuario, pendiente de plan de implementación.

## Objetivo

Mostrar el progreso del jugador en la **Greed Donation Machine** (contador acumulado y desbloqueos por hitos), que actualmente no aparece en ninguna parte de la app aunque el dato sí se guarda en el save file.

Ejemplo de caso real que motivó la feature: el jugador no sabe cuánto le falta para los desbloqueos por donaciones (ej. para Holy Mantle / Tainted Keeper) porque la app no expone ese contador.

## Alcance

**Dentro:**

- Una nueva pestaña visible en la barra principal llamada **"Donaciones"**.
- Cabecera con icono, contador, barra de progreso y resumen.
- Lista vertical de hitos de la Greed Donation Machine con su ítem desbloqueado, cantidad requerida y estado.

**Fuera (futuras iteraciones, ya pensado el espacio para acomodarlo):**

- Máquina de donación normal.
- Tokens de Eden.

## UX

### Posición en la barra de pestañas

Se añade como séptima pestaña al final de la barra existente:

```
[Desafíos] [Personajes] [Logros] [Ítems] [Trinkets] [Cartas] [Donaciones]
```

### Cabecera

Una tarjeta arriba del contenido con:

- **Sprite de la Greed Donation Machine** del juego, a la izquierda.
- **Contador grande** centrado: `{actual} / 999`.
- **Barra de progreso horizontal** debajo del contador.
- **Línea de resumen** debajo: `"Has desbloqueado {n} de {total} ítems"`.

### Lista de hitos

Lista vertical, ordenada por cantidad de monedas ascendente. Una fila por hito:

```
[icono]  {Nombre del ítem}                  [{cantidad}]   {estado}
```

- **Hitos conseguidos** (contador ≥ cantidad del hito):
  - Icono del ítem en color normal.
  - Nombre del ítem en color normal.
  - Badge verde a la derecha: `✓ Desbloqueado`.
- **Hitos pendientes** (contador < cantidad del hito):
  - Icono del ítem oscurecido / en escala de grises.
  - Nombre del ítem en color apagado.
  - Badge a la derecha: `Faltan {cantidad - actual}`.

### Tooltips

Hover sobre el icono o el nombre del ítem muestra el mismo tooltip que ya se usa en la pestaña Ítems (nombre + descripción del ítem en español). Misma fuente de datos, mismo estilo, sin duplicación.

### Estados especiales

- **Contador = 0:** barra vacía, todos los hitos en gris con "Faltan X".
- **Contador = 999 (máximo):** barra llena, mensaje `"Máquina llena"` reemplazando la línea de resumen, todos los hitos en verde.

## Datos

### De dónde sale el contador

El contador acumulado de la Greed Donation Machine se guarda en el save file de Repentance+ dentro de un chunk de contadores de 4 bytes por entrada (uno de los chunks que el parser actual extrae estructuralmente pero no decodifica todavía — `_ENTRY_SIZES` lo lista pero `parse_save` solo extrae los chunks 1, 4 y 7). El plan de implementación tendrá que:

1. Extender `tracker/save_parser.py` para extraer el chunk de contadores.
2. Identificar el índice exacto del contador de Greed dentro de ese chunk (se determina experimentalmente contra un save real con valor conocido).
3. Añadir el campo al dataclass `ParsedSave` (ej. `greed_donation: int`).
4. Propagarlo por `state_mapper.py` al estado que consume el frontend.

### Lista de hitos

La lista oficial de hitos de la Greed Donation Machine en Repentance+ se confirma durante la implementación contraseñando con `tracker/data/achievements.json` y la wiki oficial. Hasta donde sabemos al escribir este spec, hay del orden de 5-6 hitos entre 10 y 999 monedas. La estructura de datos vivirá en `tracker/data/donations.py` (nuevo) con un formato tipo:

```python
GREED_DONATION_MILESTONES = [
    {"amount": 10, "item_id": <id>, "achievement_id": <id>},
    ...
]
```

`achievement_id` permite cross-validar contra logros conocidos.

## Arquitectura / componentes nuevos

- **`tracker/data/donations.py`** — lista de hitos (cantidad, item_id, achievement_id).
- **`tracker/save_parser.py`** — extracción del contador desde el chunk de counters.
- **`tracker/state_mapper.py`** — exponer `greed_donation_count` al estado del frontend.
- **`challenges.html`** — nueva pestaña `data-view="donations"` con HTML + CSS + JS para renderizar cabecera y lista.
- **`tracker/assets/icons/`** — sprite de la Greed Donation Machine (probablemente reutilizable desde assets ya descargados o vía `tools/download_*` similares).

## Tests

- **Parser:** test que dado un save fixture con valor conocido devuelve el contador correcto. Reutilizar `tests/fixtures/20260514.rep+persistentgamedata1.dat` (verificar in-game cuánto vale) o crear fixture nuevo.
- **State mapper:** dado un `ParsedSave` con `greed_donation_count=347`, el estado expone los hitos correctos como desbloqueados/pendientes.
- **No se testea la UI** (consistente con el resto del proyecto).

## Riesgos / consideraciones

- **Índice del contador desconocido:** El offset exacto dentro del chunk de counters no está documentado en el código actual. Riesgo bajo: se determina con un save donde el valor sea conocido (basta donar en una run y comparar). Si no se logra identificar, la feature queda bloqueada hasta resolverlo.
- **Lista de hitos puede haber cambiado entre versiones de Repentance+:** Confirmar con el save del usuario y la wiki vigente.
- **Sprite de la máquina:** Si no se encuentra el sprite en assets, usar un placeholder visual (icono de moneda + texto) en la primera versión.

## Después de esta iteración

La pestaña queda diseñada para añadir, en iteraciones futuras:

- **Máquina de donación normal** — sección expandible o sub-pestaña interna bajo la cabecera de Greed.
- **Tokens de Eden** — sección adicional, formato similar (contador + lista de personajes/skins desbloqueables).

No se implementa nada de esto ahora.
