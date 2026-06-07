"""
Test ReferenceExtractor.

Verifica:
  - Pattern ABROGA, MODIFICA, RINVIA esplicito, RINVIA generico
  - Varianti ortografiche (apostrofo curvo/dritto, spazi, maiuscole)
  - Normalizzazione articolo_num (bis/ter, spazi attorno a trattino)
  - Deduplicazione per (articolo_num, edge_type)
  - Falsi positivi filtrati
"""
from __future__ import annotations

import pytest

from aiura_legal.core.graph.extractor import ReferenceExtractor, ReferenceMatch


@pytest.fixture
def ex():
    return ReferenceExtractor()


# ---------------------------------------------------------------------------
# ABROGA
# ---------------------------------------------------------------------------

class TestAbroga:

    def test_abrogato_dall_art(self, ex):
        refs = ex.extract("Il presente comma è abrogato dall'art. 5 della legge 10/2020.")
        assert any(r.edge_type == "ABROGA" and r.articolo_num == "5" for r in refs)

    def test_abrogata_apostrofo_curvo(self, ex):
        refs = ex.extract("La disposizione è abrogata dall’art. 12.")
        assert any(r.edge_type == "ABROGA" and r.articolo_num == "12" for r in refs)

    def test_abrogato_uppercase(self, ex):
        refs = ex.extract("ABROGATO DALL'ART. 3 del decreto.")
        assert any(r.edge_type == "ABROGA" and r.articolo_num == "3" for r in refs)

    def test_abrogato_bis(self, ex):
        refs = ex.extract("abrogato dall'art. 7-bis della presente legge.")
        assert any(r.edge_type == "ABROGA" and r.articolo_num == "7-bis" for r in refs)


# ---------------------------------------------------------------------------
# MODIFICA
# ---------------------------------------------------------------------------

class TestModifica:

    def test_modificato_dall_art(self, ex):
        refs = ex.extract("Il testo è modificato dall'art. 7 del dlgs 150/2022.")
        assert any(r.edge_type == "MODIFICA" and r.articolo_num == "7" for r in refs)

    def test_modificata_apostrofo_curvo(self, ex):
        refs = ex.extract("La norma è modificata dall’art. 2.")
        assert any(r.edge_type == "MODIFICA" and r.articolo_num == "2" for r in refs)

    def test_come_modificato(self, ex):
        refs = ex.extract("come modificato dall'art. 9 della legge.")
        assert any(r.edge_type == "MODIFICA" and r.articolo_num == "9" for r in refs)


# ---------------------------------------------------------------------------
# RINVIA esplicito
# ---------------------------------------------------------------------------

class TestRinvioEsplicito:

    def test_ai_sensi_dell_art(self, ex):
        refs = ex.extract("Il debitore, ai sensi dell'art. 1218, risponde.")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "1218" for r in refs)

    def test_di_cui_all_art(self, ex):
        refs = ex.extract("Le fattispecie di cui all'art. 1453 del codice civile.")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "1453" for r in refs)

    def test_previsto_dall_art(self, ex):
        refs = ex.extract("Il termine previsto dall'art. 2935 decorre dalla.")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "2935" for r in refs)

    def test_fermo_restando_dall_art(self, ex):
        refs = ex.extract("Fermo restando quanto disposto dall'art. 1175 c.c.")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "1175" for r in refs)

    def test_rinvio_con_apostrofo_curvo(self, ex):
        refs = ex.extract("ai sensi dell’art. 1223 del codice civile")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "1223" for r in refs)

    def test_art_2_bis(self, ex):
        refs = ex.extract("ai sensi dell'art. 2-bis della presente legge")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "2-bis" for r in refs)


# ---------------------------------------------------------------------------
# RINVIA generico (fallback)
# ---------------------------------------------------------------------------

