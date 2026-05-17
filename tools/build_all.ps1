# Build both IsaacTracker.exe (Windows) and IsaacTracker.AppImage (Linux).
# Run from the repo root in Windows PowerShell:
#   .\tools\build_all.ps1
#
# - Windows .exe is produced first using the local .venv.
# - Linux AppImage is built by invoking the WSL Ubuntu distro.
# - If WSL is not installed or not initialised, the Linux step is skipped
#   with a clear warning. The .exe build is not affected.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host '=== Step 1/2: Building Windows .exe ===' -ForegroundColor Cyan
$pyinstaller = Join-Path $RepoRoot '.venv\Scripts\pyinstaller.exe'
if (-not (Test-Path $pyinstaller)) {
    Write-Host "PyInstaller not found at $pyinstaller. Run 'python -m venv .venv; .\.venv\Scripts\pip install pyinstaller pywebview watchdog' first." -ForegroundColor Red
    exit 1
}
& $pyinstaller --noconfirm build.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host '[build_all] Windows build failed.' -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host '[build_all] Windows .exe ready at dist\IsaacTracker.exe' -ForegroundColor Green

Write-Host ''
Write-Host '=== Step 2/2: Building Linux AppImage (via WSL) ===' -ForegroundColor Cyan
$wslAvailable = $false
try {
    $wslList = & wsl.exe --list --quiet 2>$null
    if ($LASTEXITCODE -eq 0 -and $wslList) {
        $wslAvailable = $true
    }
} catch {
    $wslAvailable = $false
}

if (-not $wslAvailable) {
    Write-Host '[build_all] WSL is not installed or Ubuntu is not configured yet.' -ForegroundColor Yellow
    Write-Host '[build_all] Skipping Linux AppImage build.' -ForegroundColor Yellow
    Write-Host '[build_all] To enable: open Ubuntu from the Start menu and finish first-run setup, then re-run this script.' -ForegroundColor Yellow
    exit 0
}

# Convert Windows path to WSL path (C:\foo\bar -> /mnt/c/foo/bar).
$wslRoot = '/mnt/' + $RepoRoot.Substring(0,1).ToLower() + ($RepoRoot.Substring(2) -replace '\\','/')

Write-Host "[build_all] WSL repo path: $wslRoot"
& wsl.exe bash -lc "cd '$wslRoot' && bash tools/build_appimage.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host '[build_all] AppImage build failed inside WSL.' -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ''
Write-Host '[build_all] All builds finished:' -ForegroundColor Green
Write-Host '  dist\IsaacTracker.exe' -ForegroundColor Green
Write-Host '  dist\IsaacTracker-x86_64.AppImage' -ForegroundColor Green
