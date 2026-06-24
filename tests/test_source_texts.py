"""
Test source_texts — fetch del testo completo per i SearchResult.

Usa mongomock (pymongo sync, coerente con il modulo) — zero MongoDB reale.
"""
from __future__ import annotations

import mongomock
import pytest
from bson import ObjectId

from aiura_legal.core.retrieval.source_texts import (
    fetch_full_texts,
    fetch_full_texts_sync,
    fulltext_enabled,
)
from aiura_legal.core.types import SearchResult


@pytest.fixture()
def db():
    client = mongomock.MongoClient()
    return client["aiura_legal_lab_db"]


def _result(
    doc_id: str,
    corpus: str,
    snippet: str = "snippet breve",
    metadata: dict | None = None,
) -> SearchResult:
    meta = {"corpus": corpus}
    if metadata:
        meta.update(metadata)
    return SearchResult(
        doc_id=doc_id,
        score=1.0,
        snippet=snippet,
        source_id=f"src_{doc_id}",
        metadata=meta,
        source_layer="giurisprudenza" if corpus == "giurisprudenza" else "normativa",
    )


# ---------------------------------------------------------------------------
# Corpus chunks: normattiva / dottrina / studio
# ---------------------------------------------------------------------------

class TestChunksCorpora:
    @pytest.mark.parametrize("corpus", ["normattiva", "dottrina", "studio"])
    def test_fetch_per_corpus_chunks(self, db, corpus):
        oid = ObjectId()
        db["chunks"].insert_one({
            "_id": oid,
            "corpus": corpus,
            "text": f"Testo completo del chunk {corpus}. " * 30,
        })
        r = _result(str(oid), corpus)

        fetch_full_texts_sync([r], db=db)

        assert r.full_text.startswith(f"Testo completo del chunk {corpus}.")
        assert len(r.full_text) > 300

    def test_chunk_con_id_stringa(self, db):
        db["chunks"].insert_one({"_id": "id-stringa-1", "text": "Testo con id stringa."})
        r = _result("id-stringa-1", "studio")

        fetch_full_texts_sync([r], db=db)

        assert r.full_text == "Testo con id stringa."

    def test_documento_mancante_fallback_snippet(self, db):
        r = _result(str(ObjectId()), "normattiva", snippet="solo snippet")

        fetch_full_texts_sync([r], db=db)

        # full_text resta vuoto → il chiamante usa lo snippet
        assert r.full_text == ""
        assert r.snippet == "solo snippet"

    def test_full_text_preesistente_non_sovrascritto(self, db):
        r = _result(str(ObjectId()), "normattiva")
        r.full_text = "già arricchito"

        fetch_full_texts_sync([r], db=db)

        assert r.full_text == "già arricchito"


# ---------------------------------------------------------------------------
# Giurisprudenza: lookup jdoc_id + chunk_type
# ---------------------------------------------------------------------------

class TestGiurisprudenza:
    @pytest.fixture()
    def db_giuri(self, db):
        db["jurisprudence"].insert_one({
            "_id": "e65a598d71052357",
            "massima": "La massima della sentenza. " * 20,
            "motivazione": "La motivazione estesa della corte. " * 50,
            "dispositivo": "P.Q.M. la Corte rigetta il ricorso.",
        })
        return db

    @pytest.mark.parametrize("chunk_type,marker", [
        ("massima", "La massima della sentenza."),
        ("motivazione", "La motivazione estesa della corte."),
        ("dispositivo", "P.Q.M."),
    ])
    def test_fetch_per_chunk_type(self, db_giuri, chunk_type, marker):
        r = _result(
            f"e65a598d71052357_{chunk_type}",
            "giurisprudenza",
            metadata={"jdoc_id": "e65a598d71052357", "chunk_type": chunk_type},
        )

        fetch_full_texts_sync([r], db=db_giuri)

        assert r.full_text.startswith(marker)

    def test_fallback_parse_da_doc_id(self, db_giuri):
        """Senza jdoc_id/chunk_type nei metadata, parse dal doc_id hex16_tipo."""
        r = _result("e65a598d71052357_massima", "giurisprudenza")

        fetch_full_texts_sync([r], db=db_giuri)

        assert r.full_text.startswith("La massima della sentenza.")

    def test_sentenza_mancante_fallback_snippet(self, db):
        r = _result(
            "ffffffffffffffff_massima",
            "giurisprudenza",
            snippet="snippet sentenza",
            metadata={"jdoc_id": "ffffffffffffffff", "chunk_type": "massima"},
        )

        fetch_full_texts_sync([r], db=db)

        assert r.full_text == ""


# ---------------------------------------------------------------------------
# Robustezza: mai eccezioni
# ---------------------------------------------------------------------------

class TestRobustezza:
    def test_lista_vuota(self, db):
        fetch_full_texts_sync([], db=db)  # non deve sollevare

    def test_mix_corpora_un_solo_round_trip(self, db):
        oid = ObjectId()
        db["chunks"].insert_one({"_id": oid, "text": "Testo norma."})
        db["jurisprudence"].insert_one({
            "_id": "aaaabbbbccccdddd", "massima": "Massima.", "motivazione": "", "dispositivo": "",
        })
        results = [
            _result(str(oid), "normattiva"),
            _result("aaaabbbbccccdddd_massima", "giurisprudenza",
                    metadata={"jdoc_id": "aaaabbbbccccdddd", "chunk_type": "massima"}),
            _result(str(ObjectId()), "dottrina"),  # mancante
        ]

        fetch_full_texts_sync(results, db=db)

        assert results[0].full_text == "Testo norma."
        assert results[1].full_text == "Massima."
        assert results[2].full_text == ""

    def test_db_rotto_non_solleva(self):
        class _BrokenDb:
            def __getitem__(self, name):
                raise ConnectionError("MongoDB non raggiungibile")

        r = _result(str(ObjectId()), "normattiva")
        fetch_full_texts_sync([r], db=_BrokenDb())  # mai eccezioni
        assert r.full_text == ""


