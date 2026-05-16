# Pestaña "Donaciones" — Máquinas de donación (Normal + Greed)

**Fecha:** 2026-05-16
**Estado:** Aprobado por el usuario, pendiente de plan de implementación.

## Objetivo

Mostrar el progreso del jugador en las **dos máquinas de donación** que tiene el juego (la "normal" de tiendas y la "Greed Donation Machine" del modo Greed), incluyendo contador acumulado y desbloqueos por hitos. Hoy esos datos sí se guardan en el save file pero no aparecen en ninguna parte de la app.

Caso que motivó la feature: el jugador quería saber cuánto le faltaba para desbloquear "Holy Mantle como ítem inicial de The Lost", que se desbloquea al llegar a 879 monedas en la máquina de donación normal. Sin esta pestaña ese contador es invisible.

## Alcance

**Dentro:**

- Nueva pestaña **"Donaciones"** en la barra principal.
- **Sección "Máquina de donación"** (la normal de tiendas) con su contador, barra de progreso y lista de hitos.
- **Sección "Máquina de Greed"** (modo Greed) con su contador, barra de progreso y lista de hitos.
- Ambas secciones usan el mismo formato visual.

**Fuera (futuras iteraciones):**

- Tokens de Eden.
- Cualquier otro contador del chunk 2 que no sea estas dos máquinas.

## UX

### Posición en la barra de pestañas

Se añade como séptima pestaña al final:

```
[Desafíos] [Personajes] [Logros] [Ítems] [Trinkets] [Cartas] [Donaciones]
```

### Estructura de la pestaña

Dos secciones apiladas verticalmente, en este orden:

1. **Máquina de donación** (la normal — primero porque es la que más usa el jugador).
2. **Máquina de Greed** (modo Greed).

Cada sección tiene la misma estructura interna (descrita abajo).

### Cabecera de cada sección

Tarjeta con:

- **Título de sección**: "Máquina de donación" o "Máquina de Greed".
- **Icono/sprite de la máquina** a la izquierda (si tenemos el sprite; placeholder si no).
- **Contador grande** centrado: `{actual} / {máximo}` (la normal va a 1000, la de Greed a 999).
- **Barra de progreso horizontal** debajo del contador.
- **Línea de resumen** debajo: `"Has desbloqueado {n} de {total} ítems"`.

### Lista de hitos

Lista vertical bajo la cabecera, ordenada por cantidad ascendente. Una fila por hito:

```
[icono]  {Nombre del desbloqueo}              [{cantidad}]   {estado}
```

- **Hitos conseguidos** (contador ≥ cantidad del hito):
  - Icono en color, nombre normal, badge verde `✓ Desbloqueado`.
- **Hitos pendientes** (contador < cantidad del hito):
  - Icono en gris/oscurecido, nombre apagado, badge `Faltan {cantidad - actual}`.
- **Hover** sobre icono/nombre: tooltip con descripción del ítem (mismo estilo que la pestaña Ítems).

### Lista oficial de hitos

**Máquina de donación normal** (confirmada desde `tracker/data/achievements.json`):

| Monedas | Desbloqueo                          |
|---------|-------------------------------------|
| 1       | Lucky Pennies                       |
| 10      | Special Hanging Shopkeepers         |
| 30      | Wooden Nickel                       |
| 68      | Cain holds Paperclip                |
| 111     | Everything is Terrible 2!!!         |
| 234     | Special Shopkeepers                 |
| 439     | Eve holds Razor Blade               |
| 500     | Greedier!                           |
| 666     | Store Key                           |
| 879     | The Lost holds Holy Mantle          |
| 1000    | Keeper (personaje)                  |

**Máquina de Greed** (a confirmar durante implementación contra `achievements.json` — el repo no tiene la lista compilada todavía; la investigación inicial solo recuperó la lista de la máquina normal). Riesgo gestionado en sección "Riesgos".

### Estados especiales

- **Contador = 0:** barra vacía, todos los hitos en gris.
- **Contador en el máximo (1000 o 999):** barra llena, mensaje `"Máquina llena"` reemplaza la línea de resumen, todos los hitos en verde.

## Datos

### De dónde sale el contador

Los dos contadores viven en el **chunk 2 (counters)** del save file Repentance+. El parser actual estructura los 10 chunks (`_ENTRY_SIZES = (1, 4, 4, 1, 1, 1, 1, 4, 4, 1)`) pero solo decodifica los chunks 1, 4 y 7. El chunk 2 tiene 523 entradas de 4 bytes (s32 little-endian).

**Pendiente de implementación:**

1. Extender `tracker/save_parser.py` para extraer el chunk 2 como lista de enteros.
2. Identificar el índice exacto del contador de la máquina normal y del de Greed dentro de ese chunk. El método más fiable: tomar el fixture `tests/fixtures/20260514.rep+persistentgamedata1.dat`, pedir al usuario el valor real en el juego de ambos contadores, y buscar coincidencias en el chunk 2.
3. Añadir campos al dataclass `ParsedSave` (`donation_count: int`, `greed_donation_count: int`).
4. Propagar por `state_mapper.py` al estado del frontend.

### Lista de hitos

Estructura de datos en `tracker/data/donations.py` (nuevo):

```python
DONATION_MILESTONES = [
    {"amount": 1, "achievement_id": <id>, "name": "Lucky Pennies", "item_id": <id_or_None>},
    # ...
]

GREED_DONATION_MILESTONES = [
    # confirmada durante implementación
]
```

`achievement_id` permite cross-validar cada hito contra el achievement byte real del save.

## Arquitectura / componentes nuevos

- **`tracker/data/donations.py`** — listas de hitos para ambas máquinas.
- **`tracker/save_parser.py`** — extracción del chunk 2 y campos nuevos en `ParsedSave`.
- **`tracker/state_mapper.py`** — exponer `donation_count` y `greed_donation_count` en el estado, más booleanos derivados de hitos desbloqueados.
- **`challenges.html`** — pestaña `data-view="donations"` con HTML + CSS + JS para las dos secciones.
- **`tracker/assets/icons/`** — sprites de las dos máquinas si los tenemos; placeholders si no.

## Tests

- **Parser:** dado un save fixture con valores conocidos de ambos contadores, `parse_save` devuelve esos enteros.
- **State mapper:** dado un `ParsedSave` con valores específicos, el estado expone los hitos correctos como desbloqueados / pendientes.
- **Donations data:** smoke test sobre `tracker/data/donations.py` (estructura correcta, cantidades ordenadas ascendentes, IDs de achievements dentro del rango del chunk de achievements).
- **No se testea la UI** (consistente con resto del proyecto).

## Riesgos

- **Índices del chunk 2 desconocidos:** No documentados en el repo. **Mitigación:** durante implementación, pedir al usuario los valores reales en el juego y hacer reverse-engineering con el fixture. Si no se logra identificar, la feature queda bloqueada — riesgo aceptado.
- **Lista de hitos de Greed Donation Machine no compilada:** **Mitigación:** durante implementación, filtrar `achievements.json` por palabras clave ("Greed Donation", "Greed Machine", etc.) y construir la lista manualmente. Si la lista no se puede determinar de forma fiable desde el repo, queda como TBD y se renderiza la sección con "Lista pendiente" hasta resolverlo.
- **Sprites de máquinas:** Si no están en assets, usar placeholders visuales (icono genérico de moneda).

## Después de esta iteración

La pestaña queda diseñada para añadir más adelante:

- **Tokens de Eden** — sección adicional bajo las dos máquinas.

No se implementa nada de eso ahora.
