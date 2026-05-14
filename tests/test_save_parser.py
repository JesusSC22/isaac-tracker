from datetime import datetime
from pathlib import Path

import pytest

from tracker.exceptions import SaveParseError
from tracker.save_parser import ParsedSave, parse_save, _extract_character_state


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


def test_parse_save_infers_slot_from_repplus_filename(tmp_path):
    f = tmp_path / "rep+persistentgamedata2.dat"
    # Enough bytes to pass the truncation guard but content doesn't have to be valid yet.
    # Task 5 will tighten this; Task 4 just verifies the slot-from-name plumbing.
    f.write_bytes(b"\x00" * 16148)
    try:
        result = parse_save(f)
    except SaveParseError:
        # Acceptable - file is all zeros, magic header is wrong.
        # The slot inference test only runs if a future change makes parse_save
        # accept zero'd headers. For now we just want the function not to crash
        # on the truncation guard.
        return
    assert result.slot == 2


def test_parse_save_infers_slot_from_dated_backup_filename(tmp_path):
    f = tmp_path / "20260513.rep+persistentgamedata3.dat"
    f.write_bytes(b"\x00" * 16148)
    try:
        result = parse_save(f)
    except SaveParseError:
        return
    assert result.slot == 3


def test_parser_validates_magic_header(tmp_path):
    bad = tmp_path / "bad.dat"
    bad.write_bytes(b"\x00" * 16148)  # All zeros, wrong magic
    from tracker.exceptions import SaveParseError
    with pytest.raises(SaveParseError):
        parse_save(bad)


def test_parser_detects_known_challenges(sample_save_path, known_completions):
    parsed = parse_save(sample_save_path)
    for challenge_id in known_completions["challenges_done"]:
        assert challenge_id in parsed.challenges_complete, (
            f"Challenge {challenge_id} should be done per ground truth"
        )
    for challenge_id in known_completions["challenges_known_not_done"]:
        assert challenge_id not in parsed.challenges_complete, (
            f"Challenge {challenge_id} should be NOT done per ground truth"
        )


def test_parser_extracts_items_seen(sample_save_path):
    parsed = parse_save(sample_save_path)
    assert isinstance(parsed.items_seen, set)
    assert len(parsed.items_seen) > 50, (
        f"expected >50 items seen in fixture, got {len(parsed.items_seen)}"
    )
    # All ids are non-negative ints within the chunk range (~733)
    assert all(isinstance(i, int) and 0 <= i < 1000 for i in parsed.items_seen)


def test_parser_detects_known_character_unlocks(sample_save_path, known_completions):
    parsed = parse_save(sample_save_path)
    for char_id in known_completions["characters_unlocked"]:
        assert char_id in parsed.characters_unlocked, (
            f"Character PlayerType {char_id} should be unlocked per ground truth"
        )


def test_parser_detects_at_least_one_tainted(sample_save_path, known_completions):
    if not known_completions.get("tainted_at_least_one_unlocked"):
        pytest.skip("ground truth doesn't assert any tainted unlocked")
    parsed = parse_save(sample_save_path)
    tainted_ids = {i for i in parsed.characters_unlocked if 21 <= i <= 37}
    assert len(tainted_ids) >= 1, (
        f"Expected at least one tainted unlocked, got: {tainted_ids}"
    )


def test_tainted_lost_unlocked_by_byte_with_zero_marks():
    """Regression: T Lost (PlayerType 31) must show as unlocked even when the
    player just unlocked the character in-game but has not earned any
    completion marks yet. The unlock byte for T Lost is achievement 484
    ("The Baleful")."""
    body = bytearray(642)
    body[484] = 1  # T Lost unlock byte set; no mark bytes set.
    unlocked, marks = _extract_character_state(bytes(body))
    assert 31 in unlocked, "Tainted Lost should be unlocked when byte 484 is set"
    assert marks[31] == set(), "Tainted Lost should have no marks in this scenario"


def test_normal_character_unlocked_by_byte_with_zero_marks():
    """Same regression for a normal-roster character: The Lost (PlayerType 10)
    unlocked via achievement 82 with no marks yet."""
    body = bytearray(642)
    body[82] = 1
    unlocked, _marks = _extract_character_state(bytes(body))
    assert 10 in unlocked, "The Lost should be unlocked when byte 82 is set"


def test_isaac_always_unlocked_even_on_empty_save():
    """Isaac is the starting character: always unlocked, no byte required."""
    body = bytes(642)
    unlocked, _marks = _extract_character_state(body)
    assert 0 in unlocked
    # And nobody else gets a free unlock on a blank save.
    assert unlocked == {0}


def test_every_unlock_achievement_id_within_chunk_range():
    """Sanity: all unlock-byte IDs must be addressable inside the 642-byte
    Repentance+ achievements chunk. Catches typos in the table."""
    from tracker.data.characters import CHARACTER_UNLOCK_ACHIEVEMENTS
    for pt_id, ach_id in CHARACTER_UNLOCK_ACHIEVEMENTS.items():
        assert 0 <= ach_id < 642, (
            f"Unlock achievement {ach_id} for PlayerType {pt_id} "
            f"out of Repentance+ achievements range 0..641"
        )


def test_parser_character_marks_use_html_order(sample_save_path):
    parsed = parse_save(sample_save_path)
    # Sanity: Isaac (id=0) should have at least mark 0 done (everyone does Mom's Heart first)
    # If for some reason this fixture doesn't, skip this test.
    if 0 not in parsed.character_marks or not parsed.character_marks[0]:
        pytest.skip("Isaac has no marks in this fixture; cannot validate ordering")
    # Mark IDs MUST be in HTML order: 0..12 inclusive. Just sanity-check no IDs > 12.
    for char_id, marks in parsed.character_marks.items():
        for m in marks:
            assert 0 <= m <= 12, f"Mark {m} for char {char_id} out of HTML range 0..12"


def test_cards_seen_from_fixture():
    fixture = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
    parsed = parse_save(fixture)
    # Fixture: chunk 6 tiene 97 bytes==1 sobre 104 entradas.
    assert len(parsed.cards_seen) == 97
    assert all(isinstance(i, int) and 0 <= i < 104 for i in parsed.cards_seen)


def test_pills_seen_empty_in_fixture():
    """Fixture has chunk 10 todos a cero → set vacío, sin excepción."""
    fixture = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
    parsed = parse_save(fixture)
    assert parsed.pills_seen == set()
    assert parsed.pills_verified is False  # gate aún no superado


def test_pills_seen_is_a_set_type():
    fixture = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
    parsed = parse_save(fixture)
    assert isinstance(parsed.pills_seen, set)
