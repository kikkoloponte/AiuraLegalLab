"""
Test PII Anonymizer — dati SINTETICI, zero PII reali.
"""
import pytest
from aiura_legal.core.anonymizer.anonymizer import LegalAnonymizer, AnonymizationResult


@pytest.fixture
def anon():
    """Anonymizer solo Layer 1 (no spaCy nei test unitari)."""
    return LegalAnonymizer(use_spacy=False)


# ------------------------------------------------------------------
# Layer 1 — Regex
# ------------------------------------------------------------------

def test_cf_redacted(anon):
    text = "Il sig. TSTAVN80A01H501Z ha firmato il contratto."
    result = anon.anonymize(text)
    assert "TSTAVN80A01H501Z" not in result.anonymized_text
    # Il placeholder è indicizzato: [CF_REDACTED_0]
    assert any("CF_REDACTED" in k for k in result.entity_map.keys())


def test_email_redacted(anon):
    text = "Contatto: avvocato.test@studiolegale.it per informazioni."
    result = anon.anonymize(text)
    assert "avvocato.test@studiolegale.it" not in result.anonymized_text
    assert any("EMAIL_REDACTED" in k for k in result.entity_map.keys())


def test_piva_redacted(anon):
    text = "P. IVA 12345678901 intestata alla società."
    result = anon.anonymize(text)
    assert "12345678901" not in result.anonymized_text


def test_iban_redacted(anon):
    text = "Versare su IBAN IT60X0542811101000000123456."
    result = anon.anonymize(text)
    assert "IT60X0542811101000000123456" not in result.anonymized_text


def test_telefono_redacted(anon):
    text = "Chiamare il 333 1234567 per appuntamento."
    result = anon.anonymize(text)
    assert "333 1234567" not in result.anonymized_text


# ------------------------------------------------------------------
# Whitelist — riferimenti normativi NON anonimizzati
# ------------------------------------------------------------------

def test_articolo_cc_preserved(anon):
    text = "Ai sensi dell'art. 1218 c.c. il debitore è responsabile."
    result = anon.anonymize(text)
    assert "art. 1218 c.c." in result.anonymized_text


def test_dlgs_preserved(anon):
    text = "Come previsto dal D.Lgs. 231/2001 la società risponde."
    result = anon.anonymize(text)
    assert "D.Lgs. 231/2001" in result.anonymized_text


def test_corte_di_cassazione_preserved(anon):
    text = "Secondo la Corte di Cassazione, l'atto è valido."
    result = anon.anonymize(text)
    assert "Corte di Cassazione" in result.anonymized_text


def test_comune_preserved(anon):
    text = "Il Comune di Milano ha rilasciato il permesso."
    result = anon.anonymize(text)
    assert "Comune di Milano" in result.anonymized_text


def test_cass_sez_preserved(anon):
    text = "Cfr. Cass. Sez. III n. 12345/2023 per il precedente."
    result = anon.anonymize(text)
    assert "Cass. Sez. III" in result.anonymized_text


# ------------------------------------------------------------------
# entity_map e restore
# ------------------------------------------------------------------

def test_entity_map_populated(anon):
    text = "CF: TSTAVN80A01H501Z, email: test@test.it"
    result = anon.anonymize(text)
    assert len(result.entity_map) >= 2


def test_restore_identity(anon):
    text = "CF TSTAVN80A01H501Z del cliente."
    result = anon.anonymize(text)
    # Il placeholder nel testo deve essere nella entity_map
    assert any("TSTAVN80A01H501Z" == v for v in result.entity_map.values())
    restored = anon.restore(result.anonymized_text, result.entity_map)
    assert "TSTAVN80A01H501Z" in restored


def test_restore_full_roundtrip(anon):
    original = "Email test@studio.it e CF TSTAVN80A01H501Z per il documento."
    result = anon.anonymize(original, doc_id="doc_test_001")
    # Verifica che i valori siano in entity_map
    values = set(result.entity_map.values())
    assert any("TSTAVN80A01H501Z" in v for v in values)
    assert any("test@studio.it" in v for v in values)
    restored = anon.restore(result.anonymized_text, result.entity_map)
    assert "TSTAVN80A01H501Z" in restored
    assert "test@studio.it" in restored


# ------------------------------------------------------------------
# Stats
# ------------------------------------------------------------------

def test_stats_count(anon):
    text = "CF TSTAVN80A01H501Z. Email a@b.it e c@d.it."
    result = anon.anonymize(text)
    assert result.stats.get("CF", 0) >= 1
    assert result.stats.get("EMAIL", 0) >= 2


def test_empty_text(anon):
    result = anon.anonymize("")
    assert result.anonymized_text == ""
    assert result.entity_map == {}


# ------------------------------------------------------------------
# Layer 2 — spaCy (smoke test con mock)
# ------------------------------------------------------------------

def test_spacy_layer_persona(tmp_path):
    """Smoke test Layer 2: mock spaCy per non richiedere it_core_news_lg nei test."""
    from unittest.mock import MagicMock, patch

    mock_nlp = MagicMock()
    mock_doc = MagicMock()

    mock_ent = MagicMock()
    mock_ent.label_ = "PER"
    mock_ent.text = "Test Avvocato Uno"
    mock_ent.start_char = 3
    mock_ent.end_char = 20
    mock_ent._.has.return_value = False  # nessun score custom

    mock_doc.ents = [mock_ent]
    mock_nlp.return_value = mock_doc

    with patch("aiura_legal.core.anonymizer.anonymizer.LegalAnonymizer._load_spacy"):
        anon_l2 = LegalAnonymizer(use_spacy=True)
        anon_l2._nlp = mock_nlp

    text = "Il Test Avvocato Uno ha redatto l'atto."
    result = anon_l2.anonymize(text)
    assert "Test Avvocato Uno" not in result.anonymized_text
    assert any("PERSONA" in k for k in result.entity_map)