# ---------------------------------------------------------------------------
# Feature flag e wrapper async
# ---------------------------------------------------------------------------

class TestFlagEAsync:
    def test_flag_default_attivo(self, monkeypatch):
        monkeypatch.delenv("AIURA_FULLTEXT_CONTEXT", raising=False)
        assert fulltext_enabled() is True

    def test_flag_zero_disattiva(self, monkeypatch):
        monkeypatch.setenv("AIURA_FULLTEXT_CONTEXT", "0")
        assert fulltext_enabled() is False

    async def test_async_wrapper_fetcha(self, db, monkeypatch):
        monkeypatch.setenv("AIURA_FULLTEXT_CONTEXT", "1")
        oid = ObjectId()
        db["chunks"].insert_one({"_id": oid, "text": "Testo async."})
        r = _result(str(oid), "normattiva")

        await fetch_full_texts([r], db=db)

        assert r.full_text == "Testo async."

    async def test_async_wrapper_skip_con_flag_off(self, db, monkeypatch):
        monkeypatch.setenv("AIURA_FULLTEXT_CONTEXT", "0")
        oid = ObjectId()
        db["chunks"].insert_one({"_id": oid, "text": "Testo che non va fetchato."})
        r = _result(str(oid), "normattiva")

        await fetch_full_texts([r], db=db)

        assert r.full_text == ""


# ---------------------------------------------------------------------------
# Sub-chunk Fase 1: motivazione_{i:03d} — lookup in chunks (non jurisprudence)
# ---------------------------------------------------------------------------

class TestGiuriSubChunkFase1:
    @pytest.fixture()
    def db_con_subchunk(self, db):
        """DB con sub-chunk motivazione Fase 1 nella collection chunks."""
        db["chunks"].insert_one({
            "_id": "e65a598d71052357_motivazione_003",
            "corpus": "giurisprudenza",
            "chunk_type": "motivazione",
            "chunk_index": 3,
            "jdoc_id": "e65a598d71052357",
            "text": "Testo del sub-chunk numero 3. " * 20,
        })
        # Anche la sentenza monolitica esiste in jurisprudence (non deve essere usata)
        db["jurisprudence"].insert_one({
            "_id": "e65a598d71052357",
            "massima": "La massima intera.",
            "motivazione": "La motivazione INTERA della sentenza. " * 50,
            "dispositivo": "Il dispositivo.",
        })
        return db

    def test_subchunk_lookup_in_chunks_collection(self, db_con_subchunk):
        """Sub-chunk motivazione_{i:03d} viene recuperato da chunks, non da jurisprudence."""
        r = _result(
            "e65a598d71052357_motivazione_003",
            "giurisprudenza",
            metadata={
                "corpus": "giurisprudenza",
                "chunk_type": "motivazione",
                "chunk_index": 3,
                "jdoc_id": "e65a598d71052357",
            },
        )

        fetch_full_texts_sync([r], db=db_con_subchunk)

        assert r.full_text.startswith("Testo del sub-chunk numero 3.")
        # Non deve contenere la motivazione intera
        assert "INTERA" not in r.full_text

    def test_subchunk_restituisce_solo_porzione(self, db_con_subchunk):
        """full_text è il testo del chunk atomico, non l'intera motivazione."""
        r = _result(
            "e65a598d71052357_motivazione_003",
            "giurisprudenza",
        )

        fetch_full_texts_sync([r], db=db_con_subchunk)

        # La motivazione intera è molto più lunga del singolo chunk
        assert len(r.full_text) < len("La motivazione INTERA della sentenza. " * 50)

    def test_subchunk_mancante_fallback_vuoto(self, db):
        """Sub-chunk non trovato → full_text vuoto (mai eccezioni)."""
        r = _result(
            "ffffffffffffffff_motivazione_007",
            "giurisprudenza",
            metadata={"corpus": "giurisprudenza", "chunk_index": 7},
        )

        fetch_full_texts_sync([r], db=db)

        assert r.full_text == ""

    def test_mix_legacy_e_subchunk(self, db_con_subchunk):
        """Mix di chunk legacy e sub-chunk Fase 1 vengono gestiti correttamente."""
        # Chunk legacy massima
        r_legacy = _result(
            "e65a598d71052357_massima",
            "giurisprudenza",
            metadata={"jdoc_id": "e65a598d71052357", "chunk_type": "massima"},
        )
        # Sub-chunk Fase 1
        r_sub = _result(
            "e65a598d71052357_motivazione_003",
            "giurisprudenza",
            metadata={"corpus": "giurisprudenza", "chunk_type": "motivazione", "chunk_index": 3},
        )

        fetch_full_texts_sync([r_legacy, r_sub], db=db_con_subchunk)

        assert r_legacy.full_text.startswith("La massima intera.")
        assert r_sub.full_text.startswith("Testo del sub-chunk numero 3.")
