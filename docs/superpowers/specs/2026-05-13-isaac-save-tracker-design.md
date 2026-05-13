# Isaac Save Tracker — Diseño

**Fecha:** 2026-05-13
**Proyecto afectado:** `C:\Users\jeiko\Downloads\isaac_challenges`
**Archivos nuevos:** Carpeta `tracker/` con código Python; build artefactos: `dist/IsaacTracker.exe`
**Archivos modificados:** `challenges.html` (≈10 líneas añadidas)
**Tipo:** Funcionalidad nueva — bridge save-file → UI existente

## Contexto

`challenges.html` es un tracker single-file (HTML+CSS+JS inline) para *The Binding of Isaac: Repentance+*. Tiene dos pestañas:

- **Desafíos** — 45 challenges con checkbox, agrupados por tier S/A/B/C/D. Estado persistido en `localStorage['challenges_state']` con keys `c_${num}` (donde `num` es 1..45, el ID interno de Isaac).
- **Personajes** — rejilla 2D donde filas = completion marks (**13 marks, IDs 0..12**, definidos en `COMPLETION_MARKS` en `challenges.html` L1068-1082) y columnas = personajes (17 normales + 17 tainted, definidos en `CHARACTERS` en `challenges.html` L759-1066). Estado persistido en `localStorage['characters_state']` con keys `${slug}_unlocked` y `${slug}_mark_${markId}`.

Actualmente el usuario marca todo a mano. Quiere que se actualice automáticamente leyendo el save file de Isaac.

## Decisiones tomadas en brainstorming

| Pregunta | Decisión |
|---|---|
| ¿Mod en Isaac? | No |
| ¿Cuándo actualizar? | Al terminar la run (cuando Isaac graba el save) |
| Versión de Isaac | Repentance+ (DLC 2024) |
| Cómo se abre `challenges.html` hoy | Doble-click → file:// en navegador |
| Runtime del puente | Single `.exe`, no instalación de runtime |
| Dirección de sync | **Save manda** — sobreescribe todo en localStorage |
| Alcance | Challenges **+** matriz de personajes |
| Servidor local | **No**, sin puertos abiertos |
| Forma del ejecutable | **App con su propia ventana** (PyWebView), no abre navegador |

## Objetivo

Producir un único `IsaacTracker.exe` que el usuario abre con doble-click. Aparece una ventana de escritorio nativa que contiene el tracker (`challenges.html`). Los checkboxes y marks reflejan el estado real del save de Isaac y se actualizan automáticamente cuando el usuario termina runs.

**No-objetivos:**
- Tracking durante la run (piso actual, items, etc.). Solo end-of-run.
- Cross-plataforma. Solo Windows 11 (lo que el usuario tiene).
- Mods, inyección, hooks al juego.
- Edición manual de checkboxes desde el .exe — bloqueada por CSS `pointer-events: none`. El `.exe` es read-only respecto al juego. Si el usuario quiere editar a mano, abre el `.html` directamente como `file://`.
- Multi-slot. Se usa el slot más recientemente modificado.

## Riesgos conocidos

### R1 — Formato del save de Repentance+
**Severidad: alta**

El formato binario del save de Isaac está reverse-engineered por la comunidad pero **Repentance+ es DLC reciente (2024)**, y los parsers públicos pueden no cubrir todos los challenges/personajes nuevos.

**Mitigación:**
1. Auditar parsers públicos existentes en GitHub (e.g. `Wofsauge/IsaacSaveParser`, `bladecoding/IsaacSaveExplorer`, forks de comunidad) durante la fase de implementación, antes de escribir desde cero.
2. Si no hay parser para Repentance+, escribir uno basándose en la documentación de la comunidad (platinumgod, fandom wiki, gists comunitarios) y un save de referencia conocido del usuario.
3. Plan B: parsear solo lo común con Repentance y dejar los challenges/marks específicos de Repentance+ como "unknown" (no se marcan automáticamente, el usuario los marca a mano si quiere).

### R2 — PyWebView + WebView2
**Severidad: baja**

PyWebView usa Edge WebView2 en Windows. Win11 lo incluye; pero hay corner cases si el WebView2 runtime se desinstaló o está corrupto. **Mitigación:** detectar al arranque y mostrar mensaje guiando al usuario al instalador oficial de Microsoft si falta.

### R3 — Slugs de challenges.html vs IDs de Isaac
**Severidad: baja**

