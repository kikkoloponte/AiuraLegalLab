"""
Test parser/pipeline TFUE — mongomock-motor, zero MongoDB reale, zero PII.

Il testo usato nei fixture è sintetico (mimico della struttura ufficiale
Parte/Titolo/Capo/Sezione/Articolo del TFUE), non una copia del testo
consolidato reale.
"""
from __future__ import annotations

import pytest
import mongomock_motor

from aiura_legal.ingestion.eu_treaties.parser import (
    TfueArticle,
    TfueDocAdapter,
    parse_tfue_html,
    parse_tfue_lines,
)
from aiura_legal.ingestion.eu_treaties.pipeline import TfuePipeline, TfueChunkResult


# ---------------------------------------------------------------------------
# Fixtures testo sintetico
# ---------------------------------------------------------------------------

_SAMPLE_LINES = [
    "PARTE TERZA",
    "LE POLITICHE E AZIONI INTERNE DELL'UNIONE",
    "TITOLO VII",
    "NORME COMUNI SULLA CONCORRENZA, SULLA FISCALITÀ E SUL RAVVICINAMENTO DELLE LEGISLAZIONI",
    "CAPO 1",
    "Le regole di concorrenza",
    "Sezione 1",
    "Regole applicabili alle imprese",
    "Articolo 101",
    "1.   Sono incompatibili con il mercato interno e vietati tutti gli accordi tra imprese.",
    "2.   Gli accordi vietati in virtù del presente articolo sono nulli di pieno diritto.",
    "Articolo 102",
    "È incompatibile con il mercato interno e vietato lo sfruttamento abusivo.",
    "TITOLO VIII",
    "POLITICA ECONOMICA E MONETARIA",
    "Articolo 119",
    "1.   Ai fini enunciati all'articolo 3 del trattato sull'Unione europea.",
    "PROTOCOLLO N. 1",
    "SUL RUOLO DEI PARLAMENTI NAZIONALI",
    "Articolo 1",
    "Testo del protocollo che non deve essere incluso nel parsing.",
]


def _sample_html() -> str:
    body = "".join(f"<p>{line}</p>" for line in _SAMPLE_LINES)
    return f"<html><body>{body}</body></html>"


# ---------------------------------------------------------------------------
# Parser — gerarchia e confini articolo
# ---------------------------------------------------------------------------

def test_parse_tfue_lines_extracts_all_articles_before_protocol():
    articles = parse_tfue_lines(_SAMPLE_LINES)
    numeri = [a.numero for a in articles]
    assert numeri == ["101", "102", "119"]


def test_parse_tfue_lines_stops_at_protocol():
    articles = parse_tfue_lines(_SAMPLE_LINES)
    # Il "Articolo 1" dentro il Protocollo non deve comparire
    assert "1" not in [a.numero for a in articles]


def test_parse_tfue_lines_captures_gerarchia():
    articles = parse_tfue_lines(_SAMPLE_LINES)
    art101 = next(a for a in articles if a.numero == "101")
    assert art101.parte == "PARTE TERZA"
    assert art101.titolo_sezione == "TITOLO VII"
    assert art101.capo == "CAPO 1"
    assert art101.sezione == "Sezione 1"


def test_parse_tfue_lines_gerarchia_resets_on_new_titolo():
    articles = parse_tfue_lines(_SAMPLE_LINES)
    art119 = next(a for a in articles if a.numero == "119")
    assert art119.titolo_sezione == "TITOLO VIII"
    # Capo/Sezione del titolo precedente non devono persistere
    assert art119.capo == ""
    assert art119.sezione == ""


def test_parse_tfue_lines_captures_body_text():
    articles = parse_tfue_lines(_SAMPLE_LINES)
    art101 = next(a for a in articles if a.numero == "101")
    assert "incompatibili con il mercato interno" in art101.testo
    assert "nulli di pieno diritto" in art101.testo


def test_parse_tfue_html_matches_parse_lines():
    articles = parse_tfue_html(_sample_html())
    assert [a.numero for a in articles] == ["101", "102", "119"]


def test_parse_tfue_lines_empty_input():
    assert parse_tfue_lines([]) == []


# ---------------------------------------------------------------------------
# Frontespizio EUR-Lex — tabella "Contiene: Gazzetta ufficiale ..." con la
# cronologia delle modifiche cita per esteso titoli di protocolli/decisioni
# (incluse righe che iniziano per "PROTOCOLLO") ben prima dell'articolato.
# ---------------------------------------------------------------------------

