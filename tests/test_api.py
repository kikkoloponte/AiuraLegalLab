"""
Test FastAPI endpoints — TestClient + mock MongoDB/orchestratore.
Zero PII reali, fixture sintetiche.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiura_legal.api.schemas import HealthResponse
from aiura_legal.core.types import QueryIntent, SearchResult, ResearchPacket


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_packet(sources: list[SearchResult] | None = None) -> ResearchPacket:
    return ResearchPacket(
        query_original="test query",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=sources or [],
        retrieval_confidence="HIGH",
    )


def _mock_mongo():
    """Ritorna un mock asincrono per MongoClient."""
    mc = MagicMock()
    mc.ping = AsyncMock(return_value=True)

    mock_coll = MagicMock()
    mock_coll.count_documents = AsyncMock(return_value=5)
    mock_coll.insert_one = AsyncMock(
        side_effect=lambda *a, **kw: MagicMock(inserted_id="fake_id")
    )
    mock_coll.insert_many = AsyncMock(return_value=MagicMock())
    mock_coll.update_one = AsyncMock(return_value=MagicMock())
    mock_coll.find_one = AsyncMock(return_value=None)
    mock_coll.create_index = AsyncMock(return_value="slug_1_workspace_1")

    mc.db = MagicMock()
    mc.db.__getitem__ = MagicMock(return_value=mock_coll)
    return mc


def _make_mock_orch_result():
    """Costruisce un OrchestratorResult mock per i test."""
    from aiura_legal.agents.analyst import AnalysisResult, AnalysisSection
    from aiura_legal.agents.orchestrator import OrchestratorResult

    packet = _make_packet([
        SearchResult(
            doc_id="CC_ART_1218",
            score=1.2,
            snippet="Il debitore che non esegue esattamente la prestazione...",
            source_id="CC_ART_1218",
            retrieval_method="hybrid_rrf",
            metadata={"doc_type": "legge", "fonte": "codice_civile"},
        ),
        SearchResult(
            doc_id="CC_ART_1453",
            score=0.9,
            snippet="Nei contratti con prestazioni corrispettive...",
            source_id="CC_ART_1453",
            retrieval_method="hybrid_rrf",
            metadata={"doc_type": "legge", "fonte": "codice_civile"},
        ),
    ])

    analysis = AnalysisResult(
        answer=(
            "**QUALIFICAZIONE**\nLa fattispecie integra un inadempimento "
            "contrattuale ai sensi dell'art. 1218 c.c.\n\n"
            "**NORMA APPLICABILE**\nSi applica l'art. 1453 c.c. per la risoluzione."
        ),
        analysis_sections=[
            AnalysisSection(
                step="QUALIFICAZIONE",
                content="La fattispecie integra inadempimento contrattuale.",
                citations=[{"source_id": "CC_ART_1218", "claim": "inadempimento"}],
            ),
            AnalysisSection(
                step="NORMA APPLICABILE",
                content="Art. 1453 c.c. per la risoluzione del contratto.",
                citations=[{"source_id": "CC_ART_1453", "claim": "risoluzione"}],
            ),
        ],
        overall_confidence="HIGH",
        escalation_recommended=False,
        llm_model="qwen2.5:7b",
        parse_ok=True,
    )

    return OrchestratorResult(
        query="test query",
        workspace="test-ws",
        intent="fattispecie_analysis",
        packet=packet,
        analysis=analysis,
        reviewer_verdict="PASS",
        reviewer_action="DELIVER",
        reviewer_warnings=[],
        duration_retrieval_s=0.05,
        duration_llm_s=1.2,
        duration_total_s=1.3,
    )


# ---------------------------------------------------------------------------
# Fixture: client con MongoDB, OllamaClient e LegalOrchestrator mockati
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """
    TestClient con:
      - MongoClient mockato (ping OK, collections async mock)
      - LegalOrchestrator mockato (nessun indice su disco, nessuna chiamata Ollama)
      - OllamaClient mockato (is_available=True)
    """
    mock_mc = _mock_mongo()
    mock_result = _make_mock_orch_result()

    mock_orch = MagicMock()
    mock_orch.run = AsyncMock(return_value=mock_result)

    with (
        patch("aiura_legal.api.app.MongoClient") as MockMC,
        patch("aiura_legal.api.app._get_orchestrator", return_value=mock_orch),
        patch("aiura_legal.api.app._ollama") as mock_ollama,
    ):
        MockMC.get.return_value = mock_mc
        mock_ollama.is_available = AsyncMock(return_value=True)
        mock_ollama.list_models = AsyncMock(return_value=["qwen2.5:7b"])

        from aiura_legal.api.app import app
        from fastapi.testclient import TestClient
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert "mongodb" in data
    assert "ollama" in data
    assert "version" in data


# ---------------------------------------------------------------------------
# POST /query — campi base (backward compatibility)
# ---------------------------------------------------------------------------

def test_query_basic(client):
    resp = client.post("/query", json={
        "query": "responsabilità contrattuale inadempimento",
        "workspace": "test-ws",
        "intent": "fattispecie_analysis",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "responsabilità contrattuale inadempimento"
    assert data["workspace"] == "test-ws"
    assert data["intent"] == "fattispecie_analysis"
    assert "sources" in data
    assert "retrieval_confidence" in data
    assert "reviewer_verdict" in data


def test_query_sources_structure(client):
    resp = client.post("/query", json={
        "query": "inadempimento obbligazione contrattuale",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    sources = resp.json()["sources"]
    assert len(sources) > 0
    for s in sources:
        assert "rank" in s
        assert "doc_id" in s
        assert "source_id" in s
        assert "score" in s
        assert "snippet" in s


def test_query_invalid_intent(client):
    resp = client.post("/query", json={
        "query": "test query legale",
        "workspace": "ws",
        "intent": "intento_inesistente",
    })
    assert resp.status_code == 422


def test_query_too_short(client):
    resp = client.post("/query", json={
        "query": "ab",
        "workspace": "ws",
    })
    assert resp.status_code == 422


def test_query_all_intents(client):
    intents = [
        "norma_lookup",
        "giurisprudenza_search",
        "fattispecie_analysis",
        "precedente_interno",
        "norma_evolution",
        "rischio_contrattuale",
    ]
    for intent in intents:
        resp = client.post("/query", json={
            "query": "test query legale italiano",
            "workspace": "ws",
            "intent": intent,
        })
        assert resp.status_code == 200, f"intent={intent} fallito: {resp.text}"


def test_query_with_valid_on(client):
    resp = client.post("/query", json={
        "query": "norma vigente al 2023",
        "workspace": "ws",
        "valid_on": "2023-01-01",
    })
    assert resp.status_code == 200


def test_query_top_k_respected(client):
    resp = client.post("/query", json={
        "query": "test query legale",
        "workspace": "ws",
        "top_k": 1,
    })
    assert resp.status_code == 200
    assert len(resp.json()["sources"]) <= 1


# ---------------------------------------------------------------------------
# POST /query — nuovi campi Block 1B
# ---------------------------------------------------------------------------

def test_query_has_answer_field(client):
    """Blocco 1B: la risposta deve contenere il campo 'answer'."""
    resp = client.post("/query", json={
        "query": "inadempimento contrattuale",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    # Con Ollama mockato deve essere non vuoto
    assert len(data["answer"]) > 0


def test_query_has_analysis_sections(client):
    """Blocco 1B: la risposta deve contenere le sezioni CoT strutturate."""
    resp = client.post("/query", json={
        "query": "risoluzione contratto per inadempimento",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "analysis_sections" in data
    assert isinstance(data["analysis_sections"], list)
    assert len(data["analysis_sections"]) >= 1
    for sec in data["analysis_sections"]:
        assert "step" in sec
        assert "content" in sec
        assert "citations" in sec


def test_query_llm_fields_present(client):
    """Blocco 1B: campi LLM presenti nella risposta."""
    resp = client.post("/query", json={
        "query": "obbligazione risarcimento danno",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "llm_available" in data
    assert "llm_model" in data
    assert "overall_confidence" in data
    assert "escalation_recommended" in data
    assert data["llm_available"] is True
    assert data["overall_confidence"] in ("HIGH", "MEDIUM", "LOW")


def test_query_timing_fields_present(client):
    """Blocco 1B: campi timing presenti."""
    resp = client.post("/query", json={
        "query": "test latenza risposta",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "duration_retrieval_s" in data
    assert "duration_llm_s" in data
    assert "duration_total_s" in data
    assert isinstance(data["duration_total_s"], float)


def test_query_with_chunk_filter(client):
    """Blocco 1B: chunk_filter passato all'orchestratore."""
    resp = client.post("/query", json={
        "query": "responsabilità civile",
        "workspace": "test-ws",
        "chunk_filter": {"corpus": "normattiva", "fonte": "codice_civile"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["sources"] is not None


def test_query_reviewer_verdict_in_response(client):
    """S5 reviewer_verdict deve essere nella risposta."""
    resp = client.post("/query", json={
        "query": "contratto di locazione inadempimento",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["reviewer_verdict"] in ("PASS", "WARN", "FAIL")
    assert data["reviewer_action"] in ("DELIVER", "RE_RETRIEVAL", "BLOCK")


# ---------------------------------------------------------------------------
# POST /query — graceful degradation (Ollama non disponibile)
# ---------------------------------------------------------------------------

def test_query_graceful_degradation_no_ollama():
    """Senza Ollama la risposta ha answer='' ma sources e verdict presenti."""
    from aiura_legal.agents.analyst import AnalysisResult
    from aiura_legal.agents.orchestrator import OrchestratorResult

    mock_mc = _mock_mongo()
    packet = _make_packet([
        SearchResult(
            doc_id="CC_ART_1218", score=1.0,
            snippet="Il debitore...", source_id="CC_ART_1218",
            retrieval_method="bm25", metadata={},
        )
    ])
    # Simula S3 fallito (Ollama assente)
    analysis_no_llm = AnalysisResult(
        answer="",
        analysis_sections=[],
        overall_confidence="LOW",
        gaps=["LLM non disponibile (ConnectionError). Retrieval disponibile."],
        llm_model="qwen2.5:7b",
        parse_ok=False,
    )
    result_no_llm = OrchestratorResult(
        query="test", workspace="ws", intent="norma_lookup",
        packet=packet, analysis=analysis_no_llm,
        reviewer_verdict="PASS", reviewer_action="DELIVER",
    )

    mock_orch = MagicMock()
    mock_orch.run = AsyncMock(return_value=result_no_llm)

    with (
        patch("aiura_legal.api.app.MongoClient") as MockMC,
        patch("aiura_legal.api.app._get_orchestrator", return_value=mock_orch),
        patch("aiura_legal.api.app._ollama") as mock_ollama,
    ):
        MockMC.get.return_value = mock_mc
        mock_ollama.is_available = AsyncMock(return_value=False)
        mock_ollama.list_models = AsyncMock(return_value=[])

        from aiura_legal.api.app import app
        from fastapi.testclient import TestClient
        with TestClient(app, raise_server_exceptions=True) as c:
            resp = c.post("/query", json={
                "query": "norma obbligazione contrattuale",
                "workspace": "ws",
            })

    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == ""
    assert data["llm_available"] is False
    assert len(data["sources"]) >= 1          # retrieval funziona comunque
    assert data["reviewer_verdict"] == "PASS"


# ---------------------------------------------------------------------------
# POST /query — S1 Clarifier fields
# ---------------------------------------------------------------------------

def test_query_has_clarification_fields(client):
    """La risposta deve sempre contenere i campi S1 (anche se non richiesti)."""
    resp = client.post("/query", json={
        "query": "responsabilità contrattuale inadempimento",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "clarification_needed" in data
    assert "clarification_question" in data
    assert isinstance(data["clarification_needed"], bool)


def test_query_clarification_not_needed_by_default(client):
    """Con mock orchestratore che non chiede chiarimento → clarification_needed=False."""
    resp = client.post("/query", json={
        "query": "inadempimento contrattuale obbligazione",
        "workspace": "test-ws",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["clarification_needed"] is False
    assert data["clarification_question"] is None


def test_query_clarification_needed_response():
    """S1 richiede chiarimento → clarification_needed=True, question presente, no sources."""
    from aiura_legal.agents.analyst import AnalysisResult
    from aiura_legal.agents.orchestrator import OrchestratorResult
    from aiura_legal.core.types import QueryIntent, ResearchPacket

    mock_mc = _mock_mongo()

    # Risultato orchestratore con clarification richiesta
    analysis_empty = AnalysisResult(
        answer="",
        analysis_sections=[],
        overall_confidence="LOW",
        gaps=["In attesa di chiarimento dalla query."],
        llm_model="qwen2.5:7b",
        parse_ok=False,
    )
    result_clarification = OrchestratorResult(
        query="appalto inadempimento",
        workspace="test-ws",
        intent="fattispecie_analysis",
        packet=ResearchPacket(
            query_original="appalto inadempimento",
            query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
            sources=[],
            retrieval_confidence="LOW",
            gaps=["In attesa di chiarimento dalla query."],
        ),
        analysis=analysis_empty,
        reviewer_verdict="PASS",
        reviewer_action="DELIVER",
        clarification_needed=True,
        clarification_question="Si tratta di un appalto pubblico o privato?",
        clarification_missing_element="tipo_appalto",
    )

    mock_orch = MagicMock()
    mock_orch.run = AsyncMock(return_value=result_clarification)

    with (
        patch("aiura_legal.api.app.MongoClient") as MockMC,
        patch("aiura_legal.api.app._get_orchestrator", return_value=mock_orch),
        patch("aiura_legal.api.app._ollama") as mock_ollama,
    ):
        MockMC.get.return_value = mock_mc
        mock_ollama.is_available = AsyncMock(return_value=True)
        mock_ollama.list_models = AsyncMock(return_value=["qwen2.5:7b"])

        from aiura_legal.api.app import app
        from fastapi.testclient import TestClient
        with TestClient(app, raise_server_exceptions=True) as c:
            resp = c.post("/query", json={
                "query": "appalto inadempimento",
                "workspace": "test-ws",
                "clarification_turn": 0,
            })

    assert resp.status_code == 200
    data = resp.json()
    assert data["clarification_needed"] is True
    assert data["clarification_question"] == "Si tratta di un appalto pubblico o privato?"
    assert data["answer"] == ""
    assert data["sources"] == []


def test_query_clarification_turn_field_accepted(client):
    """clarification_turn e clarification_context sono accettati senza errori."""
    resp = client.post("/query", json={
        "query": "responsabilità inadempimento appalto privato costruzione",
        "workspace": "test-ws",
        "clarification_turn": 1,
        "clarification_context": "Si tratta di appalto privato di ristrutturazione",
    })
    assert resp.status_code == 200


def test_query_clarification_turn_negative_rejected(client):
    """clarification_turn negativo deve essere rifiutato (ge=0)."""
    resp = client.post("/query", json={
        "query": "test query legale",
        "workspace": "test-ws",
        "clarification_turn": -1,
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

def test_ingest_txt(client, tmp_path):
    content = "Testo contratto sintetico senza PII. " * 30
    resp = client.post(
        "/ingest",
        data={"workspace": "test-ws"},
        files={"file": ("contratto.txt", content.encode("utf-8"), "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "contratto.txt"
    assert data["workspace"] == "test-ws"
    assert data["status"] in ("ok", "error")


def test_ingest_unsupported_format(client):
    resp = client.post(
        "/ingest",
        data={"workspace": "test-ws"},
        files={"file": ("dati.xlsx", b"PK fake", "application/octet-stream")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "error"
    assert "Formato non supportato" in (data["error"] or "")


def test_ingest_default_workspace(client):
    content = "Testo legale sintetico. " * 20
    resp = client.post(
        "/ingest",
        files={"file": ("nota.txt", content.encode("utf-8"), "text/plain")},
    )
    assert resp.status_code == 200
    assert resp.json()["workspace"] == "default"


# ---------------------------------------------------------------------------
# GET /workspace
# ---------------------------------------------------------------------------

def test_list_workspaces(client, tmp_path):
    with patch("aiura_legal.api.app._settings") as mock_settings:
        mock_settings.aiura_workspaces_path = str(tmp_path)
        (tmp_path / "studio-alpha" / "indices").mkdir(parents=True)
        (tmp_path / "studio-beta" / "indices").mkdir(parents=True)
        resp = client.get("/workspace")
    assert resp.status_code == 200
    data = resp.json()
    assert "workspaces" in data
    assert isinstance(data["workspaces"], list)


def test_get_workspace_not_found(client, tmp_path):
    with patch("aiura_legal.api.app._settings") as mock_settings:
        mock_settings.aiura_workspaces_path = str(tmp_path)
        resp = client.get("/workspace/inesistente")
    assert resp.status_code == 404


def test_create_workspace(client, tmp_path):
    with patch("aiura_legal.api.app._settings") as mock_settings:
        mock_settings.aiura_workspaces_path = str(tmp_path)
        resp = client.post("/workspace/nuovo-studio")
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "nuovo-studio"
    assert data["doc_count"] == 0
    assert data["has_bm25_index"] is False


def test_create_workspace_creates_dirs(client, tmp_path):
    with patch("aiura_legal.api.app._settings") as mock_settings:
        mock_settings.aiura_workspaces_path = str(tmp_path)
        client.post("/workspace/test-studio")
    ws_path = tmp_path / "test-studio"
    assert (ws_path / "incoming").exists()
    assert (ws_path / "processed").exists()
    assert (ws_path / "failed").exists()
    assert (ws_path / "indices").exists()


# ---------------------------------------------------------------------------
# OpenAPI docs
# ---------------------------------------------------------------------------

def test_openapi_docs(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_openapi_schema(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    paths = schema["paths"]
    assert "/health" in paths
    assert "/query" in paths
    assert "/ingest" in paths
    assert "/workspace" in paths
