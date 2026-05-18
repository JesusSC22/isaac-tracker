"""One-command release pipeline for IsaacTracker.

Usage:
    python release.py 1.2.0 "Lo que cambia en esta versión"

Steps:
  1. Validate version format and that it is strictly greater than the current.
  2. Verify working tree is clean and on the main branch.
  3. Write the new version into tracker/_version.py.
  4. Commit, tag v<version>.
  5. Build dist/IsaacTracker.exe with PyInstaller.
  6. Push commit + tag to origin.
  7. Create a GitHub release with the .exe attached.

Requirements:
  - gh CLI authenticated, active account = JesusSC22.
  - PyInstaller installed (preferably in .venv).
  - The repository's remote `origin` points at JesusSC22/isaac-tracker.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "JesusSC22/isaac-tracker"
REQUIRED_GH_ACCOUNT = "JesusSC22"
MAIN_BRANCH = "main"
EXE_PATH = Path("dist/IsaacTracker.exe")
VERSION_FILE = Path("tracker/_version.py")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def die(msg: str, code: int = 1) -> None:
    print(f"[release] ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print(f"[release] $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def read_current_version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not m:
        die(f"could not parse __version__ in {VERSION_FILE}")
    return m.group(1)


def parse_semver(s: str) -> tuple[int, int, int]:
    if not SEMVER_RE.match(s):
        die(f"invalid version {s!r}; expected MAJOR.MINOR.PATCH (e.g. 1.2.0)")
    a, b, c = s.split(".")
    return int(a), int(b), int(c)


def ensure_clean_tree() -> None:
    out = subprocess.run(
        ["git", "status", "--porcelain"], check=True, text=True, capture_output=True
    ).stdout
    if out.strip():
        die(
            "working tree is not clean — commit, stash, or discard your changes before releasing.\n"
            f"--- git status ---\n{out}"
        )


def ensure_on_main() -> None:
    out = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], check=True, text=True, capture_output=True
    ).stdout.strip()
    if out != MAIN_BRANCH:
        die(f"current branch is {out!r}, expected {MAIN_BRANCH!r}. Switch branches first.")


def ensure_gh_account() -> None:
    proc = subprocess.run(["gh", "auth", "status"], text=True, capture_output=True)
    combined = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        die("gh CLI is not authenticated. Run `gh auth login` first.")
    # Look for an "Active account: true" line preceded by our required account.
    blocks = re.split(r"\n(?=\s*-?\s*[A-Z])", combined)  # rough split per account block
    active_account: str | None = None
    for block in re.split(r"(?=Logged in to github\.com account )", combined):
        if "Active account: true" in block:
            m = re.search(r"account\s+(\S+)", block)
            if m:
                active_account = m.group(1)
                break
    if active_account is None:
        die("could not determine which gh account is active. Run `gh auth status` to inspect.")
    if active_account != REQUIRED_GH_ACCOUNT:
        die(
            f"active gh account is {active_account!r}, expected {REQUIRED_GH_ACCOUNT!r}.\n"
            f"Run: gh auth switch --user {REQUIRED_GH_ACCOUNT}"
        )


def write_version(new_version: str) -> None:
    VERSION_FILE.write_text(f'__version__ = "{new_version}"\n', encoding="utf-8")


def find_pyinstaller() -> list[str]:
    venv_exe = Path(".venv/Scripts/pyinstaller.exe")
    if venv_exe.exists():
        return [str(venv_exe)]
    if shutil.which("pyinstaller"):
        return ["pyinstaller"]
    die("pyinstaller not found in .venv or on PATH. `pip install pyinstaller` in the venv.")
    return []  # unreachable


def build_exe() -> None:
    if EXE_PATH.exists():
        EXE_PATH.unlink()
    cmd = find_pyinstaller() + ["build.spec", "--noconfirm", "--clean"]
    run(cmd)
    if not EXE_PATH.exists():
        die(f"build finished but {EXE_PATH} was not produced.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", help="New version, MAJOR.MINOR.PATCH")
    ap.add_argument("notes", help="Release notes shown to users on GitHub")
    ap.add_argument("--no-push", action="store_true", help="Skip git push and gh release create (dry build).")
    args = ap.parse_args()

    new_v = parse_semver(args.version)
    cur_v = parse_semver(read_current_version())
    if new_v <= cur_v:
        die(f"new version {args.version} is not greater than current {'.'.join(map(str, cur_v))}.")

    ensure_clean_tree()
    ensure_on_main()
    if not args.no_push:
        ensure_gh_account()

    write_version(args.version)
    run(["git", "add", str(VERSION_FILE)])
    run(["git", "commit", "-m", f"release: v{args.version}"])
    tag = f"v{args.version}"
    run(["git", "tag", tag])

    build_exe()

    if args.no_push:
        print(f"[release] --no-push set; built {EXE_PATH} but did not push or publish release.")
        return

    run(["git", "push", "origin", MAIN_BRANCH])
    run(["git", "push", "origin", tag])
    run([
        "gh", "release", "create", tag, str(EXE_PATH),
        "--repo", REPO,
        "--title", tag,
        "--notes", args.notes,
    ])
    print(f"[release] Done. v{args.version} is live on https://github.com/{REPO}/releases/tag/{tag}")


if __name__ == "__main__":
    main()
