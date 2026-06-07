"""
BM25 Retriever — rank_bm25 (BM25Okapi) con indici per-corpus separati.

Ogni corpus ha il suo pkl:  bm25_normattiva.pkl, bm25_dottrina.pkl,
                             bm25_studio.pkl, bm25_giurisprudenza.pkl

Vantaggi rispetto al pkl monolitico:
  - Aggiornare dottrina (191k) non tocca normattiva (278k) o giurisprudenza (316k)
  - save() ricostruisce BM25Okapi solo per i sub-indici modificati
  - BM25Okapi viene serializzato nel pkl → load istantaneo, nessun rebuild al primo search()
  - Migrazione automatica da bm25.pkl legacy al primo avvio (~5-15 secondi)
"""
from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger
from rank_bm25 import BM25Okapi

from aiura_legal.core.types import Document, SearchResult

# ─────────────────────────────────────────────────────────────────────────────
# Tokenizzazione
# ─────────────────────────────────────────────────────────────────────────────

_IT_STOPWORDS = frozenset({
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "del", "della", "dei", "degli", "delle", "da", "dal", "dalla",
    "dai", "dagli", "dalle", "a", "al", "alla", "ai", "agli", "alle",
    "in", "nel", "nella", "nei", "negli", "nelle", "su", "sul", "sulla",
    "sui", "sugli", "sulle", "con", "per", "tra", "fra", "e", "ed",
    "o", "ma", "se", "non", "che", "chi", "cui", "ne", "ci", "si",
    "è", "sono", "ha", "hanno", "era", "were", "the", "of", "and",
    "quale", "quali", "questo", "questa", "questi", "queste",
    "dopo", "prima", "oltre", "anche", "come", "quando", "dove",
    "all", "dell", "nell",
})


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\w+", text.lower())
    return [t for t in tokens if len(t) >= 2 and t not in _IT_STOPWORDS]


