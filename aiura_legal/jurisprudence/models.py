"""
Modelli dati per la pipeline giurisprudenziale.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class OrganoGiudicante(str, Enum):
    CASSAZIONE = "cassazione"
    TAR = "tar"
    CONSIGLIO_STATO = "consiglio_stato"
    CORTE_COST = "corte_cost"
    CORTE_CONTI = "corte_conti"


class SourceChannel(str, Enum):
    SCRAPING = "scraping"
    UPLOAD_STUDIO = "upload_studio"
    OPEN_DATA = "open_data"      # dati scaricati da portali open data pubblici


@dataclass
class RawSentenza:
    """Testo grezzo + metadati minimi scaricati dalla fonte."""
    numero: str
    anno: int
    organo: OrganoGiudicante
    source_url: str
    raw_html: Optional[str] = None
    raw_pdf_bytes: Optional[bytes] = None
    data_deposito: Optional[date] = None


@dataclass
class JurisprudenceDocument:
    """Sentenza strutturata pronta per indicizzazione."""
    organo: OrganoGiudicante
    numero: str
    anno: int
    data_deposito: date
    sezione: str
    materia: str

    massima: str
    motivazione: str
    dispositivo: str

    norme_citate: list[str] = field(default_factory=list)
    sentenze_citate: list[str] = field(default_factory=list)

    source_url: str = ""
    source_channel: SourceChannel = SourceChannel.SCRAPING
    is_anonymized: bool = False
    raw_pii_vault_id: Optional[str] = None

    @property
    def id(self) -> str:
        key = f"{self.organo.value}:{self.numero}:{self.anno}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
