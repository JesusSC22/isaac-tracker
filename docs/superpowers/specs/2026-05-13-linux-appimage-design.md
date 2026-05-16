# IsaacTracker en Linux (AppImage) — design

**Fecha:** 2026-05-13
**Goal:** Generar un AppImage de IsaacTracker que corra en Steam Deck (SteamOS 3, Plasma) y otras distros Linux modernas, manteniendo la build de Windows intacta.

## Decisiones

- **Formato de entrega:** AppImage (un único archivo ejecutable, sin instalación).
- **Builder:** PyInstaller dentro de WSL (Ubuntu) → `appimagetool` empaqueta el resultado.
- **GUI backend:** pywebview en Linux usa GTK + WebKit2 por defecto. Bundlamos lo mínimo y dejamos que el sistema aporte WebKit2 (en Steam Deck Plasma viene con webkit2gtk).
- **Save locator:** se añaden rutas Linux a `tracker/save_locator.py`; las de Windows quedan tal cual.

## Rutas Linux a buscar (en orden)

1. `~/.local/share/Steam/userdata/<id>/250900/remote/rep+persistentgamedata*.dat` — Steam Cloud sync. Es la fuente principal.
2. `~/.steam/steam/userdata/<id>/250900/remote/...` — symlink frecuente al anterior; lo incluimos por si la distro no lo enlaza.
3. `~/.var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/<id>/250900/remote/...` — Steam vía Flatpak (no es el caso del Steam Deck pero lo cubrimos).
4. `~/.local/share/Steam/steamapps/compatdata/250900/pfx/drive_c/users/steamuser/Documents/My Games/Binding of Isaac Repentance+/save_backups/` — backups locales generados por Isaac dentro del prefix de Proton.

## Cambios al código

- `save_locator.py`: factor out una función `_find_steam_userdata_roots_linux()` paralela a la de Windows; `iter_repentance_plus_saves` itera ambas listas.
- `app.py`: el guard `if sys.platform != "win32": return` en `_apply_window_icon` ya cubre el caso Linux (no-op). No tocar.
- `build_linux.spec` (nuevo): copia de `build.spec` adaptada para Linux (sin `icon=*.ico`, mismo `datas`, mismo `excludes`).

## Build flow

```
tools/build_all.ps1 (Windows host)
├── pyinstaller build.spec                              → dist/IsaacTracker.exe
└── wsl bash tools/build_appimage.sh                    → dist/IsaacTracker.AppImage
    ├── pyinstaller build_linux.spec                    → dist/linux/IsaacTracker/
    └── appimagetool dist/linux/IsaacTracker.AppDir     → dist/IsaacTracker.AppImage
```

## Riesgos conocidos

- **pywebview + WebKit2GTK:** El Steam Deck Plasma trae `webkit2gtk` 4.x. Si pywebview en runtime no lo encuentra, el AppImage abrirá una ventana en blanco. Mitigación: el AppImage incluye `webkit2gtk` como dependency runtime; si falta, fallback claro con mensaje.
- **WSLg requerido para test local:** Windows 11 con WSL2 trae WSLg (GUI). Solo necesitamos arrancar la ventana, no leer save. Si falla GUI en WSL no es bloqueante para que funcione en Steam Deck.

## Out of scope

- No reescribimos UI ni save_parser. Ambos son cross-platform como están.
- No soportamos Isaac de Mac (formato de save es el mismo pero las rutas son otras y nadie lo ha pedido).
