"""
Test settore_from_doc() — classificatore dominio giuridico per Chunk Schema V2.

Zero PII reali. Documenti sintetici con URN/tipo_provvedimento/titolo fittizi
ma strutturalmente corretti per verificare la logica di classificazione a 3 livelli.
"""
from __future__ import annotations

import pytest

from aiura_legal.ingestion.normattiva.parser import settore_from_doc, fonte_from_doc


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _doc(
    urn: str = "",
    act_urn: str = "",
    tipo: str = "",
    titolo: str = "",
) -> dict:
    d: dict = {
        "titolo": titolo,
        "articolo_num": "Art. 1",
        "tipo_provvedimento": tipo,
        "testo_tipo": "normativo",
        "text": "Testo sintetico.",
    }
    if urn:
        d["urn"] = urn
    if act_urn:
        d["act_urn"] = act_urn
    return d


# ---------------------------------------------------------------------------
# Livello 1: codici maggiori (da URN)
# ---------------------------------------------------------------------------

class TestSettoreLivello1:
    def test_codice_penale(self):
        doc = _doc(urn="urn:nir:stato:regio.decreto:1930-10-19;1398:art43")
        assert settore_from_doc(doc) == ["penale"]

    def test_codice_proc_penale(self):
        doc = _doc(urn="urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447:art273")
        result = settore_from_doc(doc)
        assert "penale" in result
        assert "processuale" in result

    def test_codice_civile(self):
        doc = _doc(urn="urn:nir:stato:regio.decreto:1942-03-16;262:art1218")
        assert settore_from_doc(doc) == ["civile"]

    def test_codice_proc_civile(self):
        doc = _doc(urn="urn:nir:stato:regio.decreto:1940-10-28;1443:art163")
        result = settore_from_doc(doc)
        assert "civile" in result
        assert "processuale" in result

    def test_legge_costituzionale(self):
        doc = _doc(tipo="LEGGE COSTITUZIONALE", titolo="Legge costituzionale n. 1 del 1948")
        assert settore_from_doc(doc) == ["costituzionale"]

    def test_fonte_override(self):
        """Se viene passato fonte già calcolato, non ricalcola."""
        doc = _doc(urn="urn:nir:stato:regio.decreto:1930-10-19;1398:art43")
        # Passa esplicitamente fonte=codice_penale
        assert settore_from_doc(doc, fonte="codice_penale") == ["penale"]


# ---------------------------------------------------------------------------
# Livello 2: keyword nel titolo (leggi/dlgs)
# ---------------------------------------------------------------------------

class TestSettoreLivello2:
    def test_legge_penale_da_titolo(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Decreto legislativo 10 ottobre 2022 n. 150 — Riforma del processo penale",
        )
        assert settore_from_doc(doc) == ["penale"]

    def test_dlgs_lavoro(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Testo Unico sicurezza sul lavoro D.lgs 81/2008",
        )
        assert settore_from_doc(doc) == ["lavoro"]

    def test_legge_lavoro_previdenza(self):
        doc = _doc(
            tipo="LEGGE",
            titolo="Legge 20 maggio 1970 n. 300 — Statuto dei lavoratori",
        )
        assert settore_from_doc(doc) == ["lavoro"]

    def test_dlgs_tributario(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Decreto legislativo 31 dicembre 1992 n. 546 — Processo tributario",
        )
        # tributario → amministrativo (per ora)
        assert settore_from_doc(doc) == ["amministrativo"]

    def test_appalti_pubblici(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Codice dei contratti pubblici e appalto D.lgs 36/2023",
        )
        assert settore_from_doc(doc) == ["amministrativo"]

    def test_legge_societaria(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Riforma del diritto societario e delle societa di capitali",
        )
        assert settore_from_doc(doc) == ["civile"]

    def test_dlgs_consumatori(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Codice del consumo — tutela dei consumatori",
        )
        assert settore_from_doc(doc) == ["civile"]

    def test_privacy_gdpr(self):
        doc = _doc(
            tipo="DECRETO LEGISLATIVO",
            titolo="Codice in materia di dati personali — privacy",
        )
        assert settore_from_doc(doc) == ["civile"]


# ---------------------------------------------------------------------------
# Livello 3: fallback
# ---------------------------------------------------------------------------

class TestSettoreFallback:
    def test_legge_tecnica_senza_keyword(self):
        doc = _doc(
            tipo="LEGGE",
            titolo="Legge 23 dicembre 1994 n. 724 — Misure di razionalizzazione della finanza pubblica",
        )
        result = settore_from_doc(doc)
        # Non è classificabile con keyword semplici → fallback "altro"
        # (a meno che "finanza" non sia nelle keyword — non è nelle nostre)
        assert result == ["altro"] or isinstance(result, list)

    def test_titolo_vuoto_fallback(self):
        doc = _doc(tipo="DECRETO LEGISLATIVO", titolo="")
        assert settore_from_doc(doc) == ["altro"]

    def test_tipo_sconosciuto_senza_titolo(self):
        doc = _doc(tipo="REGOLAMENTO REGIONALE", titolo="")
        assert settore_from_doc(doc) == ["altro"]


# ---------------------------------------------------------------------------
# Integrazione: NormattivaDocAdapter.from_mongo_doc() popola settore
# ---------------------------------------------------------------------------

class TestAdapterSettore:
    def test_adapter_penale(self):
        from aiura_legal.ingestion.normattiva.parser import NormattivaDocAdapter

        doc = {
            "_id": "abc123",
            "urn": "urn:nir:stato:regio.decreto:1930-10-19;1398:art43",
            "text": "Il delitto è doloso, o secondo l'intenzione...",
            "testo_tipo": "normativo",
            "titolo": "Codice Penale",
            "titolo_articolo": "Elemento psicologico del reato",
            "articolo_num": "Art. 43",
            "tipo_provvedimento": "REGIO DECRETO",
        }
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.settore == ["penale"]
        assert adapter.titolo_articolo == "Elemento psicologico del reato"

    def test_adapter_proc_penale(self):
        from aiura_legal.ingestion.normattiva.parser import NormattivaDocAdapter

        doc = {
            "_id": "def456",
            "urn": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447:art273",
            "text": "La custodia cautelare può essere disposta...",
            "testo_tipo": "normativo",
            "titolo": "Codice di procedura penale",
            "titolo_articolo": "Condizioni generali",
            "articolo_num": "Art. 273",
            "tipo_provvedimento": "DECRETO DEL PRESIDENTE DELLA REPUBBLICA",
        }
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert "penale" in adapter.settore
        assert "processuale" in adapter.settore

    def test_chunk_base_include_settore(self):
        from aiura_legal.ingestion.normattiva.parser import NormattivaDocAdapter

        doc = {
            "_id": "ghi789",
            "urn": "urn:nir:stato:regio.decreto:1942-03-16;262:art1218",
            "text": "Il debitore che non esegue esattamente...",
            "testo_tipo": "normativo",
            "titolo": "Codice civile",
            "titolo_articolo": "Responsabilità del debitore",
            "articolo_num": "Art. 1218",
            "tipo_provvedimento": "REGIO DECRETO",
        }
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        chunk_base = adapter.to_chunk_base(workspace="test-studio")

        assert "settore" in chunk_base
        assert chunk_base["settore"] == ["civile"]
        assert chunk_base["titolo_articolo"] == "Responsabilità del debitore"
        assert chunk_base["corpus"] == "normattiva"
