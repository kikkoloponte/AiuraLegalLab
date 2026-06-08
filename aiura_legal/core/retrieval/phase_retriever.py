"""
PhaseRetriever — retrieval mirato per fase nel Sequential IQRAC.

Wrapper leggero su HybridRetriever che esegue re-query focalizzate
per corpus specifico (normattiva o giurisprudenza), usando la query
distillata dalla fase precedente invece della query originale grezza.

Usato da SequentialAnalyst nelle fasi 2 (normativa) e 3 (giurisprudenza).

Anti-allucinazione (RAG over-fitting) — meccanismi in ordine di priorità:

  [1] Filtro settore (primario):
      _infer_domain() rileva il dominio dalla query/qualificazione.
      _settore_filter_normativa() costruisce il chunk_filter con settore $in [...]
      che filtra i chunk PRIMA del ranking BM25/Vector — elimina strutturalmente
      i falsi positivi (es. c.c. per query penali).

  [2] Query augmentation (secondario):
      Prefissa "diritto penale elemento soggettivo" per BM25 keyword matching
      — manteniamo come secondo strato di sicurezza.

  [3] Golden sources:
      Art. 43 c.p. e ThyssenKrupp iniettati se assenti dal packet.
"""
from __future__ import annotations

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
# Classificazione dominio giuridico
# ---------------------------------------------------------------------------

# Marcatori forti: inequivocabilmente diritto penale.
# Un solo match è sufficiente per classificare come penale.
_STRONG_CRIMINAL_MARKERS: frozenset[str] = frozenset({
    "diritto penale", "penale sostanziale", "elemento soggettivo",
    "dolo eventuale", "colpa cosciente", "preterintenzione",
    "art. 43", "art.43", "codice penale", " c.p.",
    "reato doloso", "reato colposo", "illecito penale",
    "omicidio colposo", "lesioni colpose", "omicidio doloso",
    "thyssen", "thyssenkrupp", "38343", "ss.uu. penali",
    "tentativo punibile", "antigiuridicità", "imputabilità penale",
})

# Marcatori deboli: presenti anche nel diritto civile/amministrativo.
# Richiedono almeno 2 match per classificare come penale.
_WEAK_CRIMINAL_MARKERS: frozenset[str] = frozenset({
    "penale", "penali", "reato", "dolo", "colpa",
})

# Trigger per l'iniezione di Art. 43 c.p. come golden source.
# Richiede almeno un marcatore forte per evitare falsi positivi sul "dolo" civile.
_ART43_TRIGGERS: frozenset[str] = frozenset({
    "elemento soggettivo", "dolo eventuale",
    "colpa cosciente", "preterintenzione", "art. 43", "art.43",
    "reato doloso", "reato colposo",
})

# Trigger per l'iniezione della sentenza ThyssenKrupp come golden source
_THYSSEN_TRIGGERS: frozenset[str] = frozenset({
    "dolo eventuale", "colpa cosciente",
    "thyssen", "thyssenkrupp", "38343",
    "confine dolo colpa", "distinzione dolo colpa",
})


# ---------------------------------------------------------------------------
# Classificazione dominio per filtro settore
# ---------------------------------------------------------------------------

# Keyword per rilevamento domini diversi da penale
_CIVIL_MARKERS: frozenset[str] = frozenset({
    "contratto", "obbligazione", "risarcimento", "inadempimento",
    "responsabilità civile", "art. 2043", "art. 1218", "nullità del contratto",
    "annullabilità", "recesso", "risoluzione del contratto",
})
_ADMIN_MARKERS: frozenset[str] = frozenset({
    "appalto pubblico", "pubblica amministrazione", "atto amministrativo",
    "ricorso tar", "consiglio di stato", "silenzio inadempimento",
    "autotutela", "illegittimità", "diniego", "provvedimento amministrativo",
})
_LABOR_MARKERS: frozenset[str] = frozenset({
    "licenziamento", "contratto di lavoro", "rapporto di lavoro",
    "art. 18", "reintegrazione", "mobbing", "discriminazione lavorativa",
    "ccnl", "contratto collettivo", "inps", "inail",
})


