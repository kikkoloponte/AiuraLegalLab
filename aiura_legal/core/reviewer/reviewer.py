"""
Citation Reviewer [S5] — interamente rule-based, zero LLM.
Verifica che ogni source_id nella risposta sia nel Research Packet.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date
from loguru import logger
from aiura_legal.core.types import ResearchPacket
from aiura_legal.core.graph.retriever import GraphRetriever

# Identificatori di sentenze giurisprudenziali (sha256[:16] hex)
_SENTENZA_ID_RE = re.compile(r"\b[0-9a-f]{16}\b")


# ---------------------------------------------------------------------------
# Pattern per estrarre citazioni da testo legale
# ---------------------------------------------------------------------------

_CITATION_PATTERNS = [
    r"\bCC_ART_\d+\b",
    r"\bCP_ART_\d+\b",
    r"\bCPP_ART_\d+\b",
    r"\bCASS_(?:PEN|CIV|SS_UU)_\d{4}_\d+\b",
    r"\bCEDU_\w+_\d{4}\b",
    r"\bCOST_\d{4}_\d+\b",
    r"\bDLGS_\d+_\d{4}_ART_\d+\b",
    # URN Normattiva (formato reale dei source_id nel sistema)
    r"urn:nir:[^\s,\]\"\\']+",
]

_CITATION_RE = re.compile("|".join(_CITATION_PATTERNS), re.IGNORECASE)

# Stato norma che causa FAIL CRITICO
_UNCONSTITUTIONAL_STATUS = "INCOSTITUZIONALE"


@dataclass
class ReviewResult:
    verdict: str  # "PASS" | "FAIL" | "WARN"
    checks: dict[str, str] = field(default_factory=dict)
    ungrounded_citations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    action: str = "DELIVER"  # "DELIVER" | "RE_RETRIEVAL" | "BLOCK"


class CitationReviewer:
    """
    Gatekeeper del Citation Contract.
    Verifica meccanica senza chiamate LLM.

    Args:
        graph: GraphRetriever opzionale per il check conflict_disclosure.
               Se None (default) il check è sempre PASS (backward compatible).
    """

    def __init__(
        self,
        graph: GraphRetriever | None = None,
        jurisprudence_graph=None,
        normattiva_urns: set[str] | None = None,
    ) -> None:
        self._graph = graph
        self._jgraph = jurisprudence_graph
        self._normattiva_urns: set[str] = normattiva_urns or set()

    def verify(
        self,
        response_text: str,
        research_packet: ResearchPacket,
        reference_date: date | None = None,
    ) -> ReviewResult:
        """
        Esegue tutti i check in ordine.
        Ritorna BLOCK al primo FAIL CRITICO, altrimenti aggrega WARN.
        """
        checks: dict[str, str] = {}
        warnings: list[str] = []
        ungrounded: list[str] = []

        # Set di source_id presenti nel Packet (uppercase per citazioni normative)
        packet_ids = {s.source_id.upper() for s in research_packet.sources}
        # Set di doc_id presenti nel Packet (case-sensitive per sentenze hex)
        packet_doc_ids = {s.doc_id for s in research_packet.sources}

        # Citazioni estratte dalla risposta
        cited = self.extract_citations(response_text)

        # 1. Citation Grounding
        for cit in cited:
            if cit.upper() not in packet_ids:
                ungrounded.append(cit)

        if ungrounded:
            checks["citation_grounding"] = "FAIL"
        else:
            checks["citation_grounding"] = "PASS"

        # 2. Vigenza temporale
        if reference_date:
            expired = []
            for src in research_packet.sources:
                if src.source_id.upper() in {c.upper() for c in cited}:
                    valid_to = src.metadata.get("valid_to", "")
                    if valid_to and valid_to < str(reference_date):
                        expired.append(src.source_id)
            if expired:
                checks["temporal_validity"] = "WARN"
                warnings.append(f"Norme scadute citate: {expired}")
            else:
                checks["temporal_validity"] = "PASS"
        else:
            checks["temporal_validity"] = "PASS"

        # 3. Contrasti/abrogazioni non dichiarati (via GraphRetriever)
        if self._graph and self._graph.is_available and cited:
            graph_conflicts = self._graph.get_conflicts(list({c.upper() for c in cited}))
            if graph_conflicts:
                checks["conflict_disclosure"] = "WARN"
                conflict_summary = "; ".join(f"{a}↔{b}({t})" for a, b, t in graph_conflicts[:3])
                warnings.append(f"Norme in conflitto/abrogazione: {conflict_summary}")
            else:
                checks["conflict_disclosure"] = "PASS"
        else:
            checks["conflict_disclosure"] = "PASS"

        # 4. Grounding giurisprudenziale
        sent_ids = _SENTENZA_ID_RE.findall(response_text)
        sent_ungrounded = [sid for sid in sent_ids if sid not in packet_doc_ids]
        if sent_ungrounded:
            ungrounded.extend(sent_ungrounded)
            checks["jurisprudence_grounding"] = "FAIL"
        else:
            checks["jurisprudence_grounding"] = "PASS"

        # 5. Link norma↔sentenza tramite grafo giurisprudenziale
        if self._jgraph is not None and self._normattiva_urns:
            for sid in sent_ids:
                if sid in packet_doc_ids and self._jgraph.sentenza_exists(sid):
                    for urn in self._jgraph.get_norme_per_sentenza(sid):
                        if urn not in self._normattiva_urns:
                            warnings.append(
                                f"Norma {urn} (citata in sentenza {sid}) assente in normattiva_docs"
                            )
                            checks[urn] = "NORMA_NOT_IN_NORMATTIVA"

        # 6. Incostituzionalità — FAIL CRITICO
        unconstitutional = []
        for src in research_packet.sources:
            if src.source_id.upper() in {c.upper() for c in cited}:
                status = src.metadata.get("status", "")
                if status.upper() == _UNCONSTITUTIONAL_STATUS:
                    unconstitutional.append(src.source_id)

        if unconstitutional:
            checks["constitutionality"] = "FAIL_CRITICO"
            logger.critical(
                f"Norma incostituzionale citata come vigente: {unconstitutional}"
            )
            return ReviewResult(
                verdict="FAIL",
                checks=checks,
                ungrounded_citations=ungrounded,
                warnings=[f"CRITICO: norma incostituzionale: {unconstitutional}"],
                action="BLOCK",
            )
        else:
            checks["constitutionality"] = "PASS"

        # Determina verdict finale
        any_grounding_fail = (
            checks["citation_grounding"] == "FAIL"
            or checks.get("jurisprudence_grounding") == "FAIL"
        )
        if any_grounding_fail:
            verdict = "FAIL"
            action = "RE_RETRIEVAL"
        elif warnings:
            verdict = "WARN"
            action = "DELIVER"
        else:
            verdict = "PASS"
            action = "DELIVER"

        return ReviewResult(
            verdict=verdict,
            checks=checks,
            ungrounded_citations=ungrounded,
            warnings=warnings,
            action=action,
        )

    def extract_citations(self, text: str) -> list[str]:
        """
        Estrae tutti gli identificatori di citazione dal testo.
        Rimuove la punteggiatura terminale di frase dai match URN
        (es. "urn:...~art1218." → "urn:...~art1218").
        """
        raw = _CITATION_RE.findall(text)
        cleaned = [c.rstrip(".,;:)]}'\"") for c in raw]
        return list(set(cleaned))
