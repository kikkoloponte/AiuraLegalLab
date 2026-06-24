"""
Registro degli istituti giuridici — vocabolario curato + lookup.

Scopo (vedi core/istituti/__init__.py):
  1. Tagging deterministico dei chunk normattiva per istituto (via URN articolo).
  2. Registro delle sentenze pilota per istituto (groundabili).
  3. Classificazione delle domande per istituto da un vocabolario CHIUSO, così il
     modello è costretto a scegliere (es. sequestro penale ex art. 321 c.p.p. vs
     confisca antimafia ex art. 25 d.lgs. 159/2011, che condividono il lessico
     "terzo in buona fede" e oggi confondono il retrieval).

Il seed è in registry.yaml (curato a mano, espandibile). Questo modulo lo carica
e offre lookup: per id, per URN normativo, per match lessicale, e il vocabolario
chiuso per il classificatore di Fase 1.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger

_REGISTRY_PATH = Path(__file__).resolve().parent / "registry.yaml"

_WORD_RE = re.compile(r"[a-zàèéìòóùA-Z0-9]+")


@dataclass(frozen=True)
class SentenzaPilota:
    """Sentenza pilota di un istituto. `source_id` è il chunk REALE (groundabile)
    che ne riporta il principio — può essere il massimario o la sentenza stessa.
    Vuoto finché non confermato dalla scoperta data-driven (vedi
    scripts/discover_pilot_sentences.py)."""
    organo: str               # "Cass. SS.UU." | "Corte Cost." | ...
    numero: str
    anno: str
    nome: str = ""            # "Gubert", "ThyssenKrupp"
    principio: str = ""       # holding conciso
    source_id: str = ""       # chunk groundabile (massimario/giurisprudenza)

    @property
    def riferimento(self) -> str:
        base = f"{self.organo} n. {self.numero}/{self.anno}".strip()
        return f"{base} ({self.nome})" if self.nome else base


@dataclass(frozen=True)
class Istituto:
    id: str                                   # slug stabile
    label: str
    settore: str                              # penale|civile|amministrativo|lavoro|tributario
    norme_urn: tuple[str, ...] = ()           # URN reali in corpus → tagging deterministico
    norme_riferimento: tuple[str, ...] = ()   # etichette leggibili (anche norme non ancora in KB)
    termini_chiave: tuple[str, ...] = ()      # per match lessicale / scoperta piloti
    disambigua_da: dict[str, tuple[str, ...]] = field(default_factory=dict)  # altro_id → termini distintivi
    sentenze_pilota: tuple[SentenzaPilota, ...] = ()


class IstitutoRegistry:
    """Registro in memoria con indici per id e per URN normativo."""

    def __init__(self, istituti: list[Istituto]) -> None:
        self._istituti: list[Istituto] = istituti
        self._by_id: dict[str, Istituto] = {i.id: i for i in istituti}
        # Un URN può mappare a UN solo istituto (la disambiguazione fine è
        # responsabilità del curatore: se due istituti condividono una norma,
        # va modellato esplicitamente, non lasciato implicito).
        self._by_urn: dict[str, Istituto] = {}
        for ist in istituti:
            for urn in ist.norme_urn:
                if urn in self._by_urn and self._by_urn[urn].id != ist.id:
                    logger.warning(
                        f"[IstitutoRegistry] URN {urn!r} mappato sia a "
                        f"{self._by_urn[urn].id!r} sia a {ist.id!r} — tengo il primo"
                    )
                    continue
                self._by_urn[urn] = ist

    # -- accesso base ---------------------------------------------------
    def all(self) -> list[Istituto]:
        return list(self._istituti)

    def by_id(self, istituto_id: str) -> Optional[Istituto]:
        return self._by_id.get(istituto_id)

    def by_urn(self, source_id: str) -> Optional[Istituto]:
        """Istituto di un chunk normattiva dal suo source_id (URN). None se non mappato."""
        return self._by_urn.get(source_id)

    def vocabolario(self) -> list[tuple[str, str]]:
        """(id, label) per il prompt del classificatore di Fase 1 (vocabolario CHIUSO)."""
        return [(i.id, i.label) for i in self._istituti]

    def piloti(self, istituto_id: str) -> tuple[SentenzaPilota, ...]:
        ist = self._by_id.get(istituto_id)
        return ist.sentenze_pilota if ist else ()

    # -- match lessicale ------------------------------------------------
    def match_query(self, text: str, top_k: int = 3) -> list[tuple[Istituto, float]]:
        """
        Classificazione lessicale di fallback: punteggio = quota di termini_chiave
        dell'istituto presenti nel testo, meno una penalità per i termini di
        `disambigua_da` di altri istituti (separa istituti con lessico simile).
        Deterministico — non sostituisce il classificatore LLM, lo affianca.
        """
        tokens = {t.lower() for t in _WORD_RE.findall(text)}
        low = text.lower()
        scored: list[tuple[Istituto, float]] = []
        for ist in self._istituti:
            if not ist.termini_chiave:
                continue
            hits = sum(1 for term in ist.termini_chiave if term.lower() in low)
            if hits == 0:
                continue
            score = hits / len(ist.termini_chiave)
            # Bonus se compaiono termini che lo distinguono da un istituto confondibile
            for _other_id, distintivi in ist.disambigua_da.items():
                if any(d.lower() in low for d in distintivi):
                    score += 0.25
            scored.append((ist, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def _parse_istituto(raw: dict) -> Istituto:
    piloti = tuple(
        SentenzaPilota(
            organo=str(p.get("organo", "")).strip(),
            numero=str(p.get("numero", "")).strip(),
            anno=str(p.get("anno", "")).strip(),
            nome=str(p.get("nome", "")).strip(),
            principio=str(p.get("principio", "")).strip(),
            source_id=str(p.get("source_id", "")).strip(),
        )
        for p in (raw.get("sentenze_pilota") or [])
    )
    disambigua = {
        str(k): tuple(str(v) for v in (vals or []))
        for k, vals in (raw.get("disambigua_da") or {}).items()
    }
    return Istituto(
        id=str(raw["id"]).strip(),
        label=str(raw.get("label", raw["id"])).strip(),
        settore=str(raw.get("settore", "")).strip().lower(),
        norme_urn=tuple(str(u).strip() for u in (raw.get("norme_urn") or [])),
        norme_riferimento=tuple(str(n).strip() for n in (raw.get("norme_riferimento") or [])),
        termini_chiave=tuple(str(t).strip() for t in (raw.get("termini_chiave") or [])),
        disambigua_da=disambigua,
        sentenze_pilota=piloti,
    )


def load_registry(path: Path | str = _REGISTRY_PATH) -> IstitutoRegistry:
    p = Path(path)
    if not p.exists():
        logger.warning(f"[IstitutoRegistry] seed non trovato: {p} — registro vuoto")
        return IstitutoRegistry([])
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    raw_list = data.get("istituti", [])
    istituti = [_parse_istituto(r) for r in raw_list]
    logger.info(f"[IstitutoRegistry] {len(istituti)} istituti caricati da {p.name}")
    return IstitutoRegistry(istituti)


# Singleton lazy — caricato al primo uso, condiviso nel processo.
_singleton: Optional[IstitutoRegistry] = None


def get_registry() -> IstitutoRegistry:
    global _singleton
    if _singleton is None:
        _singleton = load_registry()
    return _singleton
