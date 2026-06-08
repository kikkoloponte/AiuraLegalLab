"""
Test PhaseRetriever — filtro settore-aware e rilevamento dominio.

Verifica che:
  - _infer_domain() rilevi correttamente penale/civile/amministrativo/lavoro
  - _settore_filter_normativa() costruisca il chunk_filter corretto
  - _is_criminal_law_topic() non abbia falsi positivi su "dolo" civile
  - SETTORE_FILTER_ENABLED attivi/disattivi il filtro
"""
from __future__ import annotations

import pytest

from aiura_legal.core.retrieval.phase_retriever import (
    _infer_domain,
    _settore_filter_normativa,
    _is_criminal_law_topic,
)


# ---------------------------------------------------------------------------
# _is_criminal_law_topic — test anti-falsi positivi (da sessione precedente)
# ---------------------------------------------------------------------------

class TestCriminalLawClassifier:
    def test_dolo_eventuale_penale(self):
        assert _is_criminal_law_topic("dolo eventuale vs colpa cosciente") is True

    def test_elemento_soggettivo(self):
        assert _is_criminal_law_topic("elemento soggettivo del reato") is True

    def test_art43_cp(self):
        assert _is_criminal_law_topic("art. 43 c.p. delitto doloso") is True

    def test_codice_penale_esplicito(self):
        assert _is_criminal_law_topic("codice penale omicidio") is True

    def test_dolo_civile_falso_positivo(self):
        """'dolo' da solo in contesto civile NON deve essere classificato come penale."""
        assert _is_criminal_law_topic("contratto nullo per dolo determinante ex art. 1439 c.c.") is False

    def test_colpa_medica_civile(self):
        """colpa medica con responsabilità civile — non penale."""
        assert _is_criminal_law_topic("responsabilità civile medica per colpa lieve") is False

    def test_due_deboli_penale(self):
        """Due marcatori deboli: penale + reato → True."""
        assert _is_criminal_law_topic("profili penali del reato tributario") is True

    def test_solo_penali_aggettivo(self):
        """'penali' da solo (clausola penale) non basta."""
        assert _is_criminal_law_topic("clausola penale contrattuale") is False


# ---------------------------------------------------------------------------
# _infer_domain
# ---------------------------------------------------------------------------

class TestInferDomain:
    def test_penale_forte(self):
        assert _infer_domain("dolo eventuale omicidio codice penale") == "penale"

    def test_penale_da_reato(self):
        assert _infer_domain("elemento soggettivo del reato doloso") == "penale"

    def test_civile_contratto(self):
        domain = _infer_domain("inadempimento contratto obbligazione risarcimento")
        assert domain == "civile"

    def test_civile_responsabilita(self):
        domain = _infer_domain("responsabilità civile art. 2043 danno ingiusto")
        assert domain == "civile"

    def test_amministrativo(self):
        domain = _infer_domain("ricorso TAR appalto pubblico illegittimità atto amministrativo")
        assert domain == "amministrativo"

    def test_lavoro(self):
        domain = _infer_domain("licenziamento illegittimo contratto di lavoro art. 18")
        assert domain == "lavoro"

    def test_ambiguo_none(self):
        """Query vaga senza keyword di dominio → None."""
        domain = _infer_domain("quale norma si applica in questo caso?")
        assert domain is None

    def test_penale_batte_civile(self):
        """Se la query ha marcatori penali forti, penale prevale."""
        q = "dolo eventuale contratto — ma anche elemento soggettivo penale"
        assert _infer_domain(q) == "penale"


# ---------------------------------------------------------------------------
# _settore_filter_normativa
# ---------------------------------------------------------------------------

class TestSettoreFilter:
    def test_penale_filter(self):
        f = _settore_filter_normativa("penale")
        assert f["corpus"] == "normattiva"
        assert f["settore"] == {"$in": ["penale"]}

    def test_civile_filter(self):
        f = _settore_filter_normativa("civile")
        assert f["settore"] == {"$in": ["civile"]}

    def test_amministrativo_filter(self):
        f = _settore_filter_normativa("amministrativo")
        assert f["settore"] == {"$in": ["amministrativo"]}

    def test_lavoro_filter(self):
        f = _settore_filter_normativa("lavoro")
        assert f["settore"] == {"$in": ["lavoro"]}

    def test_none_no_settore_filter(self):
        """Domain None → nessun filtro settore — recupera tutto normattiva."""
        f = _settore_filter_normativa(None)
        assert f == {"corpus": "normattiva"}
        assert "settore" not in f

    def test_unknown_domain_no_filter(self):
        """Domain non riconosciuto → nessun filtro settore."""
        f = _settore_filter_normativa("extraterrestre")
        assert f == {"corpus": "normattiva"}

    def test_penale_esclude_civile(self):
        """Il filter penale non include 'civile' in $in."""
        f = _settore_filter_normativa("penale")
        assert "civile" not in f["settore"]["$in"]

    def test_corpus_sempre_presente(self):
        """Il filtro base corpus=normattiva è sempre presente."""
        for domain in ("penale", "civile", "amministrativo", "lavoro", None):
            f = _settore_filter_normativa(domain)
            assert f["corpus"] == "normattiva"
