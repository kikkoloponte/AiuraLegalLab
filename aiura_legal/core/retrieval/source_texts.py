"""
Source Texts — recupero del testo completo per i SearchResult.

Dopo il retrieval, i SearchResult contengono solo snippet (~300 char): troppo
poco perché l'LLM ragioni sul contenuto reale delle fonti — il modello tende a
completare il testo delle norme dal pretraining, attaccando source_id validi
a contenuti inventati. Questo modulo recupera il testo pieno da MongoDB:

  - normattiva / dottrina / studio / prassi → aiura_legal_lab_db.chunks
    (campo text, lookup per _id)
  - giurisprudenza (chunk monolitico legacy):
      aiura_legal_lab_db.jurisprudence (campi massima/motivazione/dispositivo)
  - giurisprudenza (sub-chunk Fase 1, ID: {hex16}_motivazione_{i:03d}):
      aiura_legal_lab_db.chunks (campo text, lookup per _id diretto)

Usa pymongo sync: il punto di integrazione (orchestrator/analyst) lo invoca
via asyncio.to_thread, coerente con come l'orchestrator chiama S2.

Documento mancante o MongoDB non raggiungibile → full_text resta vuoto e il
chiamante usa lo snippet come fallback. Mai eccezioni.

Feature flag: AIURA_FULLTEXT_CONTEXT (default "1").
A "0" il fetch viene saltato e il prompt torna agli snippet (rollback).
"""
from __future__ import annotations

import asyncio
import os
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.core.types import SearchResult

import re

_CHUNKS_COLLECTION = "chunks"
_JURISPRUDENCE_COLLECTION = "jurisprudence"
_GIURI_TEXT_FIELDS = ("massima", "motivazione", "dispositivo")

# Regex per riconoscere i sub-chunk Fase 1 (es. e65a598d71052357_motivazione_003)
# Distingue dal chunk monolitico legacy (e65a598d71052357_motivazione senza indice)
_GIURI_SUB_CHUNK_RE = re.compile(r"^([0-9a-f]{16})_(motivazione)_(\d{3})$")


class SourceTextsSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "aiura_legal_lab_db"


_settings = SourceTextsSettings()

# Client pymongo condiviso (lazy) — il fetch gira in thread via asyncio.to_thread
_client = None


def fulltext_enabled() -> bool:
    """Flag AIURA_FULLTEXT_CONTEXT — letto a ogni chiamata (rollback = flip env)."""
    return os.getenv("AIURA_FULLTEXT_CONTEXT", "1") == "1"


def _get_db():
    global _client
    if _client is None:
        import pymongo
        _client = pymongo.MongoClient(
            _settings.mongodb_uri, serverSelectionTimeoutMS=5000
        )
    return _client[_settings.mongodb_database]


def fetch_sources_by_source_id(
    source_ids: list[str],
    source_layer: str = "normativa",
    db=None,
) -> list[SearchResult]:
    """
    Recupera SearchResult GARANTITI per source_id esatto (lookup diretto in
    chunks). Usato per iniettare nel packet fonti "must-have" individuate dal
    registro istituti: la norma cardine di un istituto (Fase 2) e le sentenze
    pilota groundabili (Fase 3), così non dipendono dal ranking del retrieval.

    Ritorna un SearchResult per ciascun source_id trovato (il primo chunk),
    con full_text già popolato. Mai eccezioni: in errore ritorna [].
    """
    ids = [s for s in dict.fromkeys(source_ids) if s]
    if not ids:
        return []
    try:
        if db is None:
            db = _get_db()
        out: list[SearchResult] = []
        seen: set[str] = set()
        for doc in db[_CHUNKS_COLLECTION].find({"source_id": {"$in": ids}}):
            sid = str(doc.get("source_id", ""))
            if not sid or sid in seen:
                continue
            seen.add(sid)
            text = str(doc.get("text", ""))
            meta = {
                k: doc.get(k)
                for k in ("corpus", "fonte", "titolo", "titolo_articolo",
                          "articolo_num", "organo", "numero", "anno", "materia",
                          "chunk_type", "settore")
                if doc.get(k) is not None
            }
            out.append(SearchResult(
                doc_id=str(doc.get("_id", sid)),
                score=999.0,                # garantita: in cima al merge
                snippet=text[:400],
                source_id=sid,
                metadata=meta,
                source_layer=source_layer,
                full_text=text,
            ))
        return out
    except Exception as exc:  # noqa: BLE001 — iniezione best-effort, mai bloccante
        logger.warning(f"[SourceTexts] fetch_sources_by_source_id fallito ({exc})")
        return []


def _corpus_of(r: SearchResult) -> str:
    corpus = str((r.metadata or {}).get("corpus", "")).strip()
    return corpus or r.source_layer


def _is_giuri_sub_chunk(doc_id: str) -> bool:
    """True se doc_id è un sub-chunk Fase 1 (es. e65a598d71052357_motivazione_003)."""
    return bool(_GIURI_SUB_CHUNK_RE.match(doc_id))


