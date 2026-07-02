"""
Test NormattivaWebFetcher — parsing dei parametri sidebar e fallback N2Ls.

Copre la regressione: gli onclick "caricaArticolo?..." nell'HTML reale
usano l'entità HTML "&amp;" al posto di "&" tra i parametri della query
string. Senza html.unescape() prima dello split, tutti i parametri dopo
il primo vengono corrotti (es. "art.idSottoArticolo" diventa
"amp;art.idSottoArticolo"), producendo suffissi ~artN errati e facendo
sì che il fallback N2Ls scarichi sempre la stessa pagina (Art. 1).

Zero rete reale: httpx.Client viene sostituito con un doppio che serve
pagine HTML sintetiche.
"""
from __future__ import annotations

import pytest

from aiura_legal.ingestion.normattiva.connector import (
    NormattivaWebFetcher,
    _art_suffix_from_params,
)


# ---------------------------------------------------------------------------
# _extract_sidebar_params / _art_suffix_from_params
# ---------------------------------------------------------------------------

def _sidebar_html(entries: list[tuple[str, str]]) -> str:
    """entries: lista di (idArticolo, idSottoArticolo)."""
    links = "\n".join(
        f'<a onclick="caricaArticolo?art.idArticolo={art_id}&amp;'
        f'art.idSottoArticolo={sotto}&amp;art.idGruppo=1">Art. {art_id}</a>'
        for art_id, sotto in entries
    )
    return f"<html><body><div id='sidebar'>{links}</div></body></html>"


def test_extract_sidebar_params_handles_html_entity_ampersand():
    fetcher = NormattivaWebFetcher()
    html_ = _sidebar_html([("1", "1"), ("2", "1"), ("3", "2")])

    chain = fetcher._extract_sidebar_params(html_)

    assert len(chain) == 3
    assert chain[0]["art.idArticolo"] == "1"
    assert chain[0]["art.idSottoArticolo"] == "1"
    assert chain[1]["art.idArticolo"] == "2"
    # Prima della fix, questa chiave sarebbe stata "amp;art.idSottoArticolo"
    # e la lookup sotto sarebbe sempre stata "1" (default).
    assert chain[2]["art.idArticolo"] == "3"
    assert chain[2]["art.idSottoArticolo"] == "2"


def test_art_suffix_from_params_uses_correct_sotto_articolo():
    params = {"art.idArticolo": "7", "art.idSottoArticolo": "2"}
    assert _art_suffix_from_params(params) == "art7bis"


# ---------------------------------------------------------------------------
# stream_articles_n2ls — validazione difensiva
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class _FakeClient:
    """Simula il server: risponde sempre con la pagina dell'Art. 1,
    indipendentemente dal suffisso richiesto (riproduce il fallback
    silenzioso del sito quando i parametri sono malformati)."""

    def __init__(self, always_art1: bool = True, real_pages: dict | None = None):
        self._always_art1 = always_art1
        self._real_pages = real_pages or {}

    def get(self, url, headers=None, follow_redirects=True):
        if self._always_art1:
            return _FakeResponse(200, _article_page_html("1"))
        for suffix, num in self._real_pages.items():
            if url.endswith(suffix):
                return _FakeResponse(200, _article_page_html(num))
        return _FakeResponse(200, _article_page_html("1"))


def _article_page_html(num: str) -> str:
    return (
        "<html><body><div id='corpo' class='bodyTesto'>"
        f"<span class='article-num-akn'>Art. {num}</span>"
        f"<div class='art-just-text-akn'>Testo dell'articolo {num}.</div>"
        "</div></body></html>"
    )


def test_stream_articles_n2ls_warns_on_silent_server_fallback(capsys, monkeypatch):
    fetcher = NormattivaWebFetcher()
    fetcher._client = _FakeClient(always_art1=True)
    monkeypatch.setattr(fetcher, "_ensure_session", lambda referer: None)

    sidebar_params = [
        {"art.idArticolo": "1", "art.idSottoArticolo": "1"},
        {"art.idArticolo": "2", "art.idSottoArticolo": "1"},
        {"art.idArticolo": "3", "art.idSottoArticolo": "1"},
    ]

    results = list(
        fetcher.stream_articles_n2ls(
            act_urn="urn:nir:stato:regio.decreto:1942-03-16;262",
            sidebar_params=sidebar_params,
        )
    )

    assert len(results) == 3
    # Il bug (server sempre su Art. 1) produce comunque articolo_num="Art. 1"
    # per ogni entry: la validazione difensiva deve segnalarlo in log.
    out = capsys.readouterr().out
    assert "non corrisponde all'idArticolo atteso" in out


def test_stream_articles_n2ls_no_warning_when_articles_match(capsys, monkeypatch):
    fetcher = NormattivaWebFetcher()
    fetcher._client = _FakeClient(
        always_art1=False,
        real_pages={"~art1": "1", "~art2": "2", "~art3": "3"},
    )
    monkeypatch.setattr(fetcher, "_ensure_session", lambda referer: None)

    sidebar_params = [
        {"art.idArticolo": "1", "art.idSottoArticolo": "1"},
        {"art.idArticolo": "2", "art.idSottoArticolo": "1"},
        {"art.idArticolo": "3", "art.idSottoArticolo": "1"},
    ]

    results = list(
        fetcher.stream_articles_n2ls(
            act_urn="urn:nir:stato:regio.decreto:1942-03-16;262",
            sidebar_params=sidebar_params,
        )
    )

    assert [r[1]["articolo_num"] for r in results] == ["Art. 1", "Art. 2", "Art. 3"]
    out = capsys.readouterr().out
    assert "non corrisponde" not in out
    assert "possibile dato corrotto" not in out
