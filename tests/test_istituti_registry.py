"""
Test del registro degli istituti giuridici (core/istituti).

Verifica il seed reale (registry.yaml) + il parsing/lookup su YAML sintetico.
Zero dipendenze da MongoDB: il registro vive su file.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from aiura_legal.core.istituti.registry import (
    Istituto,
    SentenzaPilota,
    IstitutoRegistry,
    load_registry,
    get_registry,
)


# ---------------------------------------------------------------------------
# Seed reale
# ---------------------------------------------------------------------------

class TestSeedReale:
    """
    Il seed reale oggi contiene SOLO le voci generate da
    scripts/sync_istituti_registry.py (istituti_giuridici via CRUD UI) — le
    voci curate a mano (con sentenze_pilota verificate come Gubert/
    ThyssenKrupp e disambigua_da) sono state rimosse su richiesta esplicita.
    Questi test verificano solo invarianti strutturali generiche, non più
    contenuti specifici che non esistono più nel file.
    """
    def test_seed_si_carica(self):
        reg = get_registry()
        assert len(reg.all()) >= 3

    def test_urn_sconosciuto_ritorna_none(self):
        reg = get_registry()
        assert reg.by_urn("urn:nir:stato:legge:9999-01-01;1~art1") is None

    def test_vocabolario_non_vuoto(self):
        reg = get_registry()
        vocab = reg.vocabolario()
        assert vocab
        assert all(isinstance(v[1], str) and v[1] for v in vocab)  # label non vuote


# ---------------------------------------------------------------------------
# match_query (classificazione lessicale di fallback)
# ---------------------------------------------------------------------------

class TestMatchQuery:
    def test_match_testimonianza(self):
        reg = get_registry()
        res = reg.match_query(
            "testimonianza facolta di astensione dei prossimi congiunti segreto professionale"
        )
        assert res, "deve matchare almeno un istituto"
        assert res[0][0].id == "testimonianza_cpp"

    def test_no_match_ritorna_vuoto(self):
        reg = get_registry()
        assert reg.match_query("ricetta della carbonara") == []


# ---------------------------------------------------------------------------
# Parsing su YAML sintetico
# ---------------------------------------------------------------------------

_SYNTH = """
istituti:
  - id: test_istituto
    label: "Istituto di test"
    settore: civile
    norme_urn: ["urn:test~art1", "urn:test~art2"]
    norme_riferimento: ["art. 1 test"]
    termini_chiave: ["alfa", "beta"]
    disambigua_da:
      altro: ["gamma"]
    sentenze_pilota:
      - {organo: "Cass. SS.UU.", numero: "100", anno: "2020", nome: "Tizio", principio: "x"}
"""


class TestParsing:
    @pytest.fixture
    def reg(self, tmp_path: Path) -> IstitutoRegistry:
        p = tmp_path / "synth.yaml"
        p.write_text(_SYNTH, encoding="utf-8")
        return load_registry(p)

    def test_campi_base(self, reg):
        ist = reg.by_id("test_istituto")
        assert ist is not None
        assert ist.settore == "civile"
        assert ist.norme_urn == ("urn:test~art1", "urn:test~art2")
        assert ist.termini_chiave == ("alfa", "beta")
        assert ist.disambigua_da == {"altro": ("gamma",)}

    def test_pilota_parsato(self, reg):
        p = reg.piloti("test_istituto")[0]
        assert isinstance(p, SentenzaPilota)
        assert p.numero == "100" and p.nome == "Tizio"
        assert p.riferimento == "Cass. SS.UU. n. 100/2020 (Tizio)"

    def test_entrambi_gli_urn_indicizzati(self, reg):
        assert reg.by_urn("urn:test~art1").id == "test_istituto"
        assert reg.by_urn("urn:test~art2").id == "test_istituto"

    def test_seed_mancante_registro_vuoto(self, tmp_path):
        reg = load_registry(tmp_path / "inesistente.yaml")
        assert reg.all() == []
