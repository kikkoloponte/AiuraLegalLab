"""
Test settings_router — GET/POST /settings con whitelist completa.

Bug originale: QDRANT_URL era in _WHITELIST/_DEFAULTS ma mancava da
LLMSettings, _settings_from_env e save_settings → dichiarata configurabile
dalla Settings UI ma né mostrabile né salvabile.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from aiura_legal.api import settings_router
from aiura_legal.api.settings_router import _DEFAULTS, _WHITELIST, LLMSettings


@pytest.fixture
def env_path(tmp_path, monkeypatch):
    """Reindirizza .env su un file temporaneo e disarma il riavvio API."""
    path = tmp_path / ".env"
    monkeypatch.setattr(settings_router, "_ENV_PATH", path)
    monkeypatch.setattr(settings_router, "_do_restart", lambda: None)
    monkeypatch.delenv("AIURA_API_KEY", raising=False)
    return path


@pytest.fixture
def client(env_path):
    app = FastAPI()
    app.include_router(settings_router.router)
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# Coerenza whitelist
# ---------------------------------------------------------------------------

def test_whitelist_and_defaults_aligned():
    assert set(_WHITELIST) == set(_DEFAULTS.keys())


def test_post_persists_every_whitelist_key(client, env_path):
    """Regressione: ogni variabile in _WHITELIST deve finire nel .env dopo il POST."""
    resp = client.post("/settings", json={})
    assert resp.status_code == 200
    env_keys = {
        line.partition("=")[0]
        for line in env_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    missing = set(_WHITELIST) - env_keys
    assert not missing, f"variabili whitelist non salvate: {missing}"


# ---------------------------------------------------------------------------
# GET /settings — qdrant_url
# ---------------------------------------------------------------------------

def test_get_qdrant_url_from_env(client, env_path):
    env_path.write_text("QDRANT_URL=http://localhost:6333\n", encoding="utf-8")
    resp = client.get("/settings")
    assert resp.status_code == 200
    assert resp.json()["settings"]["qdrant_url"] == "http://localhost:6333"


def test_get_qdrant_url_default_empty(client, env_path):
    """Senza QDRANT_URL nel .env il default è vuoto = Qdrant embedded."""
    assert not env_path.exists()
    resp = client.get("/settings")
    assert resp.status_code == 200
    assert resp.json()["settings"]["qdrant_url"] == ""


# ---------------------------------------------------------------------------
# POST /settings — qdrant_url
# ---------------------------------------------------------------------------

def test_post_saves_qdrant_url(client, env_path):
    resp = client.post("/settings", json={"qdrant_url": "http://qdrant-server:6333"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert "QDRANT_URL=http://qdrant-server:6333" in env_path.read_text(encoding="utf-8")


def test_post_empty_qdrant_url_means_embedded(client, env_path):
    """Stringa vuota accettata e salvata: ripristina la embedded mode."""
    env_path.write_text("QDRANT_URL=http://localhost:6333\n", encoding="utf-8")
    resp = client.post("/settings", json={"qdrant_url": ""})
    assert resp.status_code == 200
    env_text = env_path.read_text(encoding="utf-8")
    assert "QDRANT_URL=\n" in env_text or env_text.endswith("QDRANT_URL=")


def test_post_invalid_qdrant_url_rejected(client):
    resp = client.post("/settings", json={"qdrant_url": "localhost:6333"})
    assert resp.status_code == 422


def test_post_qdrant_url_roundtrip(client, env_path):
    """Il valore salvato deve essere rileggibile identico dal GET successivo."""
    client.post("/settings", json={"qdrant_url": "http://localhost:6333"})
    resp = client.get("/settings")
    assert resp.json()["settings"]["qdrant_url"] == "http://localhost:6333"


# ---------------------------------------------------------------------------
# Validazione modello
# ---------------------------------------------------------------------------

def test_qdrant_url_trailing_slash_stripped():
    assert LLMSettings(qdrant_url="http://localhost:6333/").qdrant_url == "http://localhost:6333"


def test_qdrant_url_whitespace_only_is_empty():
    assert LLMSettings(qdrant_url="   ").qdrant_url == ""
