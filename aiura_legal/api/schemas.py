"""
Pydantic schemas per request/response API.
"""
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# /query — Request
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    workspace: str = Field(..., min_length=1, max_length=100)
    intent: str = Field(
        default="fattispecie_analysis",
        description=(
            "norma_lookup | giurisprudenza_search | fattispecie_analysis | "
            "precedente_interno | norma_evolution | rischio_contrattuale"
        ),
    )
    valid_on: Optional[date] = Field(
        default=None,
        description="Data di riferimento per il filtro vigenza (ISO 8601)",
    )
    top_k: int = Field(default=10, ge=1, le=20)
    chunk_filter: Optional[dict] = Field(
        default=None,
        description=(
            "Filtro subset chunk opzionale. "
            "Es: {'corpus': 'normattiva'} oppure {'fonte': 'codice_civile'}"
        ),
    )
    # ── S1 Clarifier ────────────────────────────────────────────────────
    clarification_turn: int = Field(
        default=0,
        ge=0,
        description=(
            "Turno di chiarimento S1. "
            "0 = prima query, 1 = seconda query con risposta utente, "
            "≥2 = procedi sempre con defaults"
        ),
    )
    clarification_context: Optional[str] = Field(
        default=None,
        description="Risposta dell'utente alla domanda di chiarimento del turno precedente.",
    )
    # ── Mode ────────────────────────────────────────────────────────────
    mode: str = Field(
        default="standard",
        pattern="^(standard|deep)$",
        description=(
            "standard: singola chiamata LLM (9 step in una volta). "
            "deep: due chiamate LLM sequenziali — Fase 1 normativa (step 1-5), "
            "Fase 2 giurisprudenziale (step 6-9). Risposte più verbose."
        ),
    )
    # ── S4 Drafter ──────────────────────────────────────────────────────
    draft_type: Optional[str] = Field(
        default=None,
        description=(
            "Tipo documento da generare con S4 Drafter. "
            "Valori: parere | citazione | comparsa | diffida | nota | contratto. "
            "Se None (default) S4 viene saltato."
        ),
    )


# ---------------------------------------------------------------------------
# /query — Response
# ---------------------------------------------------------------------------

class SourceItem(BaseModel):
    rank: int
    doc_id: str
    source_id: str
    score: float
    snippet: str
    retrieval_method: str
    metadata: dict = Field(default_factory=dict)


class AnalysisSectionItem(BaseModel):
    """Una sezione CoT dell'analisi S3."""
    step: str
    content: str
    citations: list[dict] = Field(default_factory=list)


class QueryResponse(BaseModel):
    # ── Input echo ────────────────────────────────────────────────────
    query: str
    workspace: str
    intent: str

    # ── S2 Retrieval ──────────────────────────────────────────────────
    sources: list[SourceItem]
    retrieval_confidence: str          # HIGH | MEDIUM | LOW
    gaps: list[str]

    # ── S3 Analysis (nuovo in 1B) ─────────────────────────────────────
    answer: str = ""
    """Testo generato da S3 Analyst. Vuoto se Ollama non disponibile."""
    analysis_sections: list[AnalysisSectionItem] = Field(default_factory=list)
    """Sezioni CoT strutturate (QUALIFICAZIONE, NORMA APPLICABILE, …)."""
    overall_confidence: str = "LOW"
    """Confidenza S3: HIGH | MEDIUM | LOW."""
    llm_model: str = ""
    """Modello Ollama usato da S3."""
    llm_available: bool = False
    """True se S3 ha prodotto una risposta."""
    escalation_recommended: bool = False
    """True se S3 suggerisce escalation al modello 72B."""

    # ── Timing ────────────────────────────────────────────────────────
    duration_retrieval_s: float = 0.0
    duration_llm_s: float = 0.0
    duration_total_s: float = 0.0

    # ── S1 Clarifier ──────────────────────────────────────────────────
    clarification_needed: bool = False
    """True se S1 ha richiesto chiarimento prima del retrieval."""
    clarification_question: Optional[str] = None
    """Domanda da porre all'utente (presente solo se clarification_needed=True)."""

    # ── S4 Drafter (opzionale) ────────────────────────────────────────
    draft_type: Optional[str] = None
    """Tipo documento generato da S4 (presente solo se draft_type era nella request)."""
    draft_text: str = ""
    """Testo documento con marker {{cite:}} non ancora risolti."""
    draft_rendered: str = ""
    """Testo documento con citazioni formali risolte."""
    draft_full_document: str = ""
    """Documento completo: testo renderizzato + disclaimer AI."""

    # ── S3 Deep mode (opzionale) ──────────────────────────────────────
    mode: str = "standard"
    """Modalità analisi usata: standard | deep."""
    analysis_fase_1: list[AnalysisSectionItem] = Field(default_factory=list)
    """Sezioni Fase 1 (step 1-5, solo normativa). Popolato solo se mode=deep."""
    analysis_fase_2: list[AnalysisSectionItem] = Field(default_factory=list)
    """Sezioni Fase 2 (step 6-9, giurisprudenza+conclusione). Popolato solo se mode=deep."""
    fase_2_available: bool = False
    """True se Fase 2 completata. False = risposta parziale (solo Fase 1)."""

    # ── S5 Review ─────────────────────────────────────────────────────
    reviewer_verdict: str              # PASS | WARN | FAIL
    reviewer_action: str               # DELIVER | RE_RETRIEVAL | BLOCK
    warnings: list[str]

    # ── History ───────────────────────────────────────────────────────
    history_id: Optional[str] = None
    """ID del documento query_history appena creato. Usato dal frontend per il feedback."""