_FRONT_MATTER_LINES = [
    "TESTO consolidato: 12016E/TXT — IT — 01.09.2024",
    "Il presente testo è un semplice strumento di documentazione.",
    "VERSIONE CONSOLIDATA",
    "DEL TRATTATO SUL FUNZIONAMENTO DELL'UNIONE EUROPEA",
    "Contiene:",
    "PROTOCOLLO",
    "CHE MODIFICA IL PROTOCOLLO SULLE DISPOSIZIONI TRANSITORIE",
    "DECISIONE DEL CONSIGLIO EUROPEO",
]


def test_parse_tfue_lines_skips_frontmatter_protocol_mention():
    lines = _FRONT_MATTER_LINES + _SAMPLE_LINES
    articles = parse_tfue_lines(lines)
    assert [a.numero for a in articles] == ["101", "102", "119"]


# ---------------------------------------------------------------------------
# TfueDocAdapter
# ---------------------------------------------------------------------------

def test_adapter_source_id_and_articolo_num():
    article = TfueArticle(numero="101", testo="Testo di prova.", parte="PARTE TERZA")
    adapter = TfueDocAdapter.from_article(article)
    assert adapter.source_id == "urn:eu:tfue:art101"
    assert adapter.articolo_num == "Art. 101 TFUE"


def test_adapter_to_chunk_base_fields():
    article = TfueArticle(
        numero="101", testo="Testo di prova.",
        parte="PARTE TERZA", titolo_sezione="TITOLO VII",
    )
    adapter = TfueDocAdapter.from_article(article)
    base = adapter.to_chunk_base(workspace="mio-studio")

    assert base["corpus"] == "normattiva"
    assert base["fonte"] == "trattato_ue"
    assert base["source"] == "eurlex_tfue"
    assert base["settore"] == ["unione_europea"]
    assert base["workspace"] == "mio-studio"
    assert "PARTE TERZA" in base["titolo"]
    assert "TITOLO VII" in base["titolo"]


def test_adapter_titolo_senza_gerarchia():
    article = TfueArticle(numero="1", testo="Testo.")
    adapter = TfueDocAdapter.from_article(article)
    assert adapter.titolo == "TFUE"


# ---------------------------------------------------------------------------
# TfuePipeline — chunking + persistenza MongoDB (mongomock)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_test"]


@pytest.mark.asyncio
async def test_pipeline_chunk_articles_basic(mock_db):
    pipeline = TfuePipeline(mongo_db=mock_db, workspace="mio-studio", upsert=False)
    articles = parse_tfue_lines(_SAMPLE_LINES)

    result = await pipeline.chunk_articles(articles)

    assert isinstance(result, TfueChunkResult)
    assert result.articles_processed == 3
    assert result.chunks_created >= 3

    chunks = await mock_db["chunks"].find({}).to_list(length=100)
    assert len(chunks) == result.chunks_created
    for c in chunks:
        assert c["corpus"] == "normattiva"
        assert c["fonte"] == "trattato_ue"
        assert c["workspace"] == "mio-studio"
        assert c["articolo_num"].endswith("TFUE")


@pytest.mark.asyncio
async def test_pipeline_skips_empty_text(mock_db):
    pipeline = TfuePipeline(mongo_db=mock_db, workspace="mio-studio", upsert=False)
    articles = [TfueArticle(numero="999", testo="   ")]

    result = await pipeline.chunk_articles(articles)

    assert result.articles_processed == 0
    assert result.chunks_created == 0
    count = await mock_db["chunks"].count_documents({})
    assert count == 0


@pytest.mark.asyncio
async def test_pipeline_workspace_isolation(mock_db):
    p_a = TfuePipeline(mongo_db=mock_db, workspace="ws-a", upsert=False)
    p_b = TfuePipeline(mongo_db=mock_db, workspace="ws-b", upsert=False)
    articles = parse_tfue_lines(_SAMPLE_LINES)

    await p_a.chunk_articles(articles)
    count_a = await mock_db["chunks"].count_documents({"workspace": "ws-a"})
    count_b = await mock_db["chunks"].count_documents({"workspace": "ws-b"})
    assert count_a >= 1
    assert count_b == 0

    await p_b.chunk_articles(articles)
    count_b2 = await mock_db["chunks"].count_documents({"workspace": "ws-b"})
    assert count_b2 >= 1


@pytest.mark.asyncio
async def test_pipeline_empty_article_list(mock_db):
    pipeline = TfuePipeline(mongo_db=mock_db, workspace="mio-studio", upsert=False)
    result = await pipeline.chunk_articles([])
    assert result.articles_processed == 0
    assert result.chunks_created == 0
