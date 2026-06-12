"""
Test QdrantSettings — QDRANT_URL letto via pydantic-settings (.env),
non più via os.environ diretto, e WARNING su collection vuota.

Bug originale: avviando l'API da una shell pulita, QDRANT_URL nel .env
veniva ignorato (nessun load_dotenv) → Qdrant partiva embedded con 0
punti e il retrieval vettoriale era silenziosamente disattivato.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from aiura_legal.core.retrieval.vector_retriever import (
    QdrantSettings,
    VectorRetriever,
    _COLLECTION_NAME,
)


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """Nessuna QDRANT_URL nell'ambiente e nessun .env nel CWD."""
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _mock_client(count: int = 0, has_collection: bool = True) -> MagicMock:
    client = MagicMock()
    cols = [SimpleNamespace(name=_COLLECTION_NAME)] if has_collection else []
    client.get_collections.return_value = SimpleNamespace(collections=cols)
    client.count.return_value = SimpleNamespace(count=count)
    return client


# ---------------------------------------------------------------------------
# Lettura della setting
# ---------------------------------------------------------------------------

class TestQdrantSettings:
    def test_default_embedded(self, clean_env):
        assert QdrantSettings().qdrant_url == ""

    def test_env_var(self, clean_env, monkeypatch):
        monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
        assert QdrantSettings().qdrant_url == "http://localhost:6333"

    def test_env_file(self, clean_env):
        # Il bug originale: QDRANT_URL definito SOLO nel .env (shell pulita).
        (clean_env / ".env").write_text(
            "QDRANT_URL=http://localhost:6333\n", encoding="utf-8"
        )
        assert QdrantSettings().qdrant_url == "http://localhost:6333"

    def test_env_var_vince_su_env_file(self, clean_env, monkeypatch):
        (clean_env / ".env").write_text(
            "QDRANT_URL=http://dal-file:6333\n", encoding="utf-8"
        )
        monkeypatch.setenv("QDRANT_URL", "http://dalla-shell:6333")
        assert QdrantSettings().qdrant_url == "http://dalla-shell:6333"


# ---------------------------------------------------------------------------
# _init_qdrant: modalità e warning collection vuota
# ---------------------------------------------------------------------------

class TestInitQdrant:
    def test_server_mode_da_env_file(self, clean_env):
        (clean_env / ".env").write_text(
            "QDRANT_URL=http://localhost:6333\n", encoding="utf-8"
        )
        with patch(
            "qdrant_client.QdrantClient", return_value=_mock_client(count=5)
        ) as MockQC:
            r = VectorRetriever(str(clean_env / "ws"))
        MockQC.assert_called_once_with(url="http://localhost:6333", timeout=30)
        assert r._mode == "server"

    def test_embedded_senza_url(self, clean_env):
        with patch(
            "qdrant_client.QdrantClient", return_value=_mock_client(count=5)
        ) as MockQC:
            r = VectorRetriever(str(clean_env / "ws"))
        assert r._mode == "embedded"
        assert MockQC.call_args.kwargs.get("path") == r._qdrant_path

    def test_warning_collection_vuota(self, clean_env):
        with patch(
            "qdrant_client.QdrantClient", return_value=_mock_client(count=0)
        ), patch(
            "aiura_legal.core.retrieval.vector_retriever.logger"
        ) as mock_log:
            VectorRetriever(str(clean_env / "ws"))
        assert mock_log.warning.called
        msg = mock_log.warning.call_args.args[0]
        assert "VUOTA" in msg
        assert "QDRANT_URL" in msg

    def test_warning_collection_appena_creata(self, clean_env):
        with patch(
            "qdrant_client.QdrantClient",
            return_value=_mock_client(has_collection=False),
        ), patch(
            "aiura_legal.core.retrieval.vector_retriever.logger"
        ) as mock_log:
            VectorRetriever(str(clean_env / "ws"))
        assert mock_log.warning.called

    def test_nessun_warning_con_punti(self, clean_env):
        with patch(
            "qdrant_client.QdrantClient", return_value=_mock_client(count=1234)
        ), patch(
            "aiura_legal.core.retrieval.vector_retriever.logger"
        ) as mock_log:
            VectorRetriever(str(clean_env / "ws"))
        assert not mock_log.warning.called