# ---------------------------------------------------------------------------
# /ingest
# ---------------------------------------------------------------------------

class IngestResponse(BaseModel):
    document_id: str
    filename: str
    workspace: str
    status: str                        # ok | error
    text_length: int
    chunk_count: int
    pii_stats: dict
    duration_s: float
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# /workspace
# ---------------------------------------------------------------------------

class WorkspaceInfo(BaseModel):
    name: str
    doc_count: int
    chunk_count: int
    pending_jobs: int
    has_bm25_index: bool
    has_vector_index: bool


class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceInfo]


# ---------------------------------------------------------------------------
# /annotate  — Workflow B (Document Intelligence)
# ---------------------------------------------------------------------------

class AnnotationItem(BaseModel):
    section: str
    annotation_type: str
    text: str
    level: str = ""
    source_citations: list[str] = Field(default_factory=list)
    suggested_replacement: str = ""


class AnnotateRequest(BaseModel):
    workspace: str = Field(default="default", min_length=1, max_length=100)
    chunk_filter: Optional[dict] = Field(
        default=None,
        description="Filtro subset chunk per il retrieval delle fonti.",
    )
    max_sections: int = Field(
        default=10, ge=1, le=50,
        description="Numero massimo di sezioni del documento da annotare.",
    )


class AnnotateJobResponse(BaseModel):
    """Risposta 202 Accepted — annotazione avviata in background."""
    document_id: str
    status: str = "queued"             # queued | completed | error
    message: str = ""


class AnnotateResultResponse(BaseModel):
    """Risultato completo annotazione (GET /annotate/{document_id})."""
    document_id: str
    workspace: str
    status: str                         # queued | completed | error
    annotations: list[AnnotationItem] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    overall_risk: str = "NESSUNO"
    sections_processed: int = 0
    llm_model: str = ""
    duration_s: float = 0.0
    parse_ok: bool = False
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# /folders
# ---------------------------------------------------------------------------

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    workspace: str = Field(..., min_length=1, max_length=100)


class FolderRename(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class FolderItem(BaseModel):
    id: str
    name: str
    workspace: str
    doc_count: int = 0
    created_at: str


class FolderListResponse(BaseModel):
    folders: list[FolderItem]


# ---------------------------------------------------------------------------
# /documents
# ---------------------------------------------------------------------------

class DocumentItem(BaseModel):
    id: str
    filename: str
    workspace: str
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    status: str                         # ready | processing | error
    text_length: int = 0
    chunk_count: int = 0
    pii_stats: dict = Field(default_factory=dict)
    created_at: str
    error: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentItem]
    total: int


class DocumentMoveRequest(BaseModel):
    folder_id: Optional[str] = None     # None = rimuovi dalla cartella


# ---------------------------------------------------------------------------
# /history
# ---------------------------------------------------------------------------

#: Tag validi per il feedback (usati anche nel validator FeedbackRequest)
FEEDBACK_ALLOWED_TAGS: frozenset[str] = frozenset({
    "Utile", "Parziale", "Errata",
    "Da approfondire", "Citazioni corrette", "Citazioni errate",
})


class HistoryEntry(BaseModel):
    id: str
    query: str
    workspace: str
    intent: str = "fattispecie_analysis"
    mode: str = "standard"
    verdict: str                        # PASS | WARN | FAIL | RE_RETRIEVAL
    confidence: str = "LOW"
    # Risposta completa (default vuoti per retrocompatibilità con doc vecchi)
    answer: str = ""
    answer_summary: str = ""            # mantenuto per retrocompatibilità
    analysis_sections: list[dict] = Field(default_factory=list)
    analysis_fase_1:   list[dict] = Field(default_factory=list)
    analysis_fase_2:   list[dict] = Field(default_factory=list)
    sources:           list[dict] = Field(default_factory=list)
    sources_count: int = 0
    duration_total_s: float = 0.0
    created_at: str                     # ISO 8601
    # Feedback (opzionali — presenti solo dopo PATCH /history/{id}/feedback)
    feedback_rating: Optional[int] = None
    feedback_tags:   list[str] = Field(default_factory=list)
    feedback_note:   Optional[str] = None
    feedback_at:     Optional[str] = None


class HistoryListResponse(BaseModel):
    entries: list[HistoryEntry]
    total: int
    page: int
    limit: int


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Valutazione da 1 a 5 stelle")
    tags:   list[str] = Field(default_factory=list, description="Tag qualitativi")
    note:   Optional[str] = Field(default=None, max_length=500, description="Nota libera (max 500 caratteri)")

    @field_validator("tags")
    @classmethod
    def tags_must_be_allowed(cls, v: list[str]) -> list[str]:
        invalid = set(v) - FEEDBACK_ALLOWED_TAGS
        if invalid:
            raise ValueError(f"Tag non ammessi: {invalid}. Validi: {sorted(FEEDBACK_ALLOWED_TAGS)}")
        # dedup preservando l'ordine di inserimento
        return list(dict.fromkeys(v))


# ---------------------------------------------------------------------------
# /wiki
# ---------------------------------------------------------------------------

class WikiPageItem(BaseModel):
    slug: str
    title: str
    body_md: str
    sources: list[str] = Field(default_factory=list)
    query_count: int = 0
    last_updated: str = ""
    version: int = 0
    workspace: str = "default"


class WikiListResponse(BaseModel):
    pages: list[WikiPageItem]
    total: int


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str                        # ok | degraded | error
    mongodb: bool
    ollama: bool
    version: str = "0.1.0.dev0"
