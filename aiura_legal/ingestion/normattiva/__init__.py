"""AiUra LegalLab — modulo ingestione Normattiva."""
from aiura_legal.ingestion.normattiva.parser import fonte_from_doc, NormattivaDocAdapter
from aiura_legal.ingestion.normattiva.pipeline import NormattivaPipeline

__all__ = ["fonte_from_doc", "NormattivaDocAdapter", "NormattivaPipeline"]
