"""
Modelli Pydantic per gli Istituti Giuridici (vedi
docs/superpowers/specs/2026-06-30-istituti-giuridici-crud-design.md).

Struttura 1:1 con il payload prodotto a partire dall'analisi della KB
MongoDB (aiura_legal_lab_db.chunks): metadata_ui, denominazione,
codice_riferimento, quadro_normativo, definizione_e_natura_giuridica,
elementi_costitutivi, formazione_giurisprudenziale.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

CodiceRiferimento = str  # "CC" | "CPC" | "CP" | "CPP" — validato lato UI, non vincolato qui per non bloccare casi limite (es. leggi speciali extracodicistiche)


class MetadataUI(BaseModel):
    progetto: str = "AiuraLegalLab"
    stato_istanza: str = "ready_for_ui_crud"
    fonti_mongodb_coinvolte: list[str] = Field(default_factory=list)


class RiferimentoNormativo(BaseModel):
    riferimento: str
    source_mongo_id: Optional[str] = None


class QuadroNormativo(BaseModel):
    articoli_principali: list[RiferimentoNormativo] = Field(default_factory=list)
    leggi_complementari: list[RiferimentoNormativo] = Field(default_factory=list)


class DefinizioneNaturaGiuridica(BaseModel):
    testo: Optional[str] = None
    source_mongo_id: Optional[str] = None


class ElementoCostitutivo(BaseModel):
    id_elemento_ui: str
    descrizione: str
    source_mongo_id: Optional[str] = None


class MassimaChiave(BaseModel):
    riferimento_sentenza: str
    principio_diritto: str
    source_mongo_id: Optional[str] = None


class FormazioneGiurisprudenziale(BaseModel):
    orientamento_prevalente: Optional[str] = None
    massime_chiave: list[MassimaChiave] = Field(default_factory=list)
    contrasti_risolti_o_aperti: Optional[str] = None


class IstitutoGiuridicoCreate(BaseModel):
    """Payload accettato in POST /istituti e come body di PUT /istituti/{id}."""

    metadata_ui: MetadataUI = Field(default_factory=MetadataUI)
    denominazione: str
    codice_riferimento: CodiceRiferimento
    raggruppamento: Optional[str] = None  # es. "Persone e Famiglia", "Successioni" — secondo livello dell'albero UI
    quadro_normativo: QuadroNormativo = Field(default_factory=QuadroNormativo)
    definizione_e_natura_giuridica: DefinizioneNaturaGiuridica = Field(
        default_factory=DefinizioneNaturaGiuridica
    )
    elementi_costitutivi: list[ElementoCostitutivo] = Field(default_factory=list)
    formazione_giurisprudenziale: FormazioneGiurisprudenziale = Field(
        default_factory=FormazioneGiurisprudenziale
    )


class IstitutoGiuridico(IstitutoGiuridicoCreate):
    """Documento persistito, con id/version/updated_at assegnati dallo store."""

    id: str
    version: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