Los challenges usan ID numérico directamente (`c_1`..`c_45`), trivial. Los personajes usan slugs (`isaac`, `tainted-magdalena`, etc.) que hay que mapear a los IDs internos de Isaac (Isaac=0, Magdalene=1, ...). **Mitigación:** mapping table hardcodeado en `state_mapper.py`. Es estático, no cambia entre runs.

### R4 — Sobreescritura destructiva del estado manual del usuario
**Severidad: media (usuario aceptó pero no realizó que es irreversible)**

En la primera ejecución, el .exe sobreescribe `localStorage` con lo que diga el save. Si el save dice "challenge 5 no completado" pero el usuario lo marcó a mano en la página, se desmarca. Esto es **lo que pidió** (opción "save manda"), pero conviene confirmárselo en lenguaje plano antes de implementar.

**Mitigación:** primera ejecución hace backup de `localStorage` a la key `_pre_tracker_backup` (dentro del propio localStorage) antes de sobreescribir, para que sea reversible si se arrepiente.

**Decisión consciente — sin pantalla de bienvenida:** El usuario eligió "aplica directamente" en lugar de pantalla de confirmación previa o modo "solo añadir" en la primera ejecución. El backup en localStorage es suficiente. NO implementar wizard de primera ejecución.

## Arquitectura

Una sola aplicación de escritorio Python empaquetada como `.exe`. Internamente 5 módulos:

```
tracker/
├── app.py            # Entry point + ventana PyWebView + JS bridge
├── save_locator.py   # Encuentra persistentgamedataN.dat más reciente
├── save_parser.py    # Parsea binario → objeto Python con challenges/marks
├── state_mapper.py   # Traduce IDs Isaac → slugs/keys de localStorage
├── watcher.py        # Vigila el save file con watchdog
├── assets/
│   ├── challenges.html   # copia del HTML (con ~10 líneas añadidas)
│   ├── bossrush.png
│   └── (cualquier otro asset necesario)
└── build.spec        # PyInstaller spec → IsaacTracker.exe
```

**Tecnologías:**
- Python 3.11+
- `pywebview` para la ventana nativa
- `watchdog` para file watching
- `pyinstaller --onefile --windowed` para empaquetar

**Por qué Python y no Node/Rust/Go:** Python tiene el ecosistema más maduro para manipulación de binarios ad-hoc (`struct`, `bitarray`), parsers comunitarios de Isaac están mayoritariamente en Python o C++, PyInstaller es trivial de usar, PyWebView produce ventanas nativas sin servidor.

## Componentes

### `save_locator.py`

```python
def locate_save_file() -> Path:
    """
    Busca persistentgamedataN.dat en:
      %USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\
    Fallback:
      %USERPROFILE%\Documents\My Games\Binding of Isaac Repentance\

    Returns: ruta del archivo más recientemente modificado (mtime).
    Raises: SaveNotFoundError si no encuentra ninguno.
    """
```

Auto-detecta el slot activo por `mtime`. No expone selección manual al usuario en MVP.

### `save_parser.py`

```python
@dataclass
class ParsedSave:
    slot: int
    challenges_complete: set[int]        # ej. {1, 2, 5, 7, ...}
    characters_unlocked: set[int]        # IDs de personajes desbloqueados
    character_marks: dict[int, set[int]] # char_id → set of mark_id (0..12)
    parsed_at: datetime

def parse_save(path: Path) -> ParsedSave:
    ...
```

**Implementación:**
1. Primero auditar `pip search`/GitHub: `isaac-save-parser`, `IsaacSaveParser`, etc.
2. Si hay lib usable: wrap.
3. Si no: implementar basándose en formato documentado. El save de Isaac es un binario con header + secciones; bitfields representan unlocks. La doc de la comunidad lista offsets.

**Tests:**
- Snapshot test con save real del usuario (checkear en `tracker/tests/fixtures/sample_save_*.dat` después de pedir permiso o anonimizar).
- Test de robustez: archivo corrupto/truncado debe lanzar `SaveParseError`, nunca crashear.

### `state_mapper.py`

**Tabla canónica de personajes — 34 slugs.** Copiada literalmente de `challenges.html` (L761-1058). Las inconsistencias ortográficas (`magdalene` vs `tainted-magdalena`, `the-forgotten` vs `tainted-forgotten`, `the-lost` vs `tainted-the-lost`) **se preservan tal cual** porque son las keys reales que usa `localStorage`. **NO normalizar a inglés**.

Mapeo Isaac internal char ID → slug del HTML (IDs internos de Repentance+ — verificar en parser audit con un save real del usuario; los IDs siguientes son los publicados por la comunidad para Repentance, Repentance+ puede haber añadido personajes con IDs > 21):

