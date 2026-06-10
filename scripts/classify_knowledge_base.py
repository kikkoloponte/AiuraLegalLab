#!/usr/bin/env python3
"""classify_knowledge_base.py — Pipeline batch idempotente per classificazione KB.

Fasi:
  A — Classificazione atti normattiva (LLM, act-level)
  B — Generazione sommario normattiva (LLM, article-level)
  C — Giurisprudenza settore (rule-based, zero LLM)
  D — Dottrina settore (LLM, document-level)
  E — Prassi corpus (chunking + sommario)

Uso:
  python scripts/classify_knowledge_base.py --fase all
  python scripts/classify_knowledge_base.py --fase A --workspace mio-studio
  python scripts/classify_knowledge_base.py --fase C --batch-size 200
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import httpx
import pymongo
from loguru import logger

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LMSTUDIO_URL = os.environ.get("LMSTUDIO_URL", "http://127.0.0.1:1234")
# USE_LMSTUDIO=1 (default) usa LM Studio (OpenAI-compat /v1/chat/completions)
# USE_LMSTUDIO=0 usa Ollama (/api/generate)
_USE_LMSTUDIO: bool = os.environ.get("USE_LMSTUDIO", "1") == "1"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:32b")

SETTORI_VALIDI = [
    "penale", "civile", "amministrativo", "lavoro",
    "tributario", "processuale", "costituzionale", "altro",
]

ORGANO_SETTORE_MAP: dict[str, tuple[list[str], float]] = {
    "cassazione":      (["civile", "penale"], 0.6),
    "tar":             (["amministrativo"], 0.9),
    "consiglio_stato": (["amministrativo"], 0.95),
    "corte_cost":      (["costituzionale"], 0.95),
    "corte_conti":     (["amministrativo", "tributario"], 0.85),
}

CASSAZIONE_PENALE_KEYWORDS = [
    "reato", "imputato", "condanna", "pena", "reclusione", "ergastolo",
    "omicidio", "furto", "truffa", "estorsione", "calunnia", "diffamazione",
    "lesioni", "violenza", "stalking", "sequestro", "rapina", "corruzione",
    "peculato", "concussione", "abuso", "art. 110 c.p.", "codice penale",
    "p.m.", "pubblico ministero", "gup", "tribunale penale", "cassazione penale",
]

FONTE_SETTORE_MAP: dict[str, list[str]] = {
    "agenzia_entrate": ["tributario"],
    "ade":             ["tributario"],
    "inps":            ["lavoro"],
    "min_lavoro":      ["lavoro"],
    "ministero_lavoro": ["lavoro"],
    "inail":           ["lavoro"],
    "mef":             ["tributario"],
}

# Keyword → settore per pre-classificazione rapida senza LLM.
# Ordine: più specifico prima. Primo match vince.
_KEYWORD_RULES: list[tuple[list[str], list[str], float]] = [
    # (keywords_nel_titolo_lowercase, settori, confidence)
    (["codice penale", "procedura penale", "processo penale", "codice di procedura penale"], ["penale", "processuale"], 0.95),
    (["penale", "reato", "delitto", "contravvenzione", "pena detentiva", "reclusione"], ["penale"], 0.90),
    (["codice civile", "procedura civile", "codice di procedura civile"], ["civile", "processuale"], 0.95),
    (["diritto civile", "obbligazioni", "contratti", "proprietà", "successioni", "famiglia"], ["civile"], 0.85),
    (["imposta sul reddito", "irpef", "ires", "iva", "accise", "tribut", "fiscale", "fisco", "catasto", "imposte", "tasse", "agevolazioni fiscali"], ["tributario"], 0.90),
    (["lavoro", "lavoratori", "lavoratore", "occupazione", "contratto di lavoro", "licenziamento", "sindacato", "sciopero", "inps", "inail", "previdenza", "pensione", "cassa integrazione"], ["lavoro"], 0.90),
    (["appalto pubblico", "contratti pubblici", "codice degli appalti", "pubblica amministrazione", "tar", "consiglio di stato", "procedimento amministrativo", "urbanistica", "edilizia", "esproprio", "demanio"], ["amministrativo"], 0.88),
    (["costituzione", "costituzionale", "corte costituzionale", "diritti fondamentali", "parlamento", "governo", "referendum"], ["costituzionale"], 0.90),
    (["processo", "procedura", "giurisdizione", "competenza", "appello", "cassazione", "tribunale"], ["processuale"], 0.75),
    (["ambiente", "rifiuti", "inquinamento", "paesaggio", "tutela ambientale"], ["amministrativo"], 0.82),
    (["sicurezza sul lavoro", "infortuni sul lavoro", "d.lgs. 81", "dlgs 81"], ["lavoro"], 0.95),
    (["immigrazione", "stranieri", "asilo", "cittadinanza"], ["amministrativo"], 0.85),
    (["codice del consumo", "consumatori", "tutela del consumatore"], ["civile"], 0.85),
    (["privacy", "protezione dei dati", "gdpr", "trattamento dati"], ["amministrativo", "civile"], 0.80),
    (["antimafia", "criminalità organizzata", "camorra", "mafia", "ndrangheta"], ["penale"], 0.92),
    (["bancario", "credito", "banca", "testo unico bancario", "intermediazione finanziaria", "borsa", "finanza"], ["civile", "tributario"], 0.80),
]


def _extract_year_from_urn(act_urn: str) -> int | None:
    """Estrae l'anno da un URN normattiva (es. urn:nir:stato:legge:1948-03-16;262 → 1948)."""
    import re as _re
    m = _re.search(r':(\d{4})-\d{2}-\d{2}[;~]', act_urn)
    if m:
        return int(m.group(1))
    return None


