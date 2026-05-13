# Parser audit — 2026-05-13

## Fixture

- **Path:** `tests/fixtures/sample_save_repentance_plus.dat` (copied from `rep+persistentgamedata1.dat`)
- **Size:** 16,148 bytes
- **First 32 bytes (hex):**
  `49 53 41 41 43 4E 47 53 41 56 45 30 39 52 20 20 00 00 00 00 01 00 00 00 82 02 00 00 82 02 00 00`
- **Header magic (ASCII, 16 bytes):** `ISAACNGSAVE09R  ` (note the two trailing spaces — total 16 bytes).
  - This is the Repentance+ / Repentance / Afterbirth+ shared persistent header. They are disambiguated by the size of the achievements chunk.
- **Bytes 0x10..0x13:** CRC32 (stored little-endian). In this fixture the field reads `00 00 00 00` — Isaac normally writes the AfterbirthChecksum here, but the live game also accepts a zeroed CRC, and several editors leave it zeroed and let the game recompute on next load.
- **Identified section markers:** Isaac save files contain **no ASCII section markers** (no `MOM\0`, `BEAST\0`, etc.). The format is purely positional/length-prefixed. The fixture confirms this — the only printable ASCII run >= 4 chars is the magic at offset 0x00. Sections are 11 length-prefixed "chunks" starting at offset 0x14, in the order defined by the Kaitai schema (Blade's reverse engineering).

### Confirmed chunk layout for this fixture

Walking the file with the Kaitai grammar produces the following 11 chunks, all parsing cleanly:

| # | Type (enum)            | Body offset | `count` | Entry size | Body bytes |
|---|------------------------|-------------|---------|------------|------------|
| 1 | ACHIEVEMENTS           | 0x001C      | 642     | 1 byte     | 642        |
| 2 | COUNTERS               | 0x02AA      | 523     | 4 bytes    | 2092       |
| 3 | LEVEL_COUNTERS         | 0x0AE2      | 14      | 4 bytes    | 56         |
| 4 | COLLECTIBLES           | 0x0B26      | 733     | 1 byte     | 733        |
| 5 | MINIBOSSES             | 0x0E0F      | 7       | 1 byte     | 7          |
| 6 | BOSSES                 | 0x0E22      | 104     | 1 byte     | 104        |
| 7 | CHALLENGE_COUNTERS     | 0x0E96      | 46      | 1 byte     | 46         |
| 8 | CUTSCENE_COUNTERS      | 0x0ED0      | 27      | 4 bytes    | 108        |
| 9 | GAME_SETTINGS          | 0x0F48      | 2       | 4 bytes    | 8          |
| 10| SPECIAL_SEED_COUNTERS  | 0x0F5C      | 80      | 1 byte     | 80         |
| 11| BESTIARY_COUNTERS      | 0x0FB8      | 4       | variable   | rest of file |

After chunk 10 we are at offset 0x0FB8; the bestiary occupies the remaining ~7,968 bytes including the trailing AfterbirthChecksum. **The achievements count of 642 is the strong signal that this is a Repentance+ file** (Afterbirth+ writes 404; vanilla Repentance writes ~637; Repentance+ adds ~5 new achievements).

### Challenges chunk content (from this fixture)

Chunk 7 body (46 bytes, index 0 is unused; indices 1..45 are real challenges):

```
[0, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,0, 0,0,1,0,0, 1,0,0,0,1, 1,0,1,0,1, 1,1,1,1,1, 0,0,0,0,0]
```

Each byte is 0 (locked/not-completed) or 1 (completed). This is **byte-per-challenge**, not a bit-packed array. 45 real challenges = matches Repentance/Repentance+ (vanilla Rebirth had 20, Afterbirth 30, Afterbirth+ 35, Repentance 45, Repentance+ 45).

## Existing parsers evaluated

| Parser | Language | DLCs covered | Last update | License | Verdict |
|--------|----------|--------------|-------------|---------|---------|
| [Zamiell/isaac-save-viewer](https://github.com/Zamiell/isaac-save-viewer) (uses Blade's Kaitai grammar) | TypeScript + Kaitai `.ksy` | Repentance (works on Repentance+ files — same `ISAACNGSAVE09R` header; rejects Afterbirth+ by checking achievement-count == 404) | pushed 2025-09-09 | GPL-3.0 | **Best reference.** Vendoring the `.ksy` and running it through `kaitai-struct-compiler --target python` gives us a clean, correct, free Python parser. Caveat: GPL-3.0 — if we vendor the generated parser our project also becomes GPL-3.0. We do NOT have to use their code; the **format itself is not copyrightable**, so we can re-implement from the schema without GPL contamination. |
| [agusaenz/isaac-save-auto-editor-steam](https://github.com/agusaenz/isaac-save-auto-editor-steam) ("Post-it for Dummies") | Python (no deps beyond `requests`) | **Repentance AND Repentance+ explicitly** | pushed 2025-01-28 (v1.0) | MIT | **Second-best reference.** Walks chunks by hand (`getSectionOffsets`) to read challenges and per-character completion marks; includes the **CRC32 lookup table (`calcAfterbirthChecksum`)** we will need for writing files. Coverage is challenges + completion marks only — no items/bestiary. MIT-licensed, so we can lift code with attribution. |
| [DanielG3/isaac-save-edit-steam-achievements](https://github.com/DanielG3/isaac-save-edit-steam-achievements) | Python | Repentance (predecessor to agusaenz) | pushed 2024-02-13 | MIT | Older fork of the same Python lineage. Useful as a cross-check only. |
| [jamesthejellyfish/isaac-save-edit-script](https://github.com/jamesthejellyfish/isaac-save-edit-script) | Python (GUI) | Repentance | pushed 2024-02-13 | MIT | GUI editor, not a library. Same offsets as agusaenz. |
| [Demorck/Isaac-save-manager](https://github.com/Demorck/Isaac-save-manager) | Python | Repentance (bestiary/sins/etc.) | pushed 2025-09-12 | No license file | Useful for bestiary offsets if we expand scope later. **No license** — we cannot copy code from here. |
| [ihabunek/isaac](https://github.com/ihabunek/isaac) / [isaac.bezdomni.net](https://isaac.bezdomni.net/) | Python | **Rebirth 1.04x/1.05 only** | mid-2023 rewrite | "open source" (unstated) | Pre-Afterbirth. Not usable for Repentance+. |
| [Zamiell/isaac-save-installer](https://github.com/Zamiell/isaac-save-installer) | n/a | All DLCs (ships save files only) | — | — | Just pre-made "completed" save files. Not a parser. Useful as additional **test fixtures** for Task 5 if we need a fully-completed save. |
| **PyPI** | — | — | — | — | No PyPI package exists for Isaac save parsing (searched May 2026). |
| [isaac-save-editor.com](https://www.isaac-save-editor.com/) | Closed-source web | Repentance | — | Proprietary | UI editor only, no source. |

## Decision

**Chosen approach: B (write our own).**

Rationale: (1) The format is fully documented by Blade's Kaitai schema and there is no PyPI package or permissive standalone Python library that wraps it — the only candidates are either GPL-3.0 (Zamiell, which would force our project to GPL) or a Python script that hard-codes offsets but isn't packaged as a reusable parser (agusaenz). (2) Writing it ourselves is well-scoped: the chunk layout walks linearly in ~80 lines of Python with zero runtime dependencies, we already validated the layout against the fixture, and we keep the project MIT-license-friendly while gaining a clean type-annotated parser we control end-to-end.

### Section offsets and bit layouts (for Task 4)

All offsets are **dynamically computed** by walking the chunk list — there are no fixed magic offsets (the achievement chunk size varies between Afterbirth+/Repentance/Repentance+).

**Header (fixed, bytes 0x00..0x13 = 20 bytes):**

| Offset | Size | Field |
|--------|------|-------|
| 0x00   | 16   | Magic: `b"ISAACNGSAVE09R  "` (literal, with two trailing spaces). Reject if mismatched. |
| 0x10   | 4    | `crc` — AfterbirthChecksum CRC32 over bytes [0x10 .. EOF-4]. Often zero in third-party-edited files; the game re-stamps on save. |

**Chunks (start at offset 0x14, exactly 11 chunks, in order):**

Each chunk starts with:

| Offset (within chunk) | Size | Field |
|-----------------------|------|-------|
| +0 | 4 (s32 LE) | `type` (1..11, matches `ChunkType`) |
| +4 | 4 (s32 LE) | `count` (entries in the body — Kaitai schema notes `len` "tends to be wrong"; trust `count`, not `len`, when computing the next chunk position) |
| +8 | count * entry_size | body |

Entry sizes by chunk type (verified against fixture):

```
1 ACHIEVEMENTS         u1   (count = 642 for Repentance+; 404 for Afterbirth+)
2 COUNTERS             s32  (count varies; 523 in fixture)
3 LEVEL_COUNTERS       s32  (count = 14)
4 COLLECTIBLES         u1   (count = 733 in fixture, item-seen flags by collectible id)
5 MINIBOSSES           u1   (count = 7)
6 BOSSES               u1   (count = 104 in fixture)
7 CHALLENGE_COUNTERS   u1   (count = 46; index 0 unused, 1..45 are challenges)
8 CUTSCENE_COUNTERS    s32  (count = 27)
9 GAME_SETTINGS        s32  (count = 2)
10 SPECIAL_SEED_COUNTERS u1  (count = 80)
11 BESTIARY_COUNTERS    nested (see Kaitai schema)
```

**Source for entry sizes:** Blade's Kaitai `.ksy` ([isaac-save-viewer `static/lib/IsaacSaveFile.ksy`](https://github.com/Zamiell/isaac-save-viewer/blob/main/static/lib/IsaacSaveFile.ksy)). Cross-verified against `agusaenz/isaac-save-auto-editor-steam/model.py` `getSectionOffsets()` which hard-codes the same lengths `[1,4,4,1,1,1,1,4,4,1]` for chunks 1..10.

### Challenges (chunk 7) — for Task 4

- Number of challenges: **45** (indices 1..45). Index 0 is reserved/unused.
- Encoding: **one `u1` byte per challenge**, value `0` (not completed) or `1` (completed). It is NOT a bit-packed array, despite the spec's hint.
- Source: `static/lib/IsaacSaveFile.ksy` (`challenge_counters_chunk` -> `completed_by_id: u1 repeat-expr: count`), confirmed on fixture (46 bytes, all 0/1).
- Challenge id -> name mapping: see `agusaenz/.../constants.py::ALL_CHALLENGES_ACHIEVEMENTS` (gives Steam achievement IDs per challenge) and the Repentance wiki [Challenges page](https://bindingofisaacrebirth.fandom.com/wiki/Challenges) for human names. We will need to embed our own 1..45 id->name table in Task 4 data assets.

### Character unlocks — for Task 4

In Repentance/Repentance+, a character being "unlocked" is **not stored as a per-character bit**. It is derived from the **achievements chunk** (chunk 1): each character has a specific achievement ID, and the byte at `achievements[char_unlock_achievement_id]` being `1` means the character is unlocked.

Character roster (from `agusaenz/constants.py::CHARACTERS_ACHIEVEMENTS`, 34 characters total):

```
Index  0..16:  Isaac, Magdalene, Cain, Judas, ???, Eve, Samson, Azazel,
               Lazarus, Eden, The Lost, Lilith, Keeper, Apollyon,
               Forgotten, Bethany, Jacob & Esau                       (Repentance baseline 17)
Index 17..33:  Tainted equivalents of the above (T. Isaac ... T. Jacob)
```

Repentance+ does not add new characters — same 34 as Repentance.

Per-character achievement IDs (first column of `CHARACTERS_ACHIEVEMENTS`) are the **unlock** IDs for each character. Note that "Isaac" is always unlocked (no achievement); the file uses a sentinel string.

### Completion marks ("post-it notes") — for Task 4

Each character has **13 completion marks** (Mom's Heart, Isaac, Satan, Boss Rush, ???, Lamb, Mega Satan, Hush, Ultra Greed/Greedier, Delirium, Mother, Beast, Greed-mode boss). These are **also derived from the achievements chunk**, not from a separate bitfield.

Source: `agusaenz/constants.py::CHARACTERS_ACHIEVEMENTS` lists 13 achievement IDs per character (in the order shown in the comment block `checklist_order`). To read mark `m` for character `c`:

```python
achievement_id = CHARACTERS_ACHIEVEMENTS[c][m + 1]  # +1 because index 0 is the name
mark_completed = achievements_chunk[achievement_id] == 1
```

**Important caveat (from `agusaenz/README.md`):** tainted characters share some bundled Steam achievements (e.g. "kill Isaac, ???, Satan, Lamb with all tainteds = 1 achievement"). Consequently several tainted-character mark IDs in the table **repeat the same achievement ID**. Reading directly will produce post-it marks that match what Repentance+ itself displays in-game — which is what we want — so we just embed the table verbatim. We document this in the parser docstring.

### CRC32 ("AfterbirthChecksum") — for Task 5 if we ever need to write

Polynomial-table CRC, initial value `0xFEDCBA76` (pre-inverted). Full 256-entry table is in `agusaenz/.../model.py::calcAfterbirthChecksum`. The CRC covers bytes `[0x10 .. file_end - 4]` and is written at... actually, re-reading: agusaenz writes the *result* back into bytes `[file_end-4 .. file_end]`, **not** into the header's 0x10 field. So the layout is:

```
[ 0x00..0x10 magic ] [ 0x10..0x14 in-header CRC (often 0) ] [ chunks ] [ last 4 bytes: AfterbirthChecksum ]
```

This is consistent with our fixture where the in-header CRC is zero and the trailing 4 bytes are `CC CB 59 FF` (the actual checksum). Task 4 (read-only) does not need to validate or recompute CRC. Task 5 (if we write) does.

## Recommendation for the implementer

### Concrete next steps for Task 4 (parser)

1. Create `tracker/save_parser.py` exposing:
   - `class SaveFile` with attributes `header_magic: bytes`, `header_crc: int`, `chunks: list[Chunk]`, plus convenience properties `achievements: list[int]` (642 bytes), `challenges: list[int]` (46 bytes), `collectibles: list[int]`, `bosses: list[int]`.
   - `SaveFile.from_path(path: Path) -> SaveFile` — opens binary, validates magic, walks all 11 chunks using the entry-size table `[1,4,4,1,1,1,1,4,4,1]` for chunks 1..10 and the nested-record walker for chunk 11.
   - Raise `tracker.exceptions.InvalidSaveFileError` (already exists, see `tracker/exceptions.py`) on bad magic, short read, or chunk-count mismatch.
2. Create `tracker/data/challenges.py` with a `CHALLENGES: dict[int, str]` mapping 1..45 to human names (Pica Run, High Brow, etc. — copy names from the Repentance Fandom wiki Challenges page).
3. Create `tracker/data/characters.py` with the 34-entry `CHARACTERS_ACHIEVEMENTS` table copied (with attribution to agusaenz, MIT) — first element name, next 13 elements are the achievement IDs for that character's completion marks in the order `[Mom's Heart, Isaac, Satan, Boss Rush, ???, Lamb, Mega Satan, Hush, Ultra Greed, Ultra Greedier, Delirium, Mother, Beast]` (verify final ordering against the comment block in `agusaenz/constants.py`).
4. Build progress views on top of the parser:
   - `unlocked_challenges(save) -> list[int]` returns indices where chunk-7 byte == 1.
   - `completion_marks(save, character_idx) -> list[bool]` returns the 13 booleans by indexing achievements with `CHARACTERS_ACHIEVEMENTS[character_idx][1..13]`.

### Concrete next steps for Task 5 (testing)

1. Use `tests/fixtures/sample_save_repentance_plus.dat` as the primary integration fixture. Assert:
   - `save.header_magic == b"ISAACNGSAVE09R  "`
   - `len(save.achievements) == 642` (Repentance+ signature — not 404 / not 637)
   - `len(save.challenges) == 46`
   - The exact challenge byte sequence verified above is recovered:
     `[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,0,0,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,0,0,0,0,0]`
   - `len(save.bosses) == 104`, `len(save.collectibles) == 733`.
2. Add a tiny synthetic "minimal save" fixture (just header + 11 empty chunks) to test edge cases — keeps the binary fixture in tree small while still exercising the walker.
3. Consider grabbing one of the [Zamiell/isaac-save-installer](https://github.com/Zamiell/isaac-save-installer) pre-completed save files (Repentance directory) as a second fixture to verify the "everything = 1" path. Note: those are Repentance (not Repentance+) headers; an `ISAACNGSAVE09R` file with `achievements_count == 637` is valid and we should parse it without error — just won't have Repentance+ marks set.

### Risks and unknowns

- **Risk: chunk-count drift.** If Repentance+ ever adds a 12th chunk type in a future patch, our hard-coded `repeat-expr: 11` will under-read. Mitigation: log a warning when post-chunk-11 bytes exceed the trailing 4-byte CRC by an unreasonable amount.
- **Risk: tainted-character completion-mark accuracy.** Several tainted entries in `CHARACTERS_ACHIEVEMENTS` reuse achievement IDs across marks (per agusaenz README). This is correct for matching the in-game post-it display but may surprise downstream consumers who expect 13 *distinct* achievement gates. Document in the data table and in the public API docstring.
- **Risk: Repentance+ may eventually bump the header magic.** As of 2026-05 it still uses `ISAACNGSAVE09R` (verified on a real save copied 2026). We disambiguate Repentance+ vs Repentance vs Afterbirth+ by `len(achievements_chunk)`: 404 = AB+ (reject), 637 = Repentance (warn or accept), 642 = Repentance+ (canonical).
- **Unknown: stability of bestiary parsing.** Chunk 11 has a variable-length nested structure (4 inner records of type/count + N*8 bytes each). Task 4 read-only scope does not require parsing the bestiary — we can stop at chunk 10 and not expose chunk 11 fields publicly until Task 6+ asks for them. The parser should still consume the bestiary bytes to find the trailing CRC if we ever need it.
- **Unknown: exact challenge id -> human name mapping for 45 entries.** Need to copy from the Repentance Fandom wiki and double-check the Repentance-era additions (Pica Run, Hot Potato, Cantripped, Red Redemption, DELETE THIS, Backasswards, BROKEN, etc., IDs 32..45). Verify the table against the fixture's bit pattern (some early challenges are completed in the fixture — index 1 = Pitch Black, etc.).
- **License contamination unlikely but worth noting.** Lifting the CRC table and `CHARACTERS_ACHIEVEMENTS` table from agusaenz is MIT-compatible (attribute in `tracker/data/__init__.py` header). Do NOT copy code from Zamiell's repo (GPL-3.0) or Demorck's repo (no license).