```python
CHARACTER_ID_TO_SLUG = {
    # Normales (PlayerType IDs según vanilla Repentance):
    0:  "isaac",
    1:  "magdalene",
    2:  "cain",
    3:  "judas",
    4:  "blue-baby",       # Isaac internal: "???"
    5:  "eve",
    6:  "samson",
    7:  "azazel",
    8:  "lazarus",
    9:  "eden",
    10: "the-lost",
    13: "lilith",          # 11, 12 son sub-formas de Lazarus
    14: "keeper",
    15: "apollyon",
    16: "the-forgotten",
    # 17: "the-soul" — sub-forma del Forgotten, NO se trackea en este HTML
    19: "bethany",
    20: "jacob-and-esau",
    # 21 "esau" es la sub-forma de Jacob — NO se trackea
    # Tainted (PlayerType IDs 21+ aproximadamente — verificar en audit):
    21: "tainted-isaac",
    22: "tainted-magdalena",
    23: "tainted-cain",
    24: "tainted-judas",
    25: "tainted-blue-baby",
    26: "tainted-eve",
    27: "tainted-samson",
    28: "tainted-azazel",
    29: "tainted-lazarus",
    30: "tainted-eden",
    31: "tainted-the-lost",
    32: "tainted-lilith",
    33: "tainted-keeper",
    34: "tainted-apollyon",
    35: "tainted-forgotten",
    36: "tainted-bethany",
    37: "tainted-jacob-and-esau",
}
```

**13 completion marks** (canónico, copiado de `COMPLETION_MARKS` en `challenges.html` L1068-1082):

```python
MARK_ORDER = [
    (0,  "Mom's Heart / It Lives"),
    (1,  "Isaac"),
    (2,  "Satan"),
    (3,  "??? (Blue Baby)"),
    (4,  "The Lamb"),
    (5,  "Boss Rush"),
    (6,  "Hush"),
    (7,  "Mega Satan"),
    (8,  "Ultra Greed"),         # Greed mode kill (normal)
    (9,  "Ultra Greedier"),      # Greedier mode kill — bit DISTINTO en save
    (10, "Delirium"),
    (11, "Mother"),
    (12, "The Beast"),
]
```

**Crítico — Ultra Greed vs Ultra Greedier:** Son dos marks separadas (IDs 8 y 9) con bits distintos en el save. El parser tiene que distinguirlas. Esto es un error común porque visualmente parecen una sola kill; documentarlo en el código del parser.

```python
def build_localstorage_state(parsed: ParsedSave) -> dict:
    """
    Returns:
      {
        "challenges_state": {"c_1": true, "c_2": false, ..., "c_45": false},
        "characters_state": {
          "isaac_unlocked": true,
          "isaac_mark_0": true, "isaac_mark_1": true, ..., "isaac_mark_12": false,
          ...
        }
      }
    """
```

**Validación del mapeo:** Como test de regresión, `state_mapper.py` debe contener una lista hardcodeada de los 34 slugs esperados (copiada de `challenges.html`) y un test que falle si el output omite cualquiera de ellos. Esto evita que un parser que ignore tainted-X por error pase silenciosamente.

```python
EXPECTED_CHARACTER_SLUGS = [
    # Normales (17, en orden de challenges.html L761-905)
    "isaac", "cain", "apollyon", "magdalene", "lazarus", "bethany", "eden",
    "judas", "blue-baby", "eve", "samson", "azazel", "the-forgotten",
    "lilith", "jacob-and-esau", "the-lost", "keeper",
    # Tainted (17, en orden de challenges.html L914-1058)
    "tainted-cain", "tainted-isaac", "tainted-magdalena", "tainted-bethany",
    "tainted-apollyon", "tainted-judas", "tainted-lazarus", "tainted-forgotten",
    "tainted-jacob-and-esau", "tainted-eve", "tainted-azazel",
    "tainted-blue-baby", "tainted-samson", "tainted-lilith", "tainted-eden",
    "tainted-the-lost", "tainted-keeper",
]
```

### `watcher.py`

```python
class SaveWatcher:
    def __init__(self, save_path: Path, on_change: Callable[[], None]):
        ...

    def start(self): ...
    def stop(self): ...
```

Usa `watchdog.observers.Observer` apuntado al *directorio* del save (no al archivo — algunos editores recrean el archivo, y watchdog necesita ver la creación).

