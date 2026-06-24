"""
Riclassifica via LLM i documenti di dottrina finiti in settore=["altro"]
nella run originale di classify_knowledge_base.py --fase D.

Motivazione: fase_d salta i documenti che hanno gia' settore_confidence > 0,
quindi non rielabora mai i risultati "altro" (confidence 0.5-0.9) anche se
sono poco informativi. Questo script li intercetta esplicitamente e usa
uno snippet piu' lungo (1500 caratteri vs i 600 originali) per dare
all'LLM piu' contesto.

Idempotente/riprendibile: checkpoint append-only separato da quello di
classify_knowledge_base.py (non lo sporca).

Uso:
    python scripts/reclassify_dottrina_altro.py --model qwen2.5-14b-instruct
    python scripts/reclassify_dottrina_altro.py --model google/gemma-4-31b  # piu' lento, piu' accurato
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pymongo
from loguru import logger

sys.path.insert(0, str(ROOT / "scripts"))
from classify_knowledge_base import (  # noqa: E402
    _llm_generate, _parse_settori_response, SETTORI_VALIDI, _JSON_SYSTEM,
)

CHECKPOINT_PATH = ROOT / "classify_checkpoints" / "dottrina_altro_reclassification.json"
SNIPPET_LEN = 1500

# Riviste note il cui nome nel colophon/frontespizio rivela il settore senza
# bisogno di leggere l'articolo — zero LLM, zero rischio (controllato a mano
# il 2026-06-16: 349/355 dei doc "altro" sono "Sistema Penale").
import re as _re  # noqa: E402
_JOURNAL_RULES: list[tuple[str, list[str]]] = [
    (r"sistema penale|gian luigi gatta|diritto penale contemporaneo|dirittopenaleuomo", ["penale"]),
]


def _journal_classify(text: str) -> tuple[list[str], float] | None:
    t = (text or "")[:2000].lower()
    for pattern, settori in _JOURNAL_RULES:
        if _re.search(pattern, t):
            return settori, 0.95
    return None


def _load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        try:
            return json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Checkpoint corrotto, riparto da zero")
    return {}


def _save_checkpoint(data: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5-14b-instruct")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    client = pymongo.MongoClient("mongodb://localhost:27017")
    coll = client["aiura_legal_lab_db"]["chunks"]

    checkpoint = _load_checkpoint()
    already_done = set(checkpoint.keys())

    pipeline = [
        {"$match": {"corpus": "dottrina", "settore": ["altro"]}},
        {"$group": {
            "_id": "$document_id",
            "first_text": {"$first": "$text"},
            "n_chunks": {"$sum": 1},
        }},
    ]
    docs = list(coll.aggregate(pipeline))
    logger.info(f"Documenti dottrina con settore=['altro']: {len(docs)}")

    if args.dry_run:
        for d in docs[:10]:
            logger.info(f"  {d['_id']}: {d['n_chunks']} chunk, snippet={d['first_text'][:100]!r}")
        return

    processed = 0
    changed = 0
    for doc in docs:
        doc_id = str(doc["_id"])
        if doc_id in already_done:
            continue

        text = doc.get("first_text", "")

        journal_result = _journal_classify(text)
        if journal_result:
            settori, confidence = journal_result
            result = coll.update_many(
                {"document_id": doc["_id"], "corpus": "dottrina"},
                {"$set": {"settore": settori, "settore_confidence": confidence}},
            )
            changed += 1
            logger.info(f"  {doc_id}: altro → {settori} ({confidence:.2f}) [regola rivista] — {result.modified_count} chunk")
            checkpoint[doc_id] = {"settori": settori, "confidence": confidence, "source": "journal_rule"}
            processed += 1
            continue

        prompt = f"""Classifica il documento di dottrina giuridica italiana nel settore appropriato.
Leggi con attenzione il testo: anche se sembra generico a prima vista, cerca segnali
specifici (terminologia, riferimenti normativi, contesto) che indichino la materia.

Testo (inizio, fino a {SNIPPET_LEN} caratteri):
{text[:SNIPPET_LEN]}

Settori validi: {", ".join(SETTORI_VALIDI)}

Rispondi SOLO con JSON valido:
{{"settori": ["settore1"], "confidence": 0.8}}

Usa "altro" solo se davvero non c'e' nessun segnale di materia specifica. JSON:"""

        try:
            raw = _llm_generate(prompt, args.model, timeout=120, system=_JSON_SYSTEM)
            settori, confidence = _parse_settori_response(raw)
        except Exception as e:
            logger.warning(f"  {doc_id}: errore LLM ({e}), skip")
            continue

        result = coll.update_many(
            {"document_id": doc["_id"], "corpus": "dottrina"},
            {"$set": {"settore": settori, "settore_confidence": confidence}},
        )
        if settori != ["altro"]:
            changed += 1
            logger.info(f"  {doc_id}: altro → {settori} ({confidence:.2f}) — {result.modified_count} chunk")
        else:
            logger.debug(f"  {doc_id}: confermato altro ({confidence:.2f})")

        checkpoint[doc_id] = {"settori": settori, "confidence": confidence}
        processed += 1
        if processed % 25 == 0:
            _save_checkpoint(checkpoint)
            logger.info(f"  Checkpoint salvato: {processed}/{len(docs) - len(already_done)} processati")

    _save_checkpoint(checkpoint)
    logger.success(
        f"Completato: {processed} documenti processati, {changed} riclassificati "
        f"da 'altro' a una materia specifica"
    )


if __name__ == "__main__":
    main()
