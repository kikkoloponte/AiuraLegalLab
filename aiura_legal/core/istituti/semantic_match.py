"""
Match semantico istituto via embedding — terzo path tra lessicale
(`IstitutoRegistry.match_query`, esatto ma fragile su parafrasi) e fallback LLM
(chiamata già fatta in Fase 1, ma il vocabolario id:label non basta al modello
per ragionare su domande astratte che non nominano l'istituto).

Riusa il modello già in produzione per Qdrant (VectorRetrieverV2,
intfloat/multilingual-e5-base, convenzione prefissi "query: "/"passage: ")
così non introduce un modello nuovo da mantenere.

Ogni istituto è embeddato una sola volta (label + termini_chiave +
norme_riferimento) e il vettore è cachato su disco: l'embedding non dipende
dalla domanda, solo dal contenuto del registro. La cache si invalida da sola
quando registry.yaml cambia (hash del contenuto embeddabile).
"""
from __future__ import annotations

import hashlib
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger

from aiura_legal.core.istituti.registry import Istituto, IstitutoRegistry

_CACHE_PATH = Path(__file__).resolve().parent / "registry_embeddings.pkl"
_MODEL_NAME = "intfloat/multilingual-e5-base"
_QUERY_PREFIX = "query: "
_PASSAGE_PREFIX = "passage: "

# Soglia calibrata empiricamente su un piccolo set di domande astratte
# (vedi test_semantic_match.py) — sotto soglia, nessun match: si passa al
# fallback LLM esistente invece di forzare una corrispondenza incerta.
DEFAULT_THRESHOLD = 0.78


def _istituto_text(ist: Istituto) -> str:
    parts = [ist.label, *ist.termini_chiave, *ist.norme_riferimento]
    return " — ".join(p for p in parts if p)


def _content_hash(istituti: list[Istituto]) -> str:
    h = hashlib.sha1()
    for ist in sorted(istituti, key=lambda i: i.id):
        h.update(ist.id.encode("utf-8"))
        h.update(_istituto_text(ist).encode("utf-8"))
    return h.hexdigest()


