"""
Repentance+ save parser.

Walks the binary chunk format used by `rep+persistentgamedata{N}.dat`:

    [ 20-byte header ]
      [ 16 B magic = b"ISAACNGSAVE09R  " ]
      [  4 B in-header CRC (often 0) ]
    [ 11 length-prefixed chunks, each ]
      [ 12 B header: type (s32 LE) | len (s32 LE) | count (s32 LE) ]
      [ count * entry_size body bytes ]
    [ trailing 4 B AfterbirthChecksum ]

Notes on the header's `len` field: in this format `len` is NOT the body byte
length. It tends to be `count * 4` regardless of entry size, which means
walking by `len` alone overshoots for u1 chunks (achievements, collectibles,
bosses, etc.). We instead use the entry-size table `[1,4,4,1,1,1,1,4,4,1]`
(for chunks 1..10) from Blade's Kaitai schema, cross-verified against the
fixture. Body byte length = `count * entry_size`. We do not need to parse
chunk 11 (bestiary) for this tracker.

The achievements chunk (chunk 1) is the source of character unlock state and
per-character completion marks; the challenges chunk (chunk 7) is a
46-byte array of 0/1 flags (index 0 unused, indices 1..45 real).

The mapping from save-file mark order to HTML-display mark order is applied
inside the parser, so consumers see HTML order (0..12) directly. See
`tracker/data/characters.py` for the lookup tables.

Reference: tracker/PARSER_AUDIT.md
"""
from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tracker.data.characters import (
    AGUSAENZ_INDEX_TO_PLAYERTYPE,
    CHARACTERS_ACHIEVEMENTS,
    SAVE_TO_HTML_MARK,
)
from tracker.exceptions import SaveParseError


@dataclass(frozen=True)
class ParsedSave:
    """Result of parsing a Repentance+ save file.

    challenges_complete: set of challenge IDs (1..45) that are completed.
    characters_unlocked: set of internal Isaac PlayerType IDs unlocked
        (Isaac=0 is always considered unlocked even if no achievement byte exists).
    character_marks: per-character set of completion-mark IDs (0..12) completed.
        Mark IDs are in HTML-display order, NOT save-file order. The mapping
        from save-order to HTML-order is applied by the parser.
    achievements_unlocked: set of achievement byte indices that are set to 1
        in the save's achievements chunk. The Isaac game numbers achievements
        from 1 upward; we keep the raw byte index (so index 50 ↔ achievement
        50 in the game's own numbering). Used by the "Logros" view to render
        global completion.
    items_seen: set of collectible IDs (byte indices in the COLLECTIBLES
        chunk, chunk 4) the player has touched at least once. The Isaac engine
        sets byte[id]=1 when an item is picked up for the first time; that
        flag persists across runs and is the source of truth for the
        Collection Page. Used by the "Ítems" view.
    parsed_at: when this parse ran. Useful for logging / UI footer.
    """
    slot: int
    challenges_complete: set[int] = field(default_factory=set)
    characters_unlocked: set[int] = field(default_factory=set)
    character_marks: dict[int, set[int]] = field(default_factory=dict)
    achievements_unlocked: set[int] = field(default_factory=set)
    items_seen: set[int] = field(default_factory=set)
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Truncation guard. Smallest plausibly-valid Isaac save is ~16KB. We use 256
# as a conservative floor — the magic-header check rejects garbage above it.
_MIN_SAVE_SIZE_BYTES = 256

# Repentance/Repentance+ save magic (16 bytes, two trailing spaces).
_MAGIC = b"ISAACNGSAVE09R  "

# Header layout
_HEADER_SIZE = 20  # 16 B magic + 4 B in-header CRC
_CHUNK_HEADER_SIZE = 12  # 3 x s32 LE: type, len, count

# Entry size in bytes for chunks 1..10. Chunk 11 (bestiary) has a nested
# variable-length structure we do not parse.
_ENTRY_SIZES = (1, 4, 4, 1, 1, 1, 1, 4, 4, 1)

# Chunk type IDs we actually care about (1-indexed).
_CHUNK_ACHIEVEMENTS = 1
_CHUNK_COLLECTIBLES = 4
_CHUNK_CHALLENGE_COUNTERS = 7

# Challenges chunk: 46 bytes; index 0 is unused, indices 1..45 are challenges.
_NUM_CHALLENGES = 45

# Slot inference: filenames are either `rep+persistentgamedata{N}.dat` (Steam)
# or `YYYYMMDD.rep+persistentgamedata{N}.dat` (local backup). We extract N.
_SLOT_NAME_RE = re.compile(r"persistentgamedata(\d+)\.dat$", re.IGNORECASE)


