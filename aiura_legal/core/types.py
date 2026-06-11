"""
Tipi condivisi — AiUra LegalLab.
Solo dataclass e enum, zero logica.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class QueryIntent(Enum):
    NORMA_LOOKUP = "norma_lookup"
    GIURISPRUDENZA_SEARCH = "giurisprudenza_search"
    FATTISPECIE_ANALYSIS = "fattispecie_analysis"
    PRECEDENTE_INTERNO = "precedente_interno"
    NORMA_EVOLUTION = "norma_evolution"
    RISCHIO_CONTRATTUALE = "rischio_contrattuale"


@dataclass
class Document:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)
    source_id: str = ""
    source_authority: str = ""
    is_anonymized: bool = False
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


@dataclass
class SearchResult:
    doc_id: str
    score: float
    snippet: str
    metadata: dict = field(default_factory=dict)
    source_id: str = ""
    retrieval_method: str = ""
    source_layer: str = "normativa"  # "normativa" | "giurisprudenza" | "dottrina" | "studio"
    full_text: str = ""              # testo completo da MongoDB (source_texts) — "" = usa snippet


@dataclass
class ResearchPacket:
    query_original: str
    query_intent: QueryIntent
    sources: list[SearchResult] = field(default_factory=list)
    retrieval_confidence: str = "LOW"
    gaps: list[str] = field(default_factory=list)
    kb_version: dict = field(default_factory=dict)
