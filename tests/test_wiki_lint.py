"""Test WikiLinter — stale, body vuoto, URN orfano → LintReport corretto."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import mongomock_motor

from aiura_legal.wiki.lint import WikiLinter, LintReport
from aiura_legal.wiki.store import WikiPage, WikiStore


@pytest.fixture
def db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_test"]


@pytest.fixture
def store(db):
    return WikiStore(db)


@pytest.fixture
def source_db():
    """DB sorgente mock per normattiva_docs."""
    client = mongomock_motor.AsyncMongoMockClient()
    return client["legal_lab_test"]


@pytest.fixture
def linter(store, source_db):
    return WikiLinter(store, source_db)


async def _seed_page(store, slug, body_md="## Sintesi\nContenuto.\n\n## Fonti\n",
                     sources=None, days_old=0, workspace="test-ws"):
    page = WikiPage(
        slug=slug,
        title=slug.replace("_", " ").title(),
        body_md=body_md,
        sources=sources or [],
        last_updated=datetime.now(timezone.utc) - timedelta(days=days_old),
        workspace=workspace,
    )
    await store.save_page(page)


@pytest.mark.asyncio
async def test_lint_stale_pages(linter, store, source_db):
    await _seed_page(store, "vecchia", days_old=40)
    await _seed_page(store, "recente", days_old=5)

    report = await linter.run("test-ws")
    assert "vecchia" in report.stale_pages
    assert "recente" not in report.stale_pages


@pytest.mark.asyncio
async def test_lint_empty_body(linter, store, source_db):
    await _seed_page(store, "vuota", body_md="  ")
    await _seed_page(store, "piena", body_md="## Sintesi\nContenuto lungo abbastanza per superare la soglia minima.\n\n## Fonti\n")

    report = await linter.run("test-ws")
    assert "vuota" in report.empty_bodies
    assert "piena" not in report.empty_bodies


@pytest.mark.asyncio
async def test_lint_orphan_urns(linter, store, source_db):
    # inserisce un URN valido in normattiva_docs
    await source_db["normattiva_docs"].insert_one({"urn": "urn:nir:valido"})

    await _seed_page(store, "con_urn_valido", sources=["urn:nir:valido"])
    await _seed_page(store, "con_urn_orfano", sources=["urn:nir:inesistente"])

    report = await linter.run("test-ws")
    orphan_slugs = [slug for slug, _ in report.orphan_urns]
    assert "con_urn_orfano" in orphan_slugs
    assert "con_urn_valido" not in orphan_slugs


@pytest.mark.asyncio
async def test_lint_total_pages_count(linter, store, source_db):
    await _seed_page(store, "pagina_1")
    await _seed_page(store, "pagina_2")
    await _seed_page(store, "pagina_altro_ws", workspace="altro")

    report = await linter.run("test-ws")
    assert report.total_pages == 2


@pytest.mark.asyncio
async def test_lint_summary_format(linter, store, source_db):
    report = LintReport(
        stale_pages=["p1"],
        empty_bodies=["p2", "p3"],
        orphan_urns=[("p4", "urn:x")],
        total_pages=10,
    )
    summary = report.summary()
    assert "10" in summary
    assert "1" in summary
    assert "2" in summary
