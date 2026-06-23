"""
BM25 Retriever — bm25s (Fase 1) con indici per-corpus separati.

Ogni corpus ha il suo pkl:  bm25_normattiva.pkl, bm25_dottrina.pkl,
                             bm25_studio.pkl, bm25_giurisprudenza.pkl

Vantaggi rispetto al pkl monolitico:
  - Aggiornare dottrina (191k) non tocca normattiva (278k) o giurisprudenza
  - save() ricostruisce l'indice solo per i sub-indici modificati
  - Migrazione automatica da bm25.pkl legacy al primo avvio

Cambio backend (Fase 1 — ESITO A spike bm25s):
  - bm25s al posto di rank_bm25 (BM25Okapi)
  - 220x piu' veloce in query (4.6ms vs 1013ms su 500k doc)
  - Full-text indicizzato (rimosso il troncamento text[:200])

Schema versione:
  _BM25_SCHEMA_VERSION = 2 (Fase 1: bm25s + full-text)
  Se il pkl caricato ha schema < 2, il sub-indice viene marcato dirty
  e ricostruito al prossimo save().
"""
from __future__ import annotations

import json
import pickle
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger

from aiura_legal.core.types import Document, SearchResult
from aiura_legal.core.retrieval.debug_log import rlog, rlog_sources

# Schema version — incrementa per forzare rebuild automatico dei pkl esistenti
_BM25_SCHEMA_VERSION = 2

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
    "e'", "sono", "ha", "hanno", "era", "were", "the", "of", "and",
    "quale", "quali", "questo", "questa", "questi", "queste",
    "dopo", "prima", "oltre", "anche", "come", "quando", "dove",
    "all", "dell", "nell",
})


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\w+", text.lower())
    return [t for t in tokens if len(t) >= 2 and t not in _IT_STOPWORDS]


