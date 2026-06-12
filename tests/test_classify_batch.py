"""
tests/test_classify_batch.py — Test pipeline batch classify_knowledge_base.py

Test 1: Fase A con mock LLM — 3 atti classificati e salvati nel checkpoint
Test 2: Resume Fase A — checkpoint parziale, solo atti mancanti processati
Test 3: Fase C rule-based — mapping organo→settore + disambiguazione cassazione
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Assicurati che il modulo sia importabile
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import delle funzioni da testare
from scripts.classify_knowledge_base import (
    _parse_settori_response,
    _classify_cassazione,
    _build_settore_prompt,
    _load_checkpoint,
    _append_checkpoint,
    ORGANO_SETTORE_MAP,
    SETTORI_VALIDI,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_mongo(normattiva_docs: list[dict], existing_chunks: int = 0):
    """Crea un mock MongoClient con dati predefiniti."""
    mock_client = MagicMock()

    # legal_lab.normattiva_docs
    mock_source_coll = MagicMock()
    act_urns = list({d.get("act_urn", d.get("urn", "")) for d in normattiva_docs})
    mock_source_coll.distinct.return_value = act_urns

    def find_side_effect(query, projection=None, limit=None):
        act_urn = query.get("act_urn") or query.get("urn")
        docs = [d for d in normattiva_docs if d.get("act_urn") == act_urn or d.get("urn") == act_urn]
        if limit:
            docs = docs[:limit]
        return iter(docs)

    mock_source_coll.find.side_effect = find_side_effect

    # aiura_legal_lab_db.chunks
    mock_chunks_coll = MagicMock()
    mock_update_result = MagicMock()
    mock_update_result.modified_count = existing_chunks
    mock_chunks_coll.update_many.return_value = mock_update_result

    mock_legal_lab = MagicMock()
    mock_legal_lab.__getitem__ = lambda self, name: mock_source_coll

    mock_aiura = MagicMock()
    mock_aiura.__getitem__ = lambda self, name: mock_chunks_coll

    def getitem_side(name):
        if name == "legal_lab":
            return mock_legal_lab
        elif name == "aiura_legal_lab_db":
            return mock_aiura
        return MagicMock()

    mock_client.__getitem__.side_effect = getitem_side
    mock_client.close = MagicMock()

    return mock_client, mock_source_coll, mock_chunks_coll


# ---------------------------------------------------------------------------
# Test 1: Fase A con mock LLM — 3 atti classificati e salvati nel checkpoint
# ---------------------------------------------------------------------------

class TestFaseAWithMockLLM:
    def test_tre_atti_classificati(self, tmp_path: Path):
        """Fase A: 3 atti vengono classificati e salvati nel checkpoint."""
        from scripts.classify_knowledge_base import fase_a

        normattiva_docs = [
            {
                "act_urn": "urn:nir:stato:codice.civile:1942-03-16",
                "urn": "urn:nir:stato:codice.civile:1942-03-16;art1",
                "titolo": "Codice Civile",
                "titolo_articolo": "Delle persone fisiche",
            },
            {
                "act_urn": "urn:nir:stato:codice.penale:1930-10-19",
                "urn": "urn:nir:stato:codice.penale:1930-10-19;art1",
                "titolo": "Codice Penale",
                "titolo_articolo": "Dei reati in generale",
            },
            {
                "act_urn": "urn:nir:stato:decreto.legislativo:2003-09-30;165",
                "urn": "urn:nir:stato:decreto.legislativo:2003-09-30;165;art1",
                "titolo": "Norme generali sull'ordinamento del lavoro",
                "titolo_articolo": "Ambito di applicazione",
            },
        ]

        mock_llm_responses = [
            '{"settori": ["civile"], "confidence": 0.9}',
            '{"settori": ["penale"], "confidence": 0.95}',
            '{"settori": ["lavoro", "amministrativo"], "confidence": 0.85}',
        ]

        call_count = [0]

        def mock_ollama(prompt, model, timeout=120):
            resp = mock_llm_responses[call_count[0] % len(mock_llm_responses)]
            call_count[0] += 1
            return resp

        mock_client, mock_source_coll, mock_chunks_coll = _make_mock_mongo(normattiva_docs)

        with patch("scripts.classify_knowledge_base.get_mongo_client", return_value=mock_client), \
             patch("scripts.classify_knowledge_base._ollama_generate", side_effect=mock_ollama):
            fase_a("mio-studio", "test-model", 8, tmp_path)

        # Verifica checkpoint creato con 3 atti
        checkpoint_file = tmp_path / "act_classification.json"
        assert checkpoint_file.exists(), "Checkpoint non creato"

        checkpoint = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        assert len(checkpoint) == 3, f"Attesi 3 atti nel checkpoint, trovati {len(checkpoint)}"

        # Verifica che i settori siano validi
        for act_urn, entry in checkpoint.items():
            assert "settori" in entry
            assert "confidence" in entry
            for s in entry["settori"]:
                assert s in SETTORI_VALIDI, f"Settore non valido: {s}"

        # Verifica che update_many sia stato chiamato 3 volte
        assert mock_chunks_coll.update_many.call_count == 3

    def test_llm_json_invalido_fallback_altro(self, tmp_path: Path):
        """Fase A: risposta LLM non JSON → fallback a ['altro'] con confidence 0.0."""
        from scripts.classify_knowledge_base import fase_a

        normattiva_docs = [{
            "act_urn": "urn:nir:test:1",
            "titolo": "Test",
            "titolo_articolo": "Art 1",
        }]

        mock_client, mock_source_coll, mock_chunks_coll = _make_mock_mongo(normattiva_docs)

        with patch("scripts.classify_knowledge_base.get_mongo_client", return_value=mock_client), \
             patch("scripts.classify_knowledge_base._ollama_generate", return_value="risposta non valida"):
            fase_a("mio-studio", "test-model", 8, tmp_path)

        checkpoint = json.loads((tmp_path / "act_classification.json").read_text(encoding="utf-8"))
        entry = checkpoint.get("urn:nir:test:1", {})
        assert entry.get("settori") == ["altro"]
        assert entry.get("confidence") == 0.0


# ---------------------------------------------------------------------------
# Test 2: Resume Fase A — checkpoint parziale, solo atti mancanti processati
# ---------------------------------------------------------------------------

class TestFaseAResume:
    def test_skip_atti_gia_nel_checkpoint(self, tmp_path: Path):
        """Resume: solo gli atti non presenti nel checkpoint vengono processati."""
        from scripts.classify_knowledge_base import fase_a

        normattiva_docs = [
            {"act_urn": "urn:atto:1", "titolo": "Atto 1", "titolo_articolo": ""},
            {"act_urn": "urn:atto:2", "titolo": "Atto 2", "titolo_articolo": ""},
            {"act_urn": "urn:atto:3", "titolo": "Atto 3", "titolo_articolo": ""},
        ]

        # Simula checkpoint parziale: atto 1 e 2 già classificati
        existing_checkpoint = {
            "urn:atto:1": {"settori": ["civile"], "confidence": 0.9, "titolo": "Atto 1"},
            "urn:atto:2": {"settori": ["penale"], "confidence": 0.85, "titolo": "Atto 2"},
        }
        checkpoint_file = tmp_path / "act_classification.json"
        checkpoint_file.write_text(
            json.dumps(existing_checkpoint, ensure_ascii=False), encoding="utf-8"
        )

        llm_call_count = [0]

        def mock_ollama(prompt, model, timeout=120, system=None):
            llm_call_count[0] += 1
            # Formato batch: array JSON con un oggetto per ogni atto nel prompt
            return '[{"act_urn": "urn:atto:3", "settori": ["amministrativo"], "confidence": 0.8}]'

        mock_client, mock_source_coll, mock_chunks_coll = _make_mock_mongo(normattiva_docs)

        with patch("scripts.classify_knowledge_base.get_mongo_client", return_value=mock_client), \
             patch("scripts.classify_knowledge_base._ollama_generate", side_effect=mock_ollama):
            fase_a("mio-studio", "test-model", 8, tmp_path)

        # LLM chiamato solo 1 volta (solo urn:atto:3 mancante)
        assert llm_call_count[0] == 1, \
            f"LLM chiamato {llm_call_count[0]} volte, attesa 1 (solo atto 3 mancante)"

        # update_many chiamato solo per atto 3
        assert mock_chunks_coll.update_many.call_count == 1

        # Checkpoint finale ha tutti e 3 gli atti
        final_checkpoint = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        assert len(final_checkpoint) == 3, \
            f"Checkpoint finale atteso 3 atti, trovati {len(final_checkpoint)}"
        assert "urn:atto:3" in final_checkpoint

    def test_no_duplicati_nel_checkpoint(self, tmp_path: Path):
        """Resume: esecuzione ripetuta non crea duplicati nel checkpoint."""
        from scripts.classify_knowledge_base import fase_a

        normattiva_docs = [{"act_urn": "urn:test:1", "titolo": "Test", "titolo_articolo": ""}]
        mock_client, _, _ = _make_mock_mongo(normattiva_docs)

        with patch("scripts.classify_knowledge_base.get_mongo_client", return_value=mock_client), \
             patch("scripts.classify_knowledge_base._ollama_generate",
                   return_value='{"settori": ["civile"], "confidence": 0.9}'):
            fase_a("mio-studio", "test-model", 8, tmp_path)
            # Seconda esecuzione
            fase_a("mio-studio", "test-model", 8, tmp_path)

        checkpoint = json.loads((tmp_path / "act_classification.json").read_text(encoding="utf-8"))
        # Deve avere esattamente 1 entry, non 2
        assert len(checkpoint) == 1


# ---------------------------------------------------------------------------
# Test 3: Fase C — rule-based mapping organo→settore
# ---------------------------------------------------------------------------

class TestFaseC:
    @pytest.mark.parametrize("organo,expected_settori,min_confidence", [
        ("tar",             ["amministrativo"],                0.85),
        ("consiglio_stato", ["amministrativo"],                0.90),
        ("corte_cost",      ["costituzionale"],                0.90),
        ("corte_conti",     ["amministrativo", "tributario"],  0.80),
    ])
    def test_mapping_organo_settore(self, organo, expected_settori, min_confidence, tmp_path):
        """Fase C: verifica mapping organo→settore per organi non-cassazione."""
        from scripts.classify_knowledge_base import fase_c
        import pymongo as pm_mod

        chunks = [
            {
                "_id": f"id_{organo}",
                "corpus": "giurisprudenza",
                "organo": organo,
                "text": "Testo della sentenza " * 10,
                "settore_confidence": 0,
            }
        ]

        captured_updates = []

        mock_coll = MagicMock()
        mock_coll.find.return_value = iter(chunks)

        def mock_bulk_write(ops, ordered=True):
            for op in ops:
                captured_updates.append(op)
            return MagicMock()

        mock_coll.bulk_write.side_effect = mock_bulk_write

        mock_aiura = MagicMock()
        mock_aiura.__getitem__ = lambda self, name: mock_coll

        mock_client = MagicMock()
        mock_client.__getitem__ = lambda self, name: mock_aiura
        mock_client.close = MagicMock()

        with patch("scripts.classify_knowledge_base.get_mongo_client", return_value=mock_client):
            fase_c("mio-studio", 100, tmp_path)

        assert len(captured_updates) == 1
        update_doc = captured_updates[0]._doc  # pymongo UpdateOne interno
        # Verifica che l'update contenga i settori attesi
        set_doc = update_doc.get("$set", {})
        assert set(set_doc.get("settore", [])) == set(expected_settori), \
            f"Settori attesi {expected_settori}, trovati {set_doc.get('settore')}"
        assert set_doc.get("settore_confidence", 0) >= min_confidence

    def test_cassazione_penale_via_keyword(self, tmp_path):
        """Fase C: cassazione con keyword penali → ['penale']."""
        settori, confidence = _classify_cassazione(
            "Il reato di omicidio è punito con la reclusione. L'imputato ha commesso il fatto."
        )
        assert settori == ["penale"]
        assert confidence >= 0.7

    def test_cassazione_civile_default(self, tmp_path):
        """Fase C: cassazione senza keyword penali → ['civile']."""
        settori, confidence = _classify_cassazione(
            "Il contratto di compravendita richiede il consenso delle parti contraenti."
        )
        assert settori == ["civile"]
        assert confidence >= 0.5

    def test_cassazione_singola_keyword_penale(self):
        """Fase C: cassazione con 1 keyword penale → ['penale'] con confidence ridotta."""
        settori, confidence = _classify_cassazione("Il reato è prescritto.")
        assert settori == ["penale"]
        assert 0.5 <= confidence < 0.9

    def test_chunk_troppo_corto_non_classificato(self, tmp_path):
        """Fase C: chunk con testo < 20 char → is_indexed=False."""
        from scripts.classify_knowledge_base import fase_c

        chunks = [
            {
                "_id": "id_short",
                "corpus": "giurisprudenza",
                "organo": "tar",
                "text": "Breve",
                "settore_confidence": 0,
            }
        ]

        captured_updates = []

        mock_coll = MagicMock()
        mock_coll.find.return_value = iter(chunks)

        def mock_bulk_write(ops, ordered=True):
            for op in ops:
                captured_updates.append(op)
            return MagicMock()

        mock_coll.bulk_write.side_effect = mock_bulk_write

        mock_aiura = MagicMock()
        mock_aiura.__getitem__ = lambda self, name: mock_coll
        mock_client = MagicMock()
        mock_client.__getitem__ = lambda self, name: mock_aiura
        mock_client.close = MagicMock()

        with patch("scripts.classify_knowledge_base.get_mongo_client", return_value=mock_client):
            fase_c("mio-studio", 100, tmp_path)

        assert len(captured_updates) == 1
        update_doc = captured_updates[0]._doc
        assert update_doc.get("$set", {}).get("is_indexed") is False

    def test_tutti_gli_organi_mappati(self):
        """Tutti gli organi in ORGANO_SETTORE_MAP producono settori validi."""
        for organo, (settori, confidence) in ORGANO_SETTORE_MAP.items():
            for s in settori:
                assert s in SETTORI_VALIDI, f"Settore non valido per {organo}: {s}"
            assert 0.0 <= confidence <= 1.0


# ---------------------------------------------------------------------------
# Test helper: _parse_settori_response
# ---------------------------------------------------------------------------

class TestParseSettoriResponse:
    def test_json_valido(self):
        raw = '{"settori": ["civile", "processuale"], "confidence": 0.87}'
        settori, confidence = _parse_settori_response(raw)
        assert settori == ["civile", "processuale"]
        assert confidence == pytest.approx(0.87)

    def test_json_con_testo_attorno(self):
        raw = 'Ecco la risposta: {"settori": ["penale"], "confidence": 0.9} Fine.'
        settori, confidence = _parse_settori_response(raw)
        assert settori == ["penale"]

    def test_settori_non_validi_filtrati(self):
        raw = '{"settori": ["civile", "spazio", "altro"], "confidence": 0.5}'
        settori, confidence = _parse_settori_response(raw)
        assert "spazio" not in settori
        assert "civile" in settori

    def test_json_invalido_fallback(self):
        raw = "Non so rispondere"
        settori, confidence = _parse_settori_response(raw)
        assert settori == ["altro"]
        assert confidence == 0.0

    def test_json_vuoto_settori(self):
        raw = '{"settori": [], "confidence": 0.5}'
        settori, confidence = _parse_settori_response(raw)
        assert settori == ["altro"]

    def test_confidence_clamp(self):
        raw = '{"settori": ["civile"], "confidence": 1.5}'
        _, confidence = _parse_settori_response(raw)
        assert confidence <= 1.0

        raw = '{"settori": ["civile"], "confidence": -0.5}'
        _, confidence = _parse_settori_response(raw)
        assert confidence >= 0.0
