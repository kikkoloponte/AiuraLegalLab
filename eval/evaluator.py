"""
AiUra LegalLab — Eval core.

Metriche:
  - groundedness:  % source_id con pattern URN/interno riconoscibile
  - recall@k:      |retrieved ∩ expected| / |expected| con match tollerante ~art
  - latency_ms:    round-trip HTTP verso POST /query
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx
from loguru import logger


# ---------------------------------------------------------------------------
# Intent mapping  (valori JSONL → valori accettati dall'API)
# ---------------------------------------------------------------------------

#: Mappa i valori shorthand usati nei file JSONL ai valori del QueryIntent dell'API.
#: "retrieval"  → norma_lookup          (ricerca norma specifica)
#: "reasoning"  → fattispecie_analysis  (analisi/ragionamento multi-fonte)
INTENT_MAP: dict[str, str] = {
    "retrieval":             "norma_lookup",
    "reasoning":             "fattispecie_analysis",
    # pass-through per file già allineati all'API
    "norma_lookup":          "norma_lookup",
    "giurisprudenza_search": "giurisprudenza_search",
    "fattispecie_analysis":  "fattispecie_analysis",
    "norma_evolution":       "norma_evolution",
    "rischio_contrattuale":  "rischio_contrattuale",
    "precedente_interno":    "precedente_interno",
}

_DEFAULT_INTENT = "norma_lookup"

# Pattern source_id considerati "grounded" (non allucinati)
_GROUNDED_PATTERNS: list[re.Pattern] = [
    re.compile(r"^urn:nir:"),
    re.compile(r"^CC_ART_\d+"),
    re.compile(r"^CASS_(PEN|CIV|SS_UU)_\d{4}_\d+"),
    re.compile(r"^COST_ART_\d+"),
    re.compile(r"^CEDU_"),
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EvalQuery:
    """Una query di valutazione caricata da un file JSONL."""

    id: str
    query: str
    workspace: str
    intent: str                              # valore raw dal JSONL (es. "retrieval")
    expected_source_ids: list[str] = field(default_factory=list)
    module: str = ""                         # es. "cod_civ", "pen", "lav"
    difficulty: str = "medium"               # "easy" | "medium" | "hard"
    top_k: int = 10
    query_type: str = ""                     # "case" | "doctrine" | "" (non specificato)

    @property
    def api_intent(self) -> str:
        """Traduce il valore JSONL nel valore accettato dall'API."""
        return INTENT_MAP.get(self.intent.lower(), _DEFAULT_INTENT)


@dataclass
class EvalResult:
    """Risultato di una singola query di valutazione."""

    query_id: str
    module: str
    difficulty: str
    query: str
    latency_ms: float
    retrieved_source_ids: list[str] = field(default_factory=list)
    groundedness: float = 0.0
    recall_at_k: Optional[float] = None    # None se expected_source_ids è vuoto
    retrieval_confidence: str = ""
    reviewer_verdict: str = ""
    error: Optional[str] = None
    # Dettaglio chunk (popolato sempre — usato da --verbose e dal JSON report)
    sources: list[dict] = field(default_factory=list)


@dataclass
class ModuleStats:
    """Metriche aggregate per un singolo modulo legislativo."""

    module: str
    total: int = 0
    errors: int = 0
    mean_groundedness: float = 0.0
    mean_recall_at_k: Optional[float] = None
    mean_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    pass_rate: float = 0.0