def _keyword_classify(titolo: str, snippet: str = "") -> tuple[list[str], float] | None:
    """Classifica il settore tramite keyword matching su titolo e testo.
    Restituisce (settori, confidence) se trova un match, None altrimenti.
    Il titolo ha priorità; lo snippet abbassa la confidence di 0.05 (meno affidabile).
    """
    titolo_lower = titolo.lower()
    snippet_lower = snippet.lower()[:500]
    for keywords, settori, confidence in _KEYWORD_RULES:
        if any(kw in titolo_lower for kw in keywords):
            return settori, confidence
        if snippet_lower and any(kw in snippet_lower for kw in keywords):
            return settori, max(0.5, confidence - 0.1)
    return None


# ---------------------------------------------------------------------------
# Helpers MongoDB
# ---------------------------------------------------------------------------

def get_mongo_client() -> pymongo.MongoClient:
    return pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)


# ---------------------------------------------------------------------------
# Helpers LLM (LM Studio OpenAI-compat o Ollama)
# ---------------------------------------------------------------------------

_JSON_SYSTEM = (
    "Sei un classificatore JSON per il diritto italiano. "
    "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido nel formato richiesto. "
    "Non scrivere codice Python, non aggiungere spiegazioni, nessun testo fuori dal JSON."
)


def _llm_generate(
    prompt: str, model: str, timeout: int = 120, system: str | None = None
) -> str:
    """Chiama LM Studio (default) o Ollama in modalità sincrona."""
    if _USE_LMSTUDIO:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024,
            "stream": False,
        }
        # Disabilita il reasoning per modelli Gemma 4 / thinking models (classificazione non lo richiede)
        if os.environ.get("DISABLE_THINKING", "1") == "1":
            payload["enable_thinking"] = False
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(f"{LMSTUDIO_URL}/v1/chat/completions", json=payload)
            resp.raise_for_status()
            msg = resp.json()["choices"][0]["message"]
            # Modelli reasoning (es. Gemma 4) mettono il thinking in reasoning_content
            # e la risposta in content. Se content è vuoto, usa reasoning_content come fallback.
            return msg.get("content") or msg.get("reasoning_content") or ""
    else:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 200},
        }
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")


# Alias per retrocompatibilità con le chiamate esistenti nello script
_ollama_generate = _llm_generate


async def _ollama_generate_async(
    prompt: str, model: str, client: httpx.AsyncClient, semaphore: asyncio.Semaphore
) -> str:
    """Chiama LM Studio (default) o Ollama in modalità asincrona."""
    async with semaphore:
        if _USE_LMSTUDIO:
            messages: list[dict] = [
                {"role": "system", "content": _JSON_SYSTEM},
                {"role": "user", "content": prompt},
            ]
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2048,  # sommario: articolo completo + ragionamento
                "stream": False,
            }
            resp = await client.post(f"{LMSTUDIO_URL}/v1/chat/completions", json=payload, timeout=300)
            resp.raise_for_status()
            msg = resp.json()["choices"][0]["message"]
            return msg.get("content") or msg.get("reasoning_content") or ""
        else:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200},
            }
            resp = await client.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json().get("response", "")


