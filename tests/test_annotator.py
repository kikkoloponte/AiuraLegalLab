"""
test_annotator.py — test per AnnotatorAgent (S6) e endpoint /annotate.

Copertura:
  TestSplitSections        (6) — splitting, paragrafi, max_sections, sezioni brevi
  TestBuildPrompt          (4) — contiene section_id, fonti, istruzione, cite-constraint
  TestExtractJson          (4) — json grezzo, code fence, fallback None, malformato
  TestParseSectionResponse (5) — annotazioni valide, tipo non valido, campo vuoto, livello
  TestComputeOverallRisk   (5) — ALTO, MEDIO, BASSO, NESSUNO, precedenza
  TestComputeSummary       (3) — conteggio per tipo
  TestAnnotateMethod       (8) — happy path, Ollama error, testo vuoto, max_sections,
                                 zero annotazioni, cittazioni risolte, parse_errors parziali
  TestAnnotateEndpoints    (5) — POST 202, GET result, 404 doc mancante, 422 testo vuoto
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from aiura_legal.agents.annotator import (
    ANNOTATION_TYPES,
    Annotation,
    AnnotationResult,
    AnnotatorAgent,
)
from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_packet(sources: list[SearchResult] | None = None) -> ResearchPacket:
    if sources is None:
        sources = [
            SearchResult(
                doc_id="d1", score=0.9,
                snippet="Il debitore inadempiente è tenuto al risarcimento.",
                source_id="CC_ART_1218", retrieval_method="bm25",
                metadata={"titolo": "Codice Civile", "articolo_num": "art. 1218"},
            ),
        ]
    return ResearchPacket(
        query_original="Analisi documento",
        query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
        sources=sources,
    )


def _mock_ollama(response: str = '{"annotations": []}') -> MagicMock:
    mock = MagicMock()
    mock.model = "qwen2.5:7b"
    mock.generate = AsyncMock(return_value=response)
    return mock


_SAMPLE_TEXT = """
Articolo 1 — Oggetto del contratto

Le parti concordano la fornitura di servizi di consulenza legale
per un periodo di dodici mesi dalla data di stipula.

Articolo 2 — Corrispettivo

Il compenso pattuito ammonta a euro 5.000 mensili, pagabili entro
trenta giorni dalla ricezione della fattura.

Articolo 3 — Risoluzione

