"""
Riapplica le classificazioni settore già note nel checkpoint act_classification.json
ai chunk attuali in aiura_legal.chunks, senza richiamare l'LLM.

Necessario perché il re-chunking di mirror_normattiva.py ricrea i documenti chunk
senza preservare il campo 'settore' impostato da una run precedente di
classify_knowledge_base.py --fase A.

Uso:
    python scripts/replay_settore_checkpoint.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pymongo
from loguru import logger

CHECKPOINT_PATH = ROOT / "classify_checkpoints" / "act_classification.json"


def main() -> None:
    data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    logger.info(f"Checkpoint: {len(data):,} atti da riapplicare")

    client = pymongo.MongoClient("mongodb://localhost:27017")
    coll = client["aiura_legal_lab_db"]["chunks"]

    total_updated = 0
    total_acts_hit = 0
    for i, (act_urn, entry) in enumerate(data.items(), 1):
        settori = entry["settori"]
        confidence = entry["confidence"]
        pattern = "^" + re.escape(act_urn) + r"~art"
        result = coll.update_many(
            {
                "source_id": {"$regex": pattern},
                "corpus": "normattiva",
                "workspace": "mio-studio",
            },
            {"$set": {"settore": settori, "settore_confidence": confidence}},
        )
        if result.modified_count:
            total_acts_hit += 1
        total_updated += result.modified_count

        if i % 1000 == 0:
            logger.info(f"  {i:,}/{len(data):,} atti processati, {total_updated:,} chunk aggiornati finora")

    logger.success(
        f"Replay completato: {total_acts_hit:,}/{len(data):,} atti hanno trovato chunk, "
        f"{total_updated:,} chunk aggiornati totali"
    )


if __name__ == "__main__":
    main()
