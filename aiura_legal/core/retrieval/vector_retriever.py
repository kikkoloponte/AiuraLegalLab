"""
Vector Retriever — Qdrant server mode (Docker) con fallback embedded.

Modello: paraphrase-multilingual-MiniLM-L12-v2 (384 dim, cosine).

Connessione:
  - Server mode (preferito): QDRANT_URL=http://localhost:6333  → nessun limite di punti
  - Embedded fallback: se QDRANT_URL non è configurato → usa path locale

Qdrant è 5-10x più veloce di ChromaDB per volumi > 500k chunk:
  - Indice HNSW in Rust vs Python
  - Batch embedding diretto con SentenceTransformer (batch_size=256)
  - Filtri payload nativi ad alte prestazioni
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Optional

from loguru import logger

from aiura_legal.core.types import Document, SearchResult

_EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
_COLLECTION_NAME = "legal_docs"
_VECTOR_SIZE     = 384       # dimensioni MiniLM-L12-v2
_EMBED_BATCH     = 256       # batch embedding


# ---------------------------------------------------------------------------
# Helpers ID e filtri
# ---------------------------------------------------------------------------

def _to_qdrant_id(doc_id: str) -> str:
    """
    Converte qualsiasi ID stringa in un UUID v5 Qdrant valido.

    Gestisce due formati:
    - MongoDB ObjectId (24 hex chars):   "507f1f77bcf86cd799439011"
    - Giurisprudenza (hex16_tipo):        "e65a598d71052357_massima"

    Usa uuid.uuid5(NAMESPACE_DNS, doc_id) per produrre un UUID deterministico
    e stabile — stesso input → stesso UUID sempre.
    """
    import uuid
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))


def _date_to_int(d: date) -> int:
    """Converte date in YYYYMMDD intero per range filter numerico."""
    return int(d.strftime("%Y%m%d"))


def _parse_date_int(s: str) -> Optional[int]:
    """Parsa stringa YYYYMMDD (o YYYY-MM-DD) in int. None se non valida."""
    if not s:
        return None
    try:
        return int(s.replace("-", "")[:8])
    except (ValueError, TypeError):
        return None


def _flatten_chroma_filter(f: dict) -> dict[str, object]:
    """
    Semplifica un filtro ChromaDB-style in coppie chiave→valore/lista.

    Supporta:
      {"corpus": "normattiva"}
      {"$and": [{"corpus": "normattiva"}, {"fonte": "legge"}]}
      {"fonte": {"$in": ["legge", "dlgs"]}}
    """
    result: dict[str, object] = {}
    if "$and" in f:
        for sub in f["$and"]:
            result.update(_flatten_chroma_filter(sub))
    elif "$or" in f:
        if f["$or"]:
            result.update(_flatten_chroma_filter(f["$or"][0]))
    else:
        for k, v in f.items():
            if k.startswith("$"):
                continue
            if isinstance(v, dict) and "$in" in v:
                result[k] = v["$in"]          # lista → MatchAny
            elif isinstance(v, dict) and "$lte" in v:
                result[f"__lte__{k}"] = v["$lte"]  # range lte
            else:
                result[k] = v                  # valore esatto → MatchValue
    return result


def _build_qdrant_filter(
    chunk_filter: Optional[dict],
    valid_on: Optional[date],
):
    """
    Costruisce un Qdrant Filter da chunk_filter ChromaDB-style e valid_on.
    Ritorna None se nessun filtro è necessario.
    """
    from qdrant_client.models import (
        Filter, FieldCondition, MatchValue, MatchAny, Range,
    )

    conditions = []

    if valid_on:
        d_int = _date_to_int(valid_on)
        conditions.append(
            FieldCondition(key="valid_from_int", range=Range(lte=d_int))
        )

    if chunk_filter:
        flat = _flatten_chroma_filter(chunk_filter)
        for k, v in flat.items():
            if k.startswith("__lte__"):
                real_key = k[7:]
                val_int = _parse_date_int(str(v))
                if val_int:
                    conditions.append(
                        FieldCondition(key=f"{real_key}_int", range=Range(lte=val_int))
                    )
            elif isinstance(v, list):
                conditions.append(
                    FieldCondition(key=k, match=MatchAny(any=[str(x) for x in v]))
                )
            else:
                conditions.append(
                    FieldCondition(key=k, match=MatchValue(value=str(v)))
                )

    if not conditions:
        return None
    return Filter(must=conditions)


# ---------------------------------------------------------------------------
# VectorRetriever
# ---------------------------------------------------------------------------

class VectorRetriever:
    """
    Retriever vettoriale su Qdrant.

    Modalità:
      - Server (Docker): QDRANT_URL=http://localhost:6333 in .env
      - Embedded (fallback): dati in workspaces/<nome>/indices/qdrant/

    L'interfaccia è identica al precedente ChromaDB retriever — nessun
    altro file del progetto necessita modifiche.
    """

    def __init__(self, workspace_path: str) -> None:
        self._ws = Path(workspace_path)
        self._qdrant_path = str(self._ws / "indices" / "qdrant")
        self._client = None
        self._model = None
        self._mode: str = "embedded"
        self._init_qdrant()

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def _init_qdrant(self) -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff

            qdrant_url = os.environ.get("QDRANT_URL", "").strip()

            if qdrant_url:
                # ── Server mode (Docker) ──────────────────────────────
                self._client = QdrantClient(url=qdrant_url, timeout=30)
                self._mode = "server"
                logger.info(f"Qdrant: server mode → {qdrant_url}")
            else:
                # ── Embedded mode (fallback) ──────────────────────────
                Path(self._qdrant_path).mkdir(parents=True, exist_ok=True)
                self._client = QdrantClient(path=self._qdrant_path)
                self._mode = "embedded"
                logger.info(f"Qdrant: embedded mode → {self._qdrant_path}")

            # Crea la collection se non esiste
            existing = [c.name for c in self._client.get_collections().collections]
            if _COLLECTION_NAME not in existing:
                self._client.create_collection(
                    collection_name=_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=_VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        indexing_threshold=20_000,
                    ),
                )
                logger.info(f"Qdrant: collection '{_COLLECTION_NAME}' creata ({self._mode})")
            else:
                count = self._client.count(_COLLECTION_NAME).count
                logger.info(
                    f"Qdrant pronto [{self._mode}]: {count:,} punti"
                )

        except ImportError:
            logger.error(
                "qdrant-client non installato. Esegui: pip install qdrant-client"
            )
        except Exception as e:
            logger.error(f"Qdrant init fallita: {e}")

    def _get_model(self):
        """Lazy load del modello SentenceTransformer."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Caricamento modello embedding: {_EMBED_MODEL}")
            self._model = SentenceTransformer(_EMBED_MODEL)
        return self._model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Embedding batch con SentenceTransformer."""
        model = self._get_model()
        vecs = model.encode(
            texts,
            batch_size=_EMBED_BATCH,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vecs.tolist()

    # ------------------------------------------------------------------
    # Build / add
    # ------------------------------------------------------------------

    def add_documents_batch(
        self,
        docs: list[Document],
        batch_size: int = 512,
        skip_existing: bool = True,
    ) -> None:
        """
        Aggiunge documenti in batch a Qdrant.

        Args:
            docs:          documenti da indicizzare
            batch_size:    dimensione batch upsert (512 server, 256 embedded)
            skip_existing: se True (default), controlla quali UUID esistono già
                           in Qdrant e li salta — evita re-embedding inutili.
                           Impostare a False solo dopo un cambio modello embedding
                           (usa --force-reindex in build_indexes.py).
        """
        if not self._client:
            return

        effective_batch = batch_size if self._mode == "server" else min(batch_size, 256)

        from qdrant_client.models import PointStruct

        total_skipped = 0
        total_upserted = 0

        for i in range(0, len(docs), effective_batch):
            batch = docs[i : i + effective_batch]

            # ── Skip-existing: controlla quali UUID sono già in Qdrant ──
            if skip_existing:
                uuids = [_to_qdrant_id(d.id) for d in batch]
                try:
                    existing = self._client.retrieve(
                        collection_name=_COLLECTION_NAME,
                        ids=uuids,
                        with_payload=False,
                        with_vectors=False,
                    )
                    existing_set = {str(p.id) for p in existing}
                except Exception as e:
                    logger.warning(f"Qdrant retrieve fallito, procedo senza skip: {e}")
                    existing_set = set()

                to_embed = [
                    d for d, uid in zip(batch, uuids)
                    if uid not in existing_set
                ]
                skipped = len(batch) - len(to_embed)
                total_skipped += skipped
                if skipped:
                    logger.debug(
                        f"Qdrant skip-existing: batch {i//effective_batch+1} "
                        f"— saltati {skipped}/{len(batch)} già presenti"
                    )
            else:
                to_embed = batch

            if not to_embed:
                continue

            vectors = self._embed([d.text for d in to_embed])

            points = []
            for doc, vec in zip(to_embed, vectors):
                payload = {
                    **{k: str(v) for k, v in doc.metadata.items()},
                    "source_id":      doc.source_id,
                    # ID originale (Mongo _id o jdoc_id_tipo): consente la fusione
                    # RRF con i risultati BM25/graph e l'esposizione dell'ID
                    # originale nel Research Packet (S5/frontend ne dipendono).
                    "mongo_id":       doc.id,
                    "text":           doc.text[:1000],
                    "valid_from_int": _parse_date_int(
                        str(doc.metadata.get("valid_from", ""))
                    ) or 0,
                    "valid_to_int":   _parse_date_int(
                        str(doc.metadata.get("valid_to", ""))
                    ) or 99999999,
                }
                if doc.metadata.get("workspace"):
                    payload["workspace"] = str(doc.metadata["workspace"])
                points.append(PointStruct(
                    id=_to_qdrant_id(doc.id),
                    vector=vec,
                    payload=payload,
                ))

            self._client.upsert(
                collection_name=_COLLECTION_NAME,
                points=points,
                wait=True,
            )
            total_upserted += len(points)

        if total_skipped:
            logger.info(
                f"Qdrant [{self._mode}]: {total_upserted} upsertati, "
                f"{total_skipped} saltati (già esistenti)"
            )
        else:
            logger.debug(f"Qdrant [{self._mode}]: {total_upserted} punti upsertati")

    def build(self, documents: list[Document]) -> None:
        self.add_documents_batch(documents)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 15,
        valid_on: Optional[date] = None,
        chunk_filter: Optional[dict] = None,
    ) -> list[SearchResult]:
        """
        Ricerca vettoriale con filtro opzionale per corpus/fonte/valid_on.

        chunk_filter accetta lo stesso formato ChromaDB:
          {"corpus": "normattiva"}
          {"$and": [{"corpus": "normattiva"}, {"fonte": "legge"}]}
          {"fonte": {"$in": ["legge", "dlgs"]}}
        """
        if not self._client:
            return []

        try:
            query_vec = self._embed([query])[0]
            qdrant_filter = _build_qdrant_filter(chunk_filter, valid_on)

            response = self._client.query_points(
                collection_name=_COLLECTION_NAME,
                query=query_vec,
                query_filter=qdrant_filter,
                limit=top_k,
                with_payload=True,
            )
            hits = response.points
        except Exception as e:
            logger.error(f"Qdrant search fallita [{self._mode}]: {e}")
            return []

        results = []
        for hit in hits:
            payload = hit.payload or {}
            score = float(hit.score)
            # Punti nuovi: il payload contiene mongo_id (ID originale) → usalo
            # come doc_id, coerente con BM25/graph. Punti legacy: fallback
            # all'UUID Qdrant (la fusione RRF lo gestisce in _fusion_key).
            doc_id = str(payload.get("mongo_id") or hit.id)
            results.append(SearchResult(
                doc_id=doc_id,
                score=score,
                snippet=str(payload.get("text", ""))[:300] if "text" in payload else "",
                metadata={k: v for k, v in payload.items()
                          if not k.endswith("_int")},
                source_id=payload.get("source_id", ""),
                retrieval_method="vector",
            ))
        return results

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    def save(self) -> None:
        """
        Forza ottimizzazione HNSW finale.
        In server mode imposta indexing_threshold=0 per forzare la build.
        """
        if self._client:
            try:
                from qdrant_client.models import OptimizersConfigDiff
                self._client.update_collection(
                    collection_name=_COLLECTION_NAME,
                    optimizer_config=OptimizersConfigDiff(indexing_threshold=0),
                )
                logger.info(f"Qdrant [{self._mode}]: ottimizzazione HNSW avviata")
            except Exception as e:
                logger.warning(f"Qdrant save: {e}")
        logger.info(
            f"Qdrant [{self._mode}]: dati persistiti"
            + (f" in {self._qdrant_path}" if self._mode == "embedded" else " (server Docker)")
        )

    def count(self) -> int:
        if not self._client:
            return 0
        try:
            return self._client.count(_COLLECTION_NAME).count
        except Exception:
            return 0

    def _init_chroma(self) -> None:
        """Stub di compatibilità — chiamato da build_indexes.py per il reset."""
        if self._client:
            try:
                from qdrant_client.models import Distance, VectorParams
                existing = [c.name for c in self._client.get_collections().collections]
                if _COLLECTION_NAME in existing:
                    self._client.delete_collection(_COLLECTION_NAME)
                self._client.create_collection(
                    collection_name=_COLLECTION_NAME,
                    vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
                )
                logger.info(f"Qdrant [{self._mode}]: collection ricreata da zero")
            except Exception as e:
                logger.warning(f"Qdrant reset: {e}")