**Debounce 500ms:** Isaac puede escribir el save varias veces seguidas (sav file + headers). Acumula eventos y dispara `on_change` una sola vez tras 500ms de quietud.

### `app.py`

Orquestador. Estructura:

```python
class TrackerApi:
    def __init__(self, window):
        self._window = window

    def get_initial_state(self) -> dict:
        """Llamado por JS al cargar el HTML."""
        parsed = parse_save(locate_save_file())
        return build_localstorage_state(parsed)

def main():
    window = webview.create_window(
        title="Isaac Tracker",
        html=read_embedded_html(),  # challenges.html embebido vía PyInstaller --add-data
        width=900, height=900,
        resizable=True,
    )
    api = TrackerApi(window)
    window.expose(api.get_initial_state)

    def on_save_change():
        parsed = parse_save(locate_save_file())
        state = build_localstorage_state(parsed)
        window.evaluate_js(f"window.applyIsaacState({json.dumps(state)})")

    watcher = SaveWatcher(locate_save_file().parent, on_save_change)
    watcher.start()

    try:
        webview.start()
    finally:
        watcher.stop()
```

## Cambios en `challenges.html`

Solo ~15 líneas al final del `<script>`, antes del `render()` de init. Las funciones `render()` y `renderCharacterGrid()` ya existen en el HTML (verificadas en L3373 y L3621).

```js
window.applyIsaacState = function(state) {
  // Backup en primera ejecución
  if (!localStorage.getItem('_pre_tracker_backup')) {
    localStorage.setItem('_pre_tracker_backup', JSON.stringify({
      challenges: localStorage.getItem(STORAGE_KEY),
      characters: localStorage.getItem(CHAR_STORAGE_KEY),
      timestamp: new Date().toISOString(),
    }));
  }
  saveState(state.challenges_state, STORAGE_KEY);
  saveState(state.characters_state, CHAR_STORAGE_KEY);
  render();
  renderCharacterGrid();
};

// Si pywebview está disponible (estamos dentro del .exe, no en navegador puro)
if (window.pywebview) {
  window.addEventListener('pywebviewready', async () => {
    const initial = await window.pywebview.api.get_initial_state();
    window.applyIsaacState(initial);
  });
}
```

**Importante:** este código es no-op si abres el HTML como `file://` normal (sin pywebview disponible). El HTML sigue funcionando como tracker manual standalone. Esto preserva la opción de seguir abriendo el .html sin el .exe.

### Comportamiento de clicks manuales dentro del .exe

El HTML actual permite click en cualquier checkbox/celda para alternar su estado. Dentro del `.exe`, con "save manda" como política, hay tres comportamientos posibles:

| Opción | Comportamiento | Decisión |
|---|---|---|
| A — Bloquear clicks | Deshabilitar handlers de click cuando `window.pywebview` está presente. Tracker pasa a read-only en el .exe. | **Elegida.** |
| B — Permitir clicks pero efímeros | Click marca/desmarca, pero al próximo `applyIsaacState` se sobreescribe. Confuso para el usuario. | Rechazada. |
| C — Permitir clicks y persistir | Click se queda hasta que el save lo contradiga. Va contra "save manda". | Rechazada. |

**Implementación de A:** al recibir `pywebviewready`, añadir clase `tracker-locked` al `<body>` y un CSS rule `.tracker-locked input, .tracker-locked .char-grid-cell, .tracker-locked .char-grid-col-header { pointer-events: none; cursor: default; }`. Los hover-tooltips siguen funcionando (informativos). Si el usuario quiere editar a mano, abre el `.html` como `file://` (modo manual sigue disponible).

## Flujo de datos

**Cold start:**
1. Doble-click `IsaacTracker.exe`.
2. PyWebView crea ventana → carga `challenges.html` embebido.
3. Cuando el HTML emite `pywebviewready`, JS llama `api.get_initial_state()`.
4. Python localiza save → parsea → mapea → devuelve JSON.
5. JS recibe → backup localStorage si es la 1ª vez → `saveState()` → `render()` + `renderCharacterGrid()`.

**Cuando Isaac graba:**
1. Watchdog detecta cambio en `persistentgamedata*.dat`.
2. Debounce 500ms.
3. Python parsea → mapea → llama `window.evaluate_js("window.applyIsaacState(...)")`.
4. JS aplica → renders.

**Cierre:**
1. Usuario cierra ventana.
2. `webview.start()` retorna.
3. `finally: watcher.stop()` → join threads → exit.

## Manejo de errores

