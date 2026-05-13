# Isaac Save Tracker Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers-extended-cc:subagent-driven-development (if subagents available) or superpowers-extended-cc:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single Windows `.exe` (`IsaacTracker.exe`) that opens its own desktop window showing `challenges.html`, parses the user's *Binding of Isaac: Repentance+* save file, and auto-updates the displayed checkboxes/marks at end-of-run.

**Architecture:** Python 3.11 + PyWebView (Edge WebView2) + watchdog, packaged with PyInstaller (`--onefile --windowed`). Single window, no HTTP server, no open ports. Save file is source of truth; localStorage is overwritten. JS click handlers are disabled inside the .exe (read-only UI).

**Tech Stack:** Python 3.11, `pywebview`, `watchdog`, `pyinstaller` (dev only), `pytest` (dev only).

**Reference spec:** `docs/superpowers/specs/2026-05-13-isaac-save-tracker-design.md`

---

## Pre-flight: Environment

This project is currently NOT a git repository. If you want to use the commit steps in this plan, run `git init` first. Otherwise, treat commits as optional milestone snapshots — the work is still valid.

The user is on Windows 11 with PowerShell as the default shell. All shell commands assume PowerShell. The Python install used for development MUST be 64-bit Python 3.11+ (PyWebView with WebView2 backend requires 64-bit on Windows).

## File Structure

```
isaac_challenges/
├── challenges.html                       # MODIFIED: add applyIsaacState() + lock CSS
├── bossrush.png                          # untouched
├── tracker/
│   ├── __init__.py                       # empty marker
│   ├── app.py                            # PyWebView window + orchestration
│   ├── save_locator.py                   # find latest persistentgamedataN.dat
│   ├── save_parser.py                    # parse binary → ParsedSave dataclass
│   ├── state_mapper.py                   # ParsedSave → localStorage JSON
│   ├── watcher.py                        # watchdog wrapper + debounce
│   ├── exceptions.py                     # SaveNotFoundError, SaveParseError
│   ├── assets/
│   │   └── challenges.html               # COPY of root challenges.html (bundled)
│   └── PARSER_AUDIT.md                   # Task 2 output: which parser approach
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # pytest fixtures
│   ├── test_save_locator.py
│   ├── test_save_parser.py
│   ├── test_state_mapper.py
│   ├── test_watcher.py
│   └── fixtures/
│       └── (sample_save_*.dat collected during impl)
├── build.spec                            # PyInstaller config
├── requirements.txt                      # runtime deps
├── requirements-dev.txt                  # dev-only deps
├── MANUAL_TEST.md                        # smoke test plan
└── docs/superpowers/
    ├── specs/2026-05-13-isaac-save-tracker-design.md     # already exists
    └── plans/2026-05-13-isaac-save-tracker.md            # this plan
```

**Key boundaries:**
- `save_locator` knows about filesystem, returns `Path`. No parsing.
- `save_parser` takes a `Path` and returns `ParsedSave`. No filesystem watching, no UI.
- `state_mapper` takes `ParsedSave` and returns `dict`. No I/O.
- `watcher` takes a directory and a callback. No parsing.
- `app` is the only module that glues all four together and talks to PyWebView.

This isolation is what makes each component testable without the others.

---

## Task 0: Project skeleton + dependencies

**Files:**
- Create: `tracker/__init__.py` (empty)
- Create: `tracker/assets/.gitkeep` (empty)
- Create: `tests/__init__.py` (empty)
- Create: `tests/fixtures/.gitkeep` (empty)
- Create: `requirements.txt`
- Create: `requirements-dev.txt`

- [ ] **Step 1: Create empty package markers**

```powershell
New-Item -ItemType Directory -Path tracker, tracker\assets, tests, tests\fixtures -Force
New-Item -ItemType File -Path tracker\__init__.py, tracker\assets\.gitkeep, tests\__init__.py, tests\fixtures\.gitkeep -Force
```

- [ ] **Step 2: Write `requirements.txt`**

```
pywebview==5.3.2
watchdog==4.0.2
```

- [ ] **Step 3: Write `requirements-dev.txt`**

```
-r requirements.txt
pyinstaller==6.10.0
pytest==8.3.3
```

- [ ] **Step 4: Create virtualenv and install dev deps**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Expected: pip prints "Successfully installed pywebview-5.3.2 watchdog-4.0.2 pyinstaller-6.10.0 pytest-8.3.3 ..." with no error.

- [ ] **Step 5: Verify imports**

```powershell
python -c "import webview, watchdog.observers; print('ok')"
```

Expected: prints `ok`. If `import webview` fails: `pywebview` needs `pywebview[edgechromium]` extra, install that instead.

- [ ] **Step 6: Optional commit**

```powershell
git add tracker tests requirements.txt requirements-dev.txt; if ($?) { git commit -m "chore: scaffold tracker package" }
```

---

## Task 1: Exception classes

**Files:**
- Create: `tracker/exceptions.py`
- Test: `tests/test_exceptions.py` (tiny smoke)

- [ ] **Step 1: Write the failing test**

`tests/test_exceptions.py`:

```python
from tracker.exceptions import SaveNotFoundError, SaveParseError


def test_save_not_found_is_exception():
    assert issubclass(SaveNotFoundError, Exception)


def test_save_parse_error_is_exception():
    assert issubclass(SaveParseError, Exception)


def test_save_parse_error_carries_path():
    err = SaveParseError("bad header", path="C:\\foo\\bar.dat")
    assert "bad header" in str(err)
    assert err.path == "C:\\foo\\bar.dat"
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
pytest tests/test_exceptions.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'tracker.exceptions'`.

