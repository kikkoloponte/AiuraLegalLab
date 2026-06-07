"""
Test anonymizer_bridge con mongomock-motor.
LegalAnonymizer viene mockato per isolare il bridge.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from aiura_legal.jurisprudence.anonymizer_bridge import anonymize_document
from aiura_legal.jurisprudence.models import (
    JurisprudenceDocument,
    OrganoGiudicante,
    SourceChannel,
)


def _make_doc(channel: SourceChannel = SourceChannel.UPLOAD_STUDIO) -> JurisprudenceDocument:
    return JurisprudenceDocument(
        organo=OrganoGiudicante.CASSAZIONE,
        numero="1",
        anno=2024,
        data_deposito=date(2024, 3, 1),
        sezione="III Civile",
        materia="contratti",
        massima="Mario Rossi ha subito un danno.",
        motivazione="In fatto Caio Bianchi conveniva in giudizio.",
        dispositivo="La Corte rigetta.",
        source_channel=channel,
    )


@pytest.fixture
def mock_db():
    db = MagicMock()
    collection = MagicMock()
    insert_result = MagicMock()
    insert_result.inserted_id = "507f1f77bcf86cd799439011"
    collection.insert_one = AsyncMock(return_value=insert_result)
    db.__getitem__ = MagicMock(return_value=collection)
    return db


# ---------------------------------------------------------------------------
# SCRAPING — no-op
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_scraping_noop(mock_db):
    doc = _make_doc(SourceChannel.SCRAPING)
    result = await anonymize_document(doc, mock_db)

    assert result is doc
    assert result.is_anonymized is False
    mock_db["pii_vault"].insert_one.assert_not_called()


# ---------------------------------------------------------------------------
# UPLOAD_STUDIO — anonimizza e scrive pii_vault
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_studio_writes_pii_vault(mock_db):
    doc = _make_doc(SourceChannel.UPLOAD_STUDIO)

    fake_result = MagicMock()
    fake_result.anonymized_text = "[PERSONA_001] ha subito un danno.\nIn fatto [PERSONA_002] conveniva.\nLa Corte rigetta."
    fake_result.entity_map = {"[PERSONA_001]": "Mario Rossi", "[PERSONA_002]": "Caio Bianchi"}
    fake_result.residual_pii_warnings = []

    fake_anonymizer = MagicMock(return_value=MagicMock(anonymize=MagicMock(return_value=fake_result)))

    with patch("aiura_legal.jurisprudence.anonymizer_bridge.LegalAnonymizer", fake_anonymizer):
        result = await anonymize_document(doc, mock_db)

    assert result.is_anonymized is True
    assert result.raw_pii_vault_id is not None
    assert result.source_channel == SourceChannel.UPLOAD_STUDIO
    mock_db["pii_vault"].insert_one.assert_called_once()

    call_args = mock_db["pii_vault"].insert_one.call_args[0][0]
    assert call_args["document_id"] == doc.id
    assert "[PERSONA_001]" in call_args["entity_map"]


@pytest.mark.asyncio
async def test_upload_studio_returns_new_doc_not_mutate(mock_db):
    doc = _make_doc(SourceChannel.UPLOAD_STUDIO)
    original_massima = doc.massima

    fake_result = MagicMock()
    fake_result.anonymized_text = "[X] ha subito.\nMotivazione.\nDispositivo."
    fake_result.entity_map = {"[X]": "Mario Rossi"}
    fake_result.residual_pii_warnings = []

    mock_anon = MagicMock(anonymize=MagicMock(return_value=fake_result))
    with patch("aiura_legal.jurisprudence.anonymizer_bridge.LegalAnonymizer", mock_anon):
        result = await anonymize_document(doc, mock_db)

    assert result is not doc
    assert doc.massima == original_massima  # originale non modificato
    assert result.massima != original_massima


@pytest.mark.asyncio
async def test_upload_studio_preserves_metadata(mock_db):
    doc = _make_doc(SourceChannel.UPLOAD_STUDIO)

    fake_result = MagicMock()
    fake_result.anonymized_text = "Anonimizzato."
    fake_result.entity_map = {}
    fake_result.residual_pii_warnings = []

    mock_anon = MagicMock(anonymize=MagicMock(return_value=fake_result))
    with patch("aiura_legal.jurisprudence.anonymizer_bridge.LegalAnonymizer", mock_anon):
        result = await anonymize_document(doc, mock_db)

    assert result.organo == doc.organo
    assert result.numero == doc.numero
    assert result.anno == doc.anno
    assert result.norme_citate == doc.norme_citate


@pytest.mark.asyncio
async def test_upload_studio_anonymizer_import_error_returns_original(mock_db):
    doc = _make_doc(SourceChannel.UPLOAD_STUDIO)

    with patch("aiura_legal.jurisprudence.anonymizer_bridge.LegalAnonymizer", None):
        result = await anonymize_document(doc, mock_db)

    assert result is doc
    assert result.is_anonymized is False
