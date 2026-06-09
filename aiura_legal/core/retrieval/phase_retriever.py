"""
PhaseRetriever — retrieval mirato per fase nel Sequential IQRAC.

Wrapper leggero su HybridRetriever che esegue re-query focalizzate
per corpus specifico (normattiva o giurisprudenza), usando la query
distillata dalla fase precedente invece della query originale grezza.

Usato da SequentialAnalyst nelle fasi 2 (normativa) e 3 (giurisprudenza).

Filtri settore:
  AIURA_SETTORE_FILTER=1  → filtro hard (escludi chunk fuori settore, confidence >= 0.7)
  AIURA_SETTORE_SOFT=1    → filtro soft (più candidati, penalizza fuori settore ×0.5)
  Se filtro hard restituisce < 3 risultati → fallback automatico senza filtro settore.

Anti-allucinazione criminal law:
  Per query di diritto penale, applica automaticamente query augmentation
  e golden source injection (Art. 43 c.p., Cass. SS.UU. n.38343/2014 ThyssenKrupp).
"""
from __future__ import annotations

import os

from loguru import logger

from aiura_legal.core.retrieval.hybrid_retriever import (
    HybridRetriever,
    _WEIGHTS_NORMATIVA,
    _WEIGHTS_GIURISPRUDENZA,
    _WEIGHTS_DOTTRINA,
    _FILTER_NORMATIVA,
    _FILTER_GIURISPRUDENZA,
    _FILTER_DOTTRINA,
)
from aiura_legal.core.types import SearchResult

# ---------------------------------------------------------------------------
# Env flags
# ---------------------------------------------------------------------------
_SETTORE_FILTER_ENABLED: bool = os.getenv("AIURA_SETTORE_FILTER", "0") == "1"
_SETTORE_SOFT_ENABLED: bool = os.getenv("AIURA_SETTORE_SOFT", "0") == "1"

_SOFT_PENALTY: float = 0.5
_PRASSI_SCORE_FACTOR: float = 0.05
_HARD_FILTER_MIN_RESULTS: int = 3

_WEIGHTS_PRASSI = (0.60, 0.20, 0.15)
_FILTER_PRASSI = {"corpus": "prassi"}

# ---------------------------------------------------------------------------
# Criminal law detection — golden source injection
# ---------------------------------------------------------------------------

_STRONG_CRIMINAL_MARKERS: frozenset[str] = frozenset({
    "diritto penale", "penale sostanziale", "elemento soggettivo",
    "dolo eventuale", "colpa cosciente", "preterintenzione",
    "art. 43", "art.43", "codice penale", " c.p.",
    "reato doloso", "reato colposo", "illecito penale",
    "omicidio colposo", "lesioni colpose", "omicidio doloso",
    "thyssen", "thyssenkrupp", "38343", "ss.uu. penali",
    "tentativo punibile", "antigiuridicità", "imputabilità penale",
})

_WEAK_CRIMINAL_MARKERS: frozenset[str] = frozenset({
    "penale", "penali", "reato", "dolo", "colpa",
})

_ART43_TRIGGERS: frozenset[str] = frozenset({
    "elemento soggettivo", "dolo eventuale",
    "colpa cosciente", "preterintenzione", "art. 43", "art.43",
    "reato doloso", "reato colposo",
})

_THYSSEN_TRIGGERS: frozenset[str] = frozenset({
    "dolo eventuale", "colpa cosciente",
    "thyssen", "thyssenkrupp", "38343",
    "confine dolo colpa", "distinzione dolo colpa",
})


def _is_criminal_law_topic(text: str) -> bool:
    """
    Ritorna True se il testo descrive un problema di diritto penale sostanziale.

    Logica a due livelli:
    - Un marcatore forte → True
    - Due o più marcatori deboli → True
    - Solo "dolo" o solo "colpa" → False (potrebbero essere civili)
    """
    t = text.lower()
    if any(kw in t for kw in _STRONG_CRIMINAL_MARKERS):
        return True
    return sum(1 for kw in _WEAK_CRIMINAL_MARKERS if kw in t) >= 2


def _apply_soft_penalty(results: list[SearchResult], settore: str) -> list[SearchResult]:
    """Penalizza ×0.5 i chunk il cui settore_metadata non corrisponde (modalità soft)."""
    for r in results:
        chunk_settore = (r.metadata or {}).get("settore")
        if chunk_settore and chunk_settore != settore:
            r.score = r.score * _SOFT_PENALTY
    results.sort(key=lambda x: x.score, reverse=True)
    return results


