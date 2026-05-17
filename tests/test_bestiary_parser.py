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

from tracker.save_parser import _extract_chunks  # noqa: F401 — used indirectly below


FIXTURE = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
CHUNK_BESTIARY = 11


def _read_bestiary_chunk_body(path):
    """Variante local que NO se detiene en el chunk 10.
    Los primeros 10 chunks vienen como hoy; el 11 ocupa el resto del fichero
    menos los 4 bytes de checksum final.
    """
    data = path.read_bytes()
    from tracker.save_parser import _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES
    off = _HEADER_SIZE
    for i in range(10):
        chunk_type, _len, count = struct.unpack_from("<iii", data, off)
        body_start = off + _CHUNK_HEADER_SIZE
        body_len = count * _ENTRY_SIZES[i]
        off = body_start + body_len
    chunk_type, _len, count = struct.unpack_from("<iii", data, off)
    assert chunk_type == CHUNK_BESTIARY
    body_start = off + _CHUNK_HEADER_SIZE
    body_end = len(data) - 4  # menos AfterbirthChecksum
    return count, data[body_start:body_end]


def test_bestiary_chunk_has_four_subrecords():
    count, body = _read_bestiary_chunk_body(FIXTURE)
    assert count == 4
    assert len(body) > 0


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
    from tracker.save_parser import (
        _extract_bestiary, _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES,
    )
    data = FIXTURE.read_bytes()
    off = _HEADER_SIZE
    for i in range(10):
        _t, _l, count = struct.unpack_from("<iii", data, off)
        off = off + _CHUNK_HEADER_SIZE + count * _ENTRY_SIZES[i]
    result = _extract_bestiary(data, off, len(data) - 4)
    assert len(result[3]) > 0, "kills dict must be non-empty in real save"
    assert len(result[4]) > 0, "encounters dict must be non-empty in real save"
    for d in result.values():
        for v in d.values():
            assert v >= 0


def test_packed_entity_ids_decode_to_plausible_type_variant():
    """Valida la fórmula real: packed = (type << 20) | (variant << 4).

    Es decir, ``type = packed >> 20`` y ``variant = (packed >> 4) & 0xFFF``.
    Los nibbles bajos (bits 0..3 y 16..19) deben ser 0 en todos los entries.
    """
    from tracker.save_parser import (
        _extract_bestiary, _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES,
    )
    data = FIXTURE.read_bytes()
    off = _HEADER_SIZE
    for i in range(10):
        _t, _l, count = struct.unpack_from("<iii", data, off)
        off = off + _CHUNK_HEADER_SIZE + count * _ENTRY_SIZES[i]
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
    kills = bestiary[3]
    invalid = 0
    for packed in kills:
        type_ = packed >> 20
        variant = (packed >> 4) & 0xFFF
        if not (1 <= type_ <= 1999 and 0 <= variant <= 999):
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
