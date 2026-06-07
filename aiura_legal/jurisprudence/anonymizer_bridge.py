"""
Bridge tra la pipeline giurisprudenziale e il LegalAnonymizer.
- SCRAPING: no-op (sentenze pubbliche, nessun PII rilevante)
- UPLOAD_STUDIO: anonimizza sempre e salva entity_map in pii_vault
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from loguru import logger

from aiura_legal.jurisprudence.models import JurisprudenceDocument, SourceChannel

if TYPE_CHECKING:
    import motor.motor_asyncio as motor

try:
    from aiura_legal.core.anonymizer.anonymizer import LegalAnonymizer
except ImportError:
    LegalAnonymizer = None  # type: ignore[assignment,misc]


async def anonymize_document(
    doc: JurisprudenceDocument,
    db: "motor.AsyncIOMotorDatabase",
) -> JurisprudenceDocument:
    """
    Restituisce una copia del documento anonimizzata se upload_studio.
    Scrive l'entity_map in pii_vault e imposta raw_pii_vault_id.
    """
    if doc.source_channel == SourceChannel.SCRAPING:
        return doc

    if LegalAnonymizer is None:
        logger.warning("LegalAnonymizer non disponibile — upload studio non anonimizzato")
        return doc

    anonymizer = LegalAnonymizer()
    full_text = "\n".join([doc.massima, doc.motivazione, doc.dispositivo])

    result = anonymizer.anonymize(full_text, doc_id=doc.id)

    # Salva entity_map nel pii_vault
    vault_doc = {
        "document_id": doc.id,
        "entity_map": result.entity_map,
        "workspace": "studio",
        "created_at": datetime.now(timezone.utc),
        "residual_warnings": result.residual_pii_warnings,
    }
    insert_result = await db["pii_vault"].insert_one(vault_doc)
    vault_id = str(insert_result.inserted_id)

    # Ripartisce il testo anonimizzato nelle tre sezioni originali
    anon_massima, anon_motivazione, anon_dispositivo = _split_anon_text(
        result.anonymized_text, doc
    )

    logger.info(
        "Anonimizzazione completata: doc={} vault_id={} entità={}",
        doc.id, vault_id, len(result.entity_map),
    )

    return JurisprudenceDocument(
        organo=doc.organo,
        numero=doc.numero,
        anno=doc.anno,
        data_deposito=doc.data_deposito,
        sezione=doc.sezione,
        materia=doc.materia,
        massima=anon_massima,
        motivazione=anon_motivazione,
        dispositivo=anon_dispositivo,
        norme_citate=doc.norme_citate,
        sentenze_citate=doc.sentenze_citate,
        source_url=doc.source_url,
        source_channel=doc.source_channel,
        is_anonymized=True,
        raw_pii_vault_id=vault_id,
    )


def _split_anon_text(
    anon_text: str, original: JurisprudenceDocument
) -> tuple[str, str, str]:
    """
    Ricostruisce le tre sezioni proporzionalmente alle lunghezze originali.
    Usato quando l'anonymizer restituisce un unico testo concatenato.
    """
    len_massima = len(original.massima)
    len_motivazione = len(original.motivazione)

    anon_massima = anon_text[:len_massima].strip()
    anon_motivazione = anon_text[len_massima + 1:len_massima + 1 + len_motivazione].strip()
    anon_dispositivo = anon_text[len_massima + 1 + len_motivazione + 1:].strip()

    return anon_massima, anon_motivazione, anon_dispositivo
