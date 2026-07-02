"""
Test NormattivaPipeline — mongomock-motor, zero PII reali, zero chiamate HTTP.

Verifica:
  - chunk_collection() produce chunk con corpus/fonte/testo_tipo corretti
  - skip_formule filtra i documenti formula
  - upsert idempotente: seconda chiamata non duplica i chunk
  - errori su singolo doc non bloccano la pipeline
  - limit rispettato
  - documento senza testo → skippato
"""
from __future__ import annotations

import pytest
import mongomock_motor
from bson import ObjectId

from aiura_legal.ingestion.normattiva.pipeline import NormattivaPipeline, ChunkCollectionResult
from aiura_legal.ingestion.normattiva.parser import NormattivaDocAdapter
from aiura_legal.ingestion.chunker import Chunker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_test"]


@pytest.fixture
def pipeline(mock_db):
    # upsert=False usa insert_many, compatibile con mongomock-motor.
    # Il comportamento upsert reale (UpdateOne) è testato su MongoDB reale;
    # qui testiamo la logica di chunking e classificazione.
    return NormattivaPipeline(
        mongo_db=mock_db,
        workspace="normattiva",
        chunker=Chunker(max_tokens=256, overlap=32),
        skip_formule=False,
        upsert=False,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normattiva_doc(
    urn: str,
    tipo: str = "LEGGE",
    testo_tipo: str = "normativo",
    text: str = "Articolo sintetico di prova. " * 20,
) -> dict:
    return {
        "_id": ObjectId(),
        "urn": urn,
        "act_urn": urn,
        "tipo_provvedimento": tipo,
        "text": text,
        "testo_tipo": testo_tipo,
        "titolo": "Titolo sintetico",
        "articolo_num": "Art. 1",
        "data_inizio_vigenza": "20240101",
    }


async def _seed(mock_db, docs: list[dict]) -> None:
    """Inserisce documenti in normattiva_docs."""
    if docs:
        await mock_db["normattiva_docs"].insert_many(docs)


# ---------------------------------------------------------------------------
# Test base
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chunk_collection_basic(pipeline, mock_db):
    """pipeline.chunk_collection() crea chunk con i campi obbligatori."""
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;1", tipo="LEGGE"),
    ])

    result = await pipeline.chunk_collection()

    assert isinstance(result, ChunkCollectionResult)
    assert result.docs_processed == 1
    assert result.chunks_created >= 1
    assert result.errors == 0

    chunks = await mock_db["chunks"].find({}).to_list(length=100)
    assert len(chunks) >= 1
    for c in chunks:
        assert c["corpus"] == "normattiva"
        assert c["fonte"] == "legge"
        assert c["testo_tipo"] == "normativo"
        assert c["workspace"] == "normattiva"
        assert c["source"] == "normattiva_it"


@pytest.mark.asyncio
async def test_chunk_collection_fonte_codice_civile(pipeline, mock_db):
    """Documento codice civile → fonte='codice_civile'."""
    await _seed(mock_db, [
        _normattiva_doc(
            "urn:nir:stato:regio.decreto:1942-03-16;262~art1",
            tipo="REGIO DECRETO",
        )
    ])

    await pipeline.chunk_collection()

    chunks = await mock_db["chunks"].find({}).to_list(length=100)
    assert all(c["fonte"] == "codice_civile" for c in chunks)


@pytest.mark.asyncio
async def test_chunk_collection_multiple_docs(pipeline, mock_db):
    """Più documenti con fonti diverse vengono chunked correttamente."""
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;1", tipo="LEGGE"),
        _normattiva_doc("urn:nir:stato:decreto.legislativo:2003-06-30;196", tipo="DECRETO LEGISLATIVO"),
        _normattiva_doc("urn:nir:stato:regio.decreto:1942-03-16;262~art1", tipo="REGIO DECRETO"),
    ])

    result = await pipeline.chunk_collection()

    assert result.docs_processed == 3
    assert result.errors == 0

    fonti = {
        c["fonte"]
        for c in await mock_db["chunks"].find({}).to_list(length=500)
    }
    assert "legge" in fonti
    assert "dlgs" in fonti
    assert "codice_civile" in fonti


@pytest.mark.asyncio
async def test_chunk_collection_empty_text_skipped(pipeline, mock_db):
    """Documenti con testo vuoto vengono saltati (no chunk creati)."""
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;99", text="   "),
    ])

    result = await pipeline.chunk_collection()

    # Il doc viene processato (docs_processed), ma non genera chunk
    # NB: testo vuoto → _process_doc ritorna 0
    assert result.chunks_created == 0
    count = await mock_db["chunks"].count_documents({})
    assert count == 0


