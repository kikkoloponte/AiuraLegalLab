"""
Test correct_article_urn() — correzione del numero d'articolo nell'URN
Normattiva quando diverge dal vero contenuto (vedi urn_fix.py per la causa).
"""
from aiura_legal.ingestion.normattiva.urn_fix import correct_article_urn


def test_caso_reale_sequestro_preventivo_dpr_447_1988():
    """Caso reale che ha innescato l'investigazione: DPR 447/1988 ~art380
    contiene effettivamente il testo dell'Art. 321 (sequestro preventivo)."""
    urn = "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art380"
    corrected = correct_article_urn(urn, "Art. 321")
    assert corrected == "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art321"


def test_caso_reale_codice_civile_offset():
    """Codice Civile: urn~art3 in realtà è l'Art. 1 (offset da bis/abrogati)."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262~art3"
    corrected = correct_article_urn(urn, "Art. 1.")
    assert corrected == "urn:nir:stato:regio.decreto:1942-03-16;262~art1"


def test_articolo_gia_corretto_noop():
    """Se il numero nell'URN coincide già con articolo_num, l'URN non cambia."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262~art1218"
    corrected = correct_article_urn(urn, "Art. 1218.")
    assert corrected == urn


def test_articolo_bis_preservato():
    """Suffisso lettera (bis/ter/...) viene ricostruito e normalizzato in minuscolo."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262~art2645bis"
    corrected = correct_article_urn(urn, "Art. 2645-bis.")
    assert corrected == "urn:nir:stato:regio.decreto:1942-03-16;262~art2645bis"


def test_articolo_bis_corretto_quando_urn_sbagliato():
    """Mismatch anche sul suffisso lettera: l'URN dice 'art10' ma il
    contenuto reale è 'Art. 10-bis'."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262~art10"
    corrected = correct_article_urn(urn, "Art. 10-bis.")
    assert corrected == "urn:nir:stato:regio.decreto:1942-03-16;262~art10bis"


def test_urn_non_articolo_invariato():
    """URN senza suffisso '~artN' (es. l'atto stesso) non viene toccato."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262"
    corrected = correct_article_urn(urn, "Art. 1.")
    assert corrected == urn


def test_articolo_num_vuoto_invariato():
    """Se articolo_num è vuoto/non parsabile, l'URN resta invariato (fallback sicuro)."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262~art380"
    assert correct_article_urn(urn, "") == urn
    assert correct_article_urn(urn, "Definizioni generali") == urn


def test_articolo_num_con_punto_e_spazi():
    """Formati comuni di articolo_num: 'Art. 321', 'art.321.', 'Articolo 321'."""
    urn = "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art380"
    for variant in ("Art. 321.", "art.321.", "Art 321", "ART. 321"):
        assert correct_article_urn(urn, variant) == (
            "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art321"
        )


def test_idempotente():
    """Applicare la correzione due volte produce lo stesso risultato
    (necessario per sicurezza: il parser potrebbe rielaborare lo stesso doc)."""
    urn = "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art380"
    once = correct_article_urn(urn, "Art. 321")
    twice = correct_article_urn(once, "Art. 321")
    assert once == twice
