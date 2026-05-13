"""
Repentance+ save parser.

The full parsing logic lives in Task 5 / lands as iterative additions.
Task 4 (this module) defines the public dataclass and the function signature
plus basic guards so other modules can import without runtime errors.

Reference: tracker/PARSER_AUDIT.md
Source format: ISAACNGSAVE09R - 20-byte header + 11 length-prefixed chunks.

NOTE ON MARK ORDER (read before Task 5):
The `character_marks` field uses HTML display order for mark IDs (0..12) in
the order:
    [Mom's Heart, Isaac, Satan, ???, Lamb, Boss Rush, Hush, Mega Satan,
     Ultra Greed, Ultra Greedier, Delirium, Mother, The Beast]
The save file itself uses a DIFFERENT order (agusaenz/save order):
    [Mom's Heart, Isaac, Satan, Boss Rush, ???, Lamb, Mega Satan, Hush,
     Ultra Greed, Ultra Greedier, Delirium, Mother, Beast]
Marks 3-7 are swapped between the two orderings. Task 5 will apply this
remap inside the parser so callers always see HTML order. Do NOT remap
in Task 4 - there's no parsing to remap yet.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tracker.exceptions import SaveParseError


@dataclass(frozen=True)
class ParsedSave:
    """Result of parsing a Repentance+ save file.

    challenges_complete: set of challenge IDs (1..45) that are completed.
    characters_unlocked: set of internal Isaac PlayerType IDs unlocked
        (Isaac=0 is always considered unlocked even if no achievement byte exists).
    character_marks: per-character set of completion-mark IDs (0..12) completed.
        Mark IDs are in HTML-display order, NOT save-file order. The mapping
        from save-order to HTML-order is applied by the parser (see Task 5).
    parsed_at: when this parse ran. Useful for logging / UI footer.
    """
    slot: int
    challenges_complete: set[int] = field(default_factory=set)
    characters_unlocked: set[int] = field(default_factory=set)
    character_marks: dict[int, set[int]] = field(default_factory=dict)
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Truncation guard. The smallest real save we observed is ~16KB; the smallest
# any valid Isaac save can plausibly be is the 20-byte header + 11 chunks of
# headers (each 8 bytes minimum) + at least 1 byte per chunk = ~120 bytes.
# Use 256 as a conservative floor; Task 5 will validate the magic header.
_MIN_SAVE_SIZE_BYTES = 256

# Slot inference: filenames are either `rep+persistentgamedata{N}.dat` (Steam)
# or `YYYYMMDD.rep+persistentgamedata{N}.dat` (local backup). We extract N.
_SLOT_NAME_RE = re.compile(r"persistentgamedata(\d+)\.dat$", re.IGNORECASE)


def parse_save(path: Path) -> ParsedSave:
    """Parse a Repentance+ save file from disk.

    Raises SaveParseError on missing/truncated/malformed files. Task 4 only
    validates size; Task 5 adds chunk-walking and magic-header checks.
    """
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
    # NOTE: Task 5 will replace this empty return with real parsing.
    return ParsedSave(slot=slot)


def _infer_slot_from_name(path: Path) -> int:
    """Return the slot number embedded in the filename, or 0 if not derivable."""
    m = _SLOT_NAME_RE.search(path.name)
    if m:
        return int(m.group(1))
    return 0
