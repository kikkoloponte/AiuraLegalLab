"""
Pydantic models per MongoDB.
Schema LegalAgentLab: database=legal_lab, collection=normattiva_docs, text field=text.
"""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocType(str, Enum):
    LEGGE = "legge"
    DECRETO_LEGISLATIVO = "decreto_legislativo"
    SENTENZA_CASSAZIONE = "sentenza_cassazione"
    SENTENZA_CORTE_COST = "sentenza_corte_cost"
    SENTENZA_CEDU = "sentenza_cedu"
    CONTRATTO = "contratto"
    ATTO_GIUDIZIARIO = "atto_giudiziario"
    NOTA = "nota"
    ALTRO = "altro"


class LegalDocument(BaseModel):
    """
    Documento legale in MongoDB (AiUraLegalLab).
    Il campo testo è 'text', allineato a LegalAgentLab (normattiva_docs.text).
    """
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    title: str = ""
    text: str = ""             # campo testo — allineato a LegalAgentLab
    doc_type: str = "altro"    # valori: legge, decreto_legislativo, sentenza_*, contratto...
    source: str = ""
    source_id: str = ""        # URN, CELEX, numero sentenza (cf. normattiva_docs.urn)
    workspace: str = ""
    document_date: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    # Status pipeline AiUra (non presente in LegalAgentLab)
    is_anonymized: bool = False
    is_chunked: bool = False
    is_indexed_bm25: bool = False
    is_indexed_vector: bool = False
    migrated_from_lab: bool = False
    lab_original_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


class Chunk(BaseModel):
    """Chunk di testo — unità base per BM25 e vector search."""
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    document_id: str
    chunk_index: int
    text: str
    embedding: Optional[list[float]] = None
    embedding_model: Optional[str] = None
    doc_type: str = ""
    source: str = ""
    source_id: str = ""
    workspace: str = ""
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    token_count: int = 0
    # Tipizzazione subset retrieval (SPEC §16)
    corpus:     str = "studio"     # "normattiva" | "studio" | "giurisprudenza" | "dottrina"
    fonte:      str = "altro"      # codice_civile | legge | dlgs | dl | dpr | rd | dm | altro
    testo_tipo: str = "normativo"  # "normativo" | "formula"
    # Settore giuridico — lista per supportare chunk multi-settore (es. procedura penale)
    # Valori: "penale" | "civile" | "amministrativo" | "lavoro" | "processuale" | "costituzionale" | "altro"
    # Campo opzionale: chunk senza settore non vengono esclusi dal retrieval
    settore:    list[str] = Field(default_factory=list)
    # Metadati titolo articolo (normattiva) e dottrina
    titolo_articolo:    Optional[str] = None   # propagato da normattiva_docs.titolo_articolo
    titolo_doc:         Optional[str] = None   # titolo documento/articolo (dottrina)
    autore:             Optional[str] = None   # autore/i (dottrina)
    anno_pubblicazione: Optional[int] = None   # anno pubblicazione (dottrina)
    rivista:            Optional[str] = None   # slug rivista (dottrina)
    fascicolo:          Optional[str] = None   # es. "10/2017" (dottrina)
    # Chunk Schema v3
    sommario:            Optional[str] = None   # breve abstract del chunk (40-60 tok)
    settore_confidence:  float = 0.0            # confidenza classificazione settore


class IngestionJob(BaseModel):
    """Job nella coda di ingestione asincrona (Tier 1 e Tier 2)."""
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    document_id: str
    job_type: str       # "CHUNK"|"ANONYMIZE"|"EMBED"|"INDEX_BM25"|"GRAPH"
    tier: int = 1
    status: str = "pending"  # "pending"|"processing"|"done"|"failed"
    priority: int = 5
    created_at: datetime = Field(default_factory=_utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
