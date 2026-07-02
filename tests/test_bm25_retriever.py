"""
Test BM25Retriever — filtro chunk_filter su campi multi-valore (settore).

Copre la regressione: chunk_filter={"settore": "penale"} non escludeva mai
i chunk fuori settore, perché (a) _BM25Sub.chunk_meta non salvava affatto il
campo "settore" e (b) il confronto era un'uguaglianza esatta contro il
valore list[str] reale (["penale"] == "penale" è sempre False). Il filtro
azzerava quindi ogni score indipendentemente dal settore richiesto, facendo
scattare il fallback "nessun filtro" ad ogni chiamata — scoperto testando
end-to-end il filtro settore dopo aver corretto settore_confidence in
analyst.py (prima hardcoded 0.0, mai sopra soglia).
"""
from __future__ import annotations

from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.types import Document


def _doc(doc_id: str, text: str, settore: list[str], fonte: str = "codice_penale") -> Document:
    return Document(
        id=doc_id,
        text=text,
        source_id=doc_id,
        metadata={
            "corpus": "normattiva",
            "fonte": fonte,
            "testo_tipo": "normativo",
            "settore": settore,
        },
    )


def test_filtro_settore_esclude_altri_settori(tmp_path):
    retriever = BM25Retriever(str(tmp_path))
    retriever.build([
        _doc("penale1", "sequestro preventivo per equivalente nei confronti del terzo estraneo", ["penale"]),
        _doc("civile1", "sequestro conservativo a tutela del credito nei confronti del debitore", ["civile"], fonte="codice_civile"),
    ])

    results = retriever.search(
        "sequestro terzo estraneo",
        top_k=10,
        chunk_filter={"corpus": "normattiva", "settore": "penale"},
    )

    ids = {r.doc_id for r in results if r.score > 0}
    assert "penale1" in ids
    assert "civile1" not in ids


def test_filtro_settore_include_chunk_multi_settore(tmp_path):
    """Un chunk con settore=["penale","altro"] deve comunque matchare il filtro "penale"."""
    retriever = BM25Retriever(str(tmp_path))
    retriever.build([
        _doc("multi1", "sequestro preventivo per equivalente", ["penale", "altro"]),
    ])

    results = retriever.search(
        "sequestro preventivo",
        top_k=10,
        chunk_filter={"corpus": "normattiva", "settore": "penale"},
    )

    assert any(r.doc_id == "multi1" and r.score > 0 for r in results)


def test_senza_filtro_settore_nessuna_esclusione(tmp_path):
    """Comportamento invariato quando il filtro settore non è richiesto."""
    retriever = BM25Retriever(str(tmp_path))
    retriever.build([
        _doc("penale1", "sequestro preventivo per equivalente", ["penale"]),
        _doc("civile1", "sequestro conservativo del credito", ["civile"], fonte="codice_civile"),
    ])

    results = retriever.search(
        "sequestro",
        top_k=10,
        chunk_filter={"corpus": "normattiva"},
    )

    ids = {r.doc_id for r in results if r.score > 0}
    assert "penale1" in ids
    assert "civile1" in ids
