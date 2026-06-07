"""Test WikiStore — CRUD, upsert, indici, isolamento workspace."""
import pytest
from datetime import datetime, timezone, timedelta

import mongomock_motor

from aiura_legal.wiki.store import WikiPage, WikiStore


@pytest.fixture
def db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_test"]


@pytest.fixture
def store(db):
    return WikiStore(db)


def _make_page(slug="licenziamento", workspace="test-ws") -> WikiPage:
    return WikiPage(
        slug=slug,
        title="Licenziamento per giusta causa",
        body_md="## Sintesi\nContenuto.\n\n## Fonti\n- urn:test:art1\n",
        sources=["urn:test:art1"],
        query_count=1,
        workspace=workspace,
    )


@pytest.mark.asyncio
async def test_save_and_get(store):
    page = _make_page()
    await store.save_page(page)
    retrieved = await store.get_page("licenziamento", "test-ws")
    assert retrieved is not None
    assert retrieved.slug == "licenziamento"
    assert retrieved.title == "Licenziamento per giusta causa"


@pytest.mark.asyncio
async def test_get_nonexistent_returns_none(store):
    result = await store.get_page("non_esiste", "test-ws")
    assert result is None


@pytest.mark.asyncio
async def test_upsert_updates_existing(store):
    page = _make_page()
    await store.save_page(page)
    page.version = 2
    page.query_count = 5
    await store.save_page(page)
    retrieved = await store.get_page("licenziamento", "test-ws")
    assert retrieved.version == 2
    assert retrieved.query_count == 5


@pytest.mark.asyncio
async def test_workspace_isolation(store):
    page_a = _make_page(workspace="studio-a")
    page_b = _make_page(workspace="studio-b")
    await store.save_page(page_a)
    await store.save_page(page_b)

    result_a = await store.get_page("licenziamento", "studio-a")
    result_b = await store.get_page("licenziamento", "studio-b")
    missing = await store.get_page("licenziamento", "studio-c")

    assert result_a is not None
    assert result_b is not None
    assert missing is None


@pytest.mark.asyncio
async def test_list_stale(store):
    old_page = _make_page(slug="vecchia")
    old_page.last_updated = datetime.now(timezone.utc) - timedelta(days=40)
    recent_page = _make_page(slug="recente")
    recent_page.last_updated = datetime.now(timezone.utc) - timedelta(days=5)

    await store.save_page(old_page)
    await store.save_page(recent_page)

    stale = await store.list_stale(30, "test-ws")
    slugs = [p.slug for p in stale]
    assert "vecchia" in slugs
    assert "recente" not in slugs


@pytest.mark.asyncio
async def test_search_by_urn(store):
    page = _make_page()
    page.sources = ["urn:nir:art2119", "urn:nir:art18"]
    await store.save_page(page)

    results = await store.search_by_urn("urn:nir:art2119", "test-ws")
    assert len(results) == 1
    assert results[0].slug == "licenziamento"

    no_results = await store.search_by_urn("urn:nir:art999", "test-ws")
    assert len(no_results) == 0


@pytest.mark.asyncio
async def test_list_all(store):
    await store.save_page(_make_page(slug="pagina_uno"))
    await store.save_page(_make_page(slug="pagina_due"))
    await store.save_page(_make_page(slug="altra_ws", workspace="altro"))

    pages = await store.list_all("test-ws")
    slugs = {p.slug for p in pages}
    assert "pagina_uno" in slugs
    assert "pagina_due" in slugs
    assert "altra_ws" not in slugs