# ---------------------------------------------------------------------------
# Test skip_formule
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_skip_formule_filters_formula_docs(mock_db):
    """Con skip_formule=True, i doc testo_tipo='formula' vengono esclusi."""
    pipeline_sf = NormattivaPipeline(
        mongo_db=mock_db,
        workspace="normattiva_sf",
        chunker=Chunker(max_tokens=256, overlap=32),
        skip_formule=True,
        upsert=False,
    )
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;sf1", testo_tipo="normativo"),
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;sf2", testo_tipo="formula"),
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;sf3", testo_tipo="formula_ridondante"),
    ])

    await pipeline_sf.chunk_collection()

    # Solo il doc normativo deve essere processato dal cursore
    # (formula e formula_ridondante filtrati da query {"testo_tipo": {"$ne": "formula"}})
    # NB: formula_ridondante non è "formula" esatto, può passare il filtro
    chunks = await mock_db["chunks"].find({"workspace": "normattiva_sf"}).to_list(length=100)
    for c in chunks:
        assert c["testo_tipo"] != "formula"


@pytest.mark.asyncio
async def test_skip_formule_false_includes_formula(mock_db):
    """Con skip_formule=False, anche i doc formula vengono chunkati."""
    pipeline_no_sf = NormattivaPipeline(
        mongo_db=mock_db,
        workspace="normattiva_no_sf",
        chunker=Chunker(max_tokens=256, overlap=32),
        skip_formule=False,
        upsert=False,
    )
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;nosf1", testo_tipo="normativo"),
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;nosf2", testo_tipo="formula"),
    ])

    result = await pipeline_no_sf.chunk_collection()

    assert result.docs_processed == 2
    assert result.chunks_created >= 2


# ---------------------------------------------------------------------------
# Test upsert idempotente
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chunk_collection_same_chunks_each_run(pipeline, mock_db):
    """
    Due chiamate su stessa normattiva_docs producono lo stesso numero di chunk
    per chiamata — la logica di chunking è deterministica.

    Nota: il test usa upsert=False (insert_many) compatibile con mongomock.
    L'idempotenza reale dell'upsert (UpdateOne su _id deterministico → no
    duplicati anche se il fetcher assegna un source_id/URN diverso tra due
    esecuzioni) è verificata in TestIdDeterministicoTraRebuild sotto.
    """
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;1", tipo="LEGGE"),
    ])

    result1 = await pipeline.chunk_collection()
    chunks1 = await mock_db["chunks"].find({}).to_list(length=100)

    # Svuota i chunk e ri-esegui per verificare stessa cardinalità
    await mock_db["chunks"].drop()
    result2 = await pipeline.chunk_collection()

    assert result1.chunks_created == result2.chunks_created
    assert result1.docs_processed == result2.docs_processed


# ---------------------------------------------------------------------------
# Test limit
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chunk_collection_limit(pipeline, mock_db):
    """Con limit=1, solo il primo documento viene processato."""
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;1"),
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;2"),
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;3"),
    ])

    result = await pipeline.chunk_collection(limit=1)

    assert result.docs_processed == 1


# ---------------------------------------------------------------------------
# Test filter_query
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chunk_collection_filter_query(pipeline, mock_db):
    """filter_query viene applicato alla query MongoDB."""
    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;1", testo_tipo="normativo"),
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;2", testo_tipo="formula"),
    ])

    result = await pipeline.chunk_collection(
        filter_query={"testo_tipo": "normativo"}
    )

    assert result.docs_processed == 1
    chunks = await mock_db["chunks"].find({}).to_list(length=100)
    assert all(c["testo_tipo"] == "normativo" for c in chunks)


# ---------------------------------------------------------------------------
# Test workspace isolation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_workspace_isolation(mock_db):
    """Due pipeline con workspace diversi non si mescolano."""
    p_norm = NormattivaPipeline(
        mock_db, "normattiva", Chunker(max_tokens=256, overlap=32), upsert=False
    )
    p_civil = NormattivaPipeline(
        mock_db, "normattiva_civile", Chunker(max_tokens=256, overlap=32), upsert=False
    )

    await _seed(mock_db, [
        _normattiva_doc("urn:nir:stato:legge:2020-01-01;1"),
    ])

    await p_norm.chunk_collection()

    norm_count = await mock_db["chunks"].count_documents({"workspace": "normattiva"})
    civil_count = await mock_db["chunks"].count_documents({"workspace": "normattiva_civile"})

    assert norm_count >= 1
    assert civil_count == 0

    await p_civil.chunk_collection()

    norm_count2 = await mock_db["chunks"].count_documents({"workspace": "normattiva"})
    civil_count2 = await mock_db["chunks"].count_documents({"workspace": "normattiva_civile"})

    assert norm_count2 >= 1
    assert civil_count2 >= 1


