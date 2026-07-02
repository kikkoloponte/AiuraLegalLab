"""
Id deterministico per i chunk normattiva.

Perché: l'_id di MongoDB, se lasciato generare automaticamente, non ha
relazione con l'identità reale del chunk. L'upsert storico di
NormattivaPipeline._flush() matcha su (source_id, chunk_index, workspace),
dove source_id è l'URN assegnato dal fetcher — che è POSIZIONALE (posizione
nella catena di navigazione), non un identificatore stabile del vero
articolo legislativo. Due esecuzioni separate dello scraping possono
assegnare contenuti diversi allo stesso URN (es. per un hiccup di rete che
disallinea il conteggio), facendo sì che un _id già referenziato altrove
(es. istituti_giuridici.source_mongo_id) si ritrovi silenziosamente a
puntare a un articolo diverso dopo un rebuild.

Fix: calcolare l'_id da un identificatore STABILE — fonte + numero articolo
normalizzato + eventuale data di inizio vigenza (per distinguere versioni
storiche dello stesso articolo) + chunk_index — invece che lasciarlo
assegnare da Mongo o derivarlo dall'URN posizionale. ObjectId accetta
qualsiasi valore binario a 12 byte: non serve la struttura timestamp+
contatore di Mongo, un hash troncato è un ObjectId valido a tutti gli
effetti (compatibile con ObjectId(str(id)) in tutto il codice esistente).

Stesso (fonte, articolo_num, valid_from, chunk_index) → sempre lo stesso
_id, indipendentemente da quante volte si rifà lo scraping/chunking.
"""
from __future__ import annotations

import hashlib
import re

from bson import ObjectId

_ORDINALI = (
    "bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|"
    "undecies|duodecies|terdecies|quaterdecies|quinquiesdecies"
)
_ART_NUM_RE = re.compile(
    rf"(?:Art(?:icolo)?\.?\s*)?(\d+)(?:[\s-]*({_ORDINALI})\b)?",
    re.IGNORECASE,
)


def normalize_articolo_num(raw: str) -> str:
    """
    'Art. 79.' / 'Art. 79-bis' / '79 bis' / 'Articolo 79' -> '79' / '79bis'.

    Normalizza rimuovendo prefisso "Art."/"Articolo", punteggiatura, spazi
    e trattini tra numero e suffisso (bis/ter/quater/...), così il confronto
    tra un riferimento testuale ("Art. 612-bis") e il campo articolo_num di
    un chunk ("Art. 612-bis.") sia stabile indipendentemente dal formato
    esatto della stringa sorgente.
    """
    m = _ART_NUM_RE.search(raw or "")
    if not m:
        return ""
    numero, suffisso = m.group(1), m.group(2) or ""
    return f"{numero}{suffisso}".lower()


def compute_deterministic_chunk_id(
    *,
    workspace: str,
    fonte: str,
    articolo_num: str,
    valid_from: str | None,
    chunk_index: int,
) -> ObjectId:
    """
    Deriva un ObjectId deterministico dall'identità stabile del chunk.

    fonte/articolo_num/valid_from/chunk_index devono essere gli stessi campi
    già presenti nel chunk record (to_chunk_base + chunk_index) — nessun
    campo nuovo da propagare a monte.
    """
    key = "|".join([
        workspace,
        fonte or "",
        normalize_articolo_num(articolo_num),
        valid_from or "",
        str(chunk_index),
    ])
    digest = hashlib.sha1(key.encode("utf-8")).digest()[:12]
    return ObjectId(digest)
