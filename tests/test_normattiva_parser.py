"""
Test fonte_from_doc() e NormattivaDocAdapter.

Zero PII reali. Documenti sintetici con URN/tipo_provvedimento fittizi
ma strutturalmente corretti per verificare la logica di classificazione.
"""
from __future__ import annotations

import pytest

from aiura_legal.ingestion.normattiva.parser import fonte_from_doc, NormattivaDocAdapter


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _doc(
    urn: str = "",
    act_urn: str = "",
    tipo: str = "",
    testo_tipo: str = "normativo",
    text: str = "Testo normativo sintetico.",
) -> dict:
    """Costruisce un doc Normattiva minimale per i test."""
    d: dict = {
        "text": text,
        "testo_tipo": testo_tipo,
        "titolo": "Titolo sintetico",
        "articolo_num": "Art. 1",
        "data_inizio_vigenza": "20240101",
    }
    if urn:
        d["urn"] = urn
    if act_urn:
        d["act_urn"] = act_urn
    if tipo:
        d["tipo_provvedimento"] = tipo
    return d


# ---------------------------------------------------------------------------
# fonte_from_doc — codici maggiori (priorità URN)
# ---------------------------------------------------------------------------

class TestFonteFromDocCodici:

    def test_codice_civile_via_act_urn(self):
        doc = _doc(act_urn="urn:nir:stato:regio.decreto:1942-03-16;262@2024-01-01~art1")
        assert fonte_from_doc(doc) == "codice_civile"

    def test_codice_civile_via_urn(self):
        doc = _doc(urn="urn:nir:stato:regio.decreto:1942-03-16;262~art42")
        assert fonte_from_doc(doc) == "codice_civile"

    def test_codice_penale_via_act_urn(self):
        doc = _doc(act_urn="urn:nir:stato:regio.decreto:1930-10-19;1398@2023-01-01~art575")
        assert fonte_from_doc(doc) == "codice_penale"

    def test_codice_proc_civile_via_act_urn(self):
        doc = _doc(act_urn="urn:nir:stato:regio.decreto:1940-10-28;1443~art163")
        assert fonte_from_doc(doc) == "codice_proc_civile"

    def test_codice_proc_penale_via_act_urn(self):
        doc = _doc(act_urn="urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art1")
        assert fonte_from_doc(doc) == "codice_proc_penale"

    def test_codice_civile_beats_tipo(self):
        """Il match URN deve prevalere su tipo_provvedimento."""
        doc = _doc(
            act_urn="urn:nir:stato:regio.decreto:1942-03-16;262~art1",
            tipo="LEGGE",
        )
        assert fonte_from_doc(doc) == "codice_civile"


# ---------------------------------------------------------------------------
# fonte_from_doc — tipo_provvedimento (match esatto)
# ---------------------------------------------------------------------------

class TestFonteFromDocTipoEsatto:

    def test_legge(self):
        assert fonte_from_doc(_doc(tipo="LEGGE")) == "legge"

    def test_legge_lowercase(self):
        """Match deve essere case-insensitive."""
        assert fonte_from_doc(_doc(tipo="legge")) == "legge"

    def test_decreto_legislativo(self):
        assert fonte_from_doc(_doc(tipo="DECRETO LEGISLATIVO")) == "dlgs"

    def test_decreto_legge(self):
        assert fonte_from_doc(_doc(tipo="DECRETO-LEGGE")) == "dl"

    def test_legge_costituzionale(self):
        assert fonte_from_doc(_doc(tipo="LEGGE COSTITUZIONALE")) == "legge_costituzionale"

    def test_regio_decreto(self):
        assert fonte_from_doc(_doc(tipo="REGIO DECRETO")) == "rd"

    def test_decreto_ministeriale(self):
        assert fonte_from_doc(_doc(tipo="DECRETO MINISTERIALE")) == "dm"

    def test_dpr(self):
        assert fonte_from_doc(_doc(tipo="DECRETO DEL PRESIDENTE DELLA REPUBBLICA")) == "dpr"

    def test_dpcm(self):
        assert fonte_from_doc(
            _doc(tipo="DECRETO DEL PRESIDENTE DEL CONSIGLIO DEI MINISTRI")
        ) == "dpcm"


# ---------------------------------------------------------------------------
# fonte_from_doc — match parziale (fallback)
# ---------------------------------------------------------------------------

class TestFonteFromDocTipoParziale:

    def test_partial_dpr(self):
        assert fonte_from_doc(_doc(tipo="Decreto del Presidente della Repubblica")) == "dpr"

    def test_partial_dpcm(self):
        assert fonte_from_doc(_doc(tipo="Decreto del Presidente del Consiglio dei Ministri")) == "dpcm"

    def test_partial_dm_ministeriale(self):
        assert fonte_from_doc(_doc(tipo="Decreto Ministeriale")) == "dm"

    def test_partial_dm_ministero(self):
        assert fonte_from_doc(_doc(tipo="Decreto del Ministero della Giustizia")) == "dm"


# ---------------------------------------------------------------------------
# fonte_from_doc — fallback "altro"
# ---------------------------------------------------------------------------

