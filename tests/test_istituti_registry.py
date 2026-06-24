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
    def test_seed_si_carica(self):
        reg = get_registry()
        assert len(reg.all()) >= 3

    def test_urn_penale_mappa_istituto_penale(self):
        """art. 321 c.p.p. → sequestro penale (NON antimafia)."""
        reg = get_registry()
        ist = reg.by_urn(
            "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art321"
        )
        assert ist is not None
        assert ist.id == "sequestro_preventivo_confisca_equivalente_penale"

    def test_urn_antimafia_mappa_istituto_distinto(self):
        """art. 25 d.lgs. 159/2011 → confisca antimafia, ISTITUTO DIVERSO dal penale.
        È la disambiguazione che oggi manca e fa confondere il retrieval."""
        reg = get_registry()
        ist = reg.by_urn("urn:nir:stato:decreto.legislativo:2011-09-06;159~art25")
        assert ist is not None
        assert ist.id == "confisca_antimafia_equivalente"
        # I due istituti del per-equivalente devono essere distinti
        penale = reg.by_urn(
            "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art321"
        )
        assert ist.id != penale.id

    def test_urn_sconosciuto_ritorna_none(self):
        reg = get_registry()
        assert reg.by_urn("urn:nir:stato:legge:9999-01-01;1~art1") is None

    def test_pilota_thyssenkrupp_presente(self):
        reg = get_registry()
        piloti = reg.piloti("dolo_eventuale_colpa_cosciente")
        assert any(p.nome == "ThyssenKrupp" and p.numero == "38343" for p in piloti)

    def test_pilota_gubert_presente_con_principio(self):
        reg = get_registry()
        piloti = reg.piloti("sequestro_preventivo_confisca_equivalente_penale")
        gubert = next((p for p in piloti if p.nome == "Gubert"), None)
        assert gubert is not None
        assert gubert.numero == "10561" and gubert.anno == "2014"
        assert "terzo" in gubert.principio.lower()

    def test_vocabolario_chiuso(self):
        reg = get_registry()
        vocab = reg.vocabolario()
        ids = {v[0] for v in vocab}
        assert "sequestro_preventivo_confisca_equivalente_penale" in ids
        assert all(isinstance(v[1], str) and v[1] for v in vocab)  # label non vuote


# ---------------------------------------------------------------------------
# match_query (classificazione lessicale di fallback)
# ---------------------------------------------------------------------------

class TestMatchQuery:
    def test_match_sequestro_equivalente(self):
        reg = get_registry()
        res = reg.match_query("sequestro preventivo per equivalente nei confronti del terzo estraneo")
        assert res, "deve matchare almeno un istituto"
        assert res[0][0].id == "sequestro_preventivo_confisca_equivalente_penale"

    def test_match_dolo_eventuale(self):
        reg = get_registry()
        res = reg.match_query("confine tra dolo eventuale e colpa cosciente")
        assert res[0][0].id == "dolo_eventuale_colpa_cosciente"

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
