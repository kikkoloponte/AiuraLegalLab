"""
Test DottrinaMetadataExtractor — estrazione metadati bibliografici dal testo.

Tutti i testi di test sono sintetici (nessun testo reale DPC/SP copiato).
I pattern rispecchiano il formato reale delle riviste ma con contenuto fittizio.
"""
from __future__ import annotations

import pytest

from aiura_legal.ingestion.dottrina.metadata_extractor import (
    DottrinaMetadataExtractor,
    DottrinaMetadata,
)


@pytest.fixture
def extractor() -> DottrinaMetadataExtractor:
    return DottrinaMetadataExtractor(db=None)  # db non usato in extract()


# ---------------------------------------------------------------------------
# DPC — Diritto Penale Contemporaneo
# ---------------------------------------------------------------------------

class TestDPCExtraction:
    DPC_TEXT = """\
DIRITTO PENALE
CONTEMPORANEO
Rivista trimestrale

Fascicolo 3/2019

Direttore responsabile: Francesco Viganò

Il presente contributo analizza il problema del dolo eventuale...
"""

    def test_riconosce_dpc(self, extractor):
        meta = extractor.extract(self.DPC_TEXT, document_id="dpc-001")
        assert meta.rivista == "diritto_penale_contemporaneo"

    def test_estrae_anno(self, extractor):
        meta = extractor.extract(self.DPC_TEXT, document_id="dpc-001")
        assert meta.anno_pubblicazione == 2019

    def test_estrae_fascicolo(self, extractor):
        meta = extractor.extract(self.DPC_TEXT, document_id="dpc-001")
        assert meta.fascicolo == "3/2019"

    def test_estrae_autore(self, extractor):
        meta = extractor.extract(self.DPC_TEXT, document_id="dpc-001")
        assert meta.autore is not None
        assert "Viganò" in meta.autore or "Francesco" in meta.autore

    def test_settore_penale(self, extractor):
        meta = extractor.extract(self.DPC_TEXT, document_id="dpc-001")
        assert meta.settore == ["penale"]

    def test_titolo_dpc(self, extractor):
        meta = extractor.extract(self.DPC_TEXT, document_id="dpc-001")
        assert meta.titolo_doc == "Diritto Penale Contemporaneo"

    def test_fascicolo_diverso(self, extractor):
        text = self.DPC_TEXT.replace("Fascicolo 3/2019", "Fascicolo 10/2022")
        meta = extractor.extract(text)
        assert meta.fascicolo == "10/2022"
        assert meta.anno_pubblicazione == 2022


# ---------------------------------------------------------------------------
# Sistema Penale
# ---------------------------------------------------------------------------

class TestSistemaPenaleExtraction:
    SP_TEXT = """\
Rivista scientifica quadrimestrale di diritto e procedura penale

EDITOR-IN-CHIEF Gian Luigi Gatta

Anno 2021/Fascicolo II

Il contributo tratta dell'elemento soggettivo nei reati omissivi...
"""

    def test_riconosce_sistema_penale(self, extractor):
        meta = extractor.extract(self.SP_TEXT, document_id="sp-001")
        assert meta.rivista == "sistema_penale"

    def test_estrae_anno_sp(self, extractor):
        meta = extractor.extract(self.SP_TEXT, document_id="sp-001")
        assert meta.anno_pubblicazione == 2021

    def test_estrae_fascicolo_sp(self, extractor):
        meta = extractor.extract(self.SP_TEXT, document_id="sp-001")
        assert meta.fascicolo == "Fasc. II/2021"

    def test_autore_gatta(self, extractor):
        meta = extractor.extract(self.SP_TEXT, document_id="sp-001")
        assert meta.autore == "Gatta Gian Luigi"

    def test_settore_penale_sp(self, extractor):
        meta = extractor.extract(self.SP_TEXT, document_id="sp-001")
        assert meta.settore == ["penale"]

    def test_detect_alternativo_editor(self, extractor):
        """Riconosce anche solo tramite EDITOR-IN-CHIEF."""
        text = "EDITOR-IN-CHIEF Gian Luigi Gatta\n\nArticolo sul dolo eventuale."
        meta = extractor.extract(text)
        assert meta.rivista == "sistema_penale"


# ---------------------------------------------------------------------------
# Documento generico (monografia / paper)
# ---------------------------------------------------------------------------

class TestGenericExtraction:
    GENERIC_TEXT = """\
La distinzione tra dolo eventuale e colpa cosciente

Rossi Mario

Pubblicato nel 2018 nell'ambito di un convegno di studi penalistici.

Il problema della linea di confine tra dolo eventuale e colpa cosciente
è stato oggetto di intenso dibattito dottrinale...
"""

    def test_nessuna_rivista(self, extractor):
        meta = extractor.extract(self.GENERIC_TEXT, document_id="gen-001")
        assert meta.rivista is None

    def test_titolo_da_prima_riga(self, extractor):
        meta = extractor.extract(self.GENERIC_TEXT, document_id="gen-001")
        assert meta.titolo_doc is not None
        assert "dolo eventuale" in meta.titolo_doc.lower() or "distinzione" in meta.titolo_doc.lower()

    def test_autore_da_seconda_riga(self, extractor):
        meta = extractor.extract(self.GENERIC_TEXT, document_id="gen-001")
        assert meta.autore is not None
        assert "Rossi" in meta.autore or "Mario" in meta.autore

    def test_anno_da_testo(self, extractor):
        meta = extractor.extract(self.GENERIC_TEXT, document_id="gen-001")
        assert meta.anno_pubblicazione == 2018

    def test_settore_default_penale(self, extractor):
        meta = extractor.extract(self.GENERIC_TEXT, document_id="gen-001")
        assert meta.settore == ["penale"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_testo_vuoto(self, extractor):
        meta = extractor.extract("", document_id="vuoto")
        assert meta.document_id == "vuoto"
        assert meta.rivista is None
        assert meta.titolo_doc is None
        assert meta.anno_pubblicazione is None

    def test_solo_anno(self, extractor):
        meta = extractor.extract("Testo pubblicato nel 2020.", document_id="solo-anno")
        assert meta.anno_pubblicazione == 2020

    def test_nessun_anno(self, extractor):
        meta = extractor.extract("Contributo senza data.", document_id="no-anno")
        assert meta.anno_pubblicazione is None

    def test_document_id_propagato(self, extractor):
        meta = extractor.extract("Testo qualsiasi.", document_id="doc-xyz")
        assert meta.document_id == "doc-xyz"

    def test_as_set_dict_esclude_none(self, extractor):
        meta = DottrinaMetadata(document_id="test")
        d = meta.as_set_dict()
        assert "settore" in d
        assert "rivista" not in d
        assert "titolo_doc" not in d
        assert "anno_pubblicazione" not in d

    def test_as_set_dict_include_campi_valorizzati(self, extractor):
        meta = DottrinaMetadata(
            document_id="test",
            rivista="diritto_penale_contemporaneo",
            anno_pubblicazione=2020,
            fascicolo="3/2020",
            autore="Viganò Francesco",
        )
        d = meta.as_set_dict()
        assert d["rivista"] == "diritto_penale_contemporaneo"
        assert d["anno_pubblicazione"] == 2020
        assert d["fascicolo"] == "3/2020"
        assert d["autore"] == "Viganò Francesco"
        assert d["settore"] == ["penale"]
