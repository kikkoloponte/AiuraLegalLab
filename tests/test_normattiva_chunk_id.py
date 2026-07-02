"""Test id deterministico dei chunk normattiva (chunk_id.py)."""
from __future__ import annotations

from bson import ObjectId

from aiura_legal.ingestion.normattiva.chunk_id import (
    compute_deterministic_chunk_id,
    normalize_articolo_num,
)


class TestNormalizeArticoloNum:
    def test_numero_semplice_con_punto(self):
        assert normalize_articolo_num("Art. 79.") == "79"

    def test_numero_semplice_senza_punto(self):
        assert normalize_articolo_num("Art. 79") == "79"

    def test_bis_con_trattino(self):
        assert normalize_articolo_num("Art. 612-bis") == "612bis"

    def test_bis_senza_trattino(self):
        assert normalize_articolo_num("Art. 612 bis") == "612bis"

    def test_articolo_esteso(self):
        assert normalize_articolo_num("Articolo 45") == "45"

    def test_stringa_vuota(self):
        assert normalize_articolo_num("") == ""

    def test_octies(self):
        assert normalize_articolo_num("Art. 609-octies") == "609octies"


class TestComputeDeterministicChunkId:
    def test_stesso_input_stesso_id(self):
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79.", valid_from="20000101", chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79.", valid_from="20000101", chunk_index=0,
        )
        assert id1 == id2

    def test_formati_diversi_stesso_articolo_stesso_id(self):
        """'Art. 79' e 'Art. 79.' devono normalizzare allo stesso id."""
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79.", valid_from=None, chunk_index=0,
        )
        assert id1 == id2

    def test_articoli_diversi_id_diversi(self):
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 45", valid_from=None, chunk_index=0,
        )
        assert id1 != id2

    def test_chunk_index_diverso_id_diverso(self):
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=1,
        )
        assert id1 != id2

    def test_workspace_diverso_id_diverso(self):
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="altro-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        assert id1 != id2

    def test_titolo_diverso_id_diverso(self):
        """Stesso numero articolo ma atto diverso (es. art. 79 c.c. vs c.p.p.) non collide."""
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        assert id1 != id2

    def test_valid_from_diverso_id_diverso(self):
        """Due versioni storiche dello stesso articolo non collidono."""
        id1 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from="19420101", chunk_index=0,
        )
        id2 = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from="20240101", chunk_index=0,
        )
        assert id1 != id2

    def test_ritorna_objectid_valido(self):
        result = compute_deterministic_chunk_id(
            workspace="mio-studio", titolo="REGIO DECRETO 16 marzo 1942, n. 262",
            articolo_num="Art. 79", valid_from=None, chunk_index=0,
        )
        assert isinstance(result, ObjectId)
        # round-trip: deve essere ricostruibile da stringa, come ovunque nel codice
        assert ObjectId(str(result)) == result
