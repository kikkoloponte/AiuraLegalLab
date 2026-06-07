"""
Scraper Cassazione — API Solr diretta.
Endpoint: POST italgiure.giustizia.it/sncass/isapi/hc.dll/sn.solr/sn-collection/select?app.query
Restituisce JSON con testo OCR completo — nessun Playwright necessario.
"""
from __future__ import annotations

import asyncio
import re
from datetime import date

import httpx
from loguru import logger

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza
from aiura_legal.jurisprudence.scrapers.base import BaseScraper

_SOLR_URL = (
    "https://www.italgiure.giustizia.it"
    "/sncass/isapi/hc.dll/sn.solr/sn-collection/select"
)
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.italgiure.giustizia.it/sncass/",
    "Origin": "https://www.italgiure.giustizia.it",
}
_PAGE_SIZE = 20
_MAX_RESULTS = 5000          # limite per sync settimanale
_MAX_RESULTS_INITIAL = 100_000  # limite per caricamento storico
_RATE_LIMIT_INITIAL = 0.1    # secondi tra pagine per caricamento storico (Solr regge)


class CassazioneScraper(BaseScraper):
    organo = OrganoGiudicante.CASSAZIONE
    rate_limit_seconds = 1.5

    # Override: Cassazione usa httpx direttamente, non Playwright
    async def __aenter__(self) -> "CassazioneScraper":
        self._http = httpx.AsyncClient(
            verify=False, headers=_HEADERS, timeout=httpx.Timeout(30.0)
        )
        return self  # type: ignore[return-value]

    async def __aexit__(self, *_: object) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    async def fetch_since(
        self, since: date,
        until: date | None = None,
        max_results: int = _MAX_RESULTS,
        rate_limit: float | None = None,
    ) -> list[RawSentenza]:
        """
        Scarica sentenze nel range [since, until].

        Args:
            since:       data di inizio (inclusa)
            until:       data di fine (inclusa). Se None → oggi (finestra aperta).
                         Usare finestre chiuse mensili per evitare il problema
                         di deep pagination del Solr di italgiure.
            max_results: cap sul numero di risultati
            rate_limit:  secondi tra pagine (override di rate_limit_seconds)
        """
        results: list[RawSentenza] = []
        date_from = since.strftime("%Y%m%d")
        date_to   = until.strftime("%Y%m%d") if until else "*"
        fq_filter = f"datdec:[{date_from} TO {date_to}]"
        start = 0
        effective_rate = rate_limit if rate_limit is not None else self.rate_limit_seconds

        while start < max_results:
            await asyncio.sleep(effective_rate)
            try:
                resp = await self._http.post(
                    _SOLR_URL,
                    params={"app.query": ""},
                    data={
                        "q": '(kind:"snciv" OR kind:"snpen")',
                        "fq": fq_filter,
                        "rows": _PAGE_SIZE,
                        "start": start,
                        "wt": "json",
                        "sort": "datdec asc",   # asc: stabile e prevedibile per windowing
                        "fl": "sicId,numdec,szdec,datdec,datdep,kind,materia,ocr,ocrdis,pd",
                    },
                )
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("CassazioneSolr: HTTP error — {}", exc)
                break

            data = resp.json()
            docs = data.get("response", {}).get("docs", [])
            num_found = data.get("response", {}).get("numFound", 0)

            if not docs:
                break

            for doc in docs:
                raw = self._doc_to_raw(doc)
                if raw:
                    results.append(raw)

            start += _PAGE_SIZE
            if start >= min(num_found, max_results):
                break

            logger.debug(
                "Cassazione Solr: {}/{} scaricati (since {})",
                min(start, num_found), num_found, since,
            )

        logger.info(
            "Cassazione: {} sentenze (since {} until {})",
            len(results), since, until or "oggi",
        )
        return results

    def _doc_to_raw(self, doc: dict) -> RawSentenza | None:
        try:
            sic_list = doc.get("sicId", [])
            sic_id = (sic_list[0] if sic_list else "") if isinstance(sic_list, list) else str(sic_list)
            numdec = doc.get("numdec", "").lstrip("0") or "0"
            datdec = doc.get("datdec", "")
            pd_str = doc.get("pd", "")

            anno = int(datdec[:4]) if datdec and len(datdec) >= 4 else date.today().year
            dep_date: date | None = None
            if pd_str and len(pd_str) == 8:
                try:
                    dep_date = date(int(pd_str[:4]), int(pd_str[4:6]), int(pd_str[6:8]))
                except ValueError:
                    pass

            # Testo OCR: concatena ocr (motivazione) + ocrdis (dispositivo)
            ocr_parts = doc.get("ocr", [])
            ocrdis_parts = doc.get("ocrdis", [])
            ocr = " ".join(ocr_parts) if isinstance(ocr_parts, list) else str(ocr_parts)
            ocrdis = " ".join(ocrdis_parts) if isinstance(ocrdis_parts, list) else str(ocrdis_parts)
            full_text = f"FATTO E DIRITTO\n{ocr}\n\nP.Q.M.\n{ocrdis}"

            materia = ""
            mat_list = doc.get("materia", [])
            if mat_list:
                materia = mat_list[0] if isinstance(mat_list, list) else str(mat_list)

            html = (
                f"<div class='cassazione-sentenza'>"
                f"<h1>Cass. n. {numdec}/{anno}</h1>"
                f"<p>Materia: {materia}</p>"
                f"<p>Sezione: {doc.get('szdec', '')}</p>"
                f"{full_text}"
                f"</div>"
            )

            return RawSentenza(
                numero=numdec,
                anno=anno,
                organo=self.organo,
                source_url=f"https://www.italgiure.giustizia.it/sncass/#{sic_id}",
                raw_html=html,
                data_deposito=dep_date,
            )
        except Exception as exc:
            logger.debug("CassazioneSolr: doc parsing fallito — {}", exc)
            return None