class IstitutoSemanticMatcher:
    """
    Calcola e cacha gli embedding degli istituti; matcha una query per
    cosine similarity (i vettori e5 sono normalizzati → dot product = cosine).
    """

    def __init__(self) -> None:
        self._model = None
        self._ids: list[str] = []
        self._vectors: Optional[np.ndarray] = None  # shape (n_istituti, dim)

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"[IstitutoSemanticMatcher] caricamento modello: {_MODEL_NAME}")
            self._model = SentenceTransformer(_MODEL_NAME)
        return self._model

    def _ensure_index(self, registry: IstitutoRegistry) -> None:
        istituti = registry.all()
        if not istituti:
            self._ids, self._vectors = [], None
            return

        current_hash = _content_hash(istituti)

        if _CACHE_PATH.exists():
            try:
                with open(_CACHE_PATH, "rb") as f:
                    cached = pickle.load(f)
                if cached.get("content_hash") == current_hash:
                    self._ids = cached["ids"]
                    self._vectors = cached["vectors"]
                    return
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"[IstitutoSemanticMatcher] cache corrotta, ricalcolo: {exc}")

        logger.info(
            f"[IstitutoSemanticMatcher] cache assente/obsoleta — embedding di "
            f"{len(istituti)} istituti in corso..."
        )
        model = self._get_model()
        texts = [_PASSAGE_PREFIX + _istituto_text(ist) for ist in istituti]
        vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        vectors = np.asarray(vectors, dtype=np.float32)

        self._ids = [ist.id for ist in istituti]
        self._vectors = vectors
        try:
            with open(_CACHE_PATH, "wb") as f:
                pickle.dump(
                    {"content_hash": current_hash, "ids": self._ids, "vectors": vectors}, f
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[IstitutoSemanticMatcher] impossibile salvare cache: {exc}")

    def best_match(
        self,
        query: str,
        registry: IstitutoRegistry,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> Optional[tuple[Istituto, float]]:
        """Ritorna (istituto, score) se la similarità massima supera `threshold`, altrimenti None."""
        matches = self.top_matches(query, registry, top_k=1, min_score=threshold)
        return matches[0] if matches else None

    def top_matches(
        self,
        query: str,
        registry: IstitutoRegistry,
        top_k: int = 3,
        min_score: float = DEFAULT_THRESHOLD,
    ) -> list[tuple[Istituto, float]]:
        """Ritorna fino a `top_k` istituti con score >= `min_score`, ordinati per score."""
        self._ensure_index(registry)
        if self._vectors is None or not self._ids:
            return []

        model = self._get_model()
        q_vec = model.encode(
            [_QUERY_PREFIX + query], show_progress_bar=False, normalize_embeddings=True
        )[0]
        scores = self._vectors @ q_vec
        order = np.argsort(scores)[::-1]
        out: list[tuple[Istituto, float]] = []
        for idx in order:
            score = float(scores[idx])
            if score < min_score:
                break
            istituto = registry.by_id(self._ids[idx])
            if istituto is not None:
                out.append((istituto, score))
            if len(out) >= top_k:
                break
        return out


# Soglia alta apposta: il semantico qui è solo un segnale secondario per non
# perdere casi limite — vedi nota su affidabilità in cima al modulo.
_SEMANTIC_CANDIDATE_THRESHOLD = 0.85


def suggest_istituto_candidates(
    query: str,
    registry: IstitutoRegistry,
    matcher: "IstitutoSemanticMatcher",
    top_k: int = 3,
) -> list[Istituto]:
    """
    Candidati per una domanda di chiarimento a scelta multipla (S1 Clarifier).

    Fonte primaria: coppie esplicitamente marcate come confondibili via
    `disambigua_da` nel registry (es. sequestro CPP vs confisca antimafia,
    curate a mano proprio perché condividono lessico come "terzo in buona
    fede"). Non basta un generico match lessicale multiplo: query come
    "inadempimento in un contratto di locazione" matchano sia `adempimento_cc`
    sia `locazione_cc`, ma non sono un'ambiguità reale — sono due concetti
    entrambi pertinenti, non un aut-aut. Il segnale `disambigua_da` è invece
    un aut-aut dichiarato esplicitamente dal curatore, quindi affidabile.

    Il semantico resta una fonte secondaria con soglia molto alta (0.85):
    nei test si è visto che con testo breve (label+termini_chiave) non
    discrimina bene tra istituti penalistici affini — usarlo come fonte
    primaria proporrebbe candidati sbagliati come opzioni, peggio che non
    chiedere nulla.
    """
    lexical = registry.match_query(query, top_k=top_k + 2)
    lexical_ids = {ist.id for ist, _score in lexical}

    seen: dict[str, Istituto] = {}
    for ist, _score in lexical:
        if ist.id not in seen and any(other_id in lexical_ids for other_id in ist.disambigua_da):
            seen.setdefault(ist.id, ist)
            for other_id in ist.disambigua_da:
                if other_id in lexical_ids:
                    other = next((o for o, _s in lexical if o.id == other_id), None)
                    if other is not None:
                        seen.setdefault(other.id, other)

    if len(seen) < 2:
        try:
            for ist, _score in matcher.top_matches(
                query, registry, top_k=top_k, min_score=_SEMANTIC_CANDIDATE_THRESHOLD
            ):
                seen.setdefault(ist.id, ist)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[suggest_istituto_candidates] match semantico fallito: {exc}")

    if len(seen) < 2:
        return []
    return list(seen.values())[:top_k]


# Singleton di processo — il modello e la cache si caricano una sola volta.
_singleton: Optional[IstitutoSemanticMatcher] = None


def get_semantic_matcher() -> IstitutoSemanticMatcher:
    global _singleton
    if _singleton is None:
        _singleton = IstitutoSemanticMatcher()
    return _singleton
