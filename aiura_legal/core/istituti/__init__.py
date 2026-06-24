"""
Layer "Istituto giuridico" — registro curato che lega:
  - istituto → norme (URN reali, per il tagging deterministico dei chunk)
  - istituto → sentenze pilota (groundabili, per guidare il ragionamento)
  - termini chiave + disambiguazione (per classificare le domande e separare
    istituti che condividono lessico, es. sequestro penale vs confisca antimafia)

Vedi registry.py per l'API e registry.yaml per il seed curato.
"""
from aiura_legal.core.istituti.registry import (
    Istituto,
    SentenzaPilota,
    IstitutoRegistry,
    load_registry,
    get_registry,
)

__all__ = [
    "Istituto",
    "SentenzaPilota",
    "IstitutoRegistry",
    "load_registry",
    "get_registry",
]
