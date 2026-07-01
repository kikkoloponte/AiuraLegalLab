"""
Test per normalize_text — pulizia whitespace/tipografia dei chunk in ingestione.
"""
from aiura_legal.ingestion.text_normalizer import normalize_text


def test_empty_and_whitespace_only():
    assert normalize_text("") == ""
    assert normalize_text("   \n\t  ") == ""


def test_collapses_internal_newlines():
    # Caso reale osservato in un chunk normattiva (artefatto estrazione PDF).
    text = "Visti gli\narticoli 76\ne\n87 della Costituzione\n;"
    assert normalize_text(text) == "Visti gli articoli 76 e 87 della Costituzione;"


def test_collapses_multiple_spaces():
    assert normalize_text("Il   debitore    non   esegue") == "Il debitore non esegue"


def test_removes_space_before_punctuation():
    assert normalize_text("Costituzione ; legge .") == "Costituzione; legge."


def test_curly_apostrophe_normalized():
    assert normalize_text("dell’avvocato") == "dell'avvocato"
    assert normalize_text("l‘inadempimento") == "l'inadempimento"


def test_curly_quotes_normalized():
    assert normalize_text("“esempio”") == '"esempio"'


def test_strips_leading_trailing_whitespace():
    assert normalize_text("  testo  \n") == "testo"


def test_idempotent():
    cases = [
        "Visti gli\narticoli 76\ne\n87 della Costituzione\n;",
        "Il   debitore    non   esegue",
        "Costituzione ; legge .",
        "dell’avvocato",
        "“esempio”",
        "  testo  \n",
        "",
    ]
    for text in cases:
        once = normalize_text(text)
        twice = normalize_text(once)
        assert once == twice