def _merge_unique(
    primary: list[SearchResult],
    secondary: list[SearchResult],
    max_total: int,
) -> list[SearchResult]:
    """Unisce due liste di SearchResult rimuovendo duplicati per doc_id."""
    seen: set[str] = {r.doc_id for r in primary}
    merged = list(primary)
    for r in secondary:
        if r.doc_id not in seen:
            merged.append(r)
            seen.add(r.doc_id)
    return merged[:max_total]


class PhaseRetriever:
    """
    Esegue retrieval mirato per singola fase IQRAC.

    Filtri settore (opzionali):
      settore — etichetta settore giuridico (es. "penale")
      settore_confidence — float [0, 1]:
        >= 0.7 → hard filter (AIURA_SETTORE_FILTER=1 ha effetto)
        >= 0.4 → soft filter (AIURA_SETTORE_SOFT=1 ha effetto)
        < 0.4  → nessun filtro settore

    Anti-allucinazione criminal law:
      Per query di diritto penale, applica query augmentation e golden source
      injection (Art. 43 c.p., Cass. SS.UU. n.38343/2014 ThyssenKrupp).
    """

    def __init__(self, retriever: HybridRetriever) -> None:
        self._retriever = retriever

    # ------------------------------------------------------------------
    # Normativa — Fase 2
    # ------------------------------------------------------------------

    def retrieve_normativa(
        self,
        query: str,
        top_k: int = 6,
        settore: str | None = None,
        settore_confidence: float = 0.0,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=normattiva con pesi BM25-heavy.
        Usa la QUESTIONE distillata dalla Fase 1 come query.

        Per query di diritto penale: augmenta la query e inietta Art. 43 c.p.
        Se disponibile, aggiunge chunk da corpus=prassi con peso ridotto.
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query normativa vuota — skip")
            return []

        is_criminal = _is_criminal_law_topic(query)

        if is_criminal and "penale" not in query.lower()[:30]:
            query_effective = f"diritto penale elemento soggettivo {query}"
            logger.info(f"[PhaseRetriever] dominio penale rilevato — query augmentata: {query_effective[:100]!r}")
        else:
            query_effective = query

        logger.info(f"[PhaseRetriever] normativa re-query: {query_effective[:80]!r}")

        chunk_filter = self._effective_filter(
            base_filter=_FILTER_NORMATIVA,
            settore=settore,
            settore_confidence=settore_confidence,
            label="normativa",
        )
        use_soft = bool(settore and _SETTORE_SOFT_ENABLED and 0.4 <= settore_confidence < 0.7)
        top_k_retrieve = 20 if not use_soft else 40

        results = self._search_with_fallback(
            query=query_effective,
            weights=_WEIGHTS_NORMATIVA,
            chunk_filter=chunk_filter,
            base_filter=_FILTER_NORMATIVA,
            top_k_retrieve=top_k_retrieve,
            top_k_rerank=top_k,
            label="normativa",
        )

        if use_soft and settore:
            results = _apply_soft_penalty(results, settore)
            results = results[:top_k]

        if is_criminal:
            results = self._inject_art43_golden(query, results, top_k)

        prassi_results = self._retrieve_prassi(query=query_effective, settore=settore, settore_confidence=settore_confidence)
        if prassi_results:
            max_norm_score = max((r.score for r in results), default=1.0)
            for pr in prassi_results:
                pr.score = pr.score * _PRASSI_SCORE_FACTOR * max_norm_score
            results = _merge_unique(results, prassi_results, max_total=top_k + len(prassi_results))

        for r in results:
            r.source_layer = "normativa"
        logger.info(f"[PhaseRetriever] normativa: {len(results)} fonti")
        return results

    # ------------------------------------------------------------------
    # Giurisprudenza — Fase 3
    # ------------------------------------------------------------------

    def retrieve_giurisprudenza(
        self,
        query: str,
        top_k: int = 6,
        settore: str | None = None,
        settore_confidence: float = 0.0,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=giurisprudenza con pesi Vector-heavy.
        Usa QUALIFICAZIONE+QUESTIONE dalla Fase 1 come query.

        Per query su dolo eventuale vs colpa cosciente: inietta ThyssenKrupp.
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query giurisprudenza vuota — skip")
            return []

        is_criminal = _is_criminal_law_topic(query)

        if is_criminal and "penale" not in query.lower()[:30]:
            query_effective = f"diritto penale {query}"
        else:
            query_effective = query

        logger.info(f"[PhaseRetriever] giurisprudenza re-query: {query_effective[:80]!r}")

        chunk_filter = self._effective_filter(
            base_filter=_FILTER_GIURISPRUDENZA,
            settore=settore,
            settore_confidence=settore_confidence,
            label="giurisprudenza",
        )
        use_soft = bool(settore and _SETTORE_SOFT_ENABLED and 0.4 <= settore_confidence < 0.7)
        top_k_retrieve = 20 if not use_soft else 40

        results = self._search_with_fallback(
            query=query_effective,
            weights=_WEIGHTS_GIURISPRUDENZA,
            chunk_filter=chunk_filter,
            base_filter=_FILTER_GIURISPRUDENZA,
            top_k_retrieve=top_k_retrieve,
            top_k_rerank=top_k,
            label="giurisprudenza",
        )

        if use_soft and settore:
            results = _apply_soft_penalty(results, settore)
            results = results[:top_k]

        if is_criminal:
            results = self._inject_thyssen_golden(query, results, top_k)

        for r in results:
            r.source_layer = "giurisprudenza"
        logger.info(f"[PhaseRetriever] giurisprudenza: {len(results)} fonti")
        return results

    # ------------------------------------------------------------------
    # Dottrina — Fase 2
    # ------------------------------------------------------------------

    def retrieve_dottrina(
        self,
        query: str,
        top_k: int = 4,
        settore: str | None = None,
        settore_confidence: float = 0.0,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=dottrina con pesi bilanciati BM25+Vector.
        Ritorna lista vuota (non errore) se nessun documento dottrinale è indicizzato.
        """
        if not query.strip():
            return []

        logger.info(f"[PhaseRetriever] dottrina re-query: {query[:80]!r}")

        chunk_filter = self._effective_filter(
            base_filter=_FILTER_DOTTRINA,
            settore=settore,
            settore_confidence=settore_confidence,
            label="dottrina",
        )
        use_soft = bool(settore and _SETTORE_SOFT_ENABLED and 0.4 <= settore_confidence < 0.7)
        top_k_retrieve = 10 if not use_soft else 20

        results = self._search_with_fallback(
            query=query,
            weights=_WEIGHTS_DOTTRINA,
            chunk_filter=chunk_filter,
            base_filter=_FILTER_DOTTRINA,
            top_k_retrieve=top_k_retrieve,
            top_k_rerank=top_k,
            label="dottrina",
        )

        if use_soft and settore:
            results = _apply_soft_penalty(results, settore)
            results = results[:top_k]

        for r in results:
            r.source_layer = "dottrina"
        logger.info(f"[PhaseRetriever] dottrina: {len(results)} fonti")
        return results

    # ------------------------------------------------------------------
    # Prassi — supplementare a normativa
    # ------------------------------------------------------------------

    def _retrieve_prassi(
        self,
        query: str,
        settore: str | None = None,
        settore_confidence: float = 0.0,
        top_k: int = 3,
    ) -> list[SearchResult]:
        """Corpus prassi — graceful skip se assente."""
        try:
            chunk_filter = self._effective_filter(
                base_filter=_FILTER_PRASSI,
                settore=settore,
                settore_confidence=settore_confidence,
                label="prassi",
            )
            results = self._retriever._search_round(
                query=query,
                weights=_WEIGHTS_PRASSI,
                chunk_filter=chunk_filter,
                valid_on=None,
                top_k_retrieve=top_k * 3,
                top_k_rerank=top_k,
            )
            for r in results:
                r.source_layer = "prassi"
            if results:
                logger.info(f"[PhaseRetriever] prassi: {len(results)} fonti")
            return results
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"[PhaseRetriever] prassi skip: {exc}")
            return []

    # ------------------------------------------------------------------
    # Golden source injection — criminal law
    # ------------------------------------------------------------------

    def _inject_art43_golden(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """Inietta Art. 43 c.p. come golden source per query su elemento soggettivo."""
        t = query.lower()
        if not any(kw in t for kw in _ART43_TRIGGERS):
            return results

        def _is_art43(r: SearchResult) -> bool:
            meta = r.metadata or {}
            art = (meta.get("articolo_num") or meta.get("articolo") or "").lower()
            fonte = (meta.get("fonte") or "").lower()
            titolo = (meta.get("titolo") or r.snippet or "").lower()
            return (
                ("43" in art and ("penale" in fonte or "penale" in titolo))
                or "elemento soggettivo" in titolo
                or ("art. 43" in titolo and "penale" in titolo)
            )

        if any(_is_art43(r) for r in results):
            logger.debug("[PhaseRetriever] Art. 43 c.p. già presente — skip golden inject")
            return results

        golden_query = (
            "art 43 codice penale elemento soggettivo dolo colpa "
            "preterintenzione delitto doloso colposo"
        )
        logger.info("[PhaseRetriever] Art. 43 c.p. assente — ricerca golden source...")
        golden = self._retriever._search_round(
            query=golden_query,
            weights=_WEIGHTS_NORMATIVA,
            chunk_filter=_FILTER_NORMATIVA,
            valid_on=None,
            top_k_retrieve=8,
            top_k_rerank=2,
        )
        for r in golden:
            r.source_layer = "normativa"

        if not golden:
            logger.warning("[PhaseRetriever] Art. 43 c.p. non trovato — verificare corpus normattiva")
            return results

        logger.info(f"[PhaseRetriever] iniettati {len(golden)} golden source (Art. 43 c.p.)")
        existing_ids = {r.source_id for r in results}
        new_golden = [r for r in golden if r.source_id not in existing_ids]
        return (new_golden + results)[: top_k + len(new_golden)]

    def _inject_thyssen_golden(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """Inietta Cass. SS.UU. n.38343/2014 (ThyssenKrupp) per query su dolo eventuale."""
        t = query.lower()
        if not any(kw in t for kw in _THYSSEN_TRIGGERS):
            return results

        def _is_thyssen(r: SearchResult) -> bool:
            meta = r.metadata or {}
            n = str(meta.get("numero") or "")
            s = r.snippet.lower()
            return (
                "38343" in n
                or "thyssen" in s
                or "38343" in s
                or ("sezioni unite" in s and ("dolo eventuale" in s or "colpa cosciente" in s))
            )

        if any(_is_thyssen(r) for r in results):
            logger.debug("[PhaseRetriever] ThyssenKrupp già presente — skip golden inject")
            return results

        golden_query = (
            "Cassazione Sezioni Unite penali 38343 2014 ThyssenKrupp "
            "dolo eventuale colpa cosciente criteri diagnostici"
        )
        logger.info("[PhaseRetriever] ThyssenKrupp assente — ricerca golden source...")
        golden = self._retriever._search_round(
            query=golden_query,
            weights=_WEIGHTS_GIURISPRUDENZA,
            chunk_filter=_FILTER_GIURISPRUDENZA,
            valid_on=None,
            top_k_retrieve=8,
            top_k_rerank=2,
        )
        for r in golden:
            r.source_layer = "giurisprudenza"

        if not golden:
            logger.info("[PhaseRetriever] ThyssenKrupp n.38343/2014 non nel DB — caricarla con /jurisprudence/upload")
            return results

        logger.info(f"[PhaseRetriever] iniettati {len(golden)} golden source (Cass. SS.UU. 38343/2014)")
        existing_ids = {r.source_id for r in results}
        new_golden = [r for r in golden if r.source_id not in existing_ids]
        return (new_golden + results)[: top_k + len(new_golden)]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _effective_filter(
        self,
        base_filter: dict,
        settore: str | None,
        settore_confidence: float,
        label: str,
    ) -> dict:
        """Calcola il filtro effettivo tenendo conto di settore_confidence."""
        if not settore:
            return base_filter

        if settore_confidence >= 0.7 and _SETTORE_FILTER_ENABLED:
            logger.debug(f"[PhaseRetriever] {label}: filtro hard settore={settore!r}")
            return {**base_filter, "settore": settore}

        if settore_confidence >= 0.4 and _SETTORE_SOFT_ENABLED:
            logger.debug(f"[PhaseRetriever] {label}: filtro soft (penalità post-hoc) settore={settore!r}")

        return base_filter

    def _search_with_fallback(
        self,
        query: str,
        weights: tuple[float, float, float],
        chunk_filter: dict,
        base_filter: dict,
        top_k_retrieve: int,
        top_k_rerank: int,
        label: str,
    ) -> list[SearchResult]:
        """
        Esegue _search_round con chunk_filter.
        Se hard filter restituisce < _HARD_FILTER_MIN_RESULTS, fallback senza filtro settore.
        """
        results = self._retriever._search_round(
            query=query,
            weights=weights,
            chunk_filter=chunk_filter,
            valid_on=None,
            top_k_retrieve=top_k_retrieve,
            top_k_rerank=top_k_rerank,
        )

        if chunk_filter != base_filter and len(results) < _HARD_FILTER_MIN_RESULTS:
            logger.warning(
                f"[PhaseRetriever] {label}: hard filter → {len(results)} risultati "
                f"(< {_HARD_FILTER_MIN_RESULTS}), fallback senza filtro settore"
            )
            results = self._retriever._search_round(
                query=query,
                weights=weights,
                chunk_filter=base_filter,
                valid_on=None,
                top_k_retrieve=top_k_retrieve,
                top_k_rerank=top_k_rerank,
            )

        return results
