"""Settori giuridici — regole keyword condivise tra classificazione KB (offline,
scripts/classify_knowledge_base.py) e classificazione query (online, hybrid_retriever.py).

Le regole sono intenzionalmente le stesse nei due lati: un atto classificato come
"tributario" da queste keyword deve poter essere richiamato da una query che usa
le stesse keyword.
"""
from __future__ import annotations

SETTORI_VALIDI = [
    "penale", "civile", "amministrativo", "lavoro",
    "tributario", "processuale", "costituzionale", "altro",
]

# Keyword → settori → confidence. Ordine: più specifico prima.
# Usato per classificazione atti/dottrina (titolo, primo match vince) e per
# classificazione query (scan completo, multi-label — vedi classify_query).
KEYWORD_RULES: list[tuple[list[str], list[str], float]] = [
    (["codice penale", "procedura penale", "processo penale", "codice di procedura penale"], ["penale", "processuale"], 0.95),
    (["penale", "reato", "delitto", "contravvenzione", "pena detentiva", "reclusione"], ["penale"], 0.90),
    (["codice civile", "procedura civile", "codice di procedura civile"], ["civile", "processuale"], 0.95),
    (["diritto civile", "obbligazioni", "contratti", "proprietà", "successioni", "famiglia"], ["civile"], 0.85),
    (["imposta sul reddito", "irpef", "ires", "iva", "accise", "tribut", "fiscale", "fisco", "catasto", "imposte", "tasse", "agevolazioni fiscali"], ["tributario"], 0.90),
    (["lavoro", "lavoratori", "lavoratore", "occupazione", "contratto di lavoro", "licenziamento", "sindacato", "sciopero", "inps", "inail", "previdenza", "pensione", "cassa integrazione"], ["lavoro"], 0.90),
    (["appalto pubblico", "contratti pubblici", "codice degli appalti", "pubblica amministrazione", "tar", "consiglio di stato", "procedimento amministrativo", "urbanistica", "edilizia", "esproprio", "demanio"], ["amministrativo"], 0.88),
    (["costituzione", "costituzionale", "corte costituzionale", "diritti fondamentali", "parlamento", "governo", "referendum"], ["costituzionale"], 0.90),
    (["processo", "procedura", "giurisdizione", "competenza", "appello", "cassazione", "tribunale"], ["processuale"], 0.75),
    (["ambiente", "rifiuti", "inquinamento", "paesaggio", "tutela ambientale"], ["amministrativo"], 0.82),
    (["sicurezza sul lavoro", "infortuni sul lavoro", "d.lgs. 81", "dlgs 81"], ["lavoro"], 0.95),
    (["immigrazione", "stranieri", "asilo", "cittadinanza"], ["amministrativo"], 0.85),
    (["codice del consumo", "consumatori", "tutela del consumatore"], ["civile"], 0.85),
    (["privacy", "protezione dei dati", "gdpr", "trattamento dati"], ["amministrativo", "civile"], 0.80),
    (["antimafia", "criminalità organizzata", "camorra", "mafia", "ndrangheta"], ["penale"], 0.92),
    (["bancario", "credito", "banca", "testo unico bancario", "intermediazione finanziaria", "borsa", "finanza"], ["civile", "tributario"], 0.80),
]


def classify_keywords(titolo: str, snippet: str = "") -> tuple[list[str], float] | None:
    """Classificazione act-level: primo match vince. Titolo ha priorità sullo snippet."""
    titolo_lower = titolo.lower()
    snippet_lower = snippet.lower()[:500]
    for keywords, settori, confidence in KEYWORD_RULES:
        if any(kw in titolo_lower for kw in keywords):
            return settori, confidence
        if snippet_lower and any(kw in snippet_lower for kw in keywords):
            return settori, max(0.5, confidence - 0.1)
    return None


def classify_query(query: str) -> list[tuple[str, float]]:
    """Classificazione query-level: multi-label, zero LLM, latenza trascurabile.

    A differenza di classify_keywords (act-level, primo match vince), qui
    scansioniamo tutte le regole: una query può toccare più settori
    ("licenziamento e tassazione" → lavoro + tributario), e il risultato è
    un bonus soft nel reranking, non un filtro — non c'è motivo di troncare
    al primo match.

    Ritorna lista di (settore, confidence) ordinata per confidence decrescente,
    confidence massima per settore se più regole lo colpiscono.
    """
    query_lower = query.lower()
    best: dict[str, float] = {}
    for keywords, settori, confidence in KEYWORD_RULES:
        if any(kw in query_lower for kw in keywords):
            for s in settori:
                if confidence > best.get(s, 0.0):
                    best[s] = confidence
    return sorted(best.items(), key=lambda x: x[1], reverse=True)