def _parse_settori_response(raw: str) -> tuple[list[str], float]:
    """Parse risposta LLM JSON per classificazione settori.

    Strategia robusta: cerca il primo oggetto JSON che contenga 'settori',
    evitando di catturare tutto il testo (es. codice Python generato per errore).
    """
    import re as _re
    raw = raw.strip()

    # 1. Cerca specificamente {"settori": ...} con regex (più preciso)
    pattern = _re.compile(
        r'\{[^{}]*"settori"\s*:\s*\[[^\]]*\][^{}]*"confidence"\s*:\s*([\d.]+)[^{}]*\}',
        _re.DOTALL,
    )
    m = pattern.search(raw)
    if m:
        try:
            data = json.loads(m.group(0))
            settori = data.get("settori", ["altro"])
            confidence = float(data.get("confidence", 0.0))
            settori = [s for s in settori if s in SETTORI_VALIDI]
            if not settori:
                settori = ["altro"]
            return settori, max(0.0, min(1.0, confidence))
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # 2. Fallback: prova ogni coppia {…} dal più corto al più lungo
    for m2 in _re.finditer(r'\{[^{}]+\}', raw, _re.DOTALL):
        try:
            data = json.loads(m2.group(0))
            if "settori" in data:
                settori = data.get("settori", ["altro"])
                confidence = float(data.get("confidence", 0.0))
                settori = [s for s in settori if s in SETTORI_VALIDI]
                if not settori:
                    settori = ["altro"]
                return settori, max(0.0, min(1.0, confidence))
        except (json.JSONDecodeError, ValueError, TypeError):
            continue

    return ["altro"], 0.0


def _build_settore_prompt(
    act_urn: str,
    titolo: str,
    titoli_articoli: list[str],
    testi_articoli: list[str] | None = None,
) -> str:
    articoli_str = "\n".join(f"  - {t}" for t in titoli_articoli[:5] if t.strip())
    # Se i titoli_articoli sono tutti vuoti/generici includi snippet di testo
    snippet_block = ""
    useful_titles = [t for t in titoli_articoli[:5] if len(t.strip()) > 20]
    if not useful_titles and testi_articoli:
        snippets = [t[:600].strip() for t in testi_articoli[:3] if t.strip()]
        if snippets:
            snippet_str = "\n".join(f"  [{i+1}] {s}" for i, s in enumerate(snippets))
            snippet_block = f"\nPrimi testi (estratto):\n{snippet_str}"
    return (
        f"Classifica questo atto normativo italiano. "
        f"Rispondi con un oggetto JSON con campi 'settori' (array) e 'confidence' (float 0-1).\n\n"
        f"Atto: {act_urn}\n"
        f"Titolo: {titolo}\n"
        f"Titoli articoli:\n{articoli_str or '  (non disponibili)'}"
        f"{snippet_block}\n\n"
        f"Settori validi: penale, civile, amministrativo, lavoro, tributario, processuale, costituzionale, altro\n"
        f"Scegli 1-3 settori. Risposta JSON:"
    )


def _build_batch_settore_prompt(acts: list[dict]) -> str:
    """Prompt per classificare N atti in una sola chiamata LLM.

    acts: lista di dict con chiavi act_urn, titolo, snippet (testo breve).
    Ritorna un JSON array: [{"act_urn": ..., "settori": [...], "confidence": 0.9}, ...]
    """
    lines = []
    for i, a in enumerate(acts):
        snippet = a.get("snippet", "")[:300]
        lines.append(
            f'{i+1}. act_urn="{a["act_urn"]}"\n'
            f'   titolo="{a["titolo"]}"\n'
            f'   testo="{snippet}"'
        )
    acts_str = "\n\n".join(lines)
    return (
        f"Classifica i seguenti {len(acts)} atti normativi italiani.\n"
        f"Per ognuno indica i settori giuridici pertinenti e la confidence (0.0-1.0).\n"
        f"Settori validi: penale, civile, amministrativo, lavoro, tributario, processuale, costituzionale, altro\n\n"
        f"Atti da classificare:\n\n{acts_str}\n\n"
        f'Rispondi ESCLUSIVAMENTE con un JSON array:\n'
        f'[{{"act_urn": "...", "settori": ["..."], "confidence": 0.9}}, ...]\n'
        f"Un oggetto per ogni atto, nello stesso ordine. JSON array:"
    )


