"""
AiUra LegalLab — Legal Graph (1C).

Componenti:
  ReferenceExtractor  — estrae rimandi inter-articolo con regex + euristiche
  LegalGraphBuilder   — costruisce e aggiorna il grafo NetworkX su disco
  GraphRetriever      — neighbor expansion (con filtro vigenza) e conflict detection

Import espliciti per evitare import circolari durante la build incrementale.
"""
from aiura_legal.core.graph.extractor import ReferenceExtractor, ReferenceMatch

__all__ = [
    "ReferenceExtractor",
    "ReferenceMatch",
]


def __getattr__(name: str):  # type: ignore[override]
    """Lazy import di LegalGraphBuilder e GraphRetriever."""
    if name == "LegalGraphBuilder":
        from aiura_legal.core.graph.builder import LegalGraphBuilder  # noqa: PLC0415
        return LegalGraphBuilder
    if name == "GraphRetriever":
        from aiura_legal.core.graph.retriever import GraphRetriever  # noqa: PLC0415
        return GraphRetriever
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
