# Pestaña "Donaciones" — Máquinas de donación (Normal + Greed)

**Fecha:** 2026-05-16
**Estado:** Aprobado por el usuario, pendiente de plan de implementación.

## Objetivo

Mostrar el progreso del jugador en las **dos máquinas de donación** que tiene el juego — la "normal" de tiendas y la "Greed Donation Machine" del modo Greed — incluyendo contador acumulado y desbloqueos por hitos. Hoy esos datos sí se guardan en el save file pero no aparecen en ninguna parte de la app.

Caso que motivó la feature: el jugador quería saber cuánto le falta para desbloquear "Holy Mantle como ítem inicial de The Lost", que se desbloquea al llegar a 879 monedas en la Greed Donation Machine. Sin esta pestaña ese contador es invisible.

## Alcance

**Dentro:**

- Nueva pestaña **"Donaciones"** en la barra principal.
- **Sección "Máquina de Greed"** (modo Greed) — primero porque es la que tiene el ejemplo del usuario.
- **Sección "Máquina de donación"** (la normal de tiendas) — segunda.
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

1. **Máquina de Greed** (la que tiene Holy Mantle a 879 — el ejemplo del usuario).
2. **Máquina de donación** (la normal).

### Cabecera de cada sección

Tarjeta con:

- **Título de sección**: "Máquina de Greed" o "Máquina de donación".
- **Icono/sprite de la máquina** a la izquierda (si tenemos el sprite; placeholder gris si no).
- **Contador grande** centrado: `{actual} / {máximo}` (Greed va a 1000, normal va a 999).
- **Barra de progreso horizontal** debajo del contador.
- **Línea de resumen**: `"Has desbloqueado {n} de {total} ítems"`.

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

**Greed Donation Machine** (10 hitos, confirmados desde `tracker/data/achievements.json`):

| Cantidad | Achievement ID | Nombre del desbloqueo               |
|----------|---------------:|-------------------------------------|
| 1        | 242            | Lucky Pennies                       |
| 10       | 243            | Special Hanging Shopkeepers         |
| 30       | 244            | Wooden Nickel                       |
| 68       | 245            | Cain holds Paperclip                |
| 111      | 246            | Everything is Terrible 2!!!         |
| 234      | 247            | Special Shopkeepers                 |
| 439      | 248            | Eve now holds Razor Blade           |
| 666      | 249            | Store Key                           |
| 879      | 250            | Lost holds Holy Mantle              |
| 1000     | 251            | Keeper                              |

**Máquina de donación normal** (10 hitos, confirmados desde `tracker/data/achievements.json`):

| Cantidad | Achievement ID | Nombre del desbloqueo               |
|----------|---------------:|-------------------------------------|
| 10       | 134            | Blue Map                            |
| 20       | 151            | Store Upgrade lv.1                  |
| 50       | 135            | There's Options                     |
| 100      | 152            | Store Upgrade lv.2                  |
| 150      | 136            | Black Candle                        |
| 200      | 153            | Store Upgrade lv.3                  |
| 400      | 137            | Red Candle                          |
| 600      | 154            | Store Upgrade lv.4                  |
| 900      | 59             | Blue Candle                         |
| 999      | 138            | Stop Watch                          |

### Estados especiales

- **Contador = 0:** barra vacía, todos los hitos en gris.
- **Contador en el máximo:** barra llena, mensaje `"Máquina llena"` reemplaza la línea de resumen, todos los hitos en verde.

## Datos

### De dónde sale el contador

Los dos contadores viven en el **chunk 2 (counters)** del save file Repentance+. El parser actual estructura los 10 chunks (`_ENTRY_SIZES = (1, 4, 4, 1, 1, 1, 1, 4, 4, 1)`) pero solo decodifica los chunks 1, 4 y 7. El chunk 2 tiene 523 entradas de 4 bytes (s32 little-endian).

**Pendiente de implementación (Task 0.1 del plan):**

1. Extender `tracker/save_parser.py` para extraer el chunk 2 como lista de enteros.
2. Identificar el índice exacto del contador de la máquina normal y del de Greed dentro de ese chunk.
3. Añadir campos al dataclass `ParsedSave` (`donation_count: int`, `greed_donation_count: int`).
4. Propagar por `state_mapper.py` al estado del frontend.

**Método de identificación (sin requerir input del usuario):** usar los achievements de donación como acotamiento. Si el usuario tiene desbloqueado el achievement 250 ("Lost holds Holy Mantle"), su contador Greed es ≥ 879. Si NO tiene el 251 ("Keeper"), es < 1000. Combinando varios achievements de cada lista se acota un rango estrecho para cada contador, y se busca en el chunk 2 índices cuyo valor cumpla ambos rangos. Si el método deja ambigüedad, fallback: pedir al usuario su valor exacto en el menú Stats del juego.

### Lista de hitos

Estructura de datos en `tracker/data/donations.py` (nuevo):

```python
DONATION_MILESTONES = [
    {"amount": 10, "achievement_id": 134, "name": "Blue Map"},
    # ... 10 entradas (lista normal)
]

GREED_DONATION_MILESTONES = [
    {"amount": 1, "achievement_id": 242, "name": "Lucky Pennies"},
    # ... 10 entradas (lista greed)
]
```

`achievement_id` permite cross-validar cada hito contra el achievement byte real del save (útil para tests y para la heurística de identificación de índices).

## Arquitectura / componentes nuevos

- **`tracker/data/donations.py`** — listas de hitos para ambas máquinas.
- **`tracker/save_parser.py`** — extracción del chunk 2 y campos nuevos en `ParsedSave`.
- **`tracker/state_mapper.py`** — exponer `donations_state` con contadores e hitos enriquecidos.
- **`challenges.html`** — pestaña `data-view="donations"` con HTML + CSS + JS para las dos secciones.
- **`tracker/assets/icons/`** — sprites de las dos máquinas si los tenemos; placeholders si no.

## Tests

- **Parser:** dado un save fixture con valores conocidos de ambos contadores, `parse_save` devuelve esos enteros.
- **State mapper:** dado un `ParsedSave` con valores específicos, el estado expone los hitos correctos como desbloqueados / pendientes.
- **Donations data:** smoke test sobre `tracker/data/donations.py` (estructura correcta, cantidades ordenadas ascendentes, IDs de achievements dentro del rango del chunk de achievements, hitos clave presentes como "Lost holds Holy Mantle" a 879 Greed).
- **No se testea la UI** (consistente con resto del proyecto).

## Riesgos

- **Índices del chunk 2 desconocidos:** No documentados en el repo. **Mitigación:** heurística por achievements (descrita arriba). Si la heurística no acota a un único índice por contador, fallback a pedir al usuario los valores in-game.
- **Sprites de máquinas:** Si no están en assets, usar placeholders visuales (cuadrado gris) en la primera versión.

## Después de esta iteración

La pestaña queda diseñada para añadir más adelante:

- **Tokens de Eden** — sección adicional bajo las dos máquinas.

No se implementa nada de eso ahora.