def _parse_batch_settore_response(raw: str, acts: list[dict]) -> list[tuple[list[str], float]]:
    """Parse risposta batch LLM. Ritorna lista di (settori, confidence) nella stessa sequenza di acts."""
    import re as _re
    raw = raw.strip()
    # Cerca array JSON nella risposta
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start >= 0 and end > start:
        try:
            data = json.loads(raw[start:end])
            if isinstance(data, list):
                results = []
                for item in data:
                    settori = item.get("settori", ["altro"])
                    confidence = float(item.get("confidence", 0.0))
                    settori = [s for s in settori if s in SETTORI_VALIDI] or ["altro"]
                    results.append((settori, max(0.0, min(1.0, confidence))))
                if len(results) == len(acts):
                    return results
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    # Fallback: prova a estrarre oggetti singoli per ogni act_urn
    results = []
    for act in acts:
        pattern = _re.compile(
            rf'"act_urn"\s*:\s*"{_re.escape(act["act_urn"])}"[^}}]*"settori"\s*:\s*\[([^\]]*)\][^}}]*"confidence"\s*:\s*([\d.]+)',
            _re.DOTALL,
        )
        m = pattern.search(raw)
        if m:
            try:
                settori = json.loads(f"[{m.group(1)}]")
                confidence = float(m.group(2))
                settori = [s for s in settori if s in SETTORI_VALIDI] or ["altro"]
                results.append((settori, max(0.0, min(1.0, confidence))))
                continue
            except (json.JSONDecodeError, ValueError):
                pass
        results.append((["altro"], 0.0))
    return results


def _build_sommario_prompt(testo: str) -> str:
    # Batch offline: nessun limite di contesto, passa l'articolo completo
    return f"""Genera un sommario conciso (40-60 parole) del seguente articolo normativo italiano.
Il sommario deve catturare l'essenza della norma in modo chiaro e preciso.

Articolo:
{testo}

Sommario (solo testo, no JSON, no prefissi):"""


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _load_checkpoint(checkpoint_dir: Path, filename: str) -> dict[str, Any]:
    path = checkpoint_dir / filename
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning(f"Checkpoint corrotto, ignorato: {path}")
    return {}


def _append_checkpoint(checkpoint_dir: Path, filename: str, key: str, value: Any) -> None:
    """Append-only: aggiunge una singola chiave al checkpoint JSON."""
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    path = checkpoint_dir / filename
    data = _load_checkpoint(checkpoint_dir, filename)
    data[key] = value
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_checkpoint(checkpoint_dir: Path, filename: str, data: dict) -> None:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    path = checkpoint_dir / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Helper condiviso — applica classificazione a un atto e aggiorna chunks
# ---------------------------------------------------------------------------

def _apply_classification(
    act: dict,
    settori: list[str],
    confidence: float,
    checkpoint_dir: Path,
    coll_source: Any,
    coll_chunks: Any,
) -> None:
    """Salva checkpoint e aggiorna i chunk normattiva corrispondenti a questo atto.

    I chunk non hanno 'act_urn': vengono trovati tramite source_id che corrisponde
    ai valori di normattiva_docs.urn per quell'atto.
    """
    act_urn = act["act_urn"]
    titolo = act.get("titolo", "")

    _append_checkpoint(
        checkpoint_dir, "act_classification.json",
        act_urn, {"settori": settori, "confidence": confidence, "titolo": titolo},
    )

    # Recupera tutti gli URN articolo dell'atto (normattiva_docs.urn → chunks.source_id)
    article_urns = act.get("article_urns") or []
    if not article_urns:
        # Carica on-demand se non pre-caricati
        article_urns = coll_source.distinct("urn", {"act_urn": act_urn})

    if article_urns:
        result = coll_chunks.update_many(
            {"source_id": {"$in": article_urns}, "corpus": "normattiva"},
            {"$set": {"settore": settori, "settore_confidence": confidence}},
        )
        logger.debug(f"  {act_urn} → {settori} ({confidence:.2f}) — {result.modified_count} chunks aggiornati")
    else:
        logger.debug(f"  {act_urn} → {settori} ({confidence:.2f}) — nessun article_urn trovato")


# ---------------------------------------------------------------------------
# FASE A — Classificazione atti normattiva (act-level)
# ---------------------------------------------------------------------------

