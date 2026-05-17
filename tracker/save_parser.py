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
    CHARACTER_UNLOCK_ACHIEVEMENTS,
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

        Note: there is no analogous per-card chunk in the save. Cards are
        derived from `achievements_unlocked` in `state_mapper`, since each
        unlockable card has a corresponding achievement byte in chunk 1.
    donation_count: total monedas depositadas en la Donation Machine (tiendas),
        leído del chunk 2 (counters) en el índice 8.
    greed_donation_count: total monedas depositadas en la Greed Donation
        Machine (modo Greed/Greedier), leído del chunk 2 en el índice 19.
    parsed_at: when this parse ran. Useful for logging / UI footer.
    """
    slot: int
    challenges_complete: set[int] = field(default_factory=set)
    characters_unlocked: set[int] = field(default_factory=set)
    character_marks: dict[int, set[int]] = field(default_factory=dict)
    achievements_unlocked: set[int] = field(default_factory=set)
    items_seen: set[int] = field(default_factory=set)
    donation_count: int = 0
    greed_donation_count: int = 0
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

# Chunk type IDs we actually care about (1-indexed). Note: chunk 6 is BOSSES
# (104 boss-kill flags), not cards — see tracker/PARSER_AUDIT.md. Earlier
# versions of this file misread it as cards; the Cards view now derives its
# state from achievements instead (see state_mapper._build_cards_state).
_CHUNK_ACHIEVEMENTS = 1
_CHUNK_COLLECTIBLES = 4
_CHUNK_CHALLENGE_COUNTERS = 7
_CHUNK_COUNTERS = 2
_DONATION_NORMAL_INDEX = 8   # Donation Machine (tiendas) en chunk 2 de Repentance+
_DONATION_GREED_INDEX  = 19  # Greed Donation Machine en chunk 2 de Repentance+

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
        raise SaveParseError(f"No se encontró la partida: {path}", path=str(path)) from e
    except OSError as e:
        raise SaveParseError(f"No se puede leer la partida: {e}", path=str(path)) from e
    if len(data) < _MIN_SAVE_SIZE_BYTES:
        raise SaveParseError(
            f"La partida es demasiado pequeña ({len(data)} bytes), parece estar truncada.",
            path=str(path),
        )
    if data[:16] != _MAGIC:
        raise SaveParseError(
            f"Cabecera del archivo de partida incorrecta: se obtuvo {data[:16]!r}, se esperaba {_MAGIC!r}.",
            path=str(path),
        )

    slot = _infer_slot_from_name(path)
    chunks = _extract_chunks(data, path)
    achievements = chunks[_CHUNK_ACHIEVEMENTS]
    challenges   = chunks[_CHUNK_CHALLENGE_COUNTERS]
    collectibles = chunks[_CHUNK_COLLECTIBLES]
    counters = chunks[_CHUNK_COUNTERS]
    donation_count, greed_donation_count = _extract_donation_counters(counters)

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
        donation_count=donation_count,
        greed_donation_count=greed_donation_count,
    )


def _extract_items_seen(collectibles_body: bytes) -> set[int]:
    """Return the set of collectible IDs whose byte is 1 (touched at least once)."""
    return {i for i, b in enumerate(collectibles_body) if b == 1}


# Record types del chunk 11 (bestiario). Cada sub-registro lleva una de estas
# IDs en su cabecera <ii> = (rec_type, len_field).
_BESTIARY_HITS = 1
_BESTIARY_DEATHS = 2
_BESTIARY_KILLS = 3
_BESTIARY_ENCOUNTERS = 4


def _extract_bestiary(
    data: bytes,
    after_chunk10_off: int,
    file_end: int,
) -> dict[int, dict[int, int]]:
    """Decodifica el chunk 11 (bestiario) a ``{record_type: {packed_entity_id: value}}``.

    Record types: 1=hits, 2=deaths, 3=kills, 4=encounters.

    Layout (validado contra el fixture, NO coincide con la spec del plan):
      - Cabecera del chunk 11 ya leída por el caller (12 bytes <iii> con count=4).
      - 4 sub-registros consecutivos. Cada uno:
          header  : <ii> = (rec_type:s4, len_field:s4)
          entries : (len_field // 4) entradas de 8 bytes <ii> = (packed_entity, value)
        ``len_field`` NO es bytes del body — sigue la convención del header
        de chunks "macro" (len = count * 4) independientemente del tamaño
        real de cada entry (8 bytes aquí).
      - Tras los 4 sub-registros hay 4 bytes de footer/padding que NO forman
        parte del bestiario (van antes de la AfterbirthChecksum de 4 bytes).

    El ``packed_entity_id`` se devuelve sin descomponer; la descomposición a
    ``(type, variant)`` la hace el consumidor (state_mapper). Para referencia,
    la fórmula validada es ``packed = (type << 20) | (variant << 4)``,
    es decir ``type = packed >> 20`` y ``variant = (packed >> 4) & 0xFFF``.

    Devuelve dicts vacíos si el chunk está truncado o tiene un count != 4.
    """
    out: dict[int, dict[int, int]] = {1: {}, 2: {}, 3: {}, 4: {}}
    if after_chunk10_off + _CHUNK_HEADER_SIZE > file_end:
        return out
    _chunk_type, _len, count = struct.unpack_from("<iii", data, after_chunk10_off)
    if count != 4:
        return out
    off = after_chunk10_off + _CHUNK_HEADER_SIZE
    for _ in range(count):
        if off + 8 > file_end:
            break
        rec_type, len_field = struct.unpack_from("<ii", data, off)
        off += 8
        n_entries = len_field // 4  # convención len = count*4 del header de chunks
        body_end = off + n_entries * 8
        if body_end > file_end or rec_type not in out:
            off = body_end
            continue
        for i in range(n_entries):
            entry_off = off + i * 8
            entity, value = struct.unpack_from("<ii", data, entry_off)
            out[rec_type][entity] = value
        off = body_end
    return out


def _extract_donation_counters(counters_body: bytes) -> tuple[int, int]:
    """Lee los dos contadores de donación del chunk 2 (4 bytes s32 LE por entry).

    Los índices están confirmados contra el save fixture de Repentance+
    y un save 100% completado externo (Zamiell/isaac-save-installer). Ver
    docs/superpowers/specs/2026-05-16-greed-donations-design.md sección
    "Datos" para el detalle de la identificación.
    """
    def read_at(idx: int) -> int:
        offset = idx * 4
        if offset + 4 > len(counters_body):
            return 0
        return struct.unpack_from("<i", counters_body, offset)[0]
    return read_at(_DONATION_NORMAL_INDEX), read_at(_DONATION_GREED_INDEX)


def _extract_achievements_set(achievements_body: bytes) -> set[int]:
    """Return the set of achievement byte indices that are set to 1."""
    return {i for i, b in enumerate(achievements_body) if b == 1}


def _extract_chunks(data: bytes, path: Path) -> dict[int, bytes]:
    """Walk the 10 fixed-size chunks and return {chunk_type: body_bytes}."""
    chunks: dict[int, bytes] = {}
    off = _HEADER_SIZE
    for i in range(10):
        if off + _CHUNK_HEADER_SIZE > len(data):
            raise SaveParseError(
                f"Partida truncada: se acabaron los bytes en la cabecera del bloque {i + 1}"
                f" (offset 0x{off:04X}, tamaño del archivo {len(data)}).",
                path=str(path),
            )
        chunk_type, _len_field, count = struct.unpack_from("<iii", data, off)
        body_start = off + _CHUNK_HEADER_SIZE
        body_len = count * _ENTRY_SIZES[i]
        body_end = body_start + body_len
        if body_end > len(data):
            raise SaveParseError(
                f"Partida truncada: el cuerpo del bloque {i + 1} se sale del archivo"
                f" (cuerpo 0x{body_start:04X}..0x{body_end:04X}, tamaño del archivo {len(data)}).",
                path=str(path),
            )
        chunks[chunk_type] = data[body_start:body_end]
        off = body_end

    for required, label in (
        (_CHUNK_ACHIEVEMENTS, "logros"),
        (_CHUNK_CHALLENGE_COUNTERS, "retos"),
        (_CHUNK_COLLECTIBLES, "ítems"),
        (_CHUNK_COUNTERS, "contadores"),
    ):
        if required not in chunks:
            raise SaveParseError(f"No se encontró el bloque de {label} en la partida.", path=str(path))
    return chunks


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

    A character is considered unlocked if EITHER:
    (a) its dedicated unlock-achievement byte is set in the achievements
        chunk (see `CHARACTER_UNLOCK_ACHIEVEMENTS`), OR
    (b) any of its 13 mark achievements is set (the "any-mark" heuristic).

    Isaac (PlayerType 0) is the starting character and is hard-coded as
    always unlocked.

    Rule (a) is the precise signal — the game flips that byte the first
    time the character is unlocked, before any completion mark is earned.
    Rule (b) is kept as a safety net so that an edited or pre-migration
    save with marks but no unlock byte still reports the character as
    unlocked.

    Marks are translated from agusaenz save order to HTML display order
    using `SAVE_TO_HTML_MARK`.
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
        unlock_ach = CHARACTER_UNLOCK_ACHIEVEMENTS.get(playertype_id)
        if unlock_ach is not None and 0 <= unlock_ach < ach_len and achievements_body[unlock_ach] == 1:
            unlocked.add(playertype_id)

    return unlocked, marks


def _infer_slot_from_name(path: Path) -> int:
    """Return the slot number embedded in the filename, or 0 if not derivable."""
    m = _SLOT_NAME_RE.search(path.name)
    if m:
        return int(m.group(1))
    return 0
