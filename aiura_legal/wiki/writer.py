"""
WikiWriter — genera e aggiorna pagine wiki via Ollama.
Due operazioni: estrai concetti da una risposta, fondi nuove conoscenze in una pagina.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx
from loguru import logger

if TYPE_CHECKING:
    from aiura_legal.wiki.store import WikiPage

_OLLAMA_URL = "http://localhost:11434/api/generate"
_MODEL = "qwen2.5:7b"
_TIMEOUT = 120.0

_EXTRACT_PROMPT = """\
Sei un giurista italiano. Leggi la seguente risposta legale e identifica i concetti \
giuridici principali trattati (istituti, principi, materie, fattispecie).

Risposta:
{response_text}

Domanda originale: {query}

Elenca i concetti giuridici principali. Scrivi solo i nomi, uno per riga, \
senza numerazione né spiegazioni. Massimo 5 concetti.
"""

_MERGE_PROMPT = """\
Sei un redattore giuridico italiano. Aggiorna la seguente pagina wiki con le \
nuove informazioni fornite.

Regole:
- Mantieni le sezioni esistenti (## Sintesi, ## Principi chiave, \
## Evoluzione normativa, ## Casi applicativi, ## Fonti)
- Integra le nuove informazioni nelle sezioni appropriate
- NON inventare fonti o articoli di legge non menzionati
- La sezione ## Fonti deve contenere solo gli URN forniti
- Rispondi SOLO con il markdown aggiornato, senza commenti

Pagina wiki attuale:
{current_body}

Nuove informazioni:
{new_evidence}

URN da includere in ## Fonti (sostituisci quelli esistenti con l'unione):
{urns}
"""

_EMPTY_PAGE_TEMPLATE = """\
## Sintesi
Concetto giuridico in fase di documentazione.

## Principi chiave
- Da definire

## Evoluzione normativa
- Da definire

## Casi applicativi
- Da definire

## Fonti
"""


class WikiWriter:
    def __init__(
        self,
        ollama_url: str = _OLLAMA_URL,
        model: str = _MODEL,
        timeout: float = _TIMEOUT,
    ) -> None:
        self._url = ollama_url
        self._model = model
        self._timeout = timeout

    async def extract_concepts(self, query: str, response_text: str) -> list[str]:
        prompt = _EXTRACT_PROMPT.format(query=query, response_text=response_text[:3000])
        raw = await self._generate(prompt)
        concepts = [
            line.strip()
            for line in raw.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        logger.debug(f"WikiWriter extracted {len(concepts)} concepts")
        return concepts[:5]

    async def merge_knowledge(
        self, page: "WikiPage", new_evidence: str, urns: list[str]
    ) -> str:
        current = page.body_md if page.body_md.strip() else _EMPTY_PAGE_TEMPLATE
        urn_list = "\n".join(f"- {u}" for u in urns) if urns else "- nessuno"
        prompt = _MERGE_PROMPT.format(
            current_body=current,
            new_evidence=new_evidence[:2000],
            urns=urn_list,
        )
        merged = await self._generate(prompt)
        if "## Fonti" not in merged:
            merged += f"\n\n## Fonti\n{urn_list}\n"
        return merged.strip()

    async def _generate(self, prompt: str) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 1024},
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(self._url, json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "").strip()


def slugify(text: str) -> str:
    """Genera slug ASCII da testo italiano senza dipendenze esterne."""
    replacements = {
        "à": "a", "á": "a", "è": "e", "é": "e", "ì": "i",
        "í": "i", "ò": "o", "ó": "o", "ù": "u", "ú": "u",
    }
    result = text.lower()
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    result = re.sub(r"[^a-z0-9\s-]", "", result)
    result = re.sub(r"[\s-]+", "_", result.strip())
    return result[:80]