- [ ] **Step 3: Write minimal implementation**

`tracker/exceptions.py`:

```python
class SaveNotFoundError(Exception):
    """No persistentgamedata*.dat found in expected locations."""


class SaveParseError(Exception):
    """Raised when a save file cannot be parsed."""

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message)
        self.path = path
```

- [ ] **Step 4: Run test to verify it passes**

```powershell
pytest tests/test_exceptions.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Optional commit**

```powershell
git add tracker/exceptions.py tests/test_exceptions.py; if ($?) { git commit -m "feat: tracker exception types" }
```

---

## Task 2: save_locator — find latest save file

**Files:**
- Create: `tracker/save_locator.py`
- Test: `tests/test_save_locator.py`

- [ ] **Step 1: Write failing tests**

`tests/test_save_locator.py`:

```python
import os
import time
from pathlib import Path

import pytest

from tracker.exceptions import SaveNotFoundError
from tracker.save_locator import locate_save_file, find_save_directory


def test_find_save_directory_repentance_plus_priority(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rep_plus = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+"
    rep = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance"
    rep_plus.mkdir(parents=True)
    rep.mkdir(parents=True)
    assert find_save_directory() == rep_plus


def test_find_save_directory_falls_back_to_repentance(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rep = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance"
    rep.mkdir(parents=True)
    assert find_save_directory() == rep


def test_find_save_directory_raises_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    with pytest.raises(SaveNotFoundError):
        find_save_directory()


def test_locate_save_file_picks_most_recent(tmp_path, monkeypatch):
    save_dir = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+"
    save_dir.mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    for slot, mtime_offset in [(1, -300), (2, -100), (3, -200)]:
        f = save_dir / f"persistentgamedata{slot}.dat"
        f.write_bytes(b"x")
        now = time.time()
        os.utime(f, (now + mtime_offset, now + mtime_offset))

    result = locate_save_file()
    assert result.name == "persistentgamedata2.dat"


def test_locate_save_file_raises_when_no_dat_files(tmp_path, monkeypatch):
    save_dir = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+"
    save_dir.mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    with pytest.raises(SaveNotFoundError):
        locate_save_file()
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_save_locator.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement `tracker/save_locator.py`**

```python
import os
from pathlib import Path

from tracker.exceptions import SaveNotFoundError

_CANDIDATE_DIRNAMES = [
    "Binding of Isaac Repentance+",
    "Binding of Isaac Repentance",
]


def find_save_directory() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        raise SaveNotFoundError("USERPROFILE environment variable is not set")
    base = Path(user_profile) / "Documents" / "My Games"
    for name in _CANDIDATE_DIRNAMES:
        candidate = base / name
        if candidate.is_dir():
            return candidate
    raise SaveNotFoundError(f"No Isaac save directory found under {base}")


def locate_save_file() -> Path:
    save_dir = find_save_directory()
    dat_files = list(save_dir.glob("persistentgamedata*.dat"))
    if not dat_files:
        raise SaveNotFoundError(f"No persistentgamedata*.dat files in {save_dir}")
    return max(dat_files, key=lambda p: p.stat().st_mtime)
```

- [ ] **Step 4: Run tests, verify pass**

```powershell
pytest tests/test_save_locator.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Smoke test against real system**

```powershell
python -c "from tracker.save_locator import locate_save_file; print(locate_save_file())"
```

Expected: prints a real path like `C:\Users\jeiko\Documents\My Games\Binding of Isaac Repentance+\persistentgamedata1.dat`. If user has no Isaac installed yet, expected `SaveNotFoundError` — that's fine, the parser tasks need a real save to validate, see Task 3.

- [ ] **Step 6: Commit**

```powershell
git add tracker/save_locator.py tests/test_save_locator.py; if ($?) { git commit -m "feat: locate latest Isaac save by mtime" }
```

---

## Task 3: Parser audit — decide approach

**Files:**
- Create: `tracker/PARSER_AUDIT.md`
- Collect: `tests/fixtures/sample_save_repentance_plus.dat` (a real save from user)

This task is research, not TDD. The goal is a documented decision before writing any parser code.

- [ ] **Step 1: Collect a real save file as ground truth**

Ask the user to copy their current `persistentgamedata1.dat` (or whatever slot they actively use) into `tests/fixtures/sample_save_repentance_plus.dat`. **If they can also note ~5 challenges they know are complete and ~3 character-mark combinations they know are done, write those notes into BOTH `tests/fixtures/sample_save_known_completions.md` (human-readable) AND `tests/fixtures/sample_save_known_completions.json` (test-consumable)** — those are the ground truth for parser correctness later.

JSON shape required by Task 5 fixtures:

```json
{
  "challenges_done": [1, 9, 30],
  "characters_unlocked": [0, 1, 2, 8],
  "character_marks_done": {
    "0": [0, 1, 2],
    "8": [0]
  }
}
```

(Character keys are stringified ints because JSON object keys are strings; the test converts them.)

If the user cannot or will not share their save, mark `sample_save_repentance_plus.dat` as missing in `PARSER_AUDIT.md` and have the implementation fall back to a synthetic fixture for tests. Parser correctness against real Repentance+ saves will only be verifiable in the final smoke test in that case.

- [ ] **Step 2: Search for existing parsers**

Search GitHub and pypi for parsers covering Repentance / Repentance+. Useful queries:

- `site:github.com isaac save parser repentance`
- `pip search isaac` (or `pip index versions <candidate>`)
- Known historical libs to check: `Wofsauge/IsaacSaveParser` (TBoI Save Editor — C#, format docs may help), `bladecoding/isaac-save-explorer`, community gists.

Look at the **community-documented save format** specifically: <https://bindingofisaacrebirth.fandom.com/wiki/Save_File> and any Repentance addenda.

- [ ] **Step 3: Write `tracker/PARSER_AUDIT.md`**

Document:
- Each parser/lib evaluated, last update date, language, what it covers.
- Whether Repentance+ is supported.
- Decision: (A) vendor an existing lib if Python-compatible and recent, (B) port from C#/JS docs, or (C) write from scratch from format docs.
- If (B) or (C): list the byte offsets / structure used (challenges bitmap section, character unlocks section, completion marks per character section). Include section header signatures (Isaac save files typically have section markers like `MOM\0`, `BEAST\0`, etc. — verify against fixture).

The audit MUST conclude with one of:
- **Decision A (use lib):** lib name, version pin, integration sketch.
- **Decision B (write own):** byte layout for challenges + characters + marks, with offsets and bit positions, derived from the fixture.

- [ ] **Step 4: Commit**

```powershell
git add tracker/PARSER_AUDIT.md tests/fixtures/; if ($?) { git commit -m "docs: parser audit and ground-truth fixture" }
```

---

## Task 4: save_parser — ParsedSave dataclass + skeleton

**Files:**
- Create: `tracker/save_parser.py`
- Test: `tests/test_save_parser.py`

- [ ] **Step 1: Write skeleton test**

`tests/test_save_parser.py`:

```python
from datetime import datetime
from pathlib import Path

import pytest

from tracker.exceptions import SaveParseError
from tracker.save_parser import ParsedSave, parse_save


def test_parsed_save_is_dataclass():
    p = ParsedSave(
        slot=1,
        challenges_complete={1, 3, 5},
        characters_unlocked={0, 1},
        character_marks={0: {0, 1}, 1: {0}},
        parsed_at=datetime(2026, 5, 13),
    )
    assert p.slot == 1
    assert 3 in p.challenges_complete
    assert p.character_marks[0] == {0, 1}


def test_parse_save_raises_on_truncated_file(tmp_path):
    bad = tmp_path / "bad.dat"
    bad.write_bytes(b"\x00\x00")
    with pytest.raises(SaveParseError):
        parse_save(bad)


def test_parse_save_raises_on_missing_file(tmp_path):
    with pytest.raises(SaveParseError):
        parse_save(tmp_path / "does_not_exist.dat")
```

- [ ] **Step 2: Verify they fail**

```powershell
pytest tests/test_save_parser.py -v
```

- [ ] **Step 3: Implement dataclass + stub function**

`tracker/save_parser.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tracker.exceptions import SaveParseError


@dataclass(frozen=True)
class ParsedSave:
    slot: int
    challenges_complete: set[int] = field(default_factory=set)
    characters_unlocked: set[int] = field(default_factory=set)
    character_marks: dict[int, set[int]] = field(default_factory=dict)
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


_MIN_SAVE_SIZE_BYTES = 256  # tighten in Task 5 with real offsets


def parse_save(path: Path) -> ParsedSave:
    try:
        data = path.read_bytes()
    except FileNotFoundError as e:
        raise SaveParseError(f"Save file not found: {path}", path=str(path)) from e
    except OSError as e:
        raise SaveParseError(f"Cannot read save file: {e}", path=str(path)) from e
    if len(data) < _MIN_SAVE_SIZE_BYTES:
        raise SaveParseError(
            f"Save file too small ({len(data)} bytes), looks truncated",
            path=str(path),
        )
    slot = _infer_slot_from_name(path)
    return ParsedSave(slot=slot)  # placeholder, filled in Task 5


def _infer_slot_from_name(path: Path) -> int:
    name = path.stem  # persistentgamedata1
    if name.startswith("persistentgamedata") and name[-1].isdigit():
        return int(name[-1])
    return 0
```

- [ ] **Step 4: Verify pass**

```powershell
pytest tests/test_save_parser.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```powershell
git add tracker/save_parser.py tests/test_save_parser.py; if ($?) { git commit -m "feat: ParsedSave dataclass + truncation guard" }
```

---

## Task 5: save_parser — challenges + characters + marks

**Files:**
- Modify: `tracker/save_parser.py`
- Modify: `tests/test_save_parser.py`
- Reference: `tracker/PARSER_AUDIT.md`, `tests/fixtures/sample_save_repentance_plus.dat`, `tests/fixtures/sample_save_known_completions.md`

**Branch on audit decision:**
- If **Decision A** (use lib): import the lib and wrap its output into ParsedSave fields.
- If **Decision B** (custom parser): implement based on documented byte offsets.

The TDD loop is the same regardless of which side of the branch.

- [ ] **Step 1: Add fixture-driven tests using ground truth**

For each known completion in `sample_save_known_completions.md`:

```python
def test_parser_detects_known_challenge(known_completions, sample_save_path):
    parsed = parse_save(sample_save_path)
    for challenge_id in known_completions["challenges_done"]:
        assert challenge_id in parsed.challenges_complete

def test_parser_detects_known_character_mark(known_completions, sample_save_path):
    parsed = parse_save(sample_save_path)
    for char_id, mark_ids in known_completions["character_marks_done"].items():
        for mark_id in mark_ids:
            assert mark_id in parsed.character_marks.get(char_id, set())

def test_parser_detects_unlocked_characters(known_completions, sample_save_path):
    parsed = parse_save(sample_save_path)
    for char_id in known_completions["characters_unlocked"]:
        assert char_id in parsed.characters_unlocked
```

Wire these via `conftest.py` fixtures that skip if the sample save is missing:

```python
import json
from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_save_path():
    p = FIXTURES / "sample_save_repentance_plus.dat"
    if not p.exists():
        pytest.skip("No real save fixture; cannot validate parser against ground truth")
    return p

@pytest.fixture
def known_completions():
    p = FIXTURES / "sample_save_known_completions.json"
    if not p.exists():
        pytest.skip("No ground-truth notes for fixture")
    return json.loads(p.read_text())
```

(Convert the user's `.md` notes to `.json` for machine consumption — instruct in PARSER_AUDIT.md.)

- [ ] **Step 2: Verify the new tests fail (parser returns empty)**

```powershell
pytest tests/test_save_parser.py -v
```

Expected: 3 new fixture-driven tests FAIL (assert misses), 3 original tests still pass. If fixtures are missing, the new tests SKIP — that is acceptable but parser correctness is unverified.

- [ ] **Step 3: Implement based on PARSER_AUDIT decision**

Add to `tracker/save_parser.py`:

- `_parse_challenges(data: bytes) -> set[int]`
- `_parse_characters_unlocked(data: bytes) -> set[int]`
- `_parse_character_marks(data: bytes) -> dict[int, set[int]]`

Wire these into `parse_save()`. **Each helper handles its own bounds-checking and raises `SaveParseError` with a section label.**

If the fixture isn't available, ship a documented best-effort parser based on Repentance offsets; it will be validated in the manual smoke test.

- [ ] **Step 4: Verify tests pass**

```powershell
pytest tests/test_save_parser.py -v
```

Expected: all pass (or skip if fixtures absent).

- [ ] **Step 5: Commit**

```powershell
git add tracker/save_parser.py tests/test_save_parser.py tests/conftest.py; if ($?) { git commit -m "feat: parse challenges/characters/marks from save bytes" }
```

---

## Task 6: state_mapper — challenges mapping

**Files:**
- Create: `tracker/state_mapper.py`
- Test: `tests/test_state_mapper.py`

- [ ] **Step 1: Write failing tests**

`tests/test_state_mapper.py`:

```python
from datetime import datetime, timezone

from tracker.save_parser import ParsedSave
from tracker.state_mapper import build_localstorage_state, EXPECTED_CHARACTER_SLUGS


def _empty_parsed(slot=1):
    return ParsedSave(
        slot=slot,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )


def test_empty_save_produces_all_false_challenges():
    state = build_localstorage_state(_empty_parsed())
    challenges = state["challenges_state"]
    assert set(challenges.keys()) == {f"c_{i}" for i in range(1, 46)}
    assert all(v is False for v in challenges.values())


def test_completed_challenges_marked_true():
    p = ParsedSave(
        slot=1,
        challenges_complete={1, 9, 30, 45},
        characters_unlocked=set(),
        character_marks={},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["challenges_state"]["c_1"] is True
    assert state["challenges_state"]["c_9"] is True
    assert state["challenges_state"]["c_30"] is True
    assert state["challenges_state"]["c_45"] is True
    assert state["challenges_state"]["c_2"] is False
```

- [ ] **Step 2: Verify fail**

```powershell
pytest tests/test_state_mapper.py -v
```

- [ ] **Step 3: Implement minimally**

`tracker/state_mapper.py`:

```python
from __future__ import annotations

from tracker.save_parser import ParsedSave

CHALLENGE_IDS = range(1, 46)  # Repentance has 45 challenges

EXPECTED_CHARACTER_SLUGS = [
    "isaac", "cain", "apollyon", "magdalene", "lazarus", "bethany", "eden",
    "judas", "blue-baby", "eve", "samson", "azazel", "the-forgotten",
    "lilith", "jacob-and-esau", "the-lost", "keeper",
    "tainted-cain", "tainted-isaac", "tainted-magdalena", "tainted-bethany",
    "tainted-apollyon", "tainted-judas", "tainted-lazarus", "tainted-forgotten",
    "tainted-jacob-and-esau", "tainted-eve", "tainted-azazel",
    "tainted-blue-baby", "tainted-samson", "tainted-lilith", "tainted-eden",
    "tainted-the-lost", "tainted-keeper",
]

MARK_IDS = range(0, 13)  # 0..12 inclusive (13 marks)


def build_localstorage_state(parsed: ParsedSave) -> dict:
    return {
        "challenges_state": _build_challenges(parsed),
        "characters_state": _build_characters(parsed),
        "meta": {
            "slot": parsed.slot,
            "parsed_at": parsed.parsed_at.isoformat(),
        },
    }


def _build_challenges(parsed: ParsedSave) -> dict[str, bool]:
    return {f"c_{i}": (i in parsed.challenges_complete) for i in CHALLENGE_IDS}


def _build_characters(parsed: ParsedSave) -> dict[str, bool]:
    # Filled in Task 7
    return {}
```

- [ ] **Step 4: Verify pass**

```powershell
pytest tests/test_state_mapper.py -v
```

- [ ] **Step 5: Commit**

```powershell
git add tracker/state_mapper.py tests/test_state_mapper.py; if ($?) { git commit -m "feat: map challenges to localStorage shape" }
```

---

## Task 7: state_mapper — characters mapping

**Files:**
- Modify: `tracker/state_mapper.py`
- Modify: `tests/test_state_mapper.py`

The character ID → slug mapping table is critical. Get it wrong and the .exe writes keys the HTML doesn't read.

- [ ] **Step 1: Write failing tests**

Add to `tests/test_state_mapper.py`:

```python
def test_characters_state_has_all_34_slugs():
    state = build_localstorage_state(_empty_parsed())
    chars = state["characters_state"]
    for slug in EXPECTED_CHARACTER_SLUGS:
        assert f"{slug}_unlocked" in chars
        for mark_id in range(13):
            assert f"{slug}_mark_{mark_id}" in chars


def test_characters_state_empty_save_all_false():
    state = build_localstorage_state(_empty_parsed())
    assert all(v is False for v in state["characters_state"].values())


def test_isaac_unlocked_with_marks():
    # Isaac is char_id 0 internally per spec; he has marks 0 (Mom's Heart) and 1 (Isaac).
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked={0},
        character_marks={0: {0, 1}},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["characters_state"]["isaac_unlocked"] is True
    assert state["characters_state"]["isaac_mark_0"] is True
    assert state["characters_state"]["isaac_mark_1"] is True
    assert state["characters_state"]["isaac_mark_2"] is False
    assert state["characters_state"]["cain_unlocked"] is False


def test_tainted_magdalena_spelling_preserved():
    # Spec lock-in: tainted-magdalena (Spanish a), NOT tainted-magdalene.
    state = build_localstorage_state(_empty_parsed())
    assert "tainted-magdalena_unlocked" in state["characters_state"]
    assert "tainted-magdalene_unlocked" not in state["characters_state"]
```

- [ ] **Step 2: Verify fail**

```powershell
pytest tests/test_state_mapper.py -v
```

- [ ] **Step 3: Implement character mapping**

Add to `tracker/state_mapper.py`:

```python
# Maps Isaac PlayerType internal IDs to the HTML's slug.
# These IDs are the canonical PlayerType enum values; verify in PARSER_AUDIT
# against the real save before locking in. If Repentance+ added IDs, extend here.
CHARACTER_ID_TO_SLUG: dict[int, str] = {
    0:  "isaac",
    1:  "magdalene",
    2:  "cain",
    3:  "judas",
    4:  "blue-baby",
    5:  "eve",
    6:  "samson",
    7:  "azazel",
    8:  "lazarus",
    9:  "eden",
    10: "the-lost",
    13: "lilith",
    14: "keeper",
    15: "apollyon",
    16: "the-forgotten",
    19: "bethany",
    20: "jacob-and-esau",
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

SLUG_TO_CHARACTER_ID: dict[str, int] = {v: k for k, v in CHARACTER_ID_TO_SLUG.items()}

# Sanity: every expected slug must be reachable. Catches typos at import time.
_missing = set(EXPECTED_CHARACTER_SLUGS) - set(SLUG_TO_CHARACTER_ID.keys())
if _missing:
    raise RuntimeError(f"CHARACTER_ID_TO_SLUG is missing slugs: {_missing}")
```

And replace `_build_characters`:

```python
def _build_characters(parsed: ParsedSave) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for slug in EXPECTED_CHARACTER_SLUGS:
        char_id = SLUG_TO_CHARACTER_ID[slug]
        out[f"{slug}_unlocked"] = char_id in parsed.characters_unlocked
        marks = parsed.character_marks.get(char_id, set())
        for mark_id in MARK_IDS:
            out[f"{slug}_mark_{mark_id}"] = mark_id in marks
    return out
```

- [ ] **Step 4: Verify pass**

```powershell
pytest tests/test_state_mapper.py -v
```

Expected: all tests pass. Counts: 34 chars × (1 unlock + 13 marks) = 476 keys, plus 45 challenge keys = 521 total `characters_state` + `challenges_state` keys.

- [ ] **Step 5: Commit**

```powershell
git add tracker/state_mapper.py tests/test_state_mapper.py; if ($?) { git commit -m "feat: map character unlocks and marks to slug keys" }
```

---

## Task 8: watcher — debounced file change events

**Files:**
- Create: `tracker/watcher.py`
- Test: `tests/test_watcher.py`

- [ ] **Step 1: Write failing tests**

`tests/test_watcher.py`:

```python
import threading
import time
from pathlib import Path

from tracker.watcher import SaveWatcher


def test_single_change_fires_once_after_debounce(tmp_path):
    f = tmp_path / "persistentgamedata1.dat"
    f.write_bytes(b"a")
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=200)
    w.start()
    try:
        time.sleep(0.05)
        f.write_bytes(b"ab")
        time.sleep(0.6)
        assert len(calls) == 1
    finally:
        w.stop()


def test_multiple_changes_within_window_coalesce(tmp_path):
    f = tmp_path / "persistentgamedata1.dat"
    f.write_bytes(b"a")
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=300)
    w.start()
    try:
        time.sleep(0.05)
        for byte in [b"ab", b"abc", b"abcd"]:
            f.write_bytes(byte)
            time.sleep(0.05)
        time.sleep(0.7)
        assert len(calls) == 1
    finally:
        w.stop()


def test_changes_in_different_windows_fire_separately(tmp_path):
    f = tmp_path / "persistentgamedata1.dat"
    f.write_bytes(b"a")
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=150)
    w.start()
    try:
        time.sleep(0.05)
        f.write_bytes(b"ab")
        time.sleep(0.5)
        f.write_bytes(b"abc")
        time.sleep(0.5)
        assert len(calls) == 2
    finally:
        w.stop()


def test_ignores_non_dat_files(tmp_path):
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=150)
    w.start()
    try:
        time.sleep(0.05)
        (tmp_path / "log.txt").write_bytes(b"junk")
        time.sleep(0.5)
        assert len(calls) == 0
    finally:
        w.stop()
```

- [ ] **Step 2: Verify fail**

```powershell
pytest tests/test_watcher.py -v
```

- [ ] **Step 3: Implement**

`tracker/watcher.py`:

```python
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class SaveWatcher:
    def __init__(self, save_dir: Path, on_change: Callable[[], None], debounce_ms: int = 500):
        self._save_dir = save_dir
        self._on_change = on_change
        self._debounce_s = debounce_ms / 1000.0
        self._observer: Observer | None = None
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        handler = _Handler(self._schedule_fire)
        self._observer = Observer()
        self._observer.schedule(handler, str(self._save_dir), recursive=False)
        self._observer.start()

    def stop(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None

    def _schedule_fire(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce_s, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self) -> None:
        with self._lock:
            self._timer = None
        try:
            self._on_change()
        except Exception:
            # Swallow callback errors so the watcher thread doesn't die.
            # The orchestrator is responsible for its own error reporting.
            pass


class _Handler(FileSystemEventHandler):
    def __init__(self, fire: Callable[[], None]):
        self._fire = fire

    def on_modified(self, event: FileSystemEvent) -> None:
        if self._is_save_file(event):
            self._fire()

    def on_created(self, event: FileSystemEvent) -> None:
        if self._is_save_file(event):
            self._fire()

    @staticmethod
    def _is_save_file(event: FileSystemEvent) -> bool:
        if event.is_directory:
            return False
        name = Path(event.src_path).name.lower()
        return name.startswith("persistentgamedata") and name.endswith(".dat")
```

- [ ] **Step 4: Verify pass**

```powershell
pytest tests/test_watcher.py -v
```

Expected: 4 passed. If a timing test is flaky on slow CI/Windows, bump the debounce_ms / sleeps proportionally — the tolerance is the bug, not the watcher.

- [ ] **Step 5: Commit**

```powershell
git add tracker/watcher.py tests/test_watcher.py; if ($?) { git commit -m "feat: debounced save-file watcher" }
```

---

## Task 9: HTML modifications

**Files:**
- Modify: `challenges.html` (root)
- Copy: `challenges.html` → `tracker/assets/challenges.html` (kept in sync via build, see Task 13)

The root `challenges.html` becomes dual-purpose: opens fine as `file://` (manual mode, no changes visible to the user), and behaves as the live tracker when loaded inside PyWebView.

- [ ] **Step 1: Locate end of `<script>` block**

Open `challenges.html`, scroll to the end of the last `<script>` block (around line 3842). The lines just before `</script>` are:

```js
  render();
  setTaintedVisible(localStorage.getItem(TAINTED_VISIBLE_KEY) === '1');
  const savedTab = localStorage.getItem(ACTIVE_TAB_KEY);
  if (savedTab) switchTab(savedTab);
```

- [ ] **Step 2: Append new block after the `if (savedTab) ...` line, before `</script>`**

```js
  // ====== PyWebView bridge (no-op when opened as plain file://) ======
  window.applyIsaacState = function(state) {
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

  function _enableTrackerLockedMode() {
    document.body.classList.add('tracker-locked');
  }

  window.addEventListener('pywebviewready', async () => {
    _enableTrackerLockedMode();
    try {
      const initial = await window.pywebview.api.get_initial_state();
      window.applyIsaacState(initial);
    } catch (e) {
      console.error('Failed to load initial Isaac state:', e);
    }
  });
```

- [ ] **Step 3: Add the locked-mode CSS**

Inside the existing `<style>` block, append:

```css
    body.tracker-locked input,
    body.tracker-locked .char-grid-cell,
    body.tracker-locked .char-grid-col-header,
    body.tracker-locked li {
      pointer-events: none;
      cursor: default;
    }
    body.tracker-locked .reset-btn,
    body.tracker-locked .tainted-toggle,
    body.tracker-locked .tab {
      pointer-events: auto;
      cursor: pointer;
    }
```

Note: the override line keeps tabs, reset, and the Tainted toggle interactive — those are UI controls, not data edits. (`reset-btn` is the existing reset button; verify the class name in `challenges.html` before relying on it.)

- [ ] **Step 4: Verify HTML still works in `file://` mode**

```powershell
start challenges.html
```

Manual check: the page opens, both tabs work, you can still toggle checkboxes (no `pywebviewready` event fires outside PyWebView, so `tracker-locked` is never applied), tooltips work. **Nothing should look different from before.**

- [ ] **Step 5: Commit**

```powershell
git add challenges.html; if ($?) { git commit -m "feat(html): pywebview bridge + read-only mode (no-op outside .exe)" }
```

---

## Task 10: app.py — PyWebView window

**Files:**
- Create: `tracker/app.py`

This task gets to a minimum visible result: doubling the python entry point opens the window with the HTML. No save parsing yet.

- [ ] **Step 1: Implement minimal app**

`tracker/app.py`:

```python
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import webview

from tracker.save_locator import locate_save_file
from tracker.save_parser import parse_save
from tracker.state_mapper import build_localstorage_state
from tracker.watcher import SaveWatcher
from tracker.exceptions import SaveNotFoundError, SaveParseError

logger = logging.getLogger("tracker")


def _bundled_html() -> str:
    """Return the embedded challenges.html content."""
    if getattr(sys, "frozen", False):
        # Running inside PyInstaller --onefile bundle.
        base = Path(sys._MEIPASS) / "assets"
    else:
        base = Path(__file__).parent / "assets"
    return (base / "challenges.html").read_text(encoding="utf-8")


class TrackerApi:
    def __init__(self):
        self._window: webview.Window | None = None

    def attach(self, window: webview.Window) -> None:
        self._window = window

    def get_initial_state(self) -> dict:
        try:
            parsed = parse_save(locate_save_file())
            return build_localstorage_state(parsed)
        except (SaveNotFoundError, SaveParseError) as e:
            logger.warning("Initial state unavailable: %s", e)
            return {"challenges_state": {}, "characters_state": {}, "error": str(e)}


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        filename="IsaacTracker.log",
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    api = TrackerApi()
    window = webview.create_window(
        title="Isaac Tracker",
        html=_bundled_html(),
        width=900,
        height=950,
        resizable=True,
        js_api=api,
    )
    api.attach(window)
    webview.start()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Copy HTML to assets**

```powershell
Copy-Item challenges.html tracker\assets\challenges.html -Force
```

- [ ] **Step 3: Run from the venv**

```powershell
python -m tracker.app
```

Expected: a desktop window opens, titled "Isaac Tracker", showing the challenges page. The initial state may be empty (no auto-mark yet — that's Task 11).

Manual check:
- Window opens within ~2 seconds.
- HTML renders (both tabs visible).
- Closing the window terminates the process (no zombies — check Task Manager).
- A file `IsaacTracker.log` appears with at least one INFO line.

If `webview.start()` raises about WebView2: install the Microsoft Edge WebView2 runtime: <https://developer.microsoft.com/microsoft-edge/webview2/>

- [ ] **Step 4: Commit**

```powershell
git add tracker/app.py tracker/assets/challenges.html; if ($?) { git commit -m "feat: minimal pywebview window with embedded HTML" }
```

---

## Task 11: app.py — wire initial state through JS bridge

**Files:**
- Modify: `tracker/app.py`

The `get_initial_state` method is already defined in Task 10. This task hooks up the JS side (already in `challenges.html` from Task 9) and validates the end-to-end flow on a real save.

- [ ] **Step 1: Run and observe**

```powershell
python -m tracker.app
```

Expected: window opens, then (if the user's Isaac save is detected) checkboxes auto-fill. Compare visually against `tests/fixtures/sample_save_known_completions.md` — at least the known-complete challenges should be checked.

- [ ] **Step 2: If checkboxes do NOT fill in but no error**

Open browser dev tools inside the PyWebView window (right-click → Inspect, if enabled — may need to set `webview.start(debug=True)` temporarily). Look in Console for the message logged by the `catch` block in `pywebviewready`. Read `IsaacTracker.log`.

Common failure modes and fixes:
- `pywebview.api` undefined → `js_api=api` was not passed to `create_window` correctly. Re-check Task 10 step 1.
- `applyIsaacState` not defined → HTML changes from Task 9 not in `tracker/assets/challenges.html` (must be re-copied after edits). Re-run `Copy-Item challenges.html tracker\assets\challenges.html -Force`.
- State arrives but no checkboxes change → state shape mismatch. Add `console.log(initial)` inside the handler and verify keys match `challenges_state` / `characters_state`.

- [ ] **Step 3: Verify `tracker-locked` mode is active**

Click on a challenge checkbox in the running window — it MUST NOT toggle (read-only). Click on the Tainted toggle button — it MUST still work. Click between tabs — they MUST switch.

- [ ] **Step 4: Commit (no code change, just validation)**

If you discovered a bug and fixed it during this task, commit the fix:

```powershell
git add tracker/app.py challenges.html tracker/assets/challenges.html; if ($?) { git commit -m "fix: <description>" }
```

---

## Task 12: app.py — watcher hookup for live updates

**Files:**
- Modify: `tracker/app.py`

- [ ] **Step 1: Modify `main()` to start the watcher**

Replace `main()` body:

```python
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        filename="IsaacTracker.log",
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    api = TrackerApi()
    window = webview.create_window(
        title="Isaac Tracker",
        html=_bundled_html(),
        width=900,
        height=950,
        resizable=True,
        js_api=api,
    )
    api.attach(window)

    watcher: SaveWatcher | None = None
    try:
        from tracker.save_locator import find_save_directory
        save_dir = find_save_directory()
        watcher = SaveWatcher(save_dir, on_change=lambda: _push_state(api, window))
        watcher.start()
    except SaveNotFoundError as e:
        logger.warning("Live updates disabled: %s", e)

    try:
        webview.start()
    finally:
        if watcher is not None:
            watcher.stop()


def _push_state(api: TrackerApi, window: webview.Window) -> None:
    try:
        state = api.get_initial_state()
        window.evaluate_js(f"window.applyIsaacState({json.dumps(state)})")
    except Exception:
        logger.exception("Failed to push state to UI")
```

- [ ] **Step 2: Run and trigger a save change**

```powershell
python -m tracker.app
```

While the window is open, simulate a save write:

```powershell
# In a separate PowerShell:
$save = "$env:USERPROFILE\Documents\My Games\Binding of Isaac Repentance+\persistentgamedata1.dat"
$ts = Get-Date
(Get-Item $save).LastWriteTime = $ts
```

Expected: within ~1 second the window briefly re-renders (any DOM flicker is fine). `IsaacTracker.log` should show the push (or no error). For a real end-to-end check, complete a run in Isaac and return to the main menu — the window updates.

- [ ] **Step 3: Verify clean shutdown**

Close the tracker window. In Task Manager confirm no `python.exe` or `IsaacTracker.exe` lingering.

- [ ] **Step 4: Commit**

```powershell
git add tracker/app.py; if ($?) { git commit -m "feat: live updates via save-file watcher" }
```

---

## Task 13: Build automation + asset sync

**Files:**
- Create: `build.spec`
- Create: `MANUAL_TEST.md`

This task makes the build reproducible. The PyInstaller spec embeds `challenges.html` so the .exe ships everything inline.

- [ ] **Step 1: Sync asset before build**

This is brittle if forgotten. Add a tiny sync step inline at the top of `build.spec` (PyInstaller spec files are Python):

`build.spec`:

```python
# PyInstaller spec for IsaacTracker.exe
# Build: `pyinstaller build.spec`

import shutil
from pathlib import Path

ROOT = Path.cwd()
# Ensure the bundled HTML mirrors the root copy at build time.
shutil.copyfile(ROOT / "challenges.html", ROOT / "tracker" / "assets" / "challenges.html")

a = Analysis(
    ['tracker/app.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[('tracker/assets/challenges.html', 'assets'),
           ('bossrush.png', 'assets')],  # served from MEIPASS at runtime if needed
    hiddenimports=['watchdog.observers.read_directory_changes'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='IsaacTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,                # --windowed
    icon=None,
)
```

- [ ] **Step 2: Build the .exe**

```powershell
pyinstaller build.spec
```

Expected: builds in `dist/IsaacTracker.exe`. The build will print warnings about pywebview; most are safe.

- [ ] **Step 3: Run the built .exe**

```powershell
.\dist\IsaacTracker.exe
```

Expected: same behavior as `python -m tracker.app` — window opens, save state applies, save changes auto-update. Also: `IsaacTracker.log` is written to whatever directory you launched the .exe from (the cwd, not next to the .exe). Note this in MANUAL_TEST.md.

- [ ] **Step 4: Write MANUAL_TEST.md**

```markdown
# IsaacTracker — Manual Smoke Test

Run before shipping the .exe to the user.

## Preconditions
- Windows 11 64-bit
- Microsoft Edge WebView2 Runtime installed (preinstalled on Win11)
- The Binding of Isaac: Repentance+ installed with at least one save slot used

## Test 1 — Cold launch shows real save state
1. Double-click `IsaacTracker.exe`.
2. Window opens within 3 seconds.
3. Check that 2-3 challenges you KNOW you have completed appear marked.
4. Switch to the "Personajes" tab.
5. Check that Isaac (the character) shows at least the Mom's Heart mark.

## Test 2 — Read-only behaviour
1. With the window open, click any challenge checkbox.
2. EXPECTED: checkbox does not toggle.
3. Click the "Mostrar Tainted" button.
4. EXPECTED: tainted characters appear (toggle still works).

## Test 3 — Live update after a run
1. With the tracker open, launch Isaac.
2. Complete a challenge you have not completed before (e.g. a Tier D one for speed).
3. Return to the main menu (this is when Isaac writes the save).
4. EXPECTED: within 5 seconds, the corresponding checkbox in the tracker becomes checked.

## Test 4 — Clean shutdown
1. Close the tracker window.
2. Open Task Manager.
3. EXPECTED: no `IsaacTracker.exe` or `python.exe` lingering.

## Test 5 — Backup created
1. Open the file `_pre_tracker_backup` key in localStorage (via DevTools if available, OR by opening the bundled HTML in a normal browser and inspecting Application → Local Storage).
2. EXPECTED: contains the localStorage snapshot from before the first .exe launch.
```

- [ ] **Step 5: Commit**

```powershell
git add build.spec MANUAL_TEST.md; if ($?) { git commit -m "build: PyInstaller spec + manual test plan" }
```

---

## Task 14: Final smoke test + handoff

This task is execution-only. No new code.

- [ ] **Step 1: Run all unit tests in clean order**

```powershell
pytest -v
```

Expected: all pass (some `save_parser` ground-truth tests may skip if no fixture).

- [ ] **Step 2: Execute MANUAL_TEST.md end-to-end**

Run all 5 tests in order. Document any test that fails in a new issue note at the bottom of MANUAL_TEST.md.

- [ ] **Step 3: Build the final .exe**

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
pyinstaller build.spec
```

Expected: `dist/IsaacTracker.exe` produced, size 25-40 MB.

- [ ] **Step 4: Hand the .exe to the user**

Provide the user with `dist/IsaacTracker.exe`. They double-click it. That's the entire installation.

If Test 1 of MANUAL_TEST.md fails because the parser doesn't read Repentance+ correctly (R1 in spec): file the gap in `tracker/PARSER_AUDIT.md`, hand over the .exe anyway (manual mode in the .html still works), and create a follow-up plan to extend the parser.

- [ ] **Step 5: Final commit**

```powershell
git add -A; if ($?) { git commit -m "chore: ship v1 of IsaacTracker" }
```

---

## Acceptance criteria (overall)

Plan is considered done when:

- `pytest -v` exits 0 (skips allowed for ground-truth fixture tests).
- `dist/IsaacTracker.exe` exists and passes Tests 1, 2, 4, 5 in MANUAL_TEST.md.
- Test 3 (live update) passes against at least one real Isaac run, OR is documented as blocked on R1 in PARSER_AUDIT.md with a follow-up plan.
- The standalone `challenges.html` (opened as `file://`) still works unchanged.
