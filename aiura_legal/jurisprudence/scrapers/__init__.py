from aiura_legal.jurisprudence.scrapers.base import BaseScraper
from aiura_legal.jurisprudence.scrapers.cassazione import CassazioneScraper
from aiura_legal.jurisprudence.scrapers.giustizia_amm import GiustiziaAmmScraper
from aiura_legal.jurisprudence.scrapers.corte_cost import CorteCostScraper
from aiura_legal.jurisprudence.scrapers.corte_conti import CorteContiScraper

__all__ = [
    "BaseScraper",
    "CassazioneScraper",
    "GiustiziaAmmScraper",
    "CorteCostScraper",
    "CorteContiScraper",
]