def _infer_domain(text: str) -> str | None:
    """
    Inferisce il dominio giuridico dalla query/qualificazione di Fase 1.

    Ritorna uno dei valori settore ("penale", "civile", "amministrativo", "lavoro")
    oppure None se il dominio è ambiguo o non riconoscibile.

    Usato per costruire il chunk_filter settore-aware in retrieve_normativa().
    """
    t = text.lower()
    # Penale: usa la logica esistente a due livelli (strong/weak markers)
    if _is_criminal_law_topic(t):
        return "penale"
    # Lavoro prima di civile: "contratto di lavoro" contiene "contratto"
    # che è marker civile — lavoro ha priorità più alta per specificità
    if any(kw in t for kw in _LABOR_MARKERS):
        return "lavoro"
    # Civile
    if any(kw in t for kw in _CIVIL_MARKERS):
        return "civile"
    # Amministrativo
    if any(kw in t for kw in _ADMIN_MARKERS):
        return "amministrativo"
    return None


def _settore_filter_normativa(domain: str | None) -> dict:
    """
    Costruisce il chunk_filter per corpus=normattiva con filtro settore.

    Per domini noti: aggiunge settore $in [...] per escludere strutturalmente
    i chunk di altri rami del diritto prima del ranking BM25/Vector.

    Per dominio None/ambiguo: ritorna solo {"corpus": "normattiva"} —
    nessun filtro settore, recupera tutto normattiva.

    Note su retrocompatibilità:
    - Chunk senza campo settore (pre-rebuild) → non matchano $in → esclusi.
    - Per questo motivo il filtro settore è attivato solo DOPO rebuild_knowledge_base.
    - Il flag SETTORE_FILTER_ENABLED controlla l'attivazione.
    """
    base = {"corpus": "normattiva"}
    mapping: dict[str, list[str]] = {
        "penale":         ["penale"],
        "civile":         ["civile"],
        "amministrativo": ["amministrativo"],
        "lavoro":         ["lavoro"],
        "processuale":    ["processuale"],
        "costituzionale": ["costituzionale"],
    }
    if domain in mapping:
        return {**base, "settore": {"$in": mapping[domain]}}
    return base


# Flag globale: attivato dopo rebuild_knowledge_base.py (quando tutti i chunk hanno settore)
# Può essere sovrascritto via env var AIURA_SETTORE_FILTER=1
import os as _os
SETTORE_FILTER_ENABLED: bool = _os.environ.get("AIURA_SETTORE_FILTER", "0") == "1"


def _is_criminal_law_topic(text: str) -> bool:
    """
    Ritorna True se il testo descrive un problema di diritto penale sostanziale.

    Logica a due livelli per evitare falsi positivi:
    - Un marcatore forte (es. "dolo eventuale", "codice penale") → True
    - Due o più marcatori deboli (es. "penale" + "dolo") → True
    - Solo "dolo" o solo "colpa" → False (potrebbero essere civili)

    Usata per decidere se applicare query augmentation e golden sources.
    """
    t = text.lower()
    if any(kw in t for kw in _STRONG_CRIMINAL_MARKERS):
        return True
    weak_count = sum(1 for kw in _WEAK_CRIMINAL_MARKERS if kw in t)
    return weak_count >= 2


