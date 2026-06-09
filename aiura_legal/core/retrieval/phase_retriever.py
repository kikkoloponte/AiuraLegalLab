"""
PhaseRetriever — retrieval mirato per fase nel Sequential IQRAC.

Wrapper leggero su HybridRetriever che esegue re-query focalizzate
per corpus specifico (normattiva o giurisprudenza), usando la query
distillata dalla fase precedente invece della query originale grezza.

Usato da SequentialAnalyst nelle fasi 2 (normativa) e 3 (giurisprudenza).

Filtri settore:
  AIURA_SETTORE_FILTER=1  → filtro hard (escludi chunk fuori settore)
  AIURA_SETTORE_SOFT=1    → filtro soft (più candidati, penalizza fuori settore ×0.5)
  Se filtro hard restituisce < 3 risultati → fallback automatico senza filtro settore.
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

# Peso di penalità per chunk fuori settore in modalità soft
_SOFT_PENALTY: float = 0.5

# Contributo massimo del corpus prassi al pool RRF (5 %)
_PRASSI_SCORE_FACTOR: float = 0.05

# Pesi per il corpus prassi (stesso profilo normativa ma contribuisce poco)
_WEIGHTS_PRASSI = (0.60, 0.20, 0.15)
_FILTER_PRASSI = {"corpus": "prassi"}

# Soglia fallback: se hard-filter restituisce < N risultati, riprova senza filtro
_HARD_FILTER_MIN_RESULTS: int = 3


def _build_settore_filter(base_filter: dict, settore: str | None) -> dict | None:
    """
    Costruisce il filtro chunk includendo il settore se richiesto.

    Logica:
    - AIURA_SETTORE_FILTER=1 (hard): filtro corpus + settore
    - AIURA_SETTORE_SOFT=1 (soft):  solo filtro corpus (la penalità viene applicata in post)
    - default: solo filtro corpus
    """
    if settore and _SETTORE_FILTER_ENABLED:
        return {**base_filter, "settore": settore}
    return base_filter


def _apply_soft_penalty(results: list[SearchResult], settore: str) -> list[SearchResult]:
    """
    Modalità soft: penalizza ×0.5 i chunk il cui settore_metadata non corrisponde.
    Il campo settore è in SearchResult.metadata (se presente).
    """
    for r in results:
        chunk_settore = (r.metadata or {}).get("settore")
        if chunk_settore and chunk_settore != settore:
            r.score = r.score * _SOFT_PENALTY
    # Re-sort per score dopo penalità
    results.sort(key=lambda x: x.score, reverse=True)
    return results


class PhaseRetriever:
    """
    Esegue retrieval mirato per singola fase IQRAC.

    Le query di fase sono più precise della query originale:
    vengono estratte dall'output della Fase 1 (QUESTIONE, QUALIFICAZIONE)
    e usate per recuperare fonti più pertinenti.

    Filtri settore (opzionali):
      settore — etichetta settore giuridico (es. "diritto_civile")
      settore_confidence — float [0, 1] che guida hard/soft/no filter:
        >= 0.7 → hard filter (AIURA_SETTORE_FILTER=1 ha effetto)
        >= 0.4 → soft filter (AIURA_SETTORE_SOFT=1 ha effetto)
        < 0.4  → nessun filtro settore
    """

    def __init__(self, retriever: HybridRetriever) -> None:
        self._retriever = retriever

    # ------------------------------------------------------------------
    # Normativa
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

        Se disponibile, aggiunge chunk da corpus=prassi con peso ridotto.
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query normativa vuota — skip")
            return []

        logger.info(f"[PhaseRetriever] normativa re-query: {query[:80]!r}")

        # --- Determina filtro ---
        chunk_filter = self._effective_filter(
            base_filter=_FILTER_NORMATIVA,
            settore=settore,
            settore_confidence=settore_confidence,
            label="normativa",
        )
        use_soft = bool(
            settore
            and _SETTORE_SOFT_ENABLED
            and 0.4 <= settore_confidence < 0.7
        )

        # top_k doppio per soft (più candidati prima della penalità)
        top_k_retrieve = 15 if not use_soft else 30

        results = self._search_with_fallback(
            query=query,
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

        # --- Corpus prassi (supplementare, graceful skip) ---
        prassi_results = self._retrieve_prassi(
            query=query,
            settore=settore,
            settore_confidence=settore_confidence,
        )
        if prassi_results:
            # Scalatura score prassi: contribuisce al pool con peso ridotto
            if results:
                max_norm_score = max((r.score for r in results), default=1.0)
                for pr in prassi_results:
                    pr.score = pr.score * _PRASSI_SCORE_FACTOR * max_norm_score
            results = _merge_unique(results, prassi_results, max_total=top_k + len(prassi_results))

        for r in results:
            r.source_layer = "normativa"
        logger.info(f"[PhaseRetriever] normativa: {len(results)} fonti")
        return results

    # ------------------------------------------------------------------
    # Giurisprudenza
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
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query giurisprudenza vuota — skip")
            return []

        logger.info(f"[PhaseRetriever] giurisprudenza re-query: {query[:80]!r}")

        chunk_filter = self._effective_filter(
            base_filter=_FILTER_GIURISPRUDENZA,
            settore=settore,
            settore_confidence=settore_confidence,
            label="giurisprudenza",
        )
        use_soft = bool(
            settore
            and _SETTORE_SOFT_ENABLED
            and 0.4 <= settore_confidence < 0.7
        )
        top_k_retrieve = 15 if not use_soft else 30

        results = self._search_with_fallback(
            query=query,
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

        for r in results:
            r.source_layer = "giurisprudenza"
        logger.info(f"[PhaseRetriever] giurisprudenza: {len(results)} fonti")
        return results

    # ------------------------------------------------------------------
    # Dottrina
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
        Usata nella Fase 2 (INTERPRETAZIONE) per citare manuali e commentari.
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
        use_soft = bool(
            settore
            and _SETTORE_SOFT_ENABLED
            and 0.4 <= settore_confidence < 0.7
        )
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
    # Prassi (supplementare a normativa, graceful skip se corpus assente)
    # ------------------------------------------------------------------

    def _retrieve_prassi(
        self,
        query: str,
        settore: str | None = None,
        settore_confidence: float = 0.0,
        top_k: int = 3,
    ) -> list[SearchResult]:
        """
        Recupera chunk da corpus=prassi.
        Restituisce lista vuota (senza eccezione) se il corpus non esiste.
        """
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
    # Helpers
    # ------------------------------------------------------------------

    def _effective_filter(
        self,
        base_filter: dict,
        settore: str | None,
        settore_confidence: float,
        label: str,
    ) -> dict:
        """
        Calcola il filtro effettivo tenendo conto di settore_confidence.

        - confidence >= 0.7 → hard filter se AIURA_SETTORE_FILTER=1
        - confidence >= 0.4 → soft mode (filtro solo corpus, penalità post-hoc)
        - confidence < 0.4  → nessun filtro settore
        """
        if not settore:
            return base_filter

        if settore_confidence >= 0.7 and _SETTORE_FILTER_ENABLED:
            f = {**base_filter, "settore": settore}
            logger.debug(f"[PhaseRetriever] {label}: filtro hard settore={settore!r}")
            return f

        if settore_confidence >= 0.4 and _SETTORE_SOFT_ENABLED:
            logger.debug(f"[PhaseRetriever] {label}: filtro soft (penalità post-hoc) settore={settore!r}")
            # filtro solo corpus, penalità applicata in post-processing
            return base_filter

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
        Se il filtro hard è attivo e restituisce < _HARD_FILTER_MIN_RESULTS,
        riesegue senza filtro settore (fallback) e logga un warning.
        """
        results = self._retriever._search_round(
            query=query,
            weights=weights,
            chunk_filter=chunk_filter,
            valid_on=None,
            top_k_retrieve=top_k_retrieve,
            top_k_rerank=top_k_rerank,
        )

        # Fallback se hard filter è attivo e risultati insufficienti
        if (
            chunk_filter != base_filter  # significa che c'è un filtro settore
            and len(results) < _HARD_FILTER_MIN_RESULTS
        ):
            logger.warning(
                f"[PhaseRetriever] {label}: hard filter → solo {len(results)} risultati "
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
