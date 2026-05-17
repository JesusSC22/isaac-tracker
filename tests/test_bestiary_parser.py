"""Tests del decoder del chunk 11 (bestiario) del save de Repentance+.

Fórmula del packed entity id (descubierta empíricamente contra el fixture):
    packed = (entity_type << 20) | (entity_variant << 4)

es decir, equivalente a:
    entity_type    = packed >> 20
    entity_variant = (packed >> 4) & 0xFFF

NO es ``type * 1000 + variant`` (la hipótesis original del plan); el verdadero
empaquetado mete (type:u12, variant:u12) cada uno desplazado 4 bits, con los
nibbles bajos reservados (siempre 0 en el fixture, 1510/1510 entries). Esta
fórmula se valida en ``test_packed_entity_ids_decode_to_plausible_type_variant``.

Layout del sub-registro (también difiere del plan):
    header  : <ii = (rec_type:s4, len_field:s4)
    entries : (len_field // 4) entradas de 8 bytes <ii = (packed_entity, value)

``len_field`` NO es el número de bytes del body — sigue la misma convención
que el header de los chunks "macro" del save: ``len_field == count * 4``
independientemente del tamaño real de cada entry (8 bytes aquí). Esta es la
misma observación que el comentario en la cabecera de ``save_parser.py``.

Tras los 4 sub-registros hay 4 bytes de "padding/footer" antes de los últimos
4 bytes (AfterbirthChecksum). Ambos quedan fuera del bestiario.
"""
from pathlib import Path
import struct
import struct as _struct

from tracker.save_parser import (
    _extract_bestiary,
    _BESTIARY_HITS, _BESTIARY_DEATHS, _BESTIARY_KILLS, _BESTIARY_ENCOUNTERS,
)


FIXTURE = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
CHUNK_BESTIARY = 11


def _offset_after_chunk_10(data: bytes) -> int:
    """Compute the file offset where chunk 10 ends (= chunk 11 starts)."""
    from tracker.save_parser import _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES
    off = _HEADER_SIZE
    for i in range(10):
        _t, _l, count = struct.unpack_from("<iii", data, off)
        off = off + _CHUNK_HEADER_SIZE + count * _ENTRY_SIZES[i]
    return off


def _read_bestiary_chunk_body(path):
    """Variante local que NO se detiene en el chunk 10.
    Los primeros 10 chunks vienen como hoy; el 11 ocupa el resto del fichero
    menos los 4 bytes de checksum final.
    """
    from tracker.save_parser import _CHUNK_HEADER_SIZE
    data = path.read_bytes()
    off = _offset_after_chunk_10(data)
    chunk_type, _len, count = struct.unpack_from("<iii", data, off)
    assert chunk_type == CHUNK_BESTIARY
    body_start = off + _CHUNK_HEADER_SIZE
    body_end = len(data) - 4  # menos AfterbirthChecksum
    return count, data[body_start:body_end]


def test_bestiary_chunk_has_four_subrecords():
    count, body = _read_bestiary_chunk_body(FIXTURE)
    assert count == 4
    # The four sub-records must completely consume the body (no gaps, no overflow).
    off = 0
    for _ in range(4):
        _rec_type, len_field = struct.unpack_from("<ii", body, off)
        off += 8 + len_field * 2  # len_field is count*4, entries are 8 bytes → bytes = len_field*2
        assert off <= len(body), "Sub-record overflows body"
    # Allow a small trailing footer/padding (≤16 bytes) before the AfterbirthChecksum tail
    # that's already excluded by _read_bestiary_chunk_body.
    assert 0 <= len(body) - off <= 16, (
        f"Unexpected gap between sub-records and end of bestiary body: {len(body) - off} bytes"
    )


def test_bestiary_subrecords_have_known_types():
    _, body = _read_bestiary_chunk_body(FIXTURE)
    types_found = []
    off = 0
    for _ in range(4):
        rec_type, len_field = struct.unpack_from("<ii", body, off)
        # len_field sigue la convención chunk-header del save: count*4 (NO bytes).
        # Las entries son 8 bytes (<ii> = (packed_entity, value)).
        n_entries = len_field // 4
        types_found.append(rec_type)
        off += 8 + n_entries * 8
    assert sorted(types_found) == [1, 2, 3, 4], (
        f"Tipos esperados [1,2,3,4]; obtenidos {sorted(types_found)} "
        f"(orden de aparición: {types_found})"
    )


def test_extract_bestiary_returns_nonempty_dicts():
    data = FIXTURE.read_bytes()
    off = _offset_after_chunk_10(data)
    result = _extract_bestiary(data, off, len(data) - 4)
    assert len(result[_BESTIARY_KILLS]) > 0, "kills dict must be non-empty in real save"
    assert len(result[_BESTIARY_ENCOUNTERS]) > 0, "encounters dict must be non-empty in real save"
    for d in result.values():
        for v in d.values():
            assert v >= 0