# ─────────────────────────────────────────────────────────────────────────────
# _BM25Sub — sub-indice per un singolo corpus (backend: bm25s)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class _BM25Sub:
    """
    Indice BM25 per un singolo corpus.
    Gestisce load/save/add/search/reset in modo completamente indipendente.
    Backend: bm25s (Fase 1, ESITO A).
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

    # Stato bm25s
    _bm25s_retriever: object = field(default=None, repr=False)
    dirty: bool = False

    # Array numpy per filtri vettorizzati — precalcolati su doc_metadata
    corpus_arr:     np.ndarray = field(default_factory=lambda: np.array([], dtype=object), repr=False)
    fonte_arr:      np.ndarray = field(default_factory=lambda: np.array([], dtype=object), repr=False)
    testo_tipo_arr: np.ndarray = field(default_factory=lambda: np.array([], dtype=object), repr=False)

    # Lock per il lazy-load: search() viene chiamato da thread diversi via
    # asyncio.to_thread() che condividono la stessa istanza — senza lock,
    # più thread superano il check "if not self.doc_ids" prima che uno dei
    # due imposti lo stato, causando caricamenti duplicati concorrenti da
    # disco (osservato: stesso pkl caricato 3 volte sotto query parallele).
    _load_lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

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
            # Fase 1: indicizza il testo completo del chunk (rimosso troncamento text[:200])
            # Per normattiva/dottrina: sommario + titolo_articolo + text (full)
            # Per giurisprudenza: text completo del chunk (gia' spezzato dal Chunker)
            sommario = doc.metadata.get("sommario", "") or ""
            titolo   = doc.metadata.get("titolo_articolo", "") or ""
            # Full-text: usa il testo completo del chunk, non i primi 200 caratteri
            indexed_text = f"{sommario} {titolo} {doc.text}".strip()
            # Fallback: se tutti i campi sono vuoti, usa text — mai stringa vuota nel corpus BM25
            if not indexed_text:
                indexed_text = doc.text if doc.text else " "
            tokens = _tokenize(indexed_text)
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
        self._bm25s_retriever = None
        self.dirty          = False
        self.corpus_arr = self.fonte_arr = self.testo_tipo_arr = np.array([], dtype=object)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _ensure_bm25s(self) -> None:
        """Costruisce (o ricostruisce) l'indice bm25s se dirty."""
        if not (self.dirty or self._bm25s_retriever is None):
            return
        with self._load_lock:
            if not (self.dirty or self._bm25s_retriever is None):
                return
            if self.tokenized:
                import bm25s
                logger.info(f"BM25[{self.corpus}]: build bm25s su {len(self.tokenized):,} doc...")
                corpus_tokens = [" ".join(t) for t in self.tokenized]
                retriever = bm25s.BM25()
                retriever.index(bm25s.tokenize(corpus_tokens, stopwords=None))
                self._bm25s_retriever = retriever
                logger.info(f"BM25[{self.corpus}]: pronto (bm25s)")
            else:
                self._bm25s_retriever = None
            self.dirty = False

    def search(
        self,
        query: str,
        top_k: int = 15,
        chunk_filter: Optional[dict] = None,
    ) -> list[SearchResult]:
        # Lazy load: carica da disco se il sub non e' ancora in memoria.
        # Double-checked locking: il secondo check (dentro il lock) evita che
        # un thread arrivato dopo un altro rilanci il load già completato.
        if not self.doc_ids and self.index_path.exists():
            with self._load_lock:
                if not self.doc_ids and self.index_path.exists():
                    self.load()
        self._ensure_bm25s()
        if self._bm25s_retriever is None or not self.tokenized:
            return []

        import bm25s
        tokens = _tokenize(query)
        q_str = " ".join(tokens)
        n_docs = len(self.doc_ids)
        k_req = min(top_k, n_docs)
        if k_req == 0:
            return []

        # Recupera tutti gli score per poi applicare i filtri
        try:
            results_idx, scores_arr = self._bm25s_retriever.retrieve(
                bm25s.tokenize([q_str], stopwords=None), k=n_docs
            )
            # results_idx shape: (1, n_docs), scores_arr shape: (1, n_docs)
            indices = results_idx[0].tolist()
            scores_raw = scores_arr[0].tolist()
        except Exception as exc:
            logger.warning(f"BM25s search fallita: {exc}")
            return []

        # Ricostruisce array score nella posizione originale per filtri vettorizzati
        scores: np.ndarray = np.zeros(n_docs, dtype=float)
        for pos, (idx, sc) in enumerate(zip(indices, scores_raw)):
            if 0 <= idx < n_docs:
                scores[idx] = float(sc)

        # Filtro corpus (chiave speciale)
        source_id_in: list[str] = []
        meta_filter: dict = {}
        if chunk_filter:
            for k, v in chunk_filter.items():
                if k == "_source_id_in":
                    source_id_in = list(v) if v else []
                elif k != "corpus":   # corpus e' gia' selezionato dal sub
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

        rlog(f"BM25:{self.corpus}",
             f"filter={chunk_filter} total_docs={n_docs} "
             f"non_zero_scores={int((scores > 0).sum())} → top{len(results)}")
        rlog_sources(f"BM25:{self.corpus}:top", results)
        return results

    # ------------------------------------------------------------------
    # Persist
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Salva il sub-indice. Costruisce bm25s se dirty, lo include nel pkl."""
        self._ensure_bm25s()
        self._save_state()

    def _save_raw(self) -> None:
        """Salva senza costruire bm25s (usato durante migrazione da pkl legacy)."""
        self._save_state()
        self.dirty = False

    def _save_state(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "schema_version": _BM25_SCHEMA_VERSION,
            "corpus":         self.corpus,
            "bm25s":          self._bm25s_retriever,
            "doc_ids":        self.doc_ids,
            "doc_snippets":   self.doc_snippets,
            "doc_metadata":   self.doc_metadata,
            "doc_source_ids": self.doc_source_ids,
            "tokenized":      self.tokenized,
            "chunk_meta":     self.chunk_meta,
        }
        with open(self.index_path, "wb") as f:
            pickle.dump(state, f)
        logger.info(f"BM25[{self.corpus}]: salvato {len(self.doc_ids):,} doc -> {self.index_path}")

    def load(self) -> None:
        """Carica da pkl. Se schema < 2, forza dirty per rebuild con bm25s+full-text."""
        with open(self.index_path, "rb") as f:
            state = pickle.load(f)
        schema_ver = state.get("schema_version", 1)
        self.doc_ids        = state["doc_ids"]
        self.doc_snippets   = state["doc_snippets"]
        self.doc_metadata   = state["doc_metadata"]
        self.doc_source_ids = state["doc_source_ids"]
        self.tokenized      = state.get("tokenized", state.get("corpus", []))  # compat legacy
        self.chunk_meta     = state.get("chunk_meta", {})
        self._bm25s_retriever = state.get("bm25s")  # None se pkl da schema v1
        self._rebuild_filter_arrays()
        logger.info(f"BM25[{self.corpus}]: caricato {len(self.doc_ids):,} doc da {self.index_path}")
        if schema_ver < _BM25_SCHEMA_VERSION:
            logger.info(
                f"BM25[{self.corpus}]: schema v{schema_ver} -> v{_BM25_SCHEMA_VERSION} "
                f"— marca dirty per rebuild con bm25s+full-text"
            )
            self.dirty = True
            self._bm25s_retriever = None

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
    L'API pubblica e' identica alla versione precedente monolitica.

    File:
      workspaces/<ws>/indices/bm25_normattiva.pkl
      workspaces/<ws>/indices/bm25_dottrina.pkl
      workspaces/<ws>/indices/bm25_studio.pkl
      workspaces/<ws>/indices/bm25_giurisprudenza.pkl

    Migrazione automatica: se esiste bm25.pkl (legacy) ma non i 4 separati,
    la migrazione avviene in __init__ (~5-15 secondi, nessun re-tokenize).
    Schema upgrade: pkl con schema_version < 2 vengono ricostruiti con bm25s.
    """

    def __init__(self, workspace_path: str) -> None:
        self._ws = Path(workspace_path)
        # Retrocompatibilita': path del pkl legacy (non piu' usato dopo migrazione)
        self._index_path = self._ws / "indices" / "bm25.pkl"
        self._meta_path  = self._ws / "indices" / "bm25_meta.json"

        # Sub-indici per corpus — caricati LAZY al primo search()
        # build_indexes.py non cerca mai -> non carica pkl inutili
        self._subs: dict[str, _BM25Sub] = {}
        for corpus in _KNOWN_CORPORA:
            self._subs[corpus] = _BM25Sub(corpus=corpus, ws=self._ws)

        # Migrazione da pkl monolitico legacy (fast: raw save, no rebuild)
        self._maybe_migrate_legacy()

    def load_all(self) -> None:
        """Carica tutti i sub-indici da disco (warm-up esplicito per API)."""
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
                          Chiave speciale: "_source_id_in" -> list[str] di sottostringhe.
        """
        target_corpus: Optional[str] = None
        if chunk_filter and "corpus" in chunk_filter:
            target_corpus = chunk_filter["corpus"]

        if target_corpus:
            sub = self._subs.get(target_corpus)
            if sub is None:
                logger.warning(f"BM25: sub-indice '{target_corpus}' non trovato")
                rlog("BM25:router", f"⚠ sub-indice '{target_corpus}' non trovato")
                return []
            rlog("BM25:router", f"→ corpus={target_corpus} (filtro specifico)")
            return sub.search(query, top_k=top_k, chunk_filter=chunk_filter)

        # Tutti i corpus: raccoglie e merge per score
        rlog("BM25:router",
             f"→ ALL corpora={list(self._subs.keys())} (nessun filtro corpus — attenzione a dilution)")
        all_results: list[SearchResult] = []
        for sub in self._subs.values():
            results = sub.search(query, top_k=top_k, chunk_filter=chunk_filter)
            all_results.extend(results)

        if not all_results:
            return []

        # Dedup per doc_id (tieni score piu' alto), poi sort
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
        """Salva solo i sub-indici che hanno subito modifiche (dirty=True)."""
        saved = 0
        for corpus, sub in self._subs.items():
            logger.debug(
                f"BM25.save(): corpus={corpus!r} doc_ids={len(sub.doc_ids)} "
                f"dirty={sub.dirty} pkl_exists={sub.index_path.exists()}"
            )
            if sub.dirty:
                sub.save()
                saved += 1
            elif not sub.index_path.exists() and sub.doc_ids:
                sub.save()
                saved += 1
        if saved == 0:
            logger.info("BM25.save(): nessun sub-indice da salvare (tutti dirty=False o doc_ids=0)")

        # bm25_meta.json aggregato per ispezione / kb_sync
        meta = {
            corpus: {"count": len(sub), "path": str(sub.index_path)}
            for corpus, sub in self._subs.items()
        }
        self._meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        """Ricarica tutti i sub-indici esistenti (retrocompatibilita' / warm-up API)."""
        self.load_all()

    def _reset(self) -> None:
        """Svuota tutti i sub-indici."""
        for sub in self._subs.values():
            sub.reset()

    def _remove_corpus(self, corpus_value: str) -> None:
        """Rimuove tutti i chunk di un corpus specifico."""
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
        """Corpus tokenizzato aggregato (per retrocompatibilita' con kb_sync/tests)."""
        result: list[list[str]] = []
        for sub in self._subs.values():
            result.extend(sub.tokenized)
        return result

    def __len__(self) -> int:
        return sum(len(sub) for sub in self._subs.values())

    def __bool__(self) -> bool:
        # Sempre True: l'oggetto e' valido indipendentemente dal numero di doc
        # caricati in memoria (i sub-indici sono lazy-loaded da pkl).
        return True

    # ------------------------------------------------------------------
    # Migrazione legacy bm25.pkl -> 4 pkl per-corpus
    # ------------------------------------------------------------------

    def _maybe_migrate_legacy(self) -> None:
        """
        Se esiste bm25.pkl (legacy monolitico) ma nessun pkl per-corpus,
        ripartiziona il corpus esistente nei 4 sub-indici e salva.

        Non ri-tokenizza nulla: usa il corpus gia' tokenizzato nel pkl legacy.
        Tempo stimato: ~5-15 secondi.
        """
        legacy = self._ws / "indices" / "bm25.pkl"
        if not legacy.exists():
            return
        if all(sub.index_path.exists() for sub in self._subs.values()):
            logger.info(
                "BM25: tutti i pkl per-corpus gia' presenti — "
                "rinomino bm25.pkl legacy senza caricarlo."
            )
            legacy.rename(legacy.with_suffix(".pkl.migrated"))
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
            if sub.index_path.exists():
                logger.info(
                    f"BM25 migrazione: corpus='{corpus}' — pkl gia' presente, skip"
                )
                continue
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
            # Schema v1: marca dirty per rebuild con bm25s al primo use
            sub.dirty = True
            sub._rebuild_filter_arrays()
            logger.info(f"BM25 migrazione: corpus='{corpus}' -> {len(indices):,} doc")

        # Salva i nuovi sub-indici SENZA costruire bm25s (raw save, lazy build)
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
            "BM25: migrazione completata. "
            f"bm25.pkl rinominato in bm25.pkl.migrated. "
            f"Corpus: {list(by_corpus)}. "
            "bm25s verra' costruito corpus per corpus al primo uso."
        )