def fase_a(workspace: str, model: str, batch_size: int, checkpoint_dir: Path) -> None:
    """Classifica settori per ogni act_urn distinto in normattiva_docs."""
    logger.info("=== FASE A: Classificazione atti normattiva (LLM) ===")

    checkpoint = _load_checkpoint(checkpoint_dir, "act_classification.json")
    already_done = set(checkpoint.keys())
    logger.info(f"Checkpoint: {len(already_done)} atti già classificati")

    client = get_mongo_client()
    try:
        source_db = client["legal_lab"]
        target_db = client["aiura_legal_lab_db"]
        coll_source = source_db["normattiva_docs"]
        coll_chunks = target_db["chunks"]

        # Ottieni tutti gli act_urn distinti
        act_urns = coll_source.distinct("act_urn")
        # Fallback se act_urn non esiste: usa urn
        if not act_urns:
            act_urns = coll_source.distinct("urn")
        logger.info(f"Trovati {len(act_urns)} act_urn distinti")

        processed = 0
        kw_classified = 0
        llm_classified = 0
        interrupted = False

        # --- Step 1: pre-carica titoli di tutti gli atti non ancora classificati ---
        todo_acts: list[dict] = []
        for act_urn in act_urns:
            if act_urn in already_done:
                continue
            # Recupera titolo e un testo di esempio da normattiva_docs
            docs = list(coll_source.find(
                {"act_urn": act_urn},
                {"titolo": 1, "titolo_articolo": 1, "text": 1, "urn": 1},
                limit=5,
            ))
            titolo = docs[0].get("titolo", "") if docs else act_urn
            snippet = next((d.get("text", "") for d in docs if d.get("text")), "")
            article_urns = [d["urn"] for d in docs if d.get("urn")]
            todo_acts.append({
                "act_urn": act_urn,
                "titolo": titolo,
                "snippet": snippet,
                "article_urns": article_urns,
            })

        logger.info(f"Fase A: {len(todo_acts)} atti da classificare ({len(already_done)} già nel checkpoint)")

        # --- Step 2: pre-classification (zero LLM) ---
        needs_llm: list[dict] = []
        pre_1948_skipped = 0
        for act in todo_acts:
            # Prima: keyword matching (ha priorità — una legge del 1930 sul codice penale è "penale")
            kw_result = _keyword_classify(act["titolo"], act.get("snippet", ""))
            if kw_result:
                settori, confidence = kw_result
                _apply_classification(act, settori, confidence, checkpoint_dir, coll_source, coll_chunks)
                kw_classified += 1
                continue

            # Poi: atti pre-Costituzione senza keyword → "altro" senza LLM
            act_year = _extract_year_from_urn(act["act_urn"])
            if act_year is not None and act_year < 1948:
                _apply_classification(act, ["altro"], 0.5, checkpoint_dir, coll_source, coll_chunks)
                kw_classified += 1
                pre_1948_skipped += 1
                continue

            needs_llm.append(act)

        if pre_1948_skipped:
            logger.info(f"  Pre-1948 skip: {pre_1948_skipped} atti → ['altro'] senza LLM")

        logger.info(
            f"Keyword pre-classification: {kw_classified} atti classificati, "
            f"{len(needs_llm)} rimandati a LLM"
        )

        # --- Step 3: batch LLM per gli atti ambigui (10 per prompt) ---
        LLM_BATCH = 5
        try:
            for batch_start in range(0, len(needs_llm), LLM_BATCH):
                batch = needs_llm[batch_start:batch_start + LLM_BATCH]
                try:
                    prompt = _build_batch_settore_prompt(batch)
                    raw = _ollama_generate(prompt, model, timeout=600, system=_JSON_SYSTEM)
                    logger.debug(f"  batch raw [{batch_start}]: {repr(raw[:300])}")
                    results = _parse_batch_settore_response(raw, batch)
                    for act, (settori, confidence) in zip(batch, results):
                        _apply_classification(act, settori, confidence, checkpoint_dir, coll_source, coll_chunks)
                        llm_classified += 1
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Errore batch LLM (atti {batch_start}-{batch_start+len(batch)}): {e}")
                    for act in batch:
                        _apply_classification(act, ["altro"], 0.0, checkpoint_dir, coll_source, coll_chunks)

                processed = kw_classified + llm_classified
                if processed % 500 == 0:
                    logger.info(f"Fase A: {processed}/{len(todo_acts)} atti classificati...")

        except KeyboardInterrupt:
            interrupted = True
            logger.warning("Interrotto da utente. Checkpoint salvato.")

        total = kw_classified + llm_classified
        logger.info(
            f"Fase A {'completata' if not interrupted else 'interrotta'}: "
            f"{total} atti ({kw_classified} keyword, {llm_classified} LLM)"
        )
    finally:
        client.close()


# ---------------------------------------------------------------------------
# FASE B — Generazione sommario normattiva (article-level, async)
# ---------------------------------------------------------------------------

