"""
DottrinaMetadataExtractor — estrae metadati bibliografici dal testo dei chunk dottrina.

Lavora sul testo del PRIMO chunk (chunk_index == 0) di ogni document_id e applica
$set a tutti i chunk dello stesso document_id via bulk_write.

Riviste riconosciute:
  - Diritto Penale Contemporaneo (DPC)
  - Sistema Penale

Fallback per monografie/paper: estrae titolo da prima riga non-vuota,
autore da seconda riga, anno da prima occorrenza di 4 cifre.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger


# ---------------------------------------------------------------------------
# Pattern regex per le riviste riconosciute
# ---------------------------------------------------------------------------

# DPC — Diritto Penale Contemporaneo
_RE_DPC_DETECT = re.compile(r"DIRITTO\s+PENALE.*?CONTEMPORANEO", re.IGNORECASE | re.DOTALL)
_RE_DPC_FASCICOLO = re.compile(r"Fascicolo\s+(\d+)/(\d{4})", re.IGNORECASE)
# DPC indica il direttore come "Francesco Viganò" o "Gian Luigi Gatta" nelle pagine
_RE_DPC_AUTORE = re.compile(
    r"(?:Direttore\s+responsabile|DIRETTORE)\s*[:\-]?\s*([A-ZÀÈÉÌÒÙ][a-zàèéìòù]+(?:\s+[A-ZÀÈÉÌÒÙ][a-zàèéìòù]+)+)",
    re.IGNORECASE,
)

# Sistema Penale
_RE_SP_DETECT = re.compile(
    r"(?:EDITOR-IN-CHIEF\s+Gian\s+Luigi\s+Gatta|Rivista\s+scientifica\s+quadrimestrale\s+di\s+diritto\s+e\s+procedura\s+penale)",
    re.IGNORECASE | re.DOTALL,
)
_RE_SP_ANNO_FASC = re.compile(r"Anno\s+(\d{4})/Fascicolo\s+([IVX]+)", re.IGNORECASE)

# Generico — estrai anno da qualsiasi 4 cifre plausibile (1900-2099)
_RE_ANNO = re.compile(r"\b((?:19|20)\d{2})\b")

# Autore generico — "Cognome Nome" o "Nome Cognome" nella seconda riga non vuota
# Accetta 2-4 parole con iniziale maiuscola (inclusi accenti)
_RE_AUTORE_GENERIC = re.compile(
    r"^([A-ZÀÈÉÌÒÙ][a-zàèéìòùäöü]+(?:\s+[A-ZÀÈÉÌÒÙ][a-zàèéìòùäöü]+){1,3})\s*$",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Dataclass risultato estrazione
# ---------------------------------------------------------------------------

@dataclass
class DottrinaMetadata:
    """Metadati estratti per un document_id di corpus=dottrina."""
    document_id: str
    rivista: Optional[str] = None
    titolo_doc: Optional[str] = None
    autore: Optional[str] = None
    anno_pubblicazione: Optional[int] = None
    fascicolo: Optional[str] = None
    settore: list[str] = field(default_factory=lambda: ["penale"])

    def as_set_dict(self) -> dict:
        """Ritorna il dizionario per $set MongoDB (solo campi non-None)."""
        out: dict = {"settore": self.settore}
        for key in ("rivista", "titolo_doc", "autore", "fascicolo"):
            val = getattr(self, key)
            if val is not None:
                out[key] = val
        if self.anno_pubblicazione is not None:
            out["anno_pubblicazione"] = self.anno_pubblicazione
        return out


# ---------------------------------------------------------------------------
# Estrattore
# ---------------------------------------------------------------------------

class DottrinaMetadataExtractor:
    """
    Estrae metadati bibliografici dal testo del primo chunk di ogni documento dottrina.

    Utilizzo (async — richiede motor):

        from motor.motor_asyncio import AsyncIOMotorDatabase
        extractor = DottrinaMetadataExtractor(db)
        stats = await extractor.run(workspace="mio-studio")
        print(f"Aggiornati {stats['updated']} documenti su {stats['total']}")

    Utilizzo (sync per script CLI):

        import asyncio
        asyncio.run(extractor.run())
    """

    def __init__(self, db) -> None:
        """
        Args:
            db: AsyncIOMotorDatabase (aiura_legal_lab_db)
        """
        self._db = db

    # ------------------------------------------------------------------
    # Entry point async
    # ------------------------------------------------------------------

    async def run(
        self,
        workspace: Optional[str] = None,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """
        Scansiona tutti i chunk corpus=dottrina con chunk_index=0,
        estrae metadati, applica $set a tutti i chunk dello stesso document_id.

        Args:
            workspace: filtra per workspace (None = tutti)
            dry_run:   se True, non scrive su MongoDB (solo log)

        Returns:
            {"total": N, "updated": M, "skipped": K, "errors": E}
        """
        query: dict = {"corpus": "dottrina", "chunk_index": 0}
        if workspace:
            query["workspace"] = workspace

        stats = {"total": 0, "updated": 0, "skipped": 0, "errors": 0}
        bulk_ops: list = []

        async for first_chunk in self._db.chunks.find(query):
            stats["total"] += 1
            doc_id = first_chunk.get("document_id", "")
            text = first_chunk.get("text", "")

            if not text.strip():
                logger.debug(f"[DottrinaExtractor] chunk vuoto per doc {doc_id} — skip")
                stats["skipped"] += 1
                continue

            try:
                meta = self.extract(text, document_id=doc_id)
            except Exception as exc:
                logger.warning(f"[DottrinaExtractor] errore estrazione doc {doc_id}: {exc}")
                stats["errors"] += 1
                continue

            set_dict = meta.as_set_dict()
            logger.debug(
                f"[DottrinaExtractor] doc {doc_id[:12]}... "
                f"rivista={meta.rivista} anno={meta.anno_pubblicazione} "
                f"autore={meta.autore!r}"
            )

            if not dry_run:
                from pymongo import UpdateMany
                bulk_ops.append(
                    UpdateMany(
                        {"document_id": doc_id, "corpus": "dottrina"},
                        {"$set": set_dict},
                    )
                )
            stats["updated"] += 1

            # Esegui bulk ogni 500 op per non saturare la memoria
            if len(bulk_ops) >= 500:
                await self._db.chunks.bulk_write(bulk_ops, ordered=False)
                bulk_ops.clear()

        # Flush finale
        if bulk_ops and not dry_run:
            await self._db.chunks.bulk_write(bulk_ops, ordered=False)

        logger.info(
            f"[DottrinaExtractor] done — total={stats['total']} "
            f"updated={stats['updated']} skipped={stats['skipped']} "
            f"errors={stats['errors']}"
        )
        return stats

    # ------------------------------------------------------------------
    # Logica di estrazione (sync, testabile senza MongoDB)
    # ------------------------------------------------------------------

    def extract(self, text: str, document_id: str = "") -> DottrinaMetadata:
        """
        Estrae metadati dal testo del primo chunk.
        Ritorna sempre un DottrinaMetadata (mai raise — usa None per campi non trovati).
        """
        meta = DottrinaMetadata(document_id=document_id)

        # Tenta riconoscimento rivista (priorità a pattern specifici)
        if _RE_DPC_DETECT.search(text):
            self._extract_dpc(text, meta)
        elif _RE_SP_DETECT.search(text):
            self._extract_sistema_penale(text, meta)
        else:
            self._extract_generic(text, meta)

        return meta

    # ------------------------------------------------------------------
    # Estrattori per rivista specifica
    # ------------------------------------------------------------------

    def _extract_dpc(self, text: str, meta: DottrinaMetadata) -> None:
        """Estrae metadati specifici DPC (Diritto Penale Contemporaneo)."""
        meta.rivista = "diritto_penale_contemporaneo"
        meta.titolo_doc = "Diritto Penale Contemporaneo"

        m = _RE_DPC_FASCICOLO.search(text)
        if m:
            num, anno = m.group(1), m.group(2)
            meta.fascicolo = f"{num}/{anno}"
            try:
                meta.anno_pubblicazione = int(anno)
            except ValueError:
                pass
        else:
            # Fallback: cerca anno standalone
            meta.anno_pubblicazione = _extract_year(text)

        # Autore dal direttore responsabile (proxy per articolo DPC)
        m_autore = _RE_DPC_AUTORE.search(text)
        if m_autore:
            meta.autore = _normalize_name(m_autore.group(1))

    def _extract_sistema_penale(self, text: str, meta: DottrinaMetadata) -> None:
        """Estrae metadati specifici Sistema Penale."""
        meta.rivista = "sistema_penale"
        meta.titolo_doc = "Sistema Penale"

        m = _RE_SP_ANNO_FASC.search(text)
        if m:
            anno, fasc = m.group(1), m.group(2)
            try:
                meta.anno_pubblicazione = int(anno)
            except ValueError:
                pass
            meta.fascicolo = f"Fasc. {fasc}/{anno}"
        else:
            meta.anno_pubblicazione = _extract_year(text)

        # Sistema Penale ha editor-in-chief esplicito: Gian Luigi Gatta
        meta.autore = "Gatta Gian Luigi"

    def _extract_generic(self, text: str, meta: DottrinaMetadata) -> None:
        """Estrae titolo/autore/anno da testo generico (monografie, paper)."""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # Prima riga non-vuota di lunghezza ragionevole → titolo
        for ln in lines[:5]:
            if 10 <= len(ln) <= 200:
                meta.titolo_doc = ln
                break

        # Seconda/terza riga con pattern "Cognome Nome" → autore
        candidate_lines = lines[1:6] if len(lines) > 1 else []
        for ln in candidate_lines:
            if ln == meta.titolo_doc:
                continue
            m = _RE_AUTORE_GENERIC.match(ln)
            if m:
                meta.autore = _normalize_name(m.group(1))
                break

        # Anno da prima occorrenza plausibile
        meta.anno_pubblicazione = _extract_year(text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_year(text: str) -> Optional[int]:
    """Ritorna il primo anno (1900-2099) trovato nel testo, o None."""
    m = _RE_ANNO.search(text)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def _normalize_name(name: str) -> str:
    """Normalizza spazi multipli e capitalizzazione nel nome."""
    return " ".join(name.split())
