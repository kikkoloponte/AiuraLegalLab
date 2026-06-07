"""Test WikiWriter — mock Ollama httpx, prompt italiani, merge preserva ## Fonti."""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from aiura_legal.wiki.store import WikiPage
from aiura_legal.wiki.writer import WikiWriter, slugify


def _mock_ollama_response(text: str):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"response": text}
    return mock_resp


@pytest.fixture
def writer():
    return WikiWriter(ollama_url="http://localhost:11434/api/generate")


@pytest.mark.asyncio
async def test_extract_concepts_returns_list(writer):
    ollama_output = "licenziamento per giusta causa\nart. 2119 cc\ngiustificato motivo"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_ollama_response(ollama_output))
        mock_client_cls.return_value = mock_client

        concepts = await writer.extract_concepts(
            query="Quando si può licenziare un dipendente?",
            response_text="Il licenziamento per giusta causa è disciplinato dall'art. 2119 cc.",
        )

    assert isinstance(concepts, list)
    assert len(concepts) <= 5
    assert "licenziamento per giusta causa" in concepts


@pytest.mark.asyncio
async def test_extract_concepts_prompt_italiano(writer):
    captured_payload = {}

    async def fake_post(url, json=None, **kwargs):
        captured_payload.update(json or {})
        return _mock_ollama_response("concetto uno\nconcetto due")

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = fake_post
        mock_client_cls.return_value = mock_client

        await writer.extract_concepts("query", "risposta legale")

    prompt = captured_payload.get("prompt", "")
    assert "giurista italiano" in prompt.lower() or "giuridici" in prompt.lower()
    assert "qwen2.5:7b" == captured_payload.get("model")


@pytest.mark.asyncio
async def test_merge_preserves_fonti_section(writer):
    page = WikiPage(
        slug="test",
        title="Test",
        body_md="## Sintesi\nContenuto esistente.\n\n## Fonti\n- urn:test:old\n",
        sources=["urn:test:old"],
        workspace="test",
    )
    merged_output = (
        "## Sintesi\nContenuto aggiornato.\n\n"
        "## Principi chiave\n- Principio\n\n"
        "## Evoluzione normativa\n- Nessuna\n\n"
        "## Casi applicativi\n- Caso\n\n"
        "## Fonti\n- urn:test:new\n"
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_ollama_response(merged_output))
        mock_client_cls.return_value = mock_client

        result = await writer.merge_knowledge(page, "Nuova info.", ["urn:test:new"])

    assert "## Fonti" in result


@pytest.mark.asyncio
async def test_merge_adds_fonti_if_missing(writer):
    """Se Ollama dimentica ## Fonti, il writer la ri-aggiunge."""
    page = WikiPage(slug="t", title="T", body_md="", sources=[], workspace="test")

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(
            return_value=_mock_ollama_response("## Sintesi\nTesto senza fonti.")
        )
        mock_client_cls.return_value = mock_client

        result = await writer.merge_knowledge(page, "evidence", ["urn:nir:art1"])

    assert "## Fonti" in result
    assert "urn:nir:art1" in result


@pytest.mark.parametrize("text,expected", [
    ("Licenziamento per giusta causa", "licenziamento_per_giusta_causa"),
    ("Art. 2119 c.c.", "art_2119_cc"),
    ("Responsabilità extracontrattuale", "responsabilita_extracontrattuale"),
    ("  spazi  extra  ", "spazi_extra"),
    ("", ""),
])
def test_slugify(text, expected):
    assert slugify(text) == expected