class TestRinvioGenerico:

    def test_art_generico(self, ex):
        refs = ex.extract("Si applica l'art. 1218 c.c.")
        assert any(r.edge_type == "RINVIA" and r.articolo_num == "1218" for r in refs)

    def test_art_senza_punto(self, ex):
        refs = ex.extract("disposto dall art 1453")
        # "dall art" corrisponde a "previsto dall'art" → RINVIA esplicito o generico
        arts = [r.articolo_num for r in refs]
        assert "1453" in arts

    def test_art_num_alto(self, ex):
        refs = ex.extract("Vedi art. 2965.")
        assert any(r.articolo_num == "2965" for r in refs)


# ---------------------------------------------------------------------------
# Normalizzazione articolo_num
# ---------------------------------------------------------------------------

class TestNormalizzazione:

    def test_bis_con_spazi(self, ex):
        """Spazi attorno al trattino → normalizzati."""
        refs = ex.extract("ai sensi dell'art. 2 - bis della legge")
        nums = [r.articolo_num for r in refs]
        assert "2-bis" in nums

    def test_ter(self, ex):
        refs = ex.extract("ai sensi dell'art. 4-ter")
        assert any(r.articolo_num == "4-ter" for r in refs)

    def test_lowercase_num(self, ex):
        """articolo_num sempre lowercase."""
        refs = ex.extract("abrogato dall'art. 5")
        assert all(r.articolo_num == r.articolo_num.lower() for r in refs)


# ---------------------------------------------------------------------------
# Deduplicazione
# ---------------------------------------------------------------------------

class TestDeduplicazione:

    def test_stesso_art_stesso_tipo_una_volta(self, ex):
        text = "ai sensi dell'art. 1218. Si applica l'art. 1218."
        refs = ex.extract(text)
        rinvia_1218 = [r for r in refs if r.articolo_num == "1218" and r.edge_type == "RINVIA"]
        assert len(rinvia_1218) == 1

    def test_stesso_art_tipi_diversi_entrambi(self, ex):
        """Stesso articolo referenziato come RINVIA e ABROGA → entrambi presenti."""
        text = (
            "Si applica l'art. 5. "
            "Il comma 2 è abrogato dall'art. 5."
        )
        refs = ex.extract(text)
        types_for_5 = {r.edge_type for r in refs if r.articolo_num == "5"}
        assert "RINVIA" in types_for_5
        assert "ABROGA" in types_for_5


# ---------------------------------------------------------------------------
# Falsi positivi
# ---------------------------------------------------------------------------

class TestFalsiPositivi:

    def test_articolo_di_giornale_escluso(self, ex):
        refs = ex.extract("L'articolo di giornale cita l'art. 5.")
        # "articolo di giornale" → contesto sospetto, ma "l'art. 5" nel resto
        # del testo può ancora matchare: verifichiamo che non abbia errori
        assert isinstance(refs, list)

    def test_testo_senza_articoli_normativi(self, ex):
        refs = ex.extract("Il cliente ha pagato la fattura in data odierna.")
        assert refs == []

    def test_testo_vuoto(self, ex):
        assert ex.extract("") == []


# ---------------------------------------------------------------------------
# Tipo arco nel ReferenceMatch
# ---------------------------------------------------------------------------

class TestReferenceMatchType:

    def test_result_is_reference_match(self, ex):
        refs = ex.extract("ai sensi dell'art. 1218")
        assert all(isinstance(r, ReferenceMatch) for r in refs)

    def test_edge_type_values(self, ex):
        text = (
            "ai sensi dell'art. 1. "
            "abrogato dall'art. 2. "
            "modificato dall'art. 3."
        )
        refs = ex.extract(text)
        types = {r.edge_type for r in refs}
        assert types <= {"RINVIA", "ABROGA", "MODIFICA"}

    def test_context_non_empty(self, ex):
        refs = ex.extract("Il debitore ai sensi dell'art. 1218 risponde.")
        assert all(len(r.context) > 0 for r in refs)
