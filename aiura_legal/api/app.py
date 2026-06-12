"""
AiUra LegalLab — FastAPI app.
Porta: 8765  (AIURA_API_HOST / AIURA_API_PORT da .env)

Avvio:
  python -m aiura_legal.api
  uvicorn aiura_legal.api.app:app --host 127.0.0.1 --port 8765 --reload

Catena /query (Block 1B + S1):
  S0 routing (programmatico) → S1 clarifier → S2 retrieval → S3 analysis (Ollama) → S5 review
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Optional

import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.agents.annotator import AnnotationResult, AnnotatorAgent
from aiura_legal.agents.ollama_client import OllamaClient
from aiura_legal.agents.openai_compat_client import OpenAICompatClient
from aiura_legal.agents.orchestrator import LegalOrchestrator
from aiura_legal.api.schemas import (
    AnalysisSectionItem,
    AnnotateJobResponse,
    AnnotateRequest,
    AnnotateResultResponse,
    AnnotationItem,
    DocumentItem,
    DocumentListResponse,
    DocumentMoveRequest,
    FeedbackRequest,
    FolderCreate,
    FolderItem,
    FolderListResponse,
    FolderRename,
    HealthResponse,
    HistoryEntry,
    HistoryListResponse,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    SourceItem,
    WikiListResponse,
    WikiPageItem,
    WorkspaceInfo,
    WorkspaceListResponse,
)
from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever
from aiura_legal.core.reviewer.reviewer import CitationReviewer
from aiura_legal.core.types import QueryIntent
from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.api.jurisprudence_router import router as jurisprudence_router
from aiura_legal.api.graph_router import router as graph_router
from aiura_legal.api.settings_router import router as settings_router
from aiura_legal.api.graph_router import set_graph as _set_graph
from aiura_legal.ingestion.pipeline import Tier1Pipeline
from aiura_legal.wiki.store import WikiStore
from aiura_legal.wiki.writer import WikiWriter
from aiura_legal.wiki.engine import WikiEngine
from aiura_legal.wiki.middleware import WikiMiddleware


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class ApiSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    aiura_workspaces_path: str = "C:/project/AiUraLegalLab/workspaces"
    aiura_api_host: str = "127.0.0.1"
    aiura_api_port: int = 8765
    # "ollama" (default) oppure "lmstudio" / qualsiasi backend OpenAI-compatibile
    aiura_llm_backend: str = "ollama"


_settings = ApiSettings()


# ---------------------------------------------------------------------------
# Stato applicazione (lazy init, thread-safe per FastAPI single-process)
# ---------------------------------------------------------------------------

_orchestrator_cache: dict[str, LegalOrchestrator] = {}
_reviewer = CitationReviewer()

# Wiki layer (inizializzato in lifespan dopo ping MongoDB)
_wiki_engine: WikiEngine | None = None

# LLM client: Ollama (nativo) oppure OpenAI-compatibile (LMStudio, vLLM…)
if _settings.aiura_llm_backend.lower() == "lmstudio":
    _ollama: OllamaClient | OpenAICompatClient = OpenAICompatClient()
    logger.info(
        f"LLM backend: LMStudio  "
        f"({_ollama.base_url}  model={_ollama.model})"
    )
else:
    _ollama = OllamaClient()
    logger.info(
        f"LLM backend: Ollama  "
        f"({_ollama.base_url}  model={_ollama.model})"
    )

_annotator = AnnotatorAgent(ollama=_ollama)


_BM25_CORPORA = ("normattiva", "dottrina", "studio", "giurisprudenza")


def _has_bm25_index(ws_dir: Path) -> bool:
    """True se esiste almeno un pkl BM25 per-corpus (o il legacy monolitico)."""
    indices = ws_dir / "indices"
    return any((indices / f"bm25_{c}.pkl").exists() for c in _BM25_CORPORA) or \
        (indices / "bm25.pkl").exists()


def _has_qdrant_index() -> bool:
    """
    Verifica se l'indice Qdrant è disponibile.
    In server mode (QDRANT_URL configurato): interroga il server.
    In embedded mode: controlla la cartella locale.
    """
    from aiura_legal.core.retrieval.vector_retriever import QdrantSettings
    qdrant_url = QdrantSettings().qdrant_url.strip()
    if qdrant_url:
        try:
            from qdrant_client import QdrantClient
            c = QdrantClient(url=qdrant_url, timeout=2)
            existing = [col.name for col in c.get_collections().collections]
            return "legal_docs" in existing and c.count("legal_docs").count > 0
        except Exception:
            return False
    else:
        # Embedded: controlla cartella locale (fallback)
        base = Path(_settings.aiura_workspaces_path)
        # Cerca in tutti i workspace
        for ws in base.iterdir():
            if (ws / "indices" / "qdrant").exists():
                return True
        return False


def _get_orchestrator(workspace: str) -> LegalOrchestrator:
    """
    Lazy-load LegalOrchestrator per workspace (cache in memoria).
    Crea HybridRetriever (carica indici da disco) e AnalystAgent (condivide OllamaClient).
    """
    if workspace not in _orchestrator_cache:
        ws_path = f"{_settings.aiura_workspaces_path}/{workspace}"
        logger.info(f"Caricamento indici per workspace: {workspace}")
        retriever = HybridRetriever(ws_path)
        _orchestrator_cache[workspace] = LegalOrchestrator(
            retriever=retriever,
            ollama=_ollama,
            reviewer=_reviewer,
        )
    return _orchestrator_cache[workspace]


def _intent_from_str(s: str) -> QueryIntent:
    mapping = {i.value: i for i in QueryIntent}
    intent = mapping.get(s.lower())
    if intent is None:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"intent non valido: '{s}'. Valori: {list(mapping.keys())}",
        )
    return intent


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def _lifespan(application: FastAPI):
    global _wiki_engine
    logger.info("AiUra LegalLab API avviata")
    mongo = MongoClient.get()
    ok = await mongo.ping()
    if ok:
        logger.info("MongoDB: connesso")
        wiki_store = WikiStore(mongo.db)
        await wiki_store.ensure_indexes()
        _wiki_engine = WikiEngine(wiki_store, WikiWriter())
        logger.info("Wiki layer: inizializzato")
    else:
        logger.warning("MongoDB: non raggiungibile — alcune funzioni non disponibili")
    ollama_ok = await _ollama.is_available()
    backend_name = _settings.aiura_llm_backend.upper()
    if ollama_ok:
        models = await _ollama.list_models()
        logger.info(f"{backend_name}: disponibile — modelli: {models}")
    else:
        logger.warning(f"{backend_name}: non raggiungibile — analisi LLM disabilitata")

    # ── Warm-up preventivo indici ──────────────────────────────────────────
    # ChromaDB/SentenceTransformer ha un cold start di ~20s alla prima query
    # (caricamento HNSW in RAM + embedding model). Lo eseguiamo in background
    # all'avvio così la prima query dell'utente trova tutto già in memoria.
    async def _warmup_indices():
        try:
            default_ws = _settings.aiura_workspaces_path + "/mio-studio"
            from pathlib import Path as _Path
            indices_dir = _Path(default_ws) / "indices"
            _known_corpora = ("normattiva", "dottrina", "studio", "giurisprudenza")
            has_any_bm25 = any(
                (indices_dir / f"bm25_{c}.pkl").exists() for c in _known_corpora
            ) or (indices_dir / "bm25.pkl").exists()  # legacy fallback
            if not has_any_bm25:
                return
            logger.info("Warm-up indici: avvio in background...")
            t0 = time.monotonic()
            orch = _get_orchestrator("mio-studio")
            # Esegui una query di warm-up leggera per inizializzare HNSW e SentenceTransformer
            await asyncio.to_thread(
                orch._retriever.vector.search,
                "pagamento locazione",
                5,  # top_k ridotto per il warm-up
            )
            logger.info(f"Warm-up indici completato in {time.monotonic()-t0:.1f}s")
        except Exception as e:
            logger.warning(f"Warm-up indici fallito (non-fatal): {e}")

    asyncio.create_task(_warmup_indices())

    # ── Caricamento grafo giurisprudenziale ───────────────────────────────────
    async def _load_graph_task():
        import networkx as nx
        graph_path = Path(_settings.aiura_workspaces_path) / "jurisprudence_graph.json"
        if not graph_path.exists():
            logger.warning(f"Grafo non trovato: {graph_path} — /graph disabilitato")
            return
        try:
            t0 = time.monotonic()
            logger.info("Grafo: caricamento in memoria...")
            raw = await asyncio.to_thread(graph_path.read_text, encoding="utf-8")
            data = await asyncio.to_thread(json.loads, raw)
            g: nx.DiGraph = await asyncio.to_thread(nx.node_link_graph, data, edges="links")
            _set_graph(g)
            logger.info(
                f"Grafo: {g.number_of_nodes()} nodi, {g.number_of_edges()} archi "
                f"— {time.monotonic() - t0:.1f}s"
            )
        except Exception as exc:
            logger.warning(f"Grafo: caricamento fallito (non-fatal): {exc}")

    asyncio.create_task(_load_graph_task())

    yield
    logger.info("AiUra LegalLab API spenta")


app = FastAPI(
    title="AiUra LegalLab",
    description=(
        "API multi-agente per ricerca e analisi legale con Citation Contract.\n\n"
        "Catena: S0 routing → S2 retrieval → S3 analysis (Ollama) → S5 review"
    ),
    version="0.1.0.dev0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=_lifespan,
)


def _get_wiki_engine() -> WikiEngine | None:
    return _wiki_engine


app.add_middleware(WikiMiddleware, engine_factory=_get_wiki_engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(jurisprudence_router)
app.include_router(graph_router, prefix="/graph", tags=["graph"])
app.include_router(settings_router)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    """Verifica disponibilità MongoDB e Ollama."""
    mongo_ok = await MongoClient.get().ping()
    ollama_ok = await _ollama.is_available()
    overall = "ok" if (mongo_ok and ollama_ok) else "degraded"
    return HealthResponse(
        status=overall,
        mongodb=mongo_ok,
        ollama=ollama_ok,
    )


# ---------------------------------------------------------------------------
# POST /query  — catena S0→S2→S3→S5
# ---------------------------------------------------------------------------

@app.post("/query", response_model=QueryResponse, tags=["query"])
async def query(req: QueryRequest):
    """
    Analisi legale E2E con Citation Contract.

    Catena (Block 1B):
      S0 routing   — classifica intent (programmatico)
      S2 retrieval — BM25 + Vector + CrossEncoder → Research Packet
      S3 analysis  — Ollama qwen2.5:7b CoT → risposta con fonti citate
      S5 review    — CitationReviewer verifica grounding delle citazioni

    Se Ollama non è disponibile: restituisce solo il Research Packet
    (llm_available=false, answer="") senza errori.
    """
    intent = _intent_from_str(req.intent)

    try:
        orchestrator = _get_orchestrator(req.workspace)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossibile caricare gli indici per workspace '{req.workspace}': {e}",
        )

    result = await orchestrator.run(
        query=req.query,
        intent=intent,
        valid_on=req.valid_on,
        chunk_filter=req.chunk_filter,
        workspace=req.workspace,
        clarification_turn=req.clarification_turn,
        clarification_context=req.clarification_context,
        draft_type=req.draft_type,
        mode=req.mode,
    )

    # Costruisce la lista fonti (tronca a top_k)
    sources = [
        SourceItem(
            rank=i + 1,
            doc_id=s.doc_id,
            source_id=s.source_id,
            score=round(s.score, 4),
            snippet=s.snippet[:500],
            retrieval_method=s.retrieval_method,
            metadata=s.metadata,
        )
        for i, s in enumerate(result.sources[: req.top_k])
    ]

    # Serializza le sezioni CoT (merged — backward compat)
    analysis_sections = [
        AnalysisSectionItem(step=sec.step, content=sec.content, citations=sec.citations)
        for sec in result.analysis.analysis_sections
    ]

    # Serializza sezioni deep (separate per fase)
    def _to_items(ar) -> list:
        if not ar:
            return []
        return [
            AnalysisSectionItem(step=s.step, content=s.content, citations=s.citations)
            for s in ar.analysis_sections
        ]

    return QueryResponse(
        query=req.query,
        workspace=req.workspace,
        intent=req.intent,
        # S2
        sources=sources,
        retrieval_confidence=result.retrieval_confidence,
        gaps=result.gaps,
        # S3
        answer=result.answer,
        analysis_sections=analysis_sections,
        overall_confidence=result.analysis.overall_confidence,
        llm_model=result.analysis.llm_model,
        llm_available=result.llm_available,
        escalation_recommended=result.analysis.escalation_recommended,
        # S3 deep
        mode=result.mode,
        analysis_fase_1=_to_items(result.analysis_fase_1),
        analysis_fase_2=_to_items(result.analysis_fase_2),
        fase_2_available=result.analysis_fase_2 is not None,
        # Timing
        duration_retrieval_s=result.duration_retrieval_s,
        duration_llm_s=result.duration_llm_s,
        duration_total_s=result.duration_total_s,
        # S1 Clarifier
        clarification_needed=result.clarification_needed,
        clarification_question=result.clarification_question,
        # S4 Drafter
        draft_type=result.draft.document_type if result.draft else None,
        draft_text=result.draft.raw_text if result.draft else "",
        draft_rendered=result.draft.rendered_text if result.draft else "",
        draft_full_document=result.draft.full_document if result.draft else "",
        # S5
        reviewer_verdict=result.reviewer_verdict,
        reviewer_action=result.reviewer_action,
        warnings=result.reviewer_warnings,
    )


# ---------------------------------------------------------------------------
# POST /query/stream  — Sequential IQRAC con SSE streaming fase per fase
# ---------------------------------------------------------------------------

def _phase_result_to_dict(phase) -> dict:
    """Serializza PhaseResult in dict JSON-safe per SSE."""
    return {
        "phase": phase.phase,
        "name": phase.name,
        "sections": [
            {"step": s.step, "content": s.content, "citations": s.citations}
            for s in phase.sections
        ],
        "sources_used": phase.sources_used,
        "overall_confidence": phase.overall_confidence,
        "escalation_recommended": phase.escalation_recommended,
        "gaps": phase.gaps,
        "duration_s": round(phase.duration_s, 2),
        "parse_ok": phase.parse_ok,
    }


def _sse_event(event: str, data: dict) -> str:
    # Incorpora il tipo evento dentro il JSON — il frontend legge solo le righe "data:"
    payload = json.dumps({"type": event, **data}, ensure_ascii=False)
    # Doppio \n finale + commento ping forzano flush in tutti i proxy/middleware
    return f"data: {payload}\n\n: ping\n\n"


@app.post("/query/stream", tags=["query"])
async def query_stream(req: QueryRequest) -> StreamingResponse:
    """
    Sequential IQRAC con SSE streaming: emette un evento per ogni fase completata.

    Eventi emessi:
      retrieval_done   — S2 completato, fonti disponibili
      phase_complete   — una fase IQRAC completata (phase 1-4)
      review_done      — S5 completato, verdetto finale
      clarification_needed — S1 ha richiesto chiarimento
      error            — errore non recuperabile

    Il client può mostrare ogni fase man mano che arriva.
    """
    intent = _intent_from_str(req.intent)

    try:
        orchestrator = _get_orchestrator(req.workspace)
    except Exception as e:
        async def _err():
            yield _sse_event("error", {"message": f"Workspace non disponibile: {e}"})
        return StreamingResponse(_err(), media_type="text/event-stream")

    async def _generate():
        # Accumulatori per la voce history (popolati dagli eventi phase_complete)
        all_sections: list[dict] = []

        try:
            async for event_data in orchestrator.run_sequential(
                query=req.query,
                intent=intent,
                valid_on=req.valid_on,
                chunk_filter=req.chunk_filter,
                workspace=req.workspace,
                clarification_turn=req.clarification_turn,
                clarification_context=req.clarification_context,
            ):
                event_type = event_data.get("event", "unknown")

                if event_type == "phase_complete":
                    phase = event_data["phase"]
                    # Accumula sezioni per il salvataggio history
                    for s in phase.sections:
                        all_sections.append({"step": s.step, "content": s.content, "citations": s.citations})
                    yield _sse_event("phase_complete", _phase_result_to_dict(phase))

                elif event_type == "retrieval_done":
                    yield _sse_event("retrieval_done", {
                        "sources_count": event_data["sources_count"],
                        "confidence": event_data["confidence"],
                    })

                elif event_type == "review_done":
                    # Estrai answer dalla sezione CONCLUSIONE (o dalla prima disponibile)
                    conclusione = next(
                        (s["content"] for s in all_sections if s["step"] == "CONCLUSIONE"), ""
                    )
                    answer_summary = conclusione[:300] if conclusione else ""

                    # Genera history_id e salva su MongoDB con dati completi
                    history_id = str(uuid.uuid4())
                    try:
                        mongo = MongoClient.get()
                        await mongo.db["query_history"].insert_one({
                            "_id":              history_id,
                            "query":            req.query,
                            "workspace":        req.workspace,
                            "intent":           req.intent,
                            "mode":             "standard",
                            "verdict":          event_data["verdict"],
                            "confidence":       event_data["overall_confidence"],
                            "answer":           conclusione,
                            "answer_summary":   answer_summary,
                            "analysis_sections": all_sections,
                            "sources":          event_data.get("sources", []),
                            "sources_count":    len(event_data.get("sources", [])),
                            "duration_total_s": event_data["duration_total_s"],
                            "created_at":       datetime.now(timezone.utc).isoformat(),
                        })
                    except Exception as exc:
                        logger.warning(f"[/query/stream] history save fallita: {exc}")
                        history_id = None

                    yield _sse_event("review_done", {
                        "verdict":          event_data["verdict"],
                        "action":           event_data["action"],
                        "warnings":         event_data["warnings"],
                        "overall_confidence": event_data["overall_confidence"],
                        "duration_total_s": event_data["duration_total_s"],
                        "sources":          event_data.get("sources", []),
                        "gaps":             event_data.get("gaps", []),
                        "history_id":       history_id,
                    })

                elif event_type == "clarification_needed":
                    yield _sse_event("clarification_needed", {
                        "question": event_data.get("question"),
                        "missing_element": event_data.get("missing_element"),
                    })
                    return

                elif event_type == "error":
                    yield _sse_event("error", {"message": event_data.get("message", "")})
                    return

        except Exception as exc:
            logger.error(f"[/query/stream] errore non gestito: {exc}")
            yield _sse_event("error", {"message": str(exc)})

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

@app.post("/ingest", response_model=IngestResponse, tags=["ingest"])
async def ingest(
    file: UploadFile = File(..., description="File PDF, DOCX o TXT"),
    workspace: str = Form(default="default", description="Nome workspace"),
    corpus: str = Form(
        default="studio",
        description="Corpus di destinazione: 'studio' (documenti cliente) | 'dottrina' (manuali, articoli accademici)",
    ),
):
    """
    Carica un documento e avvia la Pipeline Tier 1:
    estrazione testo → anonimizzazione PII → MongoDB → chunking.

    Usa corpus='dottrina' per caricare manuali giuridici, commentari e articoli
    accademici che verranno usati nella fase di Interpretazione dell'IQRAC.
    """
    suffix = Path(file.filename or "upload.txt").suffix.lower()
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, prefix="aiura_upload_"
    ) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        mongo = MongoClient.get()
        pipeline = Tier1Pipeline(
            mongo_db=mongo.db,
            workspace=workspace,
            corpus=corpus,
        )
        result = await pipeline.ingest(tmp_path)
        result.filename = file.filename or result.filename
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return IngestResponse(
        document_id=result.document_id,
        filename=result.filename,
        workspace=result.workspace,
        status=result.status,
        text_length=result.text_length,
        chunk_count=result.chunk_count,
        pii_stats=result.pii_stats,
        duration_s=round(result.duration_s, 3),
        error=result.error,
    )


# ---------------------------------------------------------------------------
# GET /workspace
# ---------------------------------------------------------------------------

@app.get("/workspace", response_model=WorkspaceListResponse, tags=["workspace"])
async def list_workspaces():
    """Elenca i workspace disponibili con statistiche MongoDB."""
    base = Path(_settings.aiura_workspaces_path)
    mongo = MongoClient.get()
    workspaces = []

    if base.exists():
        for ws_dir in sorted(base.iterdir()):
            if not ws_dir.is_dir():
                continue
            name = ws_dir.name
            try:
                doc_count = await mongo.db["documents"].count_documents(
                    {"workspace": name}
                )
                chunk_count = await mongo.db["chunks"].count_documents(
                    {"workspace": name}
                )
                pending = await mongo.db["ingestion_queue"].count_documents(
                    {"status": "pending"}
                )
            except Exception:
                doc_count = chunk_count = pending = -1

            workspaces.append(WorkspaceInfo(
                name=name,
                doc_count=doc_count,
                chunk_count=chunk_count,
                pending_jobs=pending,
                has_bm25_index=_has_bm25_index(ws_dir),
                has_vector_index=_has_qdrant_index(),
            ))

    return WorkspaceListResponse(workspaces=workspaces)


@app.get("/workspace/{name}", response_model=WorkspaceInfo, tags=["workspace"])
async def get_workspace(name: str):
    """Dettagli e statistiche per un workspace specifico."""
    base = Path(_settings.aiura_workspaces_path)
    ws_dir = base / name

    if not ws_dir.exists():
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{name}' non trovato",
        )

    mongo = MongoClient.get()
    try:
        doc_count = await mongo.db["documents"].count_documents({"workspace": name})
        chunk_count = await mongo.db["chunks"].count_documents({"workspace": name})
        pending = await mongo.db["ingestion_queue"].count_documents({"status": "pending"})
    except Exception:
        doc_count = chunk_count = pending = -1

    return WorkspaceInfo(
        name=name,
        doc_count=doc_count,
        chunk_count=chunk_count,
        pending_jobs=pending,
        has_bm25_index=_has_bm25_index(ws_dir),
        has_vector_index=(ws_dir / "indices" / "qdrant").exists(),
    )


@app.post(
    "/workspace/{name}",
    response_model=WorkspaceInfo,
    status_code=http_status.HTTP_201_CREATED,
    tags=["workspace"],
)
async def create_workspace(name: str):
    """Crea la struttura cartelle per un nuovo workspace."""
    base = Path(_settings.aiura_workspaces_path)
    ws_dir = base / name
    for sub in ["incoming", "processed", "failed", "indices"]:
        (ws_dir / sub).mkdir(parents=True, exist_ok=True)

    logger.info(f"Workspace creato: {name}")
    return WorkspaceInfo(
        name=name,
        doc_count=0,
        chunk_count=0,
        pending_jobs=0,
        has_bm25_index=False,
        has_vector_index=False,
    )


# ---------------------------------------------------------------------------
# POST /annotate/{document_id}  — Workflow B: Document Intelligence asincrona
# ---------------------------------------------------------------------------

async def _run_annotation_job(
    document_id: str,
    workspace: str,
    document_text: str,
    chunk_filter: Optional[dict],
    max_sections: int,
) -> None:
    """
    Background task per l'annotazione di un documento.
    Aggiorna la collection `annotations` con status=completed|error.
    """
    mongo = MongoClient.get()
    t0 = __import__("time").monotonic()

    try:
        # Retrieval fonti pertinenti al documento (query = incipit del doc)
        query_text = document_text[:500].strip()
        orchestrator = _get_orchestrator(workspace)
        packet = orchestrator._retriever.build_research_packet(
            query=query_text,
            intent=__import__(
                "aiura_legal.core.types", fromlist=["QueryIntent"]
            ).QueryIntent.FATTISPECIE_ANALYSIS,
            chunk_filter=chunk_filter,
        )

        result = await _annotator.annotate(
            document_text=document_text,
            document_id=document_id,
            packet=packet,
            max_sections=max_sections,
        )

        ann_docs = [
            {
                "section": a.section,
                "annotation_type": a.annotation_type,
                "text": a.text,
                "level": a.level,
                "source_citations": a.source_citations,
                "suggested_replacement": a.suggested_replacement,
            }
            for a in result.annotations
        ]

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        await mongo.db["annotations"].update_one(
            {"document_id": document_id},
            {
                "$set": {
                    "status": "completed",
                    "annotations": ann_docs,
                    "summary": result.summary,
                    "overall_risk": result.overall_risk,
                    "sections_processed": result.sections_processed,
                    "llm_model": result.llm_model,
                    "duration_s": result.duration_s,
                    "parse_ok": result.parse_ok,
                    "completed_at": now,
                }
            },
            upsert=False,
        )
        logger.success(
            f"[Annotate] Completato: doc={document_id}, "
            f"annotations={len(result.annotations)}, risk={result.overall_risk}"
        )

    except Exception as exc:
        logger.error(f"[Annotate] Errore background job doc={document_id}: {exc}")
        from datetime import datetime, timezone
        await mongo.db["annotations"].update_one(
            {"document_id": document_id},
            {"$set": {"status": "error", "error": str(exc),
                      "completed_at": datetime.now(timezone.utc)}},
            upsert=False,
        )


@app.post(
    "/annotate/{document_id}",
    response_model=AnnotateJobResponse,
    status_code=http_status.HTTP_202_ACCEPTED,
    tags=["annotate"],
)
async def annotate_document(
    document_id: str,
    req: AnnotateRequest,
    background_tasks: BackgroundTasks,
):
    """
    Avvia l'annotazione Document Intelligence (S6) per un documento già ingerito.

    Workflow B — asincrono:
      1. Recupera il testo del documento da MongoDB
      2. Accoda il job di annotazione (ritorna 202 immediatamente)
      3. In background: S2 retrieval → S6 annotate → salva in `annotations`
      4. Recupera il risultato con GET /annotate/{document_id}
    """
    mongo = MongoClient.get()

    # Recupera il documento
    doc = await mongo.db["documents"].find_one(
        {"_id": document_id, "workspace": req.workspace}
    )
    if doc is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Documento '{document_id}' non trovato nel workspace '{req.workspace}'",
        )

    text = doc.get("text", "")
    if not text.strip():
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Documento '{document_id}' ha testo vuoto",
        )

    # Crea il record di annotazione con status=queued
    from datetime import datetime, timezone
    await mongo.db["annotations"].update_one(
        {"document_id": document_id},
        {
            "$set": {
                "document_id": document_id,
                "workspace": req.workspace,
                "status": "queued",
                "annotations": [],
                "summary": {},
                "overall_risk": "NESSUNO",
                "sections_processed": 0,
                "created_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

    # Accoda il job in background
    background_tasks.add_task(
        _run_annotation_job,
        document_id=document_id,
        workspace=req.workspace,
        document_text=text,
        chunk_filter=req.chunk_filter,
        max_sections=req.max_sections,
    )

    logger.info(f"[Annotate] Job accodato: doc={document_id}, workspace={req.workspace}")
    return AnnotateJobResponse(
        document_id=document_id,
        status="queued",
        message="Annotazione avviata. Recupera il risultato con GET /annotate/{document_id}",
    )


@app.get(
    "/annotate/{document_id}",
    response_model=AnnotateResultResponse,
    tags=["annotate"],
)
async def get_annotation_result(document_id: str, workspace: str = "default"):
    """
    Recupera il risultato dell'annotazione per un documento.

    Status possibili:
      - queued:    job ancora in coda o in esecuzione
      - completed: annotazione terminata, risultato disponibile
      - error:     annotazione fallita (campo 'error' con il motivo)
    """
    mongo = MongoClient.get()
    record = await mongo.db["annotations"].find_one({"document_id": document_id})

    if record is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Nessuna annotazione trovata per documento '{document_id}'",
        )

    annotations = [
        AnnotationItem(
            section=a.get("section", ""),
            annotation_type=a.get("annotation_type", ""),
            text=a.get("text", ""),
            level=a.get("level", ""),
            source_citations=a.get("source_citations", []),
            suggested_replacement=a.get("suggested_replacement", ""),
        )
        for a in record.get("annotations", [])
    ]

    return AnnotateResultResponse(
        document_id=document_id,
        workspace=record.get("workspace", workspace),
        status=record.get("status", "queued"),
        annotations=annotations,
        summary=record.get("summary", {}),
        overall_risk=record.get("overall_risk", "NESSUNO"),
        sections_processed=record.get("sections_processed", 0),
        llm_model=record.get("llm_model", ""),
        duration_s=record.get("duration_s", 0.0),
        parse_ok=record.get("parse_ok", False),
        error=record.get("error"),
    )


# ---------------------------------------------------------------------------
# CRUD /folders  — gestione cartelle per workspace
# ---------------------------------------------------------------------------

@app.post("/folders", response_model=FolderItem, status_code=http_status.HTTP_201_CREATED, tags=["folders"])
async def create_folder(req: FolderCreate):
    """Crea una nuova cartella nel workspace."""
    mongo = MongoClient.get()
    folder_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": folder_id,
        "name": req.name,
        "workspace": req.workspace,
        "created_at": now,
    }
    await mongo.db["folders"].insert_one(doc)
    return FolderItem(id=folder_id, name=req.name, workspace=req.workspace, doc_count=0, created_at=now)


@app.get("/folders", response_model=FolderListResponse, tags=["folders"])
async def list_folders(workspace: str = Query(..., min_length=1)):
    """Elenca le cartelle del workspace con conteggio documenti."""
    mongo = MongoClient.get()
    cursor = mongo.db["folders"].find({"workspace": workspace}, sort=[("name", 1)])
    folder_docs = await cursor.to_list(length=200)

    folders = []
    for f in folder_docs:
        fid = str(f["_id"])
        count = await mongo.db["documents"].count_documents({"folder_id": fid, "workspace": workspace})
        folders.append(FolderItem(
            id=fid,
            name=f.get("name", ""),
            workspace=f.get("workspace", workspace),
            doc_count=count,
            created_at=f.get("created_at", ""),
        ))
    return FolderListResponse(folders=folders)


@app.patch("/folders/{folder_id}", response_model=FolderItem, tags=["folders"])
async def rename_folder(folder_id: str, req: FolderRename, workspace: str = Query(...)):
    """Rinomina una cartella."""
    mongo = MongoClient.get()
    result = await mongo.db["folders"].find_one_and_update(
        {"_id": folder_id, "workspace": workspace},
        {"$set": {"name": req.name}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Cartella non trovata")
    count = await mongo.db["documents"].count_documents({"folder_id": folder_id})
    return FolderItem(
        id=folder_id, name=result["name"], workspace=workspace,
        doc_count=count, created_at=result.get("created_at", ""),
    )


@app.delete("/folders/{folder_id}", status_code=http_status.HTTP_204_NO_CONTENT, tags=["folders"])
async def delete_folder(folder_id: str, workspace: str = Query(...)):
    """Elimina una cartella (i documenti rimangono, perdono solo la cartella)."""
    mongo = MongoClient.get()
    await mongo.db["folders"].delete_one({"_id": folder_id, "workspace": workspace})
    # Rimuovi il folder_id dai documenti appartenenti alla cartella
    await mongo.db["documents"].update_many(
        {"folder_id": folder_id, "workspace": workspace},
        {"$unset": {"folder_id": ""}, "$set": {"folder_name": None}},
    )


# ---------------------------------------------------------------------------
# GET /documents — lista documenti con filtro cartella
# DELETE /documents/{id}
# POST /documents/{id}/folder — sposta documento in cartella
# ---------------------------------------------------------------------------

def _source_to_dict(s) -> dict:
    """Serializza un SearchResult per il salvataggio completo in query_history."""
    return {
        "source_id":    s.source_id,
        "doc_id":       s.doc_id,
        "snippet":      s.snippet,
        "score":        round(float(s.score), 4),
        "metadata":     dict(s.metadata or {}),
        "source_layer": getattr(s, "source_layer", "normativa"),
    }


def _section_to_dict(s) -> dict:
    """Serializza un AnalysisSection per il salvataggio in query_history."""
    return {
        "step":      s.step,
        "content":   s.content,
        "citations": list(s.citations or []),
    }


def _doc_to_item(doc: dict, folder_name: str | None = None) -> DocumentItem:
    return DocumentItem(
        id=str(doc.get("_id", "")),
        filename=doc.get("filename", doc.get("_id", "")),
        workspace=doc.get("workspace", ""),
        folder_id=doc.get("folder_id"),
        folder_name=folder_name or doc.get("folder_name"),
        status=doc.get("status", "ready"),
        text_length=doc.get("text_length", len(doc.get("text", ""))),
        chunk_count=doc.get("chunk_count", 0),
        pii_stats=doc.get("pii_stats", {}),
        created_at=doc.get("created_at", doc.get("ingested_at", "")),
        error=doc.get("error"),
    )


@app.get("/documents", response_model=DocumentListResponse, tags=["documents"])
async def list_documents(
    workspace: str = Query(..., min_length=1),
    folder_id: Optional[str] = Query(default=None),
):
    """Lista documenti del workspace, opzionalmente filtrata per cartella."""
    mongo = MongoClient.get()
    query: dict = {"workspace": workspace}
    if folder_id == "__none__":
        query["folder_id"] = {"$exists": False}
    elif folder_id:
        query["folder_id"] = folder_id

    cursor = mongo.db["documents"].find(query, sort=[("created_at", -1)])
    docs = await cursor.to_list(length=500)
    total = await mongo.db["documents"].count_documents(query)

    # Carica i nomi delle cartelle in batch
    folder_ids = {d.get("folder_id") for d in docs if d.get("folder_id")}
    folder_names: dict[str, str] = {}
    if folder_ids:
        f_cursor = mongo.db["folders"].find({"_id": {"$in": list(folder_ids)}})
        for f in await f_cursor.to_list(length=200):
            folder_names[str(f["_id"])] = f.get("name", "")

    items = [_doc_to_item(d, folder_names.get(d.get("folder_id", ""))) for d in docs]
    return DocumentListResponse(documents=items, total=total)


@app.delete("/documents/{document_id}", status_code=http_status.HTTP_204_NO_CONTENT, tags=["documents"])
async def delete_document(document_id: str, workspace: str = Query(...)):
    """Elimina un documento e i suoi chunk dal workspace."""
    mongo = MongoClient.get()
    result = await mongo.db["documents"].delete_one({"_id": document_id, "workspace": workspace})
    if result.deleted_count == 0:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Documento non trovato")
    # Rimuovi i chunk associati
    await mongo.db["chunks"].delete_many({"document_id": document_id, "workspace": workspace})
    await mongo.db["annotations"].delete_many({"document_id": document_id})


@app.post("/documents/{document_id}/folder", response_model=DocumentItem, tags=["documents"])
async def move_document(document_id: str, req: DocumentMoveRequest, workspace: str = Query(...)):
    """Assegna o rimuove un documento da una cartella."""
    mongo = MongoClient.get()
    folder_name = None
    if req.folder_id:
        folder = await mongo.db["folders"].find_one({"_id": req.folder_id, "workspace": workspace})
        if not folder:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Cartella non trovata")
        folder_name = folder.get("name", "")

    update = (
        {"$set": {"folder_id": req.folder_id, "folder_name": folder_name}}
        if req.folder_id
        else {"$unset": {"folder_id": ""}, "$set": {"folder_name": None}}
    )
    doc = await mongo.db["documents"].find_one_and_update(
        {"_id": document_id, "workspace": workspace},
        update,
        return_document=True,
    )
    if not doc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Documento non trovato")
    return _doc_to_item(doc, folder_name)


# ---------------------------------------------------------------------------
# POST /query/stream  — catena S0→S2→S3→S5 con SSE streaming
# ---------------------------------------------------------------------------

@app.post("/query/stream/legacy", tags=["query"])
async def query_stream_legacy(req: QueryRequest):
    """
    Analisi legale (modalità standard) con risposta in streaming via Server-Sent Events.

    Usa orchestrator.run() (non-sequential) e salva in history/wiki.
    Per l'analisi Sequential IQRAC usa POST /query/stream.

    Emette eventi SSE:
      - {type: "status", agent: "S2", message: "Recupero fonti..."}
      - {type: "status", agent: "S3", message: "Analisi in corso..."}
      - {type: "status", agent: "S5", message: "Verifica citazioni..."}
      - {type: "result", data: <QueryResponse serializzato>}
      - {type: "done"}
      - {type: "error", message: "..."}  (in caso di errore)
    """
    intent = _intent_from_str(req.intent)

    async def _event_generator():
        try:
            orchestrator = _get_orchestrator(req.workspace)
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        # S2 status
        yield f"data: {json.dumps({'type': 'status', 'agent': 'S2', 'message': 'Researcher · recupero fonti...'})}\n\n"

        try:
            result = await orchestrator.run(
                query=req.query,
                intent=intent,
                valid_on=req.valid_on,
                chunk_filter=req.chunk_filter,
                workspace=req.workspace,
                clarification_turn=req.clarification_turn,
                clarification_context=req.clarification_context,
                draft_type=req.draft_type,
                mode=req.mode,
            )
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        # S3 status (emesso dopo il retrieval, prima di restituire il risultato LLM)
        yield f"data: {json.dumps({'type': 'status', 'agent': 'S3', 'message': 'Analyst · analisi in corso...'})}\n\n"
        yield f"data: {json.dumps({'type': 'status', 'agent': 'S5', 'message': 'Reviewer · verifica citazioni...'})}\n\n"

        # Assembla il payload QueryResponse
        sources = [
            {
                "rank": i + 1,
                "doc_id": s.doc_id,
                "source_id": s.source_id,
                "score": round(s.score, 4),
                "snippet": s.snippet[:500],
                "retrieval_method": s.retrieval_method,
                "metadata": s.metadata,
            }
            for i, s in enumerate(result.sources[: req.top_k])
        ]
        analysis_sections = [
            {"step": sec.step, "content": sec.content, "citations": sec.citations}
            for sec in result.analysis.analysis_sections
        ]

        # Genera l'ID history prima del payload così il frontend può subito usarlo
        history_id = str(uuid.uuid4())

        payload = {
            "query": req.query,
            "workspace": req.workspace,
            "intent": req.intent,
            "sources": sources,
            "retrieval_confidence": result.retrieval_confidence,
            "gaps": result.gaps,
            "answer": result.answer,
            "analysis_sections": analysis_sections,
            "overall_confidence": result.analysis.overall_confidence,
            "llm_model": result.analysis.llm_model,
            "llm_available": result.llm_available,
            "escalation_recommended": result.analysis.escalation_recommended,
            "duration_retrieval_s": result.duration_retrieval_s,
            "duration_llm_s": result.duration_llm_s,
            "duration_total_s": result.duration_total_s,
            "clarification_needed": result.clarification_needed,
            "clarification_question": result.clarification_question,
            "draft_type": result.draft.document_type if result.draft else None,
            "draft_text": result.draft.raw_text if result.draft else "",
            "draft_rendered": result.draft.rendered_text if result.draft else "",
            "draft_full_document": result.draft.full_document if result.draft else "",
            "reviewer_verdict": result.reviewer_verdict,
            "reviewer_action": result.reviewer_action,
            "warnings": result.reviewer_warnings,
            "history_id": history_id,
        }

        yield f"data: {json.dumps({'type': 'result', 'data': payload})}\n\n"

        # Salva in history con risposta completa (fire-and-forget)
        try:
            mongo = MongoClient.get()
            sections_all = result.analysis.analysis_sections or []
            await mongo.db["query_history"].insert_one({
                "_id":               history_id,
                "query":             req.query,
                "workspace":         req.workspace,
                "intent":            req.intent,
                "mode":              getattr(req, "mode", "standard"),
                "verdict":           result.reviewer_verdict,
                "confidence":        result.analysis.overall_confidence,
                "answer":            result.answer or "",
                "answer_summary":    (result.answer or "")[:300],
                "analysis_sections": [_section_to_dict(s) for s in sections_all],
                "analysis_fase_1":   [_section_to_dict(s) for s in (result.analysis_fase_1 or [])],
                "analysis_fase_2":   [_section_to_dict(s) for s in (result.analysis_fase_2 or [])],
                "sources":           [_source_to_dict(s) for s in result.sources],
                "sources_count":     len(result.sources),
                "duration_total_s":  result.duration_total_s,
                "created_at":        datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            logger.warning(f"[History] Salvataggio fallito: {e}")

        # Popola la Wiki se la risposta è approvata (fire-and-forget)
        # Il WikiMiddleware ascolta solo /query (non-streaming), quindi lo facciamo qui
        if result.reviewer_verdict in ("PASS", "WARN") and result.answer:
            engine = _get_wiki_engine()
            if engine is not None:
                try:
                    from aiura_legal.core.types import ResearchPacket, QueryIntent as _QI
                    packet = ResearchPacket(
                        query_original=req.query,
                        query_intent=_QI.NORMA_LOOKUP,
                        sources=result.sources,
                        retrieval_confidence=result.retrieval_confidence,
                    )
                    asyncio.create_task(
                        engine.file_response(req.query, result.answer, packet, req.workspace)
                    )
                except Exception as e:
                    logger.warning(f"[Wiki/stream] file_response fallito (non-fatal): {e}")

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# GET /history  — storico query per workspace
# GET /history/{entry_id} — dettaglio singola voce
# PATCH /history/{entry_id}/feedback — aggiunge valutazione
# ---------------------------------------------------------------------------

def _doc_to_history_entry(doc: dict) -> HistoryEntry:
    """Converte un documento MongoDB in HistoryEntry (usato da list e detail)."""
    return HistoryEntry(
        id=str(doc.get("_id", "")),
        query=doc.get("query", ""),
        workspace=doc.get("workspace", ""),
        intent=doc.get("intent", "fattispecie_analysis"),
        mode=doc.get("mode", "standard"),
        verdict=doc.get("verdict", "PASS"),
        confidence=doc.get("confidence", "LOW"),
        answer=doc.get("answer", doc.get("answer_summary", "")),
        answer_summary=doc.get("answer_summary", ""),
        analysis_sections=doc.get("analysis_sections", []),
        analysis_fase_1=doc.get("analysis_fase_1", []),
        analysis_fase_2=doc.get("analysis_fase_2", []),
        sources=doc.get("sources", []),
        sources_count=doc.get("sources_count", 0),
        duration_total_s=doc.get("duration_total_s", 0.0),
        created_at=doc.get("created_at", ""),
        feedback_rating=doc.get("feedback_rating"),
        feedback_tags=doc.get("feedback_tags", []),
        feedback_note=doc.get("feedback_note"),
        feedback_at=doc.get("feedback_at"),
    )


@app.get("/history", response_model=HistoryListResponse, tags=["history"])
async def list_history(
    workspace: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    feedback_only: bool = Query(default=False, description="Se True restituisce solo le voci con feedback"),
):
    """Restituisce la cronologia delle query per il workspace, ordinata per data desc."""
    mongo = MongoClient.get()
    skip = (page - 1) * limit
    query_filter: dict = {"workspace": workspace}
    if feedback_only:
        query_filter["feedback_at"] = {"$exists": True}

    try:
        cursor = mongo.db["query_history"].find(
            query_filter,
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit,
        )
        docs = await cursor.to_list(length=limit)
        total = await mongo.db["query_history"].count_documents(query_filter)
    except Exception as e:
        logger.error(f"[History] Errore lettura: {e}")
        return HistoryListResponse(entries=[], total=0, page=page, limit=limit)

    return HistoryListResponse(
        entries=[_doc_to_history_entry(doc) for doc in docs],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/history/{entry_id}", response_model=HistoryEntry, tags=["history"])
async def get_history_entry(entry_id: str):
    """Restituisce il dettaglio completo di una voce della cronologia."""
    mongo = MongoClient.get()
    doc = await mongo.db["query_history"].find_one({"_id": entry_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Voce non trovata")
    return _doc_to_history_entry(doc)


@app.patch("/history/{entry_id}/feedback", status_code=204, tags=["history"])
async def add_feedback(entry_id: str, body: FeedbackRequest):
    """
    Aggiunge una valutazione (stelle + tag + nota) a una voce della cronologia.
    Restituisce 409 se il feedback è già stato inviato (definitivo, non modificabile).
    """
    mongo = MongoClient.get()
    doc = await mongo.db["query_history"].find_one(
        {"_id": entry_id}, {"feedback_at": 1}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Voce non trovata")
    if doc.get("feedback_at"):
        raise HTTPException(status_code=409, detail="Feedback già inviato per questa risposta")

    await mongo.db["query_history"].update_one(
        {"_id": entry_id},
        {"$set": {
            "feedback_rating": body.rating,
            "feedback_tags":   body.tags,
            "feedback_note":   body.note,
            "feedback_at":     datetime.now(timezone.utc).isoformat(),
        }},
    )
    logger.info(f"[Feedback] entry={entry_id} rating={body.rating} tags={body.tags}")


# ---------------------------------------------------------------------------
# GET /wiki       — lista pagine wiki del workspace
# GET /wiki/{slug} — pagina singola
# ---------------------------------------------------------------------------

def _wiki_page_to_item(page) -> WikiPageItem:  # page: WikiPage dataclass
    last_upd = page.last_updated
    if hasattr(last_upd, "isoformat"):
        last_upd = last_upd.isoformat()
    return WikiPageItem(
        slug=page.slug,
        title=page.title,
        body_md=page.body_md,
        sources=page.sources,
        query_count=page.query_count,
        last_updated=str(last_upd),
        version=page.version,
        workspace=page.workspace,
    )


@app.get("/wiki", response_model=WikiListResponse, tags=["wiki"])
async def list_wiki_pages(
    workspace: str = Query(..., min_length=1),
    q: Optional[str] = Query(default=None, description="Filtro testo nel titolo"),
):
    """Elenca tutte le pagine wiki del workspace."""
    engine = _get_wiki_engine()
    if engine is None:
        return WikiListResponse(pages=[], total=0)

    pages = await engine._store.list_all(workspace)

    if q:
        q_lower = q.lower()
        pages = [p for p in pages if q_lower in p.title.lower() or q_lower in p.body_md.lower()]

    items = [_wiki_page_to_item(p) for p in pages]
    return WikiListResponse(pages=items, total=len(items))


@app.get("/wiki/{slug}", response_model=WikiPageItem, tags=["wiki"])
async def get_wiki_page(slug: str, workspace: str = Query(..., min_length=1)):
    """Recupera una pagina wiki per slug."""
    engine = _get_wiki_engine()
    if engine is None:
        raise HTTPException(status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE, detail="Wiki non disponibile")

    page = await engine._store.get_page(slug, workspace)
    if page is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Pagina '{slug}' non trovata")

    return _wiki_page_to_item(page)