async def _fase_b_async(workspace: str, model: str, batch_size: int, checkpoint_dir: Path) -> None:
    checkpoint = _load_checkpoint(checkpoint_dir, "sommario_progress.json")
    done_ids = set(checkpoint.keys())
    logger.info(f"Checkpoint sommari: {len(done_ids)} chunk già processati")

    mongo = get_mongo_client()
    try:
        coll = mongo["aiura_legal_lab_db"]["chunks"]

        cursor = coll.find(
            {"corpus": "normattiva", "testo_tipo": "normativo", "sommario": None},
            {"_id": 1, "text": 1},
        )

        chunks_batch: list[dict] = []
        processed = 0
        semaphore = asyncio.Semaphore(batch_size)

        async with httpx.AsyncClient() as http_client:

            async def process_chunk(chunk: dict) -> None:
                nonlocal processed
                chunk_id = str(chunk["_id"])
                if chunk_id in done_ids:
                    return
                prompt = _build_sommario_prompt(chunk.get("text", ""))
                try:
                    sommario = await _ollama_generate_async(prompt, model, http_client, semaphore)
                    sommario = sommario.strip()[:500]  # cap a 500 char
                    coll.update_one({"_id": chunk["_id"]}, {"$set": {"sommario": sommario}})
                    checkpoint[chunk_id] = True
                    processed += 1
                    if processed % 100 == 0:
                        _save_checkpoint(checkpoint_dir, "sommario_progress.json", checkpoint)
                        logger.info(f"Fase B: {processed} sommari generati...")
                except Exception as e:
                    logger.error(f"Errore sommario chunk {chunk_id}: {e}")

            tasks = []
            for chunk in cursor:
                tasks.append(asyncio.create_task(process_chunk(chunk)))
                if len(tasks) >= batch_size * 4:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

        _save_checkpoint(checkpoint_dir, "sommario_progress.json", checkpoint)
        logger.info(f"Fase B completata: {processed} sommari generati")
    finally:
        mongo.close()


def fase_b(workspace: str, model: str, batch_size: int, checkpoint_dir: Path) -> None:
    logger.info("=== FASE B: Generazione sommari normattiva (LLM) ===")
    try:
        asyncio.run(_fase_b_async(workspace, model, batch_size, checkpoint_dir))
    except KeyboardInterrupt:
        logger.warning("Fase B interrotta da utente. Checkpoint parziale salvato.")


# ---------------------------------------------------------------------------
# FASE C — Giurisprudenza settore (rule-based)
# ---------------------------------------------------------------------------

def _classify_cassazione(text: str) -> tuple[list[str], float]:
    """Disambigua cassazione civile/penale via keyword."""
    text_lower = text.lower()
    penale_hits = sum(1 for kw in CASSAZIONE_PENALE_KEYWORDS if kw in text_lower)
    if penale_hits >= 2:
        return ["penale"], 0.9
    elif penale_hits == 1:
        return ["penale"], 0.7
    else:
        return ["civile"], 0.75


def fase_c(workspace: str, batch_size: int, checkpoint_dir: Path) -> None:
    """Classifica settori giurisprudenza con regole (zero LLM). Idempotente."""
    logger.info("=== FASE C: Classificazione giurisprudenza (rule-based) ===")

    mongo = get_mongo_client()
    try:
        coll = mongo["aiura_legal_lab_db"]["chunks"]

        # Solo chunk senza settore già classificato
        cursor = coll.find(
            {
                "corpus": "giurisprudenza",
                "$or": [
                    {"settore_confidence": {"$exists": False}},
                    {"settore_confidence": 0},
                    {"settore_confidence": None},
                ],
            },
            {"_id": 1, "organo": 1, "text": 1},
            batch_size=batch_size,
        )

        processed = 0
        skipped_short = 0
        bulk_ops = []

        for chunk in cursor:
            try:
                text = chunk.get("text", "")

                # Filtra chunk vuoti / troppo corti
                if len(text) < 20:
                    bulk_ops.append(pymongo.UpdateOne(
                        {"_id": chunk["_id"]},
                        {"$set": {"is_indexed": False}},
                    ))
                    skipped_short += 1
                    continue

                organo_raw = (chunk.get("organo") or "").lower().replace(" ", "_")

                if organo_raw == "cassazione":
                    settori, confidence = _classify_cassazione(text)
                elif organo_raw in ORGANO_SETTORE_MAP:
                    settori, confidence = ORGANO_SETTORE_MAP[organo_raw]
                else:
                    settori, confidence = ["civile"], 0.5

                bulk_ops.append(pymongo.UpdateOne(
                    {"_id": chunk["_id"]},
                    {"$set": {"settore": settori, "settore_confidence": confidence}},
                ))
                processed += 1

                if len(bulk_ops) >= batch_size:
                    coll.bulk_write(bulk_ops, ordered=False)
                    bulk_ops = []
                    if processed % 100 == 0:
                        logger.info(f"Fase C: {processed} chunk classificati...")

            except Exception as e:
                logger.error(f"Errore chunk {chunk.get('_id')}: {e}")

        if bulk_ops:
            coll.bulk_write(bulk_ops, ordered=False)

        logger.info(f"Fase C completata: {processed} classificati, {skipped_short} troppo corti")
    finally:
        mongo.close()


