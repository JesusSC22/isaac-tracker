# Auto-update System — Design Spec

**Date:** 2026-05-18
**Status:** Approved (verbal, in chat)

## Goal

Ship updates of `IsaacTracker.exe` to end users (currently: one friend) without
the developer having to manually send the binary each release. Updates apply
in-place from inside the running app — no browser, no manual file replacement.

## User-visible behaviour

### Friend (end user)

1. Opens the tracker as always.
2. If a newer version exists on GitHub, a yellow banner appears at the top:
   `Nueva versión X.Y.Z disponible · [Actualizar ahora] [×]`
3. Click "Actualizar ahora" → progress bar appears (`Descargando… 73%`).
4. When download finishes, the tracker closes and reopens automatically on the
   new version.
5. If GitHub is unreachable, the banner never appears — the app works normally.
6. The `×` dismisses the banner for this session only; it reappears next launch.

### Developer (user)

To publish a new version, one command:

```
python release.py 1.2.0 "Lo que cambia"
```

That command:
1. Writes the version into `tracker/_version.py`.
2. Runs PyInstaller to build `dist/IsaacTracker.exe`.
3. Creates a GitHub release `v1.2.0` on `JesusSC22/isaac-tracker` with the
   `.exe` attached as a release asset and the message as release notes.

## Architecture

### Components

| File | Purpose |
|------|---------|
| `tracker/_version.py` | Single source of truth: `__version__ = "1.0.0"` |
| `tracker/updater.py` | Check GitHub releases, download new exe, swap files |
| `tracker/app.py` | Wires updater into TrackerApi; banner JS hook |
| `challenges.html` | Renders the update banner + progress UI |
| `release.py` | Build + publish pipeline |

### Data flow

```
[App start]
   │
   └─> updater.check_async()  (background thread, non-blocking)
         │
         ├─ HTTP GET api.github.com/repos/JesusSC22/isaac-tracker/releases/latest
         ├─ Compare tag (vX.Y.Z) to tracker._version.__version__
         ├─ If newer: call window.showUpdateBanner({version, asset_url})
         └─ On any error: log and stay silent

[User clicks "Actualizar ahora"]
   │
   └─> JS calls api.apply_update()
         │
         ├─ Check write permission on dir(sys.executable)
         │     └─ If denied: open browser to release page, return early
         ├─ Download asset to <exe_dir>/IsaacTracker.new.exe
         │     └─ Stream chunks, callback JS with progress %
         ├─ Write <exe_dir>/_update.bat (see Update swap below)
         ├─ subprocess.Popen([bat])  (detached, new console=False)
         └─ Cleanly close pywebview window  → process exits

[ _update.bat runs ]
   │
   ├─ Wait for IsaacTracker.exe process to exit
   ├─ move /Y IsaacTracker.new.exe → IsaacTracker.exe
   ├─ start "" IsaacTracker.exe
   └─ del %~f0   (self-delete)
```

### Update swap (Windows constraint)

Windows refuses to overwrite a running `.exe`. The standard workaround:
download the new binary next to the old one with a different name, then have a
tiny helper script (cmd `.bat`) wait for the original process to exit, move the
new file over the old, and relaunch.

`_update.bat` contents:

```bat
@echo off
:wait
timeout /t 1 /nobreak >nul
tasklist /FI "IMAGENAME eq IsaacTracker.exe" 2>nul | find /I "IsaacTracker.exe" >nul && goto wait
move /Y "%~dp0IsaacTracker.new.exe" "%~dp0IsaacTracker.exe"
start "" "%~dp0IsaacTracker.exe"
(goto) 2>nul & del "%~f0"
```

The `(goto) 2>nul & del "%~f0"` pattern is the canonical self-deleting cmd
trick (the parser has already consumed the script into memory; deleting the
file mid-execution is safe).

### Permission fallback

`os.access(dir_of_sys_executable, os.W_OK)` before downloading. If false (e.g.
the exe sits under `C:\Program Files\`), the JS gets `mode: "manual"` instead
of starting download — banner button text changes to "Descargar manualmente"
and clicking it opens the GitHub release page via `webbrowser.open`.

This case is rare for our user (their friend will keep the `.exe` in a normal
user folder), but failing silently here would be worse than the fallback.

### Version comparison

Tags use `vX.Y.Z` (semver). Strip the leading `v`, split on `.`, compare as
tuples of ints. Simple, no `packaging` dep needed.

### Error handling (silent on the user's side)

| Error | Behaviour |
|-------|-----------|
| Network down / GitHub 5xx / timeout | No banner. App works normally. |
| GitHub rate limit hit | No banner. |
| Latest release has no `.exe` asset | No banner. |
| Download fails midway | Partial `.new.exe` left in place; banner stays so user can retry; next launch will try again. |
| `_update.bat` fails (e.g. AV intercepts) | App reopens with old version. No data lost. |
| No write permission | Fallback to browser open. |

## Release script (`release.py`)

```
python release.py <version> <release_notes>
```

Steps:
1. Validate `<version>` matches `^\d+\.\d+\.\d+$`.
2. Write `tracker/_version.py` with new version.
3. `git add tracker/_version.py && git commit -m "release: v<version>"`.
4. `git tag v<version>`.
5. Run `pyinstaller build.spec` → produces `dist/IsaacTracker.exe`.
6. `git push && git push --tags`.
7. `gh release create v<version> dist/IsaacTracker.exe --notes "<release_notes>"
   --repo JesusSC22/isaac-tracker`.

Requires `gh` CLI authenticated as `JesusSC22` (currently both `JesusSC22` and
`jesussilva-mmvr` are logged in; the active account must be switched before
the first release with `gh auth switch -u JesusSC22`).

## Initial setup (one-time)

1. Switch active gh account to `JesusSC22`.
2. `gh repo create JesusSC22/isaac-tracker --public --source=. --remote=origin --push`.
3. Implement the code changes above.
4. Build v1.0.0 and publish first release.
5. Hand the release page URL to the user so they pass it to their friend
   *one last time*. After that, the friend sees updates in-app.

## What is explicitly NOT in scope

- Signing the binary (no code-signing cert).
- Delta updates (full `.exe` each time, ~30 MB).
- Multi-platform (Windows only; Linux AppImage uses a different flow).
- Rollback to older versions from inside the app.
- Telemetry on update success/failure.
- Cryptographic verification of the downloaded `.exe` (the GitHub release URL
  is HTTPS-served by GitHub itself; for a personal-use tracker with one
  friend, this is acceptable).