class PhaseRetriever:
    """
    Esegue retrieval mirato per singola fase IQRAC.

    Le query di fase sono più precise della query originale:
    vengono estratte dall'output della Fase 1 (QUESTIONE, QUALIFICAZIONE)
    e usate per recuperare fonti più pertinenti.

    Anti-allucinazione: per query di diritto penale, applica automaticamente
    query augmentation e golden source injection (Art. 43 c.p.,
    Cass. SS.UU. n.38343/2014 ThyssenKrupp).
    """

    def __init__(self, retriever: HybridRetriever) -> None:
        self._retriever = retriever

    # ------------------------------------------------------------------
    # Retrieval normativa — Fase 2
    # ------------------------------------------------------------------

    def retrieve_normativa(
        self,
        query: str,
        top_k: int = 6,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=normattiva con pesi BM25-heavy.
        Usa la QUESTIONE distillata dalla Fase 1 come query.

        Per query di diritto penale:
          - Augmenta la query con "diritto penale elemento soggettivo"
          - Inietta Art. 43 c.p. come golden source se assente dai risultati
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query normativa vuota — skip")
            return []

        is_criminal = _is_criminal_law_topic(query)

        # Fix 1 (primario): filtro settore — esclude chunk di altri rami del diritto
        # PRIMA del ranking, eliminando strutturalmente i falsi positivi.
        # Attivo solo se SETTORE_FILTER_ENABLED (dopo rebuild_knowledge_base).
        if SETTORE_FILTER_ENABLED:
            domain = _infer_domain(query)
            chunk_filter = _settore_filter_normativa(domain)
            if domain:
                logger.info(
                    f"[PhaseRetriever] filtro settore attivo: dominio={domain!r} "
                    f"filter={chunk_filter}"
                )
        else:
            chunk_filter = _FILTER_NORMATIVA

        # Fix 2 (secondario): Query augmentation per diritto penale
        # BM25 è keyword-sensitive: senza "penale" recupera spesso c.c. invece di c.p.
        # Mantenuto come secondo strato anche con filtro settore attivo.
        if is_criminal and "penale" not in query.lower()[:30]:
            query_effective = f"diritto penale elemento soggettivo {query}"
            logger.info(
                f"[PhaseRetriever] dominio penale rilevato — query augmentata: "
                f"{query_effective[:100]!r}"
            )
        else:
            query_effective = query

        logger.info(f"[PhaseRetriever] normativa re-query: {query_effective[:80]!r}")
        results = self._retriever._search_round(
            query=query_effective,
            weights=_WEIGHTS_NORMATIVA,
            chunk_filter=chunk_filter,
            valid_on=None,
            top_k_retrieve=20,   # più ampio per dare spazio ai golden sources
            top_k_rerank=top_k,
        )
        for r in results:
            r.source_layer = "normativa"

        # Fix 2: Inietta Art. 43 c.p. come golden source se topic dolo/colpa
        if is_criminal:
            results = self._inject_art43_golden(query, results, top_k)

        logger.info(f"[PhaseRetriever] normativa: {len(results)} fonti")
        return results

    def _inject_art43_golden(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """
        Fix 2 (Golden Sources): se la query riguarda dolo/colpa/elemento soggettivo
        e Art. 43 c.p. non è già nei risultati, lo recupera con ricerca diretta
        e lo inserisce in cima al packet.

        Logica: Art. 43 c.p. è il fondamento normativo per QUALSIASI questione su
        elemento soggettivo nel diritto penale italiano. Senza di esso, l'LLM
        tende a citare surrogate civili o amministrative.
        """
        t = query.lower()
        # Attiva solo per topic dolo/colpa/elemento soggettivo
        if not any(kw in t for kw in _ART43_TRIGGERS):
            return results

        # Verifica se art. 43 c.p. è già presente (controlla articolo_num + fonte)
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
            logger.debug("[PhaseRetriever] Art. 43 c.p. già presente nei risultati — skip golden inject")
            return results

        # Recupera Art. 43 c.p. con ricerca BM25 dedicata
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
            logger.warning(
                "[PhaseRetriever] Art. 43 c.p. non trovato nel DB normattiva — "
                "verificare che il corpus normattiva sia indicizzato"
            )
            return results

        logger.info(
            f"[PhaseRetriever] iniettati {len(golden)} golden source "
            f"(Art. 43 c.p.) per topic dolo/colpa"
        )
        # Merge: golden in cima, de-duplica, mantieni slice ragionevole
        existing_ids = {r.source_id for r in results}
        new_golden = [r for r in golden if r.source_id not in existing_ids]
        merged = new_golden + results
        # Lascia fino a top_k + 2 per non perdere fonti pertinenti già trovate
        return merged[: top_k + len(new_golden)]

    # ------------------------------------------------------------------
    # Retrieval giurisprudenza — Fase 3
    # ------------------------------------------------------------------

    def retrieve_giurisprudenza(
        self,
        query: str,
        top_k: int = 6,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=giurisprudenza con pesi Vector-heavy.
        Usa QUALIFICAZIONE+QUESTIONE dalla Fase 1 come query.

        Per query su dolo eventuale vs colpa cosciente:
          - Augmenta la query con termini ThyssenKrupp-specifici
          - Inietta Cass. SS.UU. n.38343/2014 se assente
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query giurisprudenza vuota — skip")
            return []

        is_criminal = _is_criminal_law_topic(query)

        # Fix 1: Query augmentation per penale/dolo eventuale
        if is_criminal and "penale" not in query.lower()[:30]:
            query_effective = f"diritto penale {query}"
        else:
            query_effective = query

        logger.info(f"[PhaseRetriever] giurisprudenza re-query: {query_effective[:80]!r}")
        results = self._retriever._search_round(
            query=query_effective,
            weights=_WEIGHTS_GIURISPRUDENZA,
            chunk_filter=_FILTER_GIURISPRUDENZA,
            valid_on=None,
            top_k_retrieve=20,
            top_k_rerank=top_k,
        )
        for r in results:
            r.source_layer = "giurisprudenza"

        # Fix 2: Inietta ThyssenKrupp come golden source per dolo eventuale
        if is_criminal:
            results = self._inject_thyssen_golden(query, results, top_k)

        logger.info(f"[PhaseRetriever] giurisprudenza: {len(results)} fonti")
        return results

    def _inject_thyssen_golden(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """
        Fix 2 (Golden Sources): se la query riguarda dolo eventuale vs colpa cosciente,
        inietta Cass. SS.UU. n.38343/2014 (ThyssenKrupp) se non già presente.

        Quella sentenza è il leading case italiano per i criteri diagnostici
        del dolo eventuale: senza di essa l'analisi giurisprudenziale è incompleta.
        """
        t = query.lower()
        if not any(kw in t for kw in _THYSSEN_TRIGGERS):
            return results

        # Verifica se ThyssenKrupp è già presente
        def _is_thyssen(r: SearchResult) -> bool:
            meta = r.metadata or {}
            n = str(meta.get("numero") or "")
            s = r.snippet.lower()
            return (
                "38343" in n
                or "thyssen" in s
                or ("38343" in s)
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
            logger.info(
                "[PhaseRetriever] ThyssenKrupp n.38343/2014 non nel DB giurisprudenza — "
                "caricarla con /jurisprudence/upload per analisi completa"
            )
            return results

        logger.info(
            f"[PhaseRetriever] iniettati {len(golden)} golden source "
            f"(Cass. SS.UU. 38343/2014) per topic dolo eventuale"
        )
        existing_ids = {r.source_id for r in results}
        new_golden = [r for r in golden if r.source_id not in existing_ids]
        merged = new_golden + results
        return merged[: top_k + len(new_golden)]

    # ------------------------------------------------------------------
    # Retrieval dottrina — Fase 2 (invariato)
    # ------------------------------------------------------------------

    def retrieve_dottrina(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=dottrina con pesi bilanciati BM25+Vector.
        Usata nella Fase 2 (INTERPRETAZIONE) per citare manuali e commentari.
        Ritorna lista vuota (non errore) se nessun documento dottrinale è indicizzato.
        """
        if not query.strip():
            return []

        logger.info(f"[PhaseRetriever] dottrina re-query: {query[:80]!r}")
        results = self._retriever._search_round(
            query=query,
            weights=_WEIGHTS_DOTTRINA,
            chunk_filter=_FILTER_DOTTRINA,
            valid_on=None,
            top_k_retrieve=10,
            top_k_rerank=top_k,
        )
        for r in results:
            r.source_layer = "dottrina"
        logger.info(f"[PhaseRetriever] dottrina: {len(results)} fonti")
        return results