def parse_save(path: Path) -> ParsedSave:
    """Parse a Repentance+ save file from disk.

    Raises SaveParseError on missing, truncated, or malformed files.
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
    if data[:16] != _MAGIC:
        raise SaveParseError(
            f"Bad magic header: got {data[:16]!r}, expected {_MAGIC!r}",
            path=str(path),
        )

    slot = _infer_slot_from_name(path)
    achievements, challenges, collectibles = _extract_chunks(data, path)

    challenges_complete = _extract_challenges(challenges)
    characters_unlocked, character_marks = _extract_character_state(achievements)
    achievements_unlocked = _extract_achievements_set(achievements)
    items_seen = _extract_items_seen(collectibles)

    return ParsedSave(
        slot=slot,
        challenges_complete=challenges_complete,
        characters_unlocked=characters_unlocked,
        character_marks=character_marks,
        achievements_unlocked=achievements_unlocked,
        items_seen=items_seen,
    )


def _extract_items_seen(collectibles_body: bytes) -> set[int]:
    """Return the set of collectible IDs whose byte is 1 (touched at least once)."""
    return {i for i, b in enumerate(collectibles_body) if b == 1}


def _extract_achievements_set(achievements_body: bytes) -> set[int]:
    """Return the set of achievement byte indices that are set to 1."""
    return {i for i, b in enumerate(achievements_body) if b == 1}


def _extract_chunks(data: bytes, path: Path) -> tuple[bytes, bytes, bytes]:
    """Walk the 10 fixed-size chunks and return (achievements, challenges, collectibles).

    We only walk through chunk 10; chunk 11 (bestiary) is not needed.
    """
    achievements: bytes | None = None
    challenges: bytes | None = None
    collectibles: bytes | None = None

    off = _HEADER_SIZE
    for i in range(10):
        if off + _CHUNK_HEADER_SIZE > len(data):
            raise SaveParseError(
                f"Save truncated: ran out of bytes at chunk {i + 1} header"
                f" (offset 0x{off:04X}, file size {len(data)})",
                path=str(path),
            )
        chunk_type, _len_field, count = struct.unpack_from("<iii", data, off)
        body_start = off + _CHUNK_HEADER_SIZE
        body_len = count * _ENTRY_SIZES[i]
        body_end = body_start + body_len
        if body_end > len(data):
            raise SaveParseError(
                f"Save truncated: chunk {i + 1} body overruns end of file"
                f" (body 0x{body_start:04X}..0x{body_end:04X}, file size {len(data)})",
                path=str(path),
            )
        body = data[body_start:body_end]
        if chunk_type == _CHUNK_ACHIEVEMENTS:
            achievements = body
        elif chunk_type == _CHUNK_COLLECTIBLES:
            collectibles = body
        elif chunk_type == _CHUNK_CHALLENGE_COUNTERS:
            challenges = body
        off = body_end

    if achievements is None:
        raise SaveParseError("No achievements chunk found in save", path=str(path))
    if challenges is None:
        raise SaveParseError("No challenges chunk found in save", path=str(path))
    if collectibles is None:
        raise SaveParseError("No collectibles chunk found in save", path=str(path))
    return achievements, challenges, collectibles


def _extract_challenges(challenges_body: bytes) -> set[int]:
    """Return the set of challenge IDs (1..45) that are completed."""
    done: set[int] = set()
    # Challenges body should have at least 46 bytes (index 0 unused).
    for i in range(1, min(_NUM_CHALLENGES + 1, len(challenges_body))):
        if challenges_body[i] == 1:
            done.add(i)
    return done


def _extract_character_state(
    achievements_body: bytes,
) -> tuple[set[int], dict[int, set[int]]]:
    """Compute unlocked characters and per-character completion-mark sets.

    A character is considered unlocked if any of its 13 mark achievements is
    set. Isaac (PlayerType 0) is also explicitly added as always-unlocked.
    This "any-mark" rule is more permissive than agusaenz's "first mark"
    convention but correctly captures tainted characters: tainted unlock
    state lives outside the achievements chunk, but if any tainted-only mark
    is set, the player must have unlocked that tainted to earn it.

    Marks are translated from agusaenz save order to HTML display order using
    `SAVE_TO_HTML_MARK`.
    """
    unlocked: set[int] = {0}  # Isaac always unlocked
    marks: dict[int, set[int]] = {}
    ach_len = len(achievements_body)

    for ag_idx, row in enumerate(CHARACTERS_ACHIEVEMENTS):
        playertype_id = AGUSAENZ_INDEX_TO_PLAYERTYPE[ag_idx]
        # row[0] is the name; row[1..14] are the 13 mark achievement IDs in save order.
        save_order_ach_ids = row[1:14]
        char_marks: set[int] = set()
        any_set = False
        for save_idx, ach_id in enumerate(save_order_ach_ids):
            ach_id_int = int(ach_id)
            if 0 <= ach_id_int < ach_len and achievements_body[ach_id_int] == 1:
                any_set = True
                html_idx = SAVE_TO_HTML_MARK[save_idx]
                char_marks.add(html_idx)
        marks[playertype_id] = char_marks
        if any_set:
            unlocked.add(playertype_id)

    return unlocked, marks


def _infer_slot_from_name(path: Path) -> int:
    """Return the slot number embedded in the filename, or 0 if not derivable."""
    m = _SLOT_NAME_RE.search(path.name)
    if m:
        return int(m.group(1))
    return 0