def test_packed_entity_ids_decode_to_plausible_type_variant():
    """Valida la fórmula real: packed = (type << 20) | (variant << 4).

    Es decir, ``type = packed >> 20`` y ``variant = (packed >> 4) & 0xFFF``.
    Los nibbles bajos (bits 0..3 y 16..19) deben ser 0 en todos los entries.
    """
    MAX_PLAUSIBLE_ENTITY_TYPE = 1999  # Repentance+ vanilla < 1000; techo holgado para mods.
    data = FIXTURE.read_bytes()
    off = _offset_after_chunk_10(data)
    bestiary = _extract_bestiary(data, off, len(data) - 4)

    # Todos los entries deben tener los nibbles bajos a 0.
    all_packed = [p for d in bestiary.values() for p in d]
    assert len(all_packed) > 0
    bad = [p for p in all_packed if (p & 0xF) != 0 or ((p >> 16) & 0xF) != 0]
    assert not bad, (
        f"{len(bad)}/{len(all_packed)} packed ids tienen nibbles bajos no nulos. "
        f"Sample: {bad[:5]} (decodificarlos requiere otro layout)"
    )

    # type y variant deben caber en u12; type==0 nunca aparece (no es entidad
    # real); type<=1999 (techo holgado para Rep+ con mods).
    kills = bestiary[_BESTIARY_KILLS]
    invalid = 0
    for packed in kills:
        type_ = packed >> 20
        variant = (packed >> 4) & 0xFFF
        if not (1 <= type_ <= MAX_PLAUSIBLE_ENTITY_TYPE and 0 <= variant <= 999):
            invalid += 1
    assert invalid == 0, (
        f"{invalid}/{len(kills)} packed ids decodifican a (type, variant) fuera "
        f"de rango. Sample: "
        f"{[(p, p>>20, (p>>4)&0xFFF) for p in list(kills)[:5]]}"
    )

    # Sanity adicional: el packed más común tras Gaper (type=10) debe ser
    # un type pequeño (entidades vanilla bajas son las más matadas).
    top_packed, top_kills = max(kills.items(), key=lambda kv: kv[1])
    top_type = top_packed >> 20
    assert top_kills > 100, f"top kill count debería ser >100, fue {top_kills}"
    assert 1 <= top_type <= 999, f"top type fue {top_type}"


# ---------------------------------------------------------------------------
# Tests sintéticos (no dependen del fixture): cubren happy-path y ramas
# defensivas de ``_extract_bestiary``.
# ---------------------------------------------------------------------------


def _build_synthetic_chunk11(records):
    """records: lista de (rec_type, [(packed_id, value), ...]).
    Devuelve (data, after_chunk10_off, file_end) listos para _extract_bestiary."""
    body = b""
    for rec_type, entries in records:
        body += _struct.pack("<ii", rec_type, len(entries) * 4)  # len_field = count * 4
        for packed, val in entries:
            body += _struct.pack("<ii", packed, val)
    # Cabecera chunk 11: (chunk_type=11, _len_unused=0, count=len(records))
    chunk_header = _struct.pack("<iii", 11, 0, len(records))
    data = chunk_header + body
    return data, 0, len(data)


def test_extract_bestiary_decodes_synthetic_buffer():
    """Verifica el decoder sobre bytes construidos a mano: cubre el camino
    feliz sin depender del fixture real."""
    data, off, end = _build_synthetic_chunk11([
        (_BESTIARY_KILLS,     [(0x05500000, 1053), (0x00A00000, 255)]),
        (_BESTIARY_DEATHS,    [(0x01200000, 7)]),
        (_BESTIARY_HITS,      [(0x01700000, 326)]),
        (_BESTIARY_ENCOUNTERS,[(0x05500000, 1)]),
    ])
    result = _extract_bestiary(data, off, end)
    assert result[_BESTIARY_KILLS] == {0x05500000: 1053, 0x00A00000: 255}
    assert result[_BESTIARY_DEATHS] == {0x01200000: 7}
    assert result[_BESTIARY_HITS] == {0x01700000: 326}
    assert result[_BESTIARY_ENCOUNTERS] == {0x05500000: 1}


def test_extract_bestiary_returns_empty_when_count_not_four():
    """Si la cabecera del chunk 11 dice count != 4, el helper devuelve dicts vacíos."""
    chunk_header = _struct.pack("<iii", 11, 0, 3)  # solo 3 sub-records
    body = _struct.pack("<ii", _BESTIARY_KILLS, 0)
    data = chunk_header + body
    result = _extract_bestiary(data, 0, len(data))
    assert result == {1: {}, 2: {}, 3: {}, 4: {}}


def test_extract_bestiary_skips_unknown_record_type():
    """Un rec_type fuera de {1..4} se salta sin romper la decodificación del resto."""
    data, off, end = _build_synthetic_chunk11([
        (_BESTIARY_KILLS,  [(0x00A00000, 5)]),
        (99,               [(0x0EADBEEF, 999)]),   # tipo desconocido (packed cabe en s32)
        (_BESTIARY_HITS,   [(0x00A00000, 3)]),
        (_BESTIARY_DEATHS, [(0x00A00000, 1)]),
    ])
    # Importante: data construido con 4 records (count == 4) y rec_type 99 entre medias.
    result = _extract_bestiary(data, off, end)
    assert result[_BESTIARY_KILLS]  == {0x00A00000: 5}
    assert result[_BESTIARY_HITS]   == {0x00A00000: 3}
    assert result[_BESTIARY_DEATHS] == {0x00A00000: 1}