| Caso | Comportamiento |
|---|---|
| Save no encontrado | Ventana muestra HTML normal sin auto-tracking. Toast/banner: "No se encontró save de Isaac. Trackeo manual activo." |
| Save corrupto / unparseable | Banner rojo: "No pude leer tu save (puede ser de una versión que no conozco). Trackeo manual activo." Log a `IsaacTracker.log` junto al .exe. |
| WebView2 ausente | Mensaje al usuario con link a `https://developer.microsoft.com/microsoft-edge/webview2/` para instalar el runtime. |
| Path con caracteres especiales | Path API usa `Path` (no strings concatenados). |
| Watcher pierde eventos (FS lag) | Cada 30s, además del watchdog, hacer un poll de mtime de respaldo. Si mtime cambió y no se procesó, disparar. |
| Save cambia mientras se parsea | Try/except con retry una vez. |
| `localStorage` rechaza el set (quota) | Improbable (datos pequeños), pero log al error y mantener última versión válida. |

## Empaquetado

`build.spec` para PyInstaller:

```python
# pseudo-config
a = Analysis(
    ['tracker/app.py'],
    datas=[('tracker/assets/challenges.html', 'assets'),
           ('tracker/assets/bossrush.png', 'assets')],
    hiddenimports=['watchdog.observers.read_directory_changes'],
)
# --onefile --windowed → dist/IsaacTracker.exe
```

Build command: `pyinstaller build.spec`

Tamaño esperado del `.exe`: 25-40 MB (Python embebido + Qt/CEF de PyWebView).

## Testing

**Niveles:**

1. **Unit tests (`tracker/tests/`):**
   - `test_save_locator.py` — fixtures con timestamps fake, verifica que devuelve el más reciente.
   - `test_save_parser.py` — snapshot tests con `sample_save_*.dat` de fixtures. Edge: archivo truncado, archivo vacío, header inválido.
   - `test_state_mapper.py` — verifica que `c_5: true` aparece sólo si el challenge 5 está en el set de completados; verifica que slugs de tainted-X coinciden con `CHARACTERS` array del HTML.
   - `test_watcher.py` — escribe a un tmp file, verifica que se dispara el callback con debounce correcto.

2. **Integration test:**
   - `test_full_flow.py` — usa un save real anonimizado, corre `parse → map → build`, valida JSON resultante contra snapshot.

3. **Manual test (smoke):**
   - Plan documentado en `tracker/MANUAL_TEST.md`:
     1. Doble-click .exe → ventana se abre.
     2. Ventana carga datos del save actual (verificar tres challenges conocidos).
     3. Abrir Isaac, completar un challenge nuevo, terminar run.
     4. Volver a la ventana del tracker → en <2s nuevo challenge marcado.
     5. Cerrar ventana → no procesos zombie.

## Decisión de YAGNI

**Cosas que NO se hacen en este MVP:**
- Bandeja del sistema / autoarranque al login.
- Selección manual de slot.
- Iconos custom, splash screen, animaciones de "loading".
- Multi-monitor positioning.
- Auto-update del .exe.
- Detección de versión de Isaac (asumimos Repentance+ — falla limpia si no).
- Telemetría/analytics.
- Modo "challenge en vivo" (solo end-of-run).

Si el usuario pide alguna en el futuro, son adiciones sobre la base diseñada aquí.

## Criterios de éxito

- Doble-click `IsaacTracker.exe` → en <3 segundos hay una ventana mostrando el tracker con el estado real del save.
- Tras completar una run de Isaac y volver al menú, en <5 segundos el tracker refleja los cambios.
- El `.exe` no abre puertos, no abre el navegador, no requiere instalación previa de Python.
- Cerrar la ventana cierra todos los procesos limpiamente.
- Si el save no se puede leer, la ventana sigue funcionando como tracker manual (no se cuelga).

## Plan de implementación (alto nivel)

Detalle del plan de implementación se elabora en el siguiente paso (skill `writing-plans`). Bloques esperados:

1. Auditar parsers públicos de Repentance+ y elegir base.
2. Implementar `save_locator` + tests.
3. Implementar `save_parser` (incluye decisión final del paso 1) + tests.
4. Implementar `state_mapper` con tabla de slugs cross-referenciada con el HTML + tests.
5. Implementar `watcher` con debounce + tests.
6. Implementar `app.py` con bridge PyWebView.
7. Añadir `applyIsaacState` y bootstrap a `challenges.html`.
8. Smoke test manual end-to-end.
9. Configurar PyInstaller y producir `dist/IsaacTracker.exe`.
10. Smoke test del `.exe` empaquetado.
