"""
Modelli dati per la pipeline prassi amministrativa.
Copre: circolari, risoluzioni, interpelli, provvedimenti.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class TipoPrassi(str, Enum):
    CIRCOLARE           = "circolare"
    RISOLUZIONE         = "risoluzione"
    RISPOSTA_INTERPELLO = "risposta_interpello"
    PROVVEDIMENTO       = "provvedimento"
    NOTA                = "nota"


class EmittentePrassi(str, Enum):
    AGENZIA_ENTRATE = "agenzia_entrate"
    MEF             = "mef"
    INPS            = "inps"
    INAIL           = "inail"


@dataclass
class RawPrassi:
    """Documento grezzo scaricato dalla fonte (prima del parsing)."""
    tipo:       TipoPrassi
    emittente:  EmittentePrassi
    numero:     str          # es. "2/E", "20", "15"
    anno:       int
    titolo:     str
    source_url: str
    pdf_url:    Optional[str]       = None
    raw_pdf_bytes: Optional[bytes]  = None
    data_emissione: Optional[date]  = None
    asset_id:   Optional[str]       = None   # Liferay analytics asset ID


@dataclass
class PrassiDocument:
    """Documento prassi strutturato, pronto per indicizzazione."""
    tipo:         TipoPrassi
    emittente:    EmittentePrassi
    numero:       str
    anno:         int
    data_emissione: date
    titolo:       str

    testo:        str          # testo completo estratto dal PDF
    materia:      str = ""     # es. "IVA", "IRPEF", "concordato preventivo"

    norme_citate:      list[str] = field(default_factory=list)
    source_url:        str = ""
    pdf_url:           str = ""
    ingested_at:       Optional[str] = None

    @property
    def id(self) -> str:
        key = f"{self.emittente.value}:{self.tipo.value}:{self.numero}:{self.anno}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    @property
    def riferimento(self) -> str:
        """Es. 'Circolare AdE n. 2/E del 24/02/2026'"""
        emittente_label = {
            EmittentePrassi.AGENZIA_ENTRATE: "AdE",
            EmittentePrassi.MEF: "MEF",
            EmittentePrassi.INPS: "INPS",
            EmittentePrassi.INAIL: "INAIL",
        }.get(self.emittente, self.emittente.value)
        tipo_label = self.tipo.value.replace("_", " ").capitalize()
        return f"{tipo_label} {emittente_label} n. {self.numero} del {self.data_emissione.strftime('%d/%m/%Y')}"
