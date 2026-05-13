# Rediseño de la pestaña Logros — Cuadrícula adaptativa

**Fecha:** 2026-05-13
**Archivo afectado:** `tracker/assets/challenges.html` (único archivo del tracker)
**Tipo:** Cambio de presentación (CSS + ancho de contenedor). No toca lógica de datos.

## Contexto

La pestaña **Logros** se introdujo en el spec `2026-05-13-isaac-achievements-tab-design.md`. Hoy renderiza 641 logros como **una lista vertical en una única columna** dentro del contenedor central de 400px del tracker. Cada fila tiene check/X, ícono pequeño (32px), nombre, descripción y `#id`, agrupados en secciones colapsables (Personajes Desbloqueados, Marcas de Personaje, etc.).

El usuario reporta que se ve "muy complicado": íconos demasiado pequeños, mucho scroll, demasiada información apretada en una sola columna estrecha.

## Objetivo

Hacer que la sección de Logros sea más fácil de leer y aproveche más pantalla, manteniendo todo lo demás (secciones colapsables, barra de progreso, lógica de marcado automático).

## Decisiones tomadas en brainstorming

| Pregunta | Decisión |
|---|---|
| Estilo general | Cuadrícula de tarjetas (cada logro como fila con ícono + texto) |
| Cuántas columnas | Adaptativo según ancho de ventana |
| Ancho global del tracker | Subir de 400px → 1200px (afecta a todas las pestañas) |
| ¿Romper layout actual de Desafíos/Personajes? | No — el ancho mayor da más espacio pero los contenidos internos mantienen sus estilos |

## Cambios concretos

### 1. Contenedor global

```css
.container { max-width: 1200px; }  /* antes: 400px */
```

Impacto en otras pestañas:
- **Desafíos**: la lista de 45 challenges seguirá centrada y legible. Como las filas son `display: flex`, se estirarán hasta 1200px de ancho. Si esto se ve raro (filas demasiado anchas), aplicamos `max-width: 500px; margin: 0 auto` a la lista de challenges para mantener su tamaño actual.
- **Personajes**: `#character-grid` ya usa `width: calc(100vw - 40px)` y rompe el container actual, así que no se ve afectado.
- **Header / barra de progreso global / tabs**: se estiran al nuevo ancho. Bien, así se ven más cómodos en pantallas modernas.

### 2. Cuadrícula adaptativa en Logros

Reemplazar `.ach-category-body` de bloque vertical a CSS Grid auto-fit:

```css
.ach-category-body {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1px;
  background: rgba(255,255,255,0.05); /* línea separadora entre celdas */
  padding: 0;
}
.ach-item {
  background: #16213e;  /* color de fondo de la sección */
  border-top: none;     /* el gap del grid hace de separador */
}
```

Breakpoints resultantes (minmax 360px):
- < 760px: 1 columna
- 760–1120px: 2 columnas
- 1120–1480px: 3 columnas (típico en 1080p/1440p)
- 1480px+: 4 columnas

### 3. Tamaños dentro de cada fila

| Elemento | Antes | Después |
|---|---|---|
| Padding fila | `8px 14px` | `12px 16px` |
| Estado ✓/✗ | `1rem`, 18px ancho | `1.3rem`, 22px ancho |
| Ícono | `32x32`, max 32px | `48x48`, max 48px |
| Nombre | `0.9rem` | `1.05rem` |
| Descripción | `0.78rem` | `0.9rem` |
| `#id` | `0.72rem`, 36px ancho | `0.78rem`, 44px ancho |
| Gap entre elementos | `10px` | `14px` |

### 4. Lo que NO cambia

- Datos: las 641 entradas, la categorización, la lógica de "completado" automática desde el save.
- Estado completado: nombre tachado verde apagado, ícono atenuado en grayscale.
- Secciones colapsables: misma estructura, mismo header con título + contador, mismo toggle ▼/►.
- Barra de progreso global (la del top con "Logros: 400 / 641 (62%)").
- Lógica JS de render (`renderAchievements`), solo cambia el CSS resultante.

## Riesgo conocido

**Layout de Desafíos a 1200px de ancho** — la lista de challenges está pensada para 400px. Si al ensancharla se ve incómoda (filas demasiado largas, mucho espacio en blanco), aplicamos un `max-width` interno a esa lista específicamente. No es un riesgo de funcionalidad, solo estético, y se ve inmediatamente al abrir el tracker.

## Verificación

1. Abrir `tracker/assets/challenges.html` en el navegador.
2. **Logros**: confirmar que en ventana ancha hay 3-4 columnas, en ventana angosta 1-2, sin solapamientos.
3. **Desafíos**: confirmar que la lista sigue legible y centrada.
4. **Personajes**: confirmar que la rejilla 2D sigue ocupando el ancho completo como antes.
5. **Barra de progreso superior y tabs**: confirmar que se ven centradas y proporcionadas.