# ---------------------------------------------------------------------------
# FASE D — Dottrina settore (LLM, document-level)
# ---------------------------------------------------------------------------

def fase_d(workspace: str, model: str, batch_size: int, checkpoint_dir: Path) -> None:
    """Classifica settori dottrina via LLM (document-level, idempotente)."""
    logger.info("=== FASE D: Classificazione dottrina (LLM, document-level) ===")

    checkpoint = _load_checkpoint(checkpoint_dir, "dottrina_classification.json")
    already_done = set(checkpoint.keys())

    mongo = get_mongo_client()
    try:
        coll = mongo["aiura_legal_lab_db"]["chunks"]

        # Documenti dottrina non ancora tutti classificati
        pipeline = [
            {"$match": {"corpus": "dottrina"}},
            {"$group": {
                "_id": "$document_id",
                "total": {"$sum": 1},
                "classified": {
                    "$sum": {
                        "$cond": [{"$gt": ["$settore_confidence", 0]}, 1, 0]
                    }
                },
                "first_chunk_id": {"$first": "$_id"},
                "first_text": {"$first": "$text"},
            }},
        ]
        docs = list(coll.aggregate(pipeline))
        logger.info(f"Trovati {len(docs)} documenti dottrina")

        processed = 0
        interrupted = False

        for doc in docs:
            doc_id = str(doc["_id"])
            if doc_id in already_done:
                continue
            # Skip se tutti i chunk già classificati
            if doc["total"] > 0 and doc["classified"] == doc["total"]:
                already_done.add(doc_id)
                continue

            try:
                first_text = doc.get("first_text", "")
                prompt = f"""Classifica il documento di dottrina giuridica italiana nel settore appropriato.

Testo (inizio):
{first_text[:600]}

Rispondi SOLO con JSON valido:
{{"settori": ["settore1"], "confidence": 0.8}}

Settori: penale, civile, amministrativo, lavoro, tributario, processuale, costituzionale, altro

JSON:"""

                raw = _ollama_generate(prompt, model)
                settori, confidence = _parse_settori_response(raw)

                # Propaga a tutti i chunk del documento
                result = coll.update_many(
                    {"document_id": doc["_id"], "corpus": "dottrina"},
                    {"$set": {"settore": settori, "settore_confidence": confidence}},
                )
                logger.debug(f"doc={doc_id}: settori={settori} → {result.modified_count} chunk aggiornati")

                _append_checkpoint(
                    checkpoint_dir, "dottrina_classification.json",
                    doc_id, {"settori": settori, "confidence": confidence}
                )

                processed += 1
                if processed % 100 == 0:
                    logger.info(f"Fase D: {processed} documenti classificati...")

            except KeyboardInterrupt:
                interrupted = True
                logger.warning("Fase D interrotta. Checkpoint salvato.")
                break
            except Exception as e:
                logger.error(f"Errore doc={doc_id}: {e}")
                _append_checkpoint(
                    checkpoint_dir, "dottrina_classification.json",
                    doc_id, {"settori": ["altro"], "confidence": 0.0, "error": str(e)}
                )

        if not interrupted:
            logger.info(f"Fase D completata: {processed} documenti classificati")
    finally:
        mongo.close()


# ---------------------------------------------------------------------------
# FASE E — Prassi corpus (chunking + sommario)
# ---------------------------------------------------------------------------

