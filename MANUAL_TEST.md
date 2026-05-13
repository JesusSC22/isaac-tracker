# IsaacTracker — Manual Smoke Test

Run this before shipping the .exe to the user.

## Preconditions
- Windows 11 64-bit.
- Microsoft Edge WebView2 Runtime installed (preinstalled on Win11).
- The Binding of Isaac: Repentance+ installed with at least one save slot in use.

## Test 1 — Cold launch shows real save state
1. Double-click `dist\IsaacTracker.exe`.
2. Window opens within ~5 seconds.
3. Open the "Desafíos" tab (default).
4. Check that 2-3 challenges you KNOW you completed are marked.
5. Switch to "Personajes" tab; verify the grid is populated.

## Test 2 — Read-only behaviour
1. With the window open, click any challenge checkbox.
2. EXPECTED: checkbox does not toggle (read-only mode).
3. Click the "Mostrar Tainted" button.
4. EXPECTED: Tainted characters appear (toggle still works).
5. Click between tabs.
6. EXPECTED: tabs switch.

## Test 3 — Live update after a run
1. With the tracker window open, launch Isaac.
2. Complete any challenge or kill any boss you haven't beaten yet.
3. Return to the main menu (this is when Isaac writes the save).
4. EXPECTED: within ~5 seconds, the new state is visible in the tracker (refresh F5 if needed, but it should be automatic).

## Test 4 — Clean shutdown
1. Close the tracker window.
2. Open Task Manager → Details tab.
3. EXPECTED: no `IsaacTracker.exe` lingering.

## Test 5 — Backup created
1. Open the bundled HTML once via `challenges.html` (file://) in your default browser.
2. Open DevTools (F12) → Application → Local Storage → file://.
3. EXPECTED: a key `_pre_tracker_backup` exists, containing your pre-tracker state from your first .exe launch.

## Troubleshooting
- If the window does not open, check `IsaacTracker.log` next to the .exe.
- If Edge WebView2 is missing, install from <https://developer.microsoft.com/microsoft-edge/webview2/>.
- If the parser fails on your save, check `tracker\PARSER_AUDIT.md` — that is the documented save format.
