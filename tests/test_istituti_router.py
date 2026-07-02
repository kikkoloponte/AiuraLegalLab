"""
Test istituti_router — solo l'endpoint /istituti/resolve-chunks (mongomock-motor,
stesso pattern di TestAnnotateEndpoints in test_annotator.py). Gli altri endpoint
CRUD non hanno ancora una suite dedicata a livello di router.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def mock_mongo_db():
    import mongomock_motor
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_lab_db"]


@pytest.fixture
def client(mock_mongo_db):
    from aiura_legal.api.istituti_router import router
    from aiura_legal.ingestion.mongodb.client import MongoClient

    with patch.object(MongoClient, "get") as mock_get:
        mock_instance = MagicMock()
        mock_instance.chunks = mock_mongo_db["chunks"]
        mock_get.return_value = mock_instance

        app = FastAPI()
        app.include_router(router, prefix="/istituti")
        yield TestClient(app)


class TestResolveChunks:

    @pytest.mark.asyncio
    async def test_risolve_chunk_esistente(self, client, mock_mongo_db):
        from bson import ObjectId

        oid = ObjectId()
        await mock_mongo_db["chunks"].insert_one({
            "_id": oid,
            "titolo": "REGIO DECRETO 19 ottobre 1930, n. 1398",
            "articolo_num": "Art. 321",
            "titolo_articolo": "Oggetto del sequestro preventivo",
            "corpus": "normattiva",
        })

        resp = client.get("/istituti/resolve-chunks", params={"ids": str(oid)})
        assert resp.status_code == 200
        labels = resp.json()["labels"]
        assert labels[str(oid)] == "Art. 321 — Oggetto del sequestro preventivo — [normattiva]"

    def test_id_malformato_omesso_senza_errore(self, client):
        resp = client.get("/istituti/resolve-chunks", params={"ids": "non-un-objectid"})
        assert resp.status_code == 200
        assert resp.json()["labels"] == {}

    @pytest.mark.asyncio
    async def test_id_inesistente_omesso(self, client, mock_mongo_db):
        from bson import ObjectId
        resp = client.get("/istituti/resolve-chunks", params={"ids": str(ObjectId())})
        assert resp.status_code == 200
        assert resp.json()["labels"] == {}

    @pytest.mark.asyncio
    async def test_lista_mista_risolve_solo_i_presenti(self, client, mock_mongo_db):
        from bson import ObjectId

        oid_ok = ObjectId()
        oid_assente = ObjectId()
        await mock_mongo_db["chunks"].insert_one({
            "_id": oid_ok, "titolo": "Titolo", "articolo_num": "Art. 1",
            "titolo_articolo": "", "corpus": "normattiva",
        })

        resp = client.get("/istituti/resolve-chunks", params={
            "ids": f"{oid_ok},{oid_assente},non-valido",
        })
        assert resp.status_code == 200
        labels = resp.json()["labels"]
        assert list(labels.keys()) == [str(oid_ok)]