@dataclass
class EvalReport:
    """Report aggregato di un'intera sessione di valutazione."""

    run_id: str
    queries_file: str
    total: int
    errors: int
    mean_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    mean_groundedness: float
    mean_recall_at_k: Optional[float]
    pass_rate: float
    per_module: dict[str, ModuleStats] = field(default_factory=dict)
    results: list[EvalResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class Evaluator:
    """
    Chiama POST /query per ogni EvalQuery e calcola le metriche.
    Non solleva mai eccezioni verso l'esterno: gli errori sono catturati
    in EvalResult.error e le metriche settate a 0.0 / None.
    """

    def __init__(
        self,
        api_base_url: str = "http://127.0.0.1:8765",
        timeout: float = 180.0,
    ) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Query singola
    # ------------------------------------------------------------------

    async def run_query(self, q: EvalQuery) -> EvalResult:
        result = EvalResult(
            query_id=q.id,
            module=q.module,
            difficulty=q.difficulty,
            query=q.query,
            latency_ms=0.0,
        )

        payload: dict = {
            "query": q.query,
            "workspace": q.workspace,
            "intent": q.api_intent,
            "top_k": q.top_k,
            # Bypass S1 Clarifier: eval non è una sessione interattiva,
            # ogni query è autonoma e deve procedere direttamente al retrieval.
            "clarification_turn": 2,
        }

        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.api_base_url}/query", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            result.latency_ms = (time.perf_counter() - t0) * 1000
            result.error = str(exc)
            logger.warning(f"[{q.id}] errore API: {exc}")
            return result

        result.latency_ms = (time.perf_counter() - t0) * 1000

        sources = data.get("sources", [])
        result.retrieved_source_ids = [s.get("source_id", "") for s in sources]
        result.retrieval_confidence = data.get("retrieval_confidence", "")
        result.reviewer_verdict = data.get("reviewer_verdict", "")
        result.sources = sources          # dettaglio completo per --verbose / JSON

        result.groundedness = self._calc_groundedness(result.retrieved_source_ids)
        result.recall_at_k = self._calc_recall_at_k(
            result.retrieved_source_ids, q.expected_source_ids
        )

        # Derive the per-query pass label using the same criterion as build_report
        # pass_count: a query passes when reviewer_verdict != "BLOCK" (no error).
        # Log the raw reviewer verdict in parentheses when it differs from "PASS"
        # so diagnostics are preserved without conflicting with the summary.
        if result.reviewer_verdict == "BLOCK":
            pass_label = "BLOCK"
        else:
            pass_label = "PASS"
        verdict_detail = (
            f"  (reviewer={result.reviewer_verdict})"
            if result.reviewer_verdict and result.reviewer_verdict != "PASS"
            else ""
        )

        logger.info(
            f"[{q.id}] {result.latency_ms:.0f}ms  "
            f"G={result.groundedness:.2f}  "
            f"R={f'{result.recall_at_k:.2f}' if result.recall_at_k is not None else 'N/A'}  "
            f"{pass_label}{verdict_detail}"
        )
        return result

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------

    async def run_all(self, queries: list[EvalQuery]) -> list[EvalResult]:
        """Esegue tutte le query in sequenza (un solo LLM locale — no parallelismo)."""
        results: list[EvalResult] = []
        for q in queries:
            r = await self.run_query(q)
            results.append(r)
        return results

    # ------------------------------------------------------------------
    # Metriche
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_groundedness(source_ids: list[str]) -> float:
        """
        Percentuale di source_id che seguono un pattern URN/interno noto.
        Un source_id vuoto o < 5 caratteri non è considerato grounded.
        """
        if not source_ids:
            return 0.0
        valid = sum(
            1
            for sid in source_ids
            if sid and len(sid) >= 5
            and any(p.match(sid) for p in _GROUNDED_PATTERNS)
        )
        return valid / len(source_ids)

    @staticmethod
    def _source_matches(retrieved: str, expected: str) -> bool:
        """
        Match tollerante per URN Normattiva con suffisso articolo (~artXXX).

        Esempi:
          retrieved="urn:nir:stato:regio.decreto:1942-03-16;262"
          expected ="urn:nir:stato:regio.decreto:1942-03-16;262~art1350"
          → True  (stessa norma, articolo non specificato nel retrieved)

          retrieved="urn:nir:stato:regio.decreto:1942-03-16;262~art1350"
          expected ="urn:nir:stato:regio.decreto:1942-03-16;262~art1350"
          → True  (match esatto)
        """
        if not retrieved or not expected:
            return False
        if retrieved == expected:
            return True
        # Confronta le basi (tutto ciò che precede "~")
        base_r = retrieved.split("~")[0].rstrip(":")
        base_e = expected.split("~")[0].rstrip(":")
        return base_r == base_e

    def _calc_recall_at_k(
        self,
        retrieved: list[str],
        expected: list[str],
    ) -> Optional[float]:
        """
        Recall@k: |retrieved ∩ expected| / |expected|.
        Ritorna None se expected è vuoto (query esplorativa senza ground truth).
        """
        if not expected:
            return None
        matched = sum(
            1
            for exp in expected
            if any(self._source_matches(ret, exp) for ret in retrieved)
        )
        return matched / len(expected)

    # ------------------------------------------------------------------
    # Aggregazione
    # ------------------------------------------------------------------

    @staticmethod
    def build_report(
        results: list[EvalResult],
        run_id: str,
        queries_file: str,
    ) -> EvalReport:
        total = len(results)
        errors = sum(1 for r in results if r.error)
        ok = [r for r in results if not r.error]

        latencies = [r.latency_ms for r in ok] or [0.0]
        groundedness_vals = [r.groundedness for r in ok] or [0.0]
        recall_vals = [r.recall_at_k for r in ok if r.recall_at_k is not None]

        pass_count = sum(
            1 for r in results if not r.error and r.reviewer_verdict != "BLOCK"
        )
        pass_rate = pass_count / total if total else 0.0

        # Per-module aggregation
        modules: dict[str, list[EvalResult]] = {}
        for r in results:
            modules.setdefault(r.module or "unknown", []).append(r)

        per_module: dict[str, ModuleStats] = {}
        for mod, mod_results in modules.items():
            mod_ok = [r for r in mod_results if not r.error]
            mod_lat = [r.latency_ms for r in mod_ok] or [0.0]
            mod_g = [r.groundedness for r in mod_ok] or [0.0]
            mod_rec = [r.recall_at_k for r in mod_ok if r.recall_at_k is not None]
            mod_pass = sum(
                1 for r in mod_results
                if not r.error and r.reviewer_verdict != "BLOCK"
            )
            per_module[mod] = ModuleStats(
                module=mod,
                total=len(mod_results),
                errors=sum(1 for r in mod_results if r.error),
                mean_groundedness=sum(mod_g) / len(mod_g),
                mean_recall_at_k=sum(mod_rec) / len(mod_rec) if mod_rec else None,
                mean_latency_ms=sum(mod_lat) / len(mod_lat),
                p95_latency_ms=_percentile(mod_lat, 95),
                pass_rate=mod_pass / len(mod_results) if mod_results else 0.0,
            )

        return EvalReport(
            run_id=run_id,
            queries_file=queries_file,
            total=total,
            errors=errors,
            mean_latency_ms=sum(latencies) / len(latencies),
            p50_latency_ms=_percentile(latencies, 50),
            p95_latency_ms=_percentile(latencies, 95),
            mean_groundedness=sum(groundedness_vals) / len(groundedness_vals),
            mean_recall_at_k=sum(recall_vals) / len(recall_vals) if recall_vals else None,
            pass_rate=pass_rate,
            per_module=per_module,
            results=results,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    idx = max(0, int(len(sorted_d) * pct / 100) - 1)
    return sorted_d[idx]