# ─────────────────────────────────────────────────────────────────────────────
# _BM25Sub — sub-indice per un singolo corpus
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class _BM25Sub:
    """
    Indice BM25 per un singolo corpus.
    Gestisce load/save/add/search/reset in modo completamente indipendente.
    """
    corpus: str
    ws: Path

    # Dati
    doc_ids:        list[str]       = field(default_factory=list)
    doc_snippets:   list[str]       = field(default_factory=list)
    doc_metadata:   list[dict]      = field(default_factory=list)
    doc_source_ids: list[str]       = field(default_factory=list)
    tokenized:      list[list[str]] = field(default_factory=list)
    chunk_meta:     dict[str, dict] = field(default_factory=dict)

    # BM25Okapi (None se corpus vuoto o non ancora costruito)
    bm25:  Optional[BM25Okapi] = field(default=None, repr=False)
    dirty: bool = False

    # Array numpy per filtri vettorizzati — precalcolati su doc_metadata
    corpus_arr:     np.ndarray = field(default_factory=lambda: np.array([], dtype=object), repr=False)
    fonte_arr:      np.ndarray = field(default_factory=lambda: np.array([], dtype=object), repr=False)
    testo_tipo_arr: np.ndarray = field(default_factory=lambda: np.array([], dtype=object), repr=False)

    @property
    def index_path(self) -> Path:
        return self.ws / "indices" / f"bm25_{self.corpus}.pkl"

    def __len__(self) -> int:
        return len(self.doc_ids)

    # ------------------------------------------------------------------
    # Add / reset
    # ------------------------------------------------------------------

    def add(self, docs: list[Document]) -> None:
        for doc in docs:
            tokens = _tokenize(doc.text)
            self.tokenized.append(tokens)
            self.doc_ids.append(doc.id)
            self.doc_snippets.append(doc.text[:300])
            self.doc_metadata.append(doc.metadata)
            self.doc_source_ids.append(doc.source_id)
            self.chunk_meta[doc.id] = {
                "corpus":     doc.metadata.get("corpus", "studio"),
                "fonte":      doc.metadata.get("fonte", "altro"),
                "testo_tipo": doc.metadata.get("testo_tipo", "normativo"),
            }
        self.dirty = True
        self._rebuild_filter_arrays()

    def reset(self) -> None:
        self.doc_ids        = []
        self.doc_snippets   = []
        self.doc_metadata   = []
        self.doc_source_ids = []
        self.tokenized      = []
        self.chunk_meta     = {}
        self.bm25           = None
        self.dirty          = False
        self.corpus_arr = self.fonte_arr = self.testo_tipo_arr = np.array([], dtype=object)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _ensure_bm25(self) -> None:
        if self.dirty or self.bm25 is None:
            if self.tokenized:
                logger.info(f"BM25[{self.corpus}]: build su {len(self.tokenized):,} doc...")
                self.bm25 = BM25Okapi(self.tokenized)
                logger.info(f"BM25[{self.corpus}]: pronto")
            else:
                self.bm25 = None
            self.dirty = False

    def search(
        self,
        query: str,
        top_k: int = 15,
        chunk_filter: Optional[dict] = None,
    ) -> list[SearchResult]:
        # Lazy load: carica da disco se il sub non è ancora in memoria
        if not self.doc_ids and self.index_path.exists():
            self.load()
        self._ensure_bm25()
        if self.bm25 is None or not self.tokenized:
            return []

        tokens = _tokenize(query)
        scores: np.ndarray = self.bm25.get_scores(tokens)

        # Filtro corpus (chiave speciale)
        source_id_in: list[str] = []
        meta_filter: dict = {}
        if chunk_filter:
            for k, v in chunk_filter.items():
                if k == "_source_id_in":
                    source_id_in = list(v) if v else []
                elif k != "corpus":   # corpus è già selezionato dal sub
                    meta_filter[k] = v

        if meta_filter:
            scores = scores.copy()
            if "fonte" in meta_filter and len(self.fonte_arr):
                scores[self.fonte_arr != meta_filter["fonte"]] = 0.0
            if "testo_tipo" in meta_filter and len(self.testo_tipo_arr):
                scores[self.testo_tipo_arr != meta_filter["testo_tipo"]] = 0.0
            other = {k: v for k, v in meta_filter.items() if k not in ("fonte", "testo_tipo")}
            if other and self.chunk_meta:
                mask = np.array([
                    all(self.chunk_meta.get(did, {}).get(k) == v for k, v in other.items())
                    for did in self.doc_ids
                ], dtype=bool)
                scores[~mask] = 0.0

        if source_id_in and self.doc_source_ids:
            scores = scores if scores.flags.writeable else scores.copy()
            sid_mask = np.array(
                [any(pat in sid for pat in source_id_in) for sid in self.doc_source_ids],
                dtype=bool,
            )
            scores[~sid_mask] = 0.0

        n = len(scores)
        k = min(top_k, n)
        if k == 0:
            return []
        top_indices = np.argpartition(scores, -k)[-k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0:
                continue
            results.append(SearchResult(
                doc_id=self.doc_ids[idx],
                score=score,
                snippet=self.doc_snippets[idx],
                metadata=self.doc_metadata[idx],
                source_id=self.doc_source_ids[idx],
                retrieval_method="bm25",
            ))
        return results

    # ------------------------------------------------------------------
    # Persist
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Salva il sub-indice. Costruisce BM25Okapi se dirty, lo include nel pkl."""
        self._ensure_bm25()
        self._save_state(self.bm25)

    def _save_raw(self) -> None:
        """
        Salva senza costruire BM25Okapi (usato durante migrazione da pkl legacy).
        Il sub viene salvato con bm25=None e dirty=False: BM25Okapi verrà
        costruito la prima volta che search() o save() vengono chiamati su quel corpus.
        """
        self._save_state(None)
        self.dirty = False

    def _save_state(self, bm25_obj) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "corpus":         self.corpus,
            "bm25":           bm25_obj,
            "doc_ids":        self.doc_ids,
            "doc_snippets":   self.doc_snippets,
            "doc_metadata":   self.doc_metadata,
            "doc_source_ids": self.doc_source_ids,
            "tokenized":      self.tokenized,
            "chunk_meta":     self.chunk_meta,
        }
        with open(self.index_path, "wb") as f:
            pickle.dump(state, f)
        logger.info(f"BM25[{self.corpus}]: salvato {len(self.doc_ids):,} doc → {self.index_path}")

    def load(self) -> None:
        """Carica da pkl. BM25Okapi è già pronto (incluso nel pkl) → nessun rebuild."""
        with open(self.index_path, "rb") as f:
            state = pickle.load(f)
        self.doc_ids        = state["doc_ids"]
        self.doc_snippets   = state["doc_snippets"]
        self.doc_metadata   = state["doc_metadata"]
        self.doc_source_ids = state["doc_source_ids"]
        self.tokenized      = state.get("tokenized", state.get("corpus", []))  # compat legacy
        self.chunk_meta     = state.get("chunk_meta", {})
        self.bm25           = state.get("bm25")   # già pronto, nessun rebuild
        self.dirty          = False
        self._rebuild_filter_arrays()
        logger.info(f"BM25[{self.corpus}]: caricato {len(self.doc_ids):,} doc da {self.index_path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _rebuild_filter_arrays(self) -> None:
        meta = self.doc_metadata
        if not meta:
            self.corpus_arr = self.fonte_arr = self.testo_tipo_arr = np.array([], dtype=object)
            return
        self.corpus_arr     = np.array([m.get("corpus",     "studio")    for m in meta], dtype=object)
        self.fonte_arr      = np.array([m.get("fonte",      "altro")     for m in meta], dtype=object)
        self.testo_tipo_arr = np.array([m.get("testo_tipo", "normativo") for m in meta], dtype=object)


# ─────────────────────────────────────────────────────────────────────────────
# BM25Retriever — interfaccia pubblica (invariata)
# ─────────────────────────────────────────────────────────────────────────────

_KNOWN_CORPORA = ("normattiva", "dottrina", "studio", "giurisprudenza")


class BM25Retriever:
    """
    Retriever BM25 con indici per-corpus separati.

    Gestisce 4 sub-indici (uno per corpus) in modo completamente indipendente.
    L'API pubblica è identica alla versione precedente monolitica.

    File:
      workspaces/<ws>/indices/bm25_normattiva.pkl
      workspaces/<ws>/indices/bm25_dottrina.pkl
      workspaces/<ws>/indices/bm25_studio.pkl
      workspaces/<ws>/indices/bm25_giurisprudenza.pkl

    Migrazione automatica: se esiste bm25.pkl (legacy) ma non i 4 separati,
    la migrazione avviene in __init__ (~5-15 secondi, nessun re-tokenize).
    """

    def __init__(self, workspace_path: str) -> None:
        self._ws = Path(workspace_path)
        # Retrocompatibilità: path del pkl legacy (non più usato dopo migrazione)
        self._index_path = self._ws / "indices" / "bm25.pkl"
        self._meta_path  = self._ws / "indices" / "bm25_meta.json"

        # Sub-indici per corpus — caricati LAZY al primo search()
        # build_indexes.py non cerca mai → non carica pkl inutili
        self._subs: dict[str, _BM25Sub] = {}
        for corpus in _KNOWN_CORPORA:
            self._subs[corpus] = _BM25Sub(corpus=corpus, ws=self._ws)

        # Migrazione da pkl monolitico legacy (fast: raw save, no BM25Okapi)
        self._maybe_migrate_legacy()

    def load_all(self) -> None:
        """
        Carica tutti i sub-indici da disco (warm-up esplicito per API).
        build_indexes.py non lo chiama mai — lavora solo sui sub che tocca.
        """
        for corpus in _KNOWN_CORPORA:
            sub = self._subs[corpus]
            if sub.index_path.exists() and not sub.doc_ids:
                sub.load()

    # ------------------------------------------------------------------
    # Sub-indice helper
    # ------------------------------------------------------------------

    def _get_or_create_sub(self, corpus: str) -> _BM25Sub:
        if corpus not in self._subs:
            self._subs[corpus] = _BM25Sub(corpus=corpus, ws=self._ws)
        return self._subs[corpus]

    # ------------------------------------------------------------------
    # Build / add  (API invariata)
    # ------------------------------------------------------------------

    def build(self, documents: list[Document]) -> None:
        """Costruisce l'indice da zero per tutti i corpus."""
        self._reset()
        self.add_documents_batch(documents)

    def add_documents_batch(self, docs: list[Document]) -> None:
        """Aggiunge documenti ai sub-indici appropriati (raggruppati per corpus)."""
        by_corpus: dict[str, list[Document]] = {}
        for doc in docs:
            c = doc.metadata.get("corpus", "studio")
            by_corpus.setdefault(c, []).append(doc)
        for corpus, cdocs in by_corpus.items():
            self._get_or_create_sub(corpus).add(cdocs)
        total = sum(len(v) for v in by_corpus.values())
        logger.debug(f"BM25: {len(docs)} doc aggiunti (corpora: {list(by_corpus)})")

    # ------------------------------------------------------------------
    # Search  (API invariata)
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 15,
        chunk_filter: Optional[dict] = None,
    ) -> list[SearchResult]:
        """
        Ricerca BM25 con filtraggio opzionale per subset.

        Se chunk_filter contiene "corpus", interroga solo il sub-indice di quel corpus.
        Altrimenti interroga tutti i sub-indici e fa merge per score.

        Args:
            query:        testo della query
            top_k:        numero massimo di risultati
            chunk_filter: dizionario di filtri sui metadati.
                          Chiave speciale: "_source_id_in" → list[str] di sottostringhe.
        """
        target_corpus: Optional[str] = None
        if chunk_filter and "corpus" in chunk_filter:
            target_corpus = chunk_filter["corpus"]

        if target_corpus:
            # Corpus specifico: query solo su quel sub-indice (lazy load incluso)
            sub = self._subs.get(target_corpus)
            if sub is None:
                logger.warning(f"BM25: sub-indice '{target_corpus}' non trovato")
                return []
            return sub.search(query, top_k=top_k, chunk_filter=chunk_filter)

        # Tutti i corpus: raccoglie e merge per score
        # Il lazy load avviene dentro sub.search() per ogni sub
        all_results: list[SearchResult] = []
        for sub in self._subs.values():
            results = sub.search(query, top_k=top_k, chunk_filter=chunk_filter)
            all_results.extend(results)

        if not all_results:
            return []

        # Dedup per doc_id (tieni score più alto), poi sort
        seen: dict[str, SearchResult] = {}
        for r in all_results:
            if r.doc_id not in seen or r.score > seen[r.doc_id].score:
                seen[r.doc_id] = r
        sorted_results = sorted(seen.values(), key=lambda r: r.score, reverse=True)
        return sorted_results[:top_k]

    # ------------------------------------------------------------------
    # Persist  (API invariata)
    # ------------------------------------------------------------------

    def save(self) -> None:
        """
        Salva solo i sub-indici che hanno subito modifiche (dirty=True).
        I sub caricati da pkl (dirty=False) non vengono toccati, anche se
        hanno bm25=None (raw save da migrazione): BM25Okapi viene costruito
        corpus per corpus la prima volta che quel corpus viene ricercato.
        """
        saved = 0
        for sub in self._subs.values():
            if sub.dirty:
                sub.save()
                saved += 1
            elif not sub.index_path.exists() and sub.doc_ids:
                # sub in memoria ma senza pkl su disco → salva
                sub.save()
                saved += 1
        if saved == 0:
            logger.debug("BM25: nessun sub-indice da salvare (tutti in sync)")

        # bm25_meta.json aggregato per ispezione / kb_sync
        meta = {
            corpus: {"count": len(sub), "path": str(sub.index_path)}
            for corpus, sub in self._subs.items()
        }
        self._meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        """
        Ricarica tutti i sub-indici esistenti (retrocompatibilità / warm-up API).
        Equivalente a load_all() — preferire load_all() nel codice nuovo.
        """
        self.load_all()

    def _reset(self) -> None:
        """Svuota tutti i sub-indici."""
        for sub in self._subs.values():
            sub.reset()

    def _remove_corpus(self, corpus_value: str) -> None:
        """
        Rimuove tutti i chunk di un corpus specifico.
        Usato da build_indexes.py --corpus X per rebuild parziale.
        """
        sub = self._subs.get(corpus_value)
        if sub is None or len(sub) == 0:
            logger.info(f"BM25 _remove_corpus('{corpus_value}'): sub-indice vuoto o assente")
            return
        n = len(sub)
        sub.reset()
        logger.info(f"BM25 _remove_corpus('{corpus_value}'): rimossi {n:,} chunk")

    # ------------------------------------------------------------------
    # Properties aggregate (usate da build_jurisprudence_indexes.py)
    # ------------------------------------------------------------------

    @property
    def _doc_ids(self) -> list[str]:
        """Tutti i doc_id da tutti i sub-indici."""
        result: list[str] = []
        for sub in self._subs.values():
            result.extend(sub.doc_ids)
        return result

    @property
    def _doc_metadata(self) -> list[dict]:
        result: list[dict] = []
        for sub in self._subs.values():
            result.extend(sub.doc_metadata)
        return result

    @property
    def _corpus(self) -> list[list[str]]:
        """Corpus tokenizzato aggregato (per retrocompatibilità con kb_sync/tests)."""
        result: list[list[str]] = []
        for sub in self._subs.values():
            result.extend(sub.tokenized)
        return result

    def __len__(self) -> int:
        return sum(len(sub) for sub in self._subs.values())

    # ------------------------------------------------------------------
    # Migrazione legacy bm25.pkl → 4 pkl per-corpus
    # ------------------------------------------------------------------

    def _maybe_migrate_legacy(self) -> None:
        """
        Se esiste bm25.pkl (legacy monolitico) ma nessun pkl per-corpus,
        ripartiziona il corpus esistente nei 4 sub-indici e salva.

        Non ri-tokenizza nulla: usa il corpus già tokenizzato nel pkl legacy.
        Tempo stimato: ~5-15 secondi.
        """
        legacy = self._ws / "indices" / "bm25.pkl"
        if not legacy.exists():
            return
        # Se almeno uno dei sub-indici per-corpus esiste, la migrazione è già avvenuta
        if any(sub.index_path.exists() for sub in self._subs.values()):
            return

        logger.info("BM25: rilevato pkl legacy monolitico — avvio migrazione per-corpus...")
        try:
            with open(legacy, "rb") as f:
                state = pickle.load(f)
        except Exception as e:
            logger.error(f"BM25: impossibile leggere bm25.pkl legacy: {e}")
            return

        doc_ids        = state.get("doc_ids", [])
        doc_snippets   = state.get("doc_snippets", [])
        doc_metadata   = state.get("doc_metadata", [])
        doc_source_ids = state.get("doc_source_ids", [])
        tokenized      = state.get("corpus", [])   # campo "corpus" nel pkl legacy = tokenized
        chunk_meta     = state.get("chunk_meta", {})

        # Raggruppa per corpus
        by_corpus: dict[str, list[int]] = {}
        for i, meta in enumerate(doc_metadata):
            c = meta.get("corpus", "studio")
            by_corpus.setdefault(c, []).append(i)

        for corpus, indices in by_corpus.items():
            sub = self._get_or_create_sub(corpus)
            for i in indices:
                sub.doc_ids.append(doc_ids[i])
                sub.doc_snippets.append(doc_snippets[i] if i < len(doc_snippets) else "")
                sub.doc_metadata.append(doc_metadata[i])
                sub.doc_source_ids.append(doc_source_ids[i] if i < len(doc_source_ids) else "")
                if i < len(tokenized):
                    sub.tokenized.append(tokenized[i])
            sub.chunk_meta.update({
                k: v for k, v in chunk_meta.items()
                if k in set(sub.doc_ids)
            })
            sub.dirty = True
            sub._rebuild_filter_arrays()
            logger.info(f"BM25 migrazione: corpus='{corpus}' → {len(indices):,} doc")

        # Salva i nuovi sub-indici SENZA costruire BM25Okapi (raw save).
        # BM25Okapi verrà costruito corpus per corpus al primo search/save
        # successivo — evita di ricostruire 470k doc all'avvio.
        for corpus in by_corpus:
            self._subs[corpus]._save_raw()

        # Aggiorna bm25_meta.json aggregato
        meta = {
            c: {"count": len(sub), "path": str(sub.index_path)}
            for c, sub in self._subs.items()
        }
        self._meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # Rinomina il legacy per non ri-triggerare la migrazione
        legacy.rename(legacy.with_suffix(".pkl.migrated"))
        logger.success(
            "BM25: migrazione completata in pochi secondi. "
            f"bm25.pkl rinominato in bm25.pkl.migrated. "
            f"Corpus: {list(by_corpus)}. "
            "BM25Okapi verra' costruito corpus per corpus al primo uso."
        )