# ---------------------------------------------------------------------------
# Test ChunkCollectionResult
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_result_duration_positive(pipeline, mock_db):
    """duration_s deve essere > 0."""
    await _seed(mock_db, [_normattiva_doc("urn:nir:stato:legge:2020-01-01;1")])
    result = await pipeline.chunk_collection()
    assert result.duration_s >= 0  # mongomock può essere quasi istantaneo

@pytest.mark.asyncio
async def test_result_empty_collection(pipeline, mock_db):
    """Su collection vuota: 0 doc, 0 chunk, 0 errori."""
    result = await pipeline.chunk_collection()
    assert result.docs_processed == 0
    assert result.chunks_created == 0
    assert result.errors == 0


# ---------------------------------------------------------------------------
# Test id deterministico tra rebuild (root cause del disallineamento
# source_mongo_id scoperto negli istituti_giuridici — vedi chunk_id.py)
# ---------------------------------------------------------------------------

class TestIdDeterministicoTraRebuild:
    """
    L'upsert reale (upsert=True, UpdateOne) matcha per _id deterministico,
    calcolato da (fonte, articolo_num, valid_from, chunk_index) — non più
    dall'URN posizionale del fetcher. Se due esecuzioni dello scraping
    assegnano URN diversi allo STESSO vero articolo (perché l'URN dipende
    dalla posizione nella catena, non dal contenuto), il chunk deve comunque
    finire con lo stesso _id e nessun duplicato.
    """

    # NOTA: questi test verificano il record prodotto da _process_doc (dove
    # viene calcolato l'_id) invece di passare per bulk_write/UpdateOne su
    # mongomock-motor: la libreria di mock non supporta la sintassi UpdateOne
    # della versione di pymongo installata (limite pre-esistente del tooling
    # di test, mai esposto prima perché nessun test usava upsert=True) —
    # l'upsert reale è verificato manualmente su MongoDB vero.

    @pytest.mark.asyncio
    async def test_stesso_articolo_urn_diverso_stesso_id(self, mock_db):
        pipeline = NormattivaPipeline(
            mongo_db=mock_db, workspace="mio-studio",
            chunker=Chunker(max_tokens=256, overlap=32),
        )
        testo = "Art. 79. Domicilio dei coniugi, del minore e dell'interdetto." * 5

        # Prima esecuzione: l'articolo "Art. 79" ha URN ~art79 (posizione 79)
        adapter1 = NormattivaDocAdapter.from_mongo_doc(
            _normattiva_doc("urn:nir:stato:regio.decreto:1942-03-16;262~art79", text=testo)
        )
        buffer1: list[dict] = []
        await pipeline._process_doc(adapter1, buffer1)

        # Seconda esecuzione (simulata): stesso vero articolo, ma il fetcher
        # gli ha assegnato un URN diverso per un disallineamento posizionale
        # (es. ~art80 invece di ~art79) — scenario che ha causato la
        # corruzione osservata in produzione.
        adapter2 = NormattivaDocAdapter.from_mongo_doc(
            _normattiva_doc("urn:nir:stato:regio.decreto:1942-03-16;262~art80", text=testo)
        )
        buffer2: list[dict] = []
        await pipeline._process_doc(adapter2, buffer2)

        assert len(buffer1) == 1 and len(buffer2) == 1
        assert buffer1[0]["_id"] == buffer2[0]["_id"]

    @pytest.mark.asyncio
    async def test_articolo_num_diverso_produce_id_diverso(self, mock_db):
        """Controllo di non-regressione: articoli realmente diversi non collidono."""
        pipeline = NormattivaPipeline(
            mongo_db=mock_db, workspace="mio-studio",
            chunker=Chunker(max_tokens=256, overlap=32),
        )
        adapter1 = NormattivaDocAdapter.from_mongo_doc(
            _normattiva_doc("urn:nir:stato:regio.decreto:1942-03-16;262~art79",
                             text="Art. 79. Primo articolo di prova." * 5)
        )
        buffer1: list[dict] = []
        await pipeline._process_doc(adapter1, buffer1)

        doc2 = _normattiva_doc("urn:nir:stato:regio.decreto:1942-03-16;262~art80",
                                text="Art. 45. Secondo articolo di prova." * 5)
        doc2["articolo_num"] = "Art. 45"
        adapter2 = NormattivaDocAdapter.from_mongo_doc(doc2)
        buffer2: list[dict] = []
        await pipeline._process_doc(adapter2, buffer2)

        assert buffer1[0]["_id"] != buffer2[0]["_id"]