class TestFonteFromDocAltro:

    def test_empty_doc(self):
        assert fonte_from_doc({}) == "altro"

    def test_unknown_tipo(self):
        assert fonte_from_doc(_doc(tipo="ORDINANZA SINDACALE")) == "altro"

    def test_no_tipo_no_urn(self):
        assert fonte_from_doc({"text": "testo"}) == "altro"

    def test_circular_urn_not_codice(self):
        """Un URN generico che non contiene frammenti dei codici → "altro" o tipo match."""
        doc = _doc(urn="urn:nir:stato:legge:2020-01-01;1", tipo="LEGGE")
        # Tipo match deve prendere il sopravvento
        assert fonte_from_doc(doc) == "legge"


# ---------------------------------------------------------------------------
# NormattivaDocAdapter
# ---------------------------------------------------------------------------

class TestNormattivaDocAdapter:

    def _make_doc(self, urn: str, tipo: str) -> dict:
        return {
            "_id": "507f1f77bcf86cd799439011",
            "urn": urn,
            "act_urn": urn,
            "tipo_provvedimento": tipo,
            "text": "Articolo sintetico di prova. " * 5,
            "testo_tipo": "normativo",
            "titolo": "Titolo atto sintetico",
            "articolo_num": "Art. 1",
            "data_inizio_vigenza": "20200101",
        }

    def test_from_mongo_doc_corpus_always_normattiva(self):
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.corpus == "normattiva"

    def test_from_mongo_doc_fonte_legge(self):
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.fonte == "legge"

    def test_from_mongo_doc_fonte_codice_civile(self):
        doc = self._make_doc(
            "urn:nir:stato:regio.decreto:1942-03-16;262~art1",
            "REGIO DECRETO",
        )
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.fonte == "codice_civile"

    def test_from_mongo_doc_testo_tipo_propagated(self):
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        doc["testo_tipo"] = "formula"
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.testo_tipo == "formula"

    def test_from_mongo_doc_doc_id_from_id(self):
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.doc_id == "507f1f77bcf86cd799439011"

    def test_from_mongo_doc_no_id_uses_urn(self):
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        del doc["_id"]
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.doc_id == "urn:nir:stato:legge:2020-01-01;1"

    def test_to_chunk_base_fields(self):
        doc = self._make_doc("urn:nir:stato:dlgs:2003-06-30;196", "DECRETO LEGISLATIVO")
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        chunk = adapter.to_chunk_base("normattiva")

        assert chunk["corpus"] == "normattiva"
        assert chunk["fonte"] == "dlgs"
        assert chunk["testo_tipo"] == "normativo"
        assert chunk["workspace"] == "normattiva"
        assert chunk["source"] == "normattiva_it"
        assert chunk["source_id"] == "urn:nir:stato:dlgs:2003-06-30;196"
        assert chunk["document_id"] == "507f1f77bcf86cd799439011"
        assert chunk["valid_from"] == "20200101"

    def test_to_chunk_base_workspace_injected(self):
        doc = self._make_doc("urn:nir:stato:legge:1994-01-01;20", "LEGGE")
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        chunk_civile = adapter.to_chunk_base("normattiva_civile")
        chunk_penale = adapter.to_chunk_base("normattiva_penale")

        assert chunk_civile["workspace"] == "normattiva_civile"
        assert chunk_penale["workspace"] == "normattiva_penale"

    def test_from_mongo_doc_idempotent(self):
        """from_mongo_doc due volte sullo stesso doc produce lo stesso risultato."""
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        a1 = NormattivaDocAdapter.from_mongo_doc(doc)
        a2 = NormattivaDocAdapter.from_mongo_doc(doc)
        assert a1.fonte == a2.fonte
        assert a1.corpus == a2.corpus
        assert a1.testo_tipo == a2.testo_tipo
        assert a1.doc_id == a2.doc_id

    def test_from_mongo_doc_valid_to_present(self):
        """data_fine_vigenza propagata in valid_to."""
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        doc["data_fine_vigenza"] = "20231231"
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.valid_to == "20231231"

    def test_from_mongo_doc_valid_to_vigente(self):
        """data_fine_vigenza='99999999' → norma ancora vigente."""
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        doc["data_fine_vigenza"] = "99999999"
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.valid_to == "99999999"

    def test_from_mongo_doc_valid_to_none_when_absent(self):
        """Se data_fine_vigenza assente → valid_to è None (vigenza sconosciuta)."""
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        doc.pop("data_fine_vigenza", None)
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        assert adapter.valid_to is None

    def test_to_chunk_base_includes_valid_to(self):
        """valid_to deve comparire nel dict restituito da to_chunk_base."""
        doc = self._make_doc("urn:nir:stato:dlgs:2003-06-30;196", "DECRETO LEGISLATIVO")
        doc["data_fine_vigenza"] = "99999999"
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        chunk = adapter.to_chunk_base("normattiva")
        assert "valid_to" in chunk
        assert chunk["valid_to"] == "99999999"

    def test_to_chunk_base_valid_to_none_propagated(self):
        """valid_to=None deve essere propagato nel chunk (non omesso)."""
        doc = self._make_doc("urn:nir:stato:legge:2020-01-01;1", "LEGGE")
        adapter = NormattivaDocAdapter.from_mongo_doc(doc)
        chunk = adapter.to_chunk_base("normattiva")
        assert "valid_to" in chunk
        assert chunk["valid_to"] is None