def _chunk_text(text: str, chunk_size: int = 256, overlap: int = 32) -> list[str]:
    """Chunking semplice a parole con overlap."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        if chunk_words:
            chunks.append(" ".join(chunk_words))
    return chunks


def _detect_prassi_settore(source_id: str, fonte: str) -> list[str]:
    """Determina settore da fonte prassi."""
    combined = f"{source_id} {fonte}".lower()
    for key, settori in FONTE_SETTORE_MAP.items():
        if key in combined:
            return settori
    return ["amministrativo"]


def fase_e(workspace: str, model: str, batch_size: int, checkpoint_dir: Path) -> None:
    """Chunking + sommario per corpus prassi. Idempotente."""
    logger.info("=== FASE E: Prassi corpus (chunking + sommario) ===")

    mongo = get_mongo_client()
    try:
        # Cerca documenti prassi — potrebbero essere in aiura_legal_lab_db o legal_lab
        aiura_db = mongo["aiura_legal_lab_db"]
        coll_docs = aiura_db["documents"]
        coll_chunks = aiura_db["chunks"]

        prassi_docs = list(coll_docs.find({"corpus": "prassi"}))
        if not prassi_docs:
            # Fallback: cerca per tipo/fonte
            prassi_docs = list(coll_docs.find({
                "$or": [
                    {"fonte": {"$in": list(FONTE_SETTORE_MAP.keys())}},
                    {"tipo": "prassi"},
                ]
            }))

        logger.info(f"Trovati {len(prassi_docs)} documenti prassi")

        processed = 0
        for doc in prassi_docs:
            doc_id = str(doc["_id"])
            source_id = doc.get("source_id", doc_id)

            # Idempotente: skip se chunk già esistono
            existing = coll_chunks.count_documents(
                {"source_id": source_id, "corpus": "prassi"},
                limit=1,
            )
            if existing:
                logger.debug(f"Skip prassi doc già indicizzato: {source_id}")
                continue

            text = doc.get("text", doc.get("content", ""))
            if not text:
                continue

            fonte = doc.get("fonte", "")
            settori = _detect_prassi_settore(source_id, fonte)

            chunks_texts = _chunk_text(text)
            chunks_to_insert = []

            for idx, chunk_text in enumerate(chunks_texts):
                # Sommario LLM
                sommario = None
                try:
                    raw = _ollama_generate(_build_sommario_prompt(chunk_text), model)
                    sommario = raw.strip()[:500]
                except Exception as e:
                    logger.warning(f"Sommario fallito per chunk {idx} di {source_id}: {e}")

                chunks_to_insert.append({
                    "document_id": doc["_id"],
                    "source_id": source_id,
                    "corpus": "prassi",
                    "chunk_index": idx,
                    "text": chunk_text,
                    "sommario": sommario,
                    "settore": settori,
                    "settore_confidence": 0.9,
                    "workspace": workspace,
                })

            if chunks_to_insert:
                coll_chunks.insert_many(chunks_to_insert)
                logger.debug(f"Inseriti {len(chunks_to_insert)} chunk per {source_id}")

            processed += 1
            if processed % 100 == 0:
                logger.info(f"Fase E: {processed} documenti processati...")

        logger.info(f"Fase E completata: {processed} documenti processati")
    finally:
        mongo.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline batch idempotente per classificazione KB"
    )
    parser.add_argument(
        "--fase",
        choices=["A", "B", "C", "D", "E", "all"],
        default="all",
        help="Fase da eseguire (default: all)",
    )
    parser.add_argument(
        "--workspace",
        default="mio-studio",
        help="Nome workspace (default: mio-studio)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Modello Ollama (default: env OLLAMA_MODEL o '{OLLAMA_MODEL}')",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Dimensione batch LLM (default: 8)",
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="./classify_checkpoints",
        help="Directory checkpoint (default: ./classify_checkpoints)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = args.model or OLLAMA_MODEL
    checkpoint_dir = Path(args.checkpoint_dir)
    fase = args.fase

    logger.info(f"classify_knowledge_base — fase={fase} workspace={args.workspace} model={model}")

    try:
        if fase in ("A", "all"):
            fase_a(args.workspace, model, args.batch_size, checkpoint_dir)
        if fase in ("B", "all"):
            fase_b(args.workspace, model, args.batch_size, checkpoint_dir)
        if fase in ("C", "all"):
            fase_c(args.workspace, args.batch_size, checkpoint_dir)
        if fase in ("D", "all"):
            fase_d(args.workspace, model, args.batch_size, checkpoint_dir)
        if fase in ("E", "all"):
            fase_e(args.workspace, model, args.batch_size, checkpoint_dir)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrotta da utente. Checkpoint salvati.")
        sys.exit(130)

    logger.info("Pipeline completata.")


if __name__ == "__main__":
    main()