Il contratto potrà essere risolto con preavviso di trenta giorni.
In caso di inadempimento si applicheranno le disposizioni di legge.
""".strip()


# ---------------------------------------------------------------------------
# TestSplitSections
# ---------------------------------------------------------------------------

class TestSplitSections:
    def test_basic_split_produces_sections(self):
        sections = AnnotatorAgent.split_sections(_SAMPLE_TEXT)
        assert len(sections) >= 1
        for sid, txt in sections:
            assert sid.startswith("§")
            assert len(txt) > 0

    def test_max_sections_respected(self):
        long_text = "\n\n".join([f"Paragrafo {i} con testo sufficientemente lungo per essere incluso." for i in range(20)])
        sections = AnnotatorAgent.split_sections(long_text, max_sections=5)
        assert len(sections) <= 5

    def test_short_sections_filtered(self):
        text = "OK\n\nTesto sufficiente per essere incluso come sezione.\n\nAB"
        sections = AnnotatorAgent.split_sections(text)
        # "OK" e "AB" (< 50 chars) non devono comparire come sezioni autonome
        for _, txt in sections:
            assert len(txt) >= 50 or len(txt) > 2  # almeno parte di un gruppo

    def test_single_paragraph_becomes_one_section(self):
        text = "Un solo paragrafo abbastanza lungo da superare il minimo."
        sections = AnnotatorAgent.split_sections(text)
        assert len(sections) == 1
        assert sections[0][0] == "§1"

    def test_section_ids_sequential(self):
        sections = AnnotatorAgent.split_sections(_SAMPLE_TEXT, max_sections=10)
        for i, (sid, _) in enumerate(sections, 1):
            assert sid == f"§{i}"

    def test_empty_text_returns_empty(self):
        sections = AnnotatorAgent.split_sections("")
        assert sections == []


# ---------------------------------------------------------------------------
# TestBuildPrompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def setup_method(self):
        self.agent = AnnotatorAgent(ollama=_mock_ollama())
        self.packet = _make_packet()

    def test_prompt_contains_section_id(self):
        prompt = self.agent._build_prompt("§2", "Testo sezione.", self.packet)
        assert "§2" in prompt

    def test_prompt_contains_source_id(self):
        prompt = self.agent._build_prompt("§1", "Testo.", self.packet)
        assert "CC_ART_1218" in prompt

    def test_prompt_contains_cite_constraint(self):
        prompt = self.agent._build_prompt("§1", "Testo.", self.packet)
        assert "LACUNA_NORMATIVA" in prompt

    def test_prompt_contains_json_instruction(self):
        prompt = self.agent._build_prompt("§1", "Testo.", self.packet)
        assert "JSON" in prompt


# ---------------------------------------------------------------------------
# TestExtractJson
# ---------------------------------------------------------------------------

class TestExtractJson:
    def setup_method(self):
        self.agent = AnnotatorAgent(ollama=_mock_ollama())

    def test_extracts_bare_json(self):
        raw = '{"annotations": []}'
        result = self.agent._extract_json(raw)
        assert result == {"annotations": []}

    def test_extracts_json_from_code_fence(self):
        raw = '```json\n{"annotations": [{"section": "§1", "type": "RISCHIO_RILEVATO"}]}\n```'
        result = self.agent._extract_json(raw)
        assert result is not None
        assert "annotations" in result

    def test_returns_none_for_invalid(self):
        result = self.agent._extract_json("Nessun JSON qui.")
        assert result is None

    def test_returns_none_for_empty(self):
        result = self.agent._extract_json("")
        assert result is None


# ---------------------------------------------------------------------------
# TestParseSectionResponse
# ---------------------------------------------------------------------------

class TestParseSectionResponse:
    def setup_method(self):
        self.agent = AnnotatorAgent(ollama=_mock_ollama())

    def test_parses_valid_annotation(self):
        raw = '''{"annotations": [
            {"section": "§1", "type": "RISCHIO_RILEVATO", "level": "ALTO",
             "text": "Termine vago.", "source_citations": ["CC_ART_1218"],
             "suggested_replacement": "Sostituire con termine preciso."}
        ]}'''
        anns = self.agent._parse_section_response(raw, "§1")
        assert len(anns) == 1
        assert anns[0].annotation_type == "RISCHIO_RILEVATO"
        assert anns[0].level == "ALTO"
        assert anns[0].source_citations == ["CC_ART_1218"]

    def test_filters_invalid_type(self):
        raw = '{"annotations": [{"section": "§1", "type": "TIPO_INVENTATO", "text": "X"}]}'
        anns = self.agent._parse_section_response(raw, "§1")
        assert anns == []

    def test_filters_empty_text(self):
        raw = '{"annotations": [{"section": "§1", "type": "SUGGERIMENTO", "text": ""}]}'
        anns = self.agent._parse_section_response(raw, "§1")
        assert anns == []

    def test_invalid_json_returns_empty(self):
        anns = self.agent._parse_section_response("Testo non JSON.", "§1")
        assert anns == []

    def test_invalid_level_normalized_to_empty(self):
        raw = '{"annotations": [{"section": "§1", "type": "RISCHIO_RILEVATO", "level": "CRITICO", "text": "X"}]}'
        anns = self.agent._parse_section_response(raw, "§1")
        assert len(anns) == 1
        assert anns[0].level == ""  # livello non valido → stringa vuota


# ---------------------------------------------------------------------------
# TestComputeOverallRisk
# ---------------------------------------------------------------------------

class TestComputeOverallRisk:
    def _ann(self, ann_type: str, level: str = "") -> Annotation:
        return Annotation(section="§1", annotation_type=ann_type,
                          text="x", level=level)

    def test_alto_when_rischio_alto(self):
        anns = [self._ann("RISCHIO_RILEVATO", "ALTO")]
        assert AnnotatorAgent.compute_overall_risk(anns) == "ALTO"

    def test_medio_when_only_medio(self):
        anns = [self._ann("RISCHIO_RILEVATO", "MEDIO")]
        assert AnnotatorAgent.compute_overall_risk(anns) == "MEDIO"

    def test_basso_when_only_basso(self):
        anns = [self._ann("RISCHIO_RILEVATO", "BASSO")]
        assert AnnotatorAgent.compute_overall_risk(anns) == "BASSO"

    def test_nessuno_when_no_rischi(self):
        anns = [self._ann("SUGGERIMENTO"), self._ann("COMMENTO_NORMATIVO")]
        assert AnnotatorAgent.compute_overall_risk(anns) == "NESSUNO"

    def test_alto_takes_precedence_over_medio(self):
        anns = [
            self._ann("RISCHIO_RILEVATO", "MEDIO"),
            self._ann("RISCHIO_RILEVATO", "ALTO"),
        ]
        assert AnnotatorAgent.compute_overall_risk(anns) == "ALTO"


# ---------------------------------------------------------------------------
# TestComputeSummary
# ---------------------------------------------------------------------------

class TestComputeSummary:
    def _ann(self, ann_type: str) -> Annotation:
        return Annotation(section="§1", annotation_type=ann_type, text="x")

    def test_counts_each_type(self):
        anns = [
            self._ann("RISCHIO_RILEVATO"),
            self._ann("RISCHIO_RILEVATO"),
            self._ann("SUGGERIMENTO"),
        ]
        summary = AnnotatorAgent.compute_summary(anns)
        assert summary["RISCHIO_RILEVATO"] == 2
        assert summary["SUGGERIMENTO"] == 1

    def test_empty_annotations_returns_empty_summary(self):
        assert AnnotatorAgent.compute_summary([]) == {}

    def test_summary_only_contains_present_types(self):
        anns = [self._ann("LACUNA_NORMATIVA")]
        summary = AnnotatorAgent.compute_summary(anns)
        assert set(summary.keys()) == {"LACUNA_NORMATIVA"}


# ---------------------------------------------------------------------------
# TestAnnotateMethod
# ---------------------------------------------------------------------------

class TestAnnotateMethod:
    @pytest.mark.asyncio
    async def test_happy_path_returns_annotation_result(self):
        raw = '''{"annotations": [
            {"section": "§1", "type": "RISCHIO_RILEVATO", "level": "MEDIO",
             "text": "Clausola rischiosa.", "source_citations": ["CC_ART_1218"]}
        ]}'''
        agent = AnnotatorAgent(ollama=_mock_ollama(raw))
        packet = _make_packet()

        result = await agent.annotate(_SAMPLE_TEXT, "doc123", packet)

        assert isinstance(result, AnnotationResult)
        assert result.document_id == "doc123"
        assert len(result.annotations) >= 1
        assert result.parse_ok is True

    @pytest.mark.asyncio
    async def test_empty_text_returns_empty_result(self):
        agent = AnnotatorAgent(ollama=_mock_ollama())
        packet = _make_packet()

        result = await agent.annotate("", "doc_empty", packet)

        assert result.parse_ok is False
        assert result.annotations == []
        assert result.sections_processed == 0

    @pytest.mark.asyncio
    async def test_ollama_error_graceful(self):
        mock_ol = MagicMock()
        mock_ol.model = "qwen2.5:7b"
        mock_ol.generate = AsyncMock(side_effect=ConnectionError("no ollama"))
        agent = AnnotatorAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.annotate(_SAMPLE_TEXT, "doc_err", packet)

        # parse_ok=False perché tutte le sezioni hanno fallito
        assert result.parse_ok is False
        assert result.annotations == []

    @pytest.mark.asyncio
    async def test_max_sections_limits_calls(self):
        """Verifica che venga chiamato Ollama al massimo max_sections volte."""
        mock_ol = _mock_ollama('{"annotations": []}')
        agent = AnnotatorAgent(ollama=mock_ol)
        packet = _make_packet()
        # Testo lungo con molti paragrafi
        long_text = "\n\n".join([f"Paragrafo {i} sufficientemente lungo da formare una sezione del documento." for i in range(20)])

        result = await agent.annotate(long_text, "doc_long", packet, max_sections=3)

        assert result.sections_processed <= 3
        assert mock_ol.generate.call_count <= 3

    @pytest.mark.asyncio
    async def test_zero_annotations_is_valid(self):
        agent = AnnotatorAgent(ollama=_mock_ollama('{"annotations": []}'))
        packet = _make_packet()

        result = await agent.annotate(_SAMPLE_TEXT, "doc_clean", packet)

        assert result.annotations == []
        assert result.overall_risk == "NESSUNO"
        assert result.parse_ok is True

    @pytest.mark.asyncio
    async def test_overall_risk_computed_correctly(self):
        raw = '''{"annotations": [
            {"section": "§1", "type": "RISCHIO_RILEVATO", "level": "ALTO",
             "text": "Grave lacuna.", "source_citations": []}
        ]}'''
        agent = AnnotatorAgent(ollama=_mock_ollama(raw))
        packet = _make_packet()

        result = await agent.annotate(_SAMPLE_TEXT, "doc_risk", packet)

        assert result.overall_risk == "ALTO"

    @pytest.mark.asyncio
    async def test_summary_populated(self):
        raw = '''{"annotations": [
            {"section": "§1", "type": "SUGGERIMENTO", "text": "Migliorare."},
            {"section": "§1", "type": "SUGGERIMENTO", "text": "Altro suggerimento."}
        ]}'''
        agent = AnnotatorAgent(ollama=_mock_ollama(raw))
        packet = _make_packet()

        result = await agent.annotate(_SAMPLE_TEXT, "doc_summary", packet)

        assert result.summary.get("SUGGERIMENTO", 0) >= 1

    @pytest.mark.asyncio
    async def test_partial_ollama_errors_ok_if_some_sections_succeed(self):
        """Se almeno una sezione risponde correttamente, parse_ok=True."""
        call_count = 0

        async def flaky_generate(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("timeout")
            return '{"annotations": []}'

        mock_ol = MagicMock()
        mock_ol.model = "qwen2.5:7b"
        mock_ol.generate = flaky_generate
        agent = AnnotatorAgent(ollama=mock_ol)
        packet = _make_packet()

        # Testo con 2 paragrafi ciascuno > _SECTION_MAX_CHARS → 2 sezioni distinte
        word = "contratto "
        para1 = "Prima sezione contrattuale. " + word * 120   # ~1200+ chars
        para2 = "Seconda sezione normativa. " + word * 120
        two_section_text = para1 + "\n\n" + para2

        result = await agent.annotate(two_section_text, "doc_partial", packet, max_sections=5)

        # §1 ha fallito, §2 ha risposto → parse_ok=True (1 errore su 2 sezioni)
        assert result.sections_processed == 2
        assert result.parse_ok is True


# ---------------------------------------------------------------------------
# TestAnnotateEndpoints
# ---------------------------------------------------------------------------

class TestAnnotateEndpoints:
    """Test degli endpoint /annotate via httpx AsyncClient (mongomock-motor)."""

    @pytest.fixture
    def mock_mongo_db(self):
        """Motor database mock per i test API annotate."""
        import mongomock_motor
        client = mongomock_motor.AsyncMongoMockClient()
        return client["aiura_legal"]

    @pytest.mark.asyncio
    async def test_post_annotate_returns_202(self, mock_mongo_db):
        """POST /annotate/{doc_id} → 202 con status=queued."""
        from aiura_legal.api.app import app
        from aiura_legal.ingestion.mongodb.client import MongoClient

        # Inserisce un documento di test nel mock DB
        doc_id = "test_doc_annotate"
        await mock_mongo_db["documents"].insert_one({
            "_id": doc_id,
            "workspace": "default",
            "text": _SAMPLE_TEXT,
        })

        with patch.object(MongoClient, "get") as mock_get:
            mock_instance = MagicMock()
            mock_instance.db = mock_mongo_db
            mock_get.return_value = mock_instance

            # Mock anche l'orchestratore per evitare accesso a indici su disco
            with patch("aiura_legal.api.app._get_orchestrator") as mock_orch:
                mock_retriever = MagicMock()
                mock_retriever.build_research_packet = MagicMock(
                    return_value=_make_packet()
                )
                mock_orch_instance = MagicMock()
                mock_orch_instance._retriever = mock_retriever
                mock_orch.return_value = mock_orch_instance

                # Mock annotator per non chiamare Ollama
                with patch("aiura_legal.api.app._annotator") as mock_ann:
                    mock_ann.annotate = AsyncMock(return_value=AnnotationResult(
                        document_id=doc_id, annotations=[], summary={},
                        overall_risk="NESSUNO", sections_processed=1,
                        llm_model="qwen2.5:7b", duration_s=0.1, parse_ok=True,
                    ))

                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test",
                    ) as client:
                        resp = await client.post(
                            f"/annotate/{doc_id}",
                            json={"workspace": "default"},
                        )

        assert resp.status_code == 202
        body = resp.json()
        assert body["document_id"] == doc_id
        assert body["status"] == "queued"

    @pytest.mark.asyncio
    async def test_post_annotate_404_document_not_found(self, mock_mongo_db):
        """POST /annotate/{doc_id} → 404 se documento non in MongoDB."""
        from aiura_legal.api.app import app
        from aiura_legal.ingestion.mongodb.client import MongoClient

        with patch.object(MongoClient, "get") as mock_get:
            mock_instance = MagicMock()
            mock_instance.db = mock_mongo_db   # collection vuota
            mock_get.return_value = mock_instance

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.post(
                    "/annotate/nonexistent_doc",
                    json={"workspace": "default"},
                )

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_post_annotate_422_empty_text(self, mock_mongo_db):
        """POST /annotate/{doc_id} → 422 se documento ha testo vuoto."""
        from aiura_legal.api.app import app
        from aiura_legal.ingestion.mongodb.client import MongoClient

        await mock_mongo_db["documents"].insert_one({
            "_id": "empty_doc",
            "workspace": "default",
            "text": "   ",
        })

        with patch.object(MongoClient, "get") as mock_get:
            mock_instance = MagicMock()
            mock_instance.db = mock_mongo_db
            mock_get.return_value = mock_instance

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.post(
                    "/annotate/empty_doc",
                    json={"workspace": "default"},
                )

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_annotation_result_completed(self, mock_mongo_db):
        """GET /annotate/{doc_id} → risultato completato."""
        from aiura_legal.api.app import app
        from aiura_legal.ingestion.mongodb.client import MongoClient

        doc_id = "completed_doc"
        await mock_mongo_db["annotations"].insert_one({
            "document_id": doc_id,
            "workspace": "default",
            "status": "completed",
            "annotations": [{
                "section": "§1",
                "annotation_type": "SUGGERIMENTO",
                "text": "Migliorare clausola.",
                "level": "",
                "source_citations": [],
                "suggested_replacement": "",
            }],
            "summary": {"SUGGERIMENTO": 1},
            "overall_risk": "NESSUNO",
            "sections_processed": 2,
            "llm_model": "qwen2.5:7b",
            "duration_s": 1.5,
            "parse_ok": True,
        })

        with patch.object(MongoClient, "get") as mock_get:
            mock_instance = MagicMock()
            mock_instance.db = mock_mongo_db
            mock_get.return_value = mock_instance

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.get(f"/annotate/{doc_id}")

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "completed"
        assert body["overall_risk"] == "NESSUNO"
        assert len(body["annotations"]) == 1
        assert body["annotations"][0]["annotation_type"] == "SUGGERIMENTO"

    @pytest.mark.asyncio
    async def test_get_annotation_result_404(self, mock_mongo_db):
        """GET /annotate/{doc_id} → 404 se non esiste record annotazione."""
        from aiura_legal.api.app import app
        from aiura_legal.ingestion.mongodb.client import MongoClient

        with patch.object(MongoClient, "get") as mock_get:
            mock_instance = MagicMock()
            mock_instance.db = mock_mongo_db
            mock_get.return_value = mock_instance

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.get("/annotate/niente")

        assert resp.status_code == 404
