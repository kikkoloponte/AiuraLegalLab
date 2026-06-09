"""Test Chunk Schema v3 — sommario e settore_confidence."""
import json
import pytest
from aiura_legal.ingestion.mongodb.models import Chunk


def test_chunk_defaults():
    """Chunk senza i nuovi campi ha valori default corretti."""
    chunk = Chunk(document_id="doc1", chunk_index=0, text="testo di prova")
    assert chunk.sommario is None
    assert chunk.settore_confidence == 0.0


def test_chunk_with_new_fields():
    """Chunk con sommario e settore_confidence si serializza/deserializza correttamente."""
    chunk = Chunk(
        document_id="doc1",
        chunk_index=0,
        text="Art. 1 del codice civile",
        sommario="Primo articolo del codice civile",
        settore_confidence=0.95,
    )
    assert chunk.sommario == "Primo articolo del codice civile"
    assert chunk.settore_confidence == 0.95

    # Serializzazione a dict
    d = chunk.model_dump()
    assert d["sommario"] == "Primo articolo del codice civile"
    assert d["settore_confidence"] == 0.95

    # Round-trip JSON
    json_str = chunk.model_dump_json()
    restored = Chunk.model_validate_json(json_str)
    assert restored.sommario == chunk.sommario
    assert restored.settore_confidence == chunk.settore_confidence


def test_retrocompatibility_old_dict():
    """Un dict MongoDB senza i nuovi campi si carica senza errore."""
    old_doc = {
        "document_id": "doc_old",
        "chunk_index": 1,
        "text": "Vecchio chunk senza v3 fields",
        "corpus": "normattiva",
        "fonte": "legge",
        "testo_tipo": "normativo",
    }
    chunk = Chunk.model_validate(old_doc)
    assert chunk.sommario is None
    assert chunk.settore_confidence == 0.0
    assert chunk.text == "Vecchio chunk senza v3 fields"