def _giuri_lookup_key(r: SearchResult) -> tuple[Optional[str], Optional[str]]:
    """Ritorna (jdoc_id, chunk_type) dai metadata, con fallback sul doc_id "hex16_tipo".

    Per i sub-chunk Fase 1 ({hex16}_motivazione_{i:03d}) il lookup viene
    gestito separatamente via _is_giuri_sub_chunk: questa funzione non li elabora.
    """
    meta = r.metadata or {}
    jdoc_id = str(meta.get("jdoc_id", "")).strip() or None
    chunk_type = str(meta.get("chunk_type", "")).strip() or None
    if not jdoc_id or not chunk_type:
        # doc_id giurisprudenza legacy = f"{jdoc_id}_{chunk_type}"
        # (esclude i sub-chunk Fase 1 che hanno formato {hex16}_motivazione_{i:03d})
        parts = r.doc_id.rsplit("_", 1)
        if len(parts) == 2 and parts[1] in _GIURI_TEXT_FIELDS:
            jdoc_id = jdoc_id or parts[0]
            chunk_type = chunk_type or parts[1]
    if chunk_type not in _GIURI_TEXT_FIELDS:
        chunk_type = None
    return jdoc_id, chunk_type


def fetch_full_texts_sync(results: list[SearchResult], db=None) -> None:
    """
    Popola in-place SearchResult.full_text per ogni risultato che non lo ha già.

    Args:
        results: risultati da arricchire (modificati in-place)
        db:      database pymongo iniettabile per i test (default: da settings)

    Non solleva mai eccezioni: in caso di errore i full_text restano vuoti
    e il chiamante usa lo snippet.
    """
    todo = [r for r in results if not r.full_text]
    if not todo:
        return

    try:
        if db is None:
            db = _get_db()

        # ── Partiziona per tipo di lookup ─────────────────────────────
        chunk_results: list[SearchResult] = []
        giuri_results: list[SearchResult] = []       # chunk monolitici legacy
        giuri_sub_results: list[SearchResult] = []   # sub-chunk Fase 1 (→ chunks collection)
        for r in todo:
            if _corpus_of(r) == "giurisprudenza":
                if _is_giuri_sub_chunk(r.doc_id):
                    giuri_sub_results.append(r)  # lookup diretto in chunks
                else:
                    giuri_results.append(r)      # lookup legacy in jurisprudence
            else:
                chunk_results.append(r)

        # ── Corpus chunks: lookup batch per _id ───────────────────────
        if chunk_results:
            oid_map: dict = {}
            str_ids: list[str] = []
            for r in chunk_results:
                try:
                    oid_map[ObjectId(r.doc_id)] = r.doc_id
                except (InvalidId, TypeError):
                    str_ids.append(r.doc_id)

            texts_by_id: dict[str, str] = {}
            if oid_map:
                for doc in db[_CHUNKS_COLLECTION].find(
                    {"_id": {"$in": list(oid_map)}}, {"text": 1}
                ):
                    texts_by_id[oid_map[doc["_id"]]] = str(doc.get("text", ""))
            if str_ids:
                for doc in db[_CHUNKS_COLLECTION].find(
                    {"_id": {"$in": str_ids}}, {"text": 1}
                ):
                    texts_by_id[str(doc["_id"])] = str(doc.get("text", ""))

            for r in chunk_results:
                r.full_text = texts_by_id.get(r.doc_id, "")

        # ── Sub-chunk giurisprudenza Fase 1: lookup diretto in chunks ──
        if giuri_sub_results:
            sub_str_ids = [r.doc_id for r in giuri_sub_results]
            sub_texts: dict[str, str] = {}
            for doc in db[_CHUNKS_COLLECTION].find(
                {"_id": {"$in": sub_str_ids}}, {"text": 1}
            ):
                sub_texts[str(doc["_id"])] = str(doc.get("text", ""))
            for r in giuri_sub_results:
                r.full_text = sub_texts.get(r.doc_id, "")

        # ── Giurisprudenza legacy: lookup batch per jdoc_id ───────────
        if giuri_results:
            keys = [_giuri_lookup_key(r) for r in giuri_results]
            jdoc_ids = sorted({k[0] for k in keys if k[0]})
            docs_by_id: dict[str, dict] = {}
            if jdoc_ids:
                projection = {f: 1 for f in _GIURI_TEXT_FIELDS}
                for doc in db[_JURISPRUDENCE_COLLECTION].find(
                    {"_id": {"$in": jdoc_ids}}, projection
                ):
                    docs_by_id[str(doc["_id"])] = doc

            for r, (jdoc_id, chunk_type) in zip(giuri_results, keys):
                if not jdoc_id or not chunk_type:
                    continue
                doc = docs_by_id.get(jdoc_id)
                if doc is not None:
                    r.full_text = str(doc.get(chunk_type, "") or "")

        found = sum(1 for r in todo if r.full_text)
        logger.debug(f"[SourceTexts] full_text: {found}/{len(todo)} risultati arricchiti")

    except Exception as exc:  # noqa: BLE001 — fallback snippet, mai eccezioni
        logger.warning(f"[SourceTexts] fetch full_text fallito ({exc}) — fallback snippet")


async def fetch_full_texts(results: list[SearchResult], db=None) -> None:
    """Wrapper async: esegue il fetch sync in thread (come l'orchestrator con S2)."""
    if not fulltext_enabled():
        return
    await asyncio.to_thread(fetch_full_texts_sync, results, db)
