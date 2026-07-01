"""
Citation Reviewer [S5] — interamente rule-based, zero LLM.
Verifica che ogni source_id nella risposta sia nel Research Packet.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date
from loguru import logger
from aiura_legal.core.types import ResearchPacket
from aiura_legal.core.graph.retriever import GraphRetriever

# Identificatori di sentenze giurisprudenziali (sha256[:16] hex)
_SENTENZA_ID_RE = re.compile(r"\b[0-9a-f]{16}\b")

# Regex per estrarre l'hex16 base da un doc_id chunk (legacy o Fase 1)
# - Legacy:  e65a598d71052357  (puro hex16 — usato come doc_id)
# - Fase 1:  e65a598d71052357_motivazione_003 (sub-chunk)
_CHUNK_PREFIX_RE = re.compile(r"^([0-9a-f]{16})")

# Citazione di sentenza in formato "numero/anno" (es. "29164/2021") — formato
# leggibile che l'LLM usa spontaneamente al posto dell'hex16 interno mostrato
# nel prompt. Non è un identificatore canonico del sistema, ma se risolve a
# una fonte realmente presente nel Research Packet va trattato come grounded
# (vedi _resolve_numero_anno_citations).
_NUMERO_ANNO_RE = re.compile(r"^\d+/\d{4}$")

# URN normattiva: separa il prefisso dell'atto dal frammento articolo finale
# (es. "urn:nir:...regio.decreto:1930-10-19;1398~art322-ter" → atto + "322-ter").
# Usato per risolvere citazioni con URN "logico" (l'articolo come l'LLM lo
# conosce dal pretraining) quando il corpus indicizza quello stesso articolo
# sotto un frammento storicamente diverso (rinumerazioni legislative: es. l'art.
# 322-ter c.p. è memorizzato nel corpus come "~art383" del R.D. 1398/1930).
_URN_ART_RE = re.compile(r"^(.*~art)([\w\-]+)$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Pattern per estrarre citazioni da testo legale
# ---------------------------------------------------------------------------

_CITATION_PATTERNS = [
    r"\bCC_ART_\d+\b",
    r"\bCP_ART_\d+\b",
    r"\bCPP_ART_\d+\b",
    r"\bCASS_(?:PEN|CIV|SS_UU)_\d{4}_\d+\b",
    r"\bCEDU_\w+_\d{4}\b",
    r"\bCOST_\d{4}_\d+\b",
    r"\bDLGS_\d+_\d{4}_ART_\d+\b",
    # URN Normattiva (formato reale dei source_id nel sistema)
    r"urn:nir:[^\s,\]\"\\']+",
]

_CITATION_RE = re.compile("|".join(_CITATION_PATTERNS), re.IGNORECASE)

# Stato norma che causa FAIL CRITICO
_UNCONSTITUTIONAL_STATUS = "INCOSTITUZIONALE"

# ---------------------------------------------------------------------------
# Claim relevance — overlap lessicale claim↔fonte (zero LLM)
# ---------------------------------------------------------------------------

# Stopword italiane + connettivi giuridici ricorrenti: escluse dal tokenizer
# perché compaiono ovunque e gonfiano artificialmente l'overlap anche tra
# claim e fonte completamente scorrelate.
_STOPWORDS_IT: frozenset[str] = frozenset({
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da",
    "in", "con", "su", "per", "tra", "fra", "e", "ed", "o", "ma", "se", "che",
    "non", "del", "della", "dello", "dei", "degli", "delle", "al", "allo",
    "alla", "ai", "agli", "alle", "nel", "nello", "nella", "nei", "negli",
    "nelle", "sul", "sullo", "sulla", "sui", "sugli", "sulle", "dal", "dallo",
    "dalla", "dai", "dagli", "dalle", "come", "anche", "ai sensi", "art",
    "art.", "articolo", "comma", "ai", "sensi", "questo", "questa", "questi",
    "queste", "cui", "quale", "quali", "ogni", "essere", "avere", "tale",
    "tali", "sono", "è", "stato", "stata", "stati", "state",
})

_WORD_RE = re.compile(r"[a-zàèéìòù]+", re.IGNORECASE)
_MIN_TOKEN_LEN = 3

# Sotto questa soglia di copertura (frazione di token "di contenuto" del claim
# trovati nel testo della fonte citata) la citazione è marcata come
# topicamente sospetta. Soglia volutamente bassa: il check deve solo
# scartare casi di citazione completamente scorrelata, non penalizzare
# parafrasi legittime — i falsi positivi diventano WARN, non BLOCK.
_CLAIM_RELEVANCE_MIN_COVERAGE = 0.15
_CLAIM_RELEVANCE_MIN_TOKENS = 3  # claim troppo corti non sono valutabili


def _tokenize(text: str) -> set[str]:
    words = _WORD_RE.findall((text or "").lower())
    return {w for w in words if len(w) >= _MIN_TOKEN_LEN and w not in _STOPWORDS_IT}


def _claim_coverage(claim_tokens: set[str], source_tokens: set[str]) -> float:
    """Frazione di token del claim presenti nel testo della fonte citata."""
    if not claim_tokens:
        return 1.0
    return len(claim_tokens & source_tokens) / len(claim_tokens)


@dataclass
class ReviewResult:
    verdict: str  # "PASS" | "FAIL" | "WARN"
    checks: dict[str, str] = field(default_factory=dict)
    ungrounded_citations: list[str] = field(default_factory=list)
    irrelevant_citations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    action: str = "DELIVER"  # "DELIVER" | "RE_RETRIEVAL" | "BLOCK"


class CitationReviewer:
    """
    Gatekeeper del Citation Contract.
    Verifica meccanica senza chiamate LLM.

    Args:
        graph: GraphRetriever opzionale per il check conflict_disclosure.
               Se None (default) il check è sempre PASS (backward compatible).
    """

    def __init__(
        self,
        graph: GraphRetriever | None = None,
        jurisprudence_graph=None,
        normattiva_urns: set[str] | None = None,
    ) -> None:
        self._graph = graph
        self._jgraph = jurisprudence_graph
        self._normattiva_urns: set[str] = normattiva_urns or set()

    def verify(
        self,
        response_text: str,
        research_packet: ResearchPacket,
        reference_date: date | None = None,
        structured_cited_ids: list[str] | None = None,
        phase_source_ids: set[str] | None = None,
        phase_sources_metadata: dict[str, dict] | None = None,
        cited_claims: list[dict] | None = None,
        ref_map: dict[str, str] | None = None,
    ) -> ReviewResult:
        """
        Esegue tutti i check in ordine.
        Ritorna BLOCK al primo FAIL CRITICO, altrimenti aggrega WARN.

        Args:
            structured_cited_ids: source_id estratti direttamente dai citations[]
                delle PhaseResult (pre-parsati dalla struttura JSON). Vengono
                aggiunti a quelli estratti via regex dal testo, catturando anche
                ID non-standard come hash hex o etichette posizionali.
            phase_source_ids: source_id delle fonti restituite dal PhaseRetriever
                (Fase 2 normativa+dottrina, Fase 3 giurisprudenza). Non sono nel
                packet S2 iniziale ma sono fonti legittime mostrate all'LLM.
            phase_sources_metadata: source_id → metadata delle fonti del
                PhaseRetriever. Usato per risolvere citazioni in formato
                "numero/anno" (vedi _resolve_numero_anno_citations) e per il
                claim relevance check.
            cited_claims: lista di {"source_id":, "claim":} dalle citations[]
                strutturate delle PhaseResult. Permette il check di rilevanza
                topica (claim↔testo fonte) — citazioni formalmente grounded
                (source_id presente nel packet) ma il cui claim non condivide
                vocabolario con il testo della fonte citata sono sospette di
                allucinazione "a posteriori" (citazione corretta agganciata a
                un'affermazione che la fonte non supporta).
            ref_map: "F1"/"F2"… → source_id reale, unione dei ref_map di tutte
                le PhaseResult. Il modello cita SOLO il riferimento mostrato nel
                prompt (mai il source_id grezzo, vedi analyst._assign_refs):
                questa mappa lo risolve al source_id reale prima del grounding
                check, così un modello piccolo non deve mai copiare/ricostruire
                URN o hash — elimina sia il bug "copia male l'id" sia il bug
                "allucina un id plausibile ma non mostrato".
        """
        checks: dict[str, str] = {}
        warnings: list[str] = []
        ungrounded: list[str] = []

        # Set di source_id presenti nel Packet (uppercase per citazioni normative)
        # Esteso con le fonti del PhaseRetriever (Fase 2/3) mostrate all'LLM.
        # phase_sources_metadata è incluso anche se phase_source_ids non viene
        # passato (le sue chiavi SONO source_id di fonti mostrate all'LLM) —
        # evita che i due parametri debbano restare sincronizzati dal chiamante.
        _phase_ids_all = set(phase_source_ids or set()) | set((phase_sources_metadata or {}).keys())
        _phase_ids_upper = {sid.upper() for sid in _phase_ids_all}
        packet_ids = {s.source_id.upper() for s in research_packet.sources} | _phase_ids_upper
        # Set di doc_id presenti nel Packet (case-sensitive per sentenze hex)
        packet_doc_ids = {s.doc_id for s in research_packet.sources} | _phase_ids_all

        # Estende packet_ids con l'hex16 BASE delle sentenze (senza suffisso di
        # sezione, es. "_motivazione"/"_massima"). Al modello viene insegnato a
        # citare le sentenze con l'hex16 nudo (forma canonica) anche quando il
        # source_id mostrato nel prompt ha un suffisso — senza questa estensione
        # il check #1 (match letterale) le marca come ungrounded per falso
        # positivo, mentre il check #4 (jurisprudence_grounding) le riconosce
        # correttamente. Le due verifiche devono essere coerenti.
        _hex16_bases: set[str] = set()
        for sid in (packet_ids | {d for d in packet_doc_ids}):
            m = _CHUNK_PREFIX_RE.match(sid.lower())
            if m:
                _hex16_bases.add(m.group(1).upper())
        packet_ids |= _hex16_bases

        # Citazioni estratte dalla risposta (regex + structured)
        cited_from_text = self.extract_citations(response_text)
        cited_structured = list(structured_cited_ids or [])
        # Unione deduplicata: i structured passano senza regex-filter
        cited = list({c.upper(): c for c in cited_from_text + cited_structured}.values())

        # Risolve citazioni "numero/anno" (es. "29164/2021") all'hex16/source_id
        # canonico se la sentenza è realmente nel Research Packet o nelle fonti
        # del PhaseRetriever — altrimenti resta non risolta e viene marcata
        # ungrounded normalmente (non è un bypass del Citation Contract).
        numero_anno_map = self._build_numero_anno_map(research_packet, phase_sources_metadata)
        cited = self._resolve_numero_anno_citations(cited, numero_anno_map)

        # Risolve URN "logici" su articoli storicamente rinumerati (es. l'LLM
        # cita "~art322-ter" per l'art. 322-ter c.p. mentre il corpus lo
        # indicizza come "~art383" del R.D. 1398/1930): se stesso atto e stesso
        # articolo per nome, è la stessa norma — non un'allucinazione.
        articolo_map = self._build_articolo_map(research_packet, phase_sources_metadata)
        cited = self._resolve_articolo_citations(cited, articolo_map)

        # Risolve i riferimenti "F1"/"F2"… al source_id reale (vedi docstring
        # del parametro ref_map). Applicata anche a cited_claims, così il
        # claim-relevance check (1b) può ritrovare il testo della fonte vera.
        if ref_map:
            cited = self._resolve_ref_citations(cited, ref_map)
            if cited_claims:
                cited_claims = [
                    {**c, "source_id": ref_map.get(str(c.get("source_id", "")).upper(), c.get("source_id"))}
                    if isinstance(c, dict) else c
                    for c in cited_claims
                ]

        # 1. Citation Grounding
        for cit in cited:
            if cit.upper() not in packet_ids:
                ungrounded.append(cit)

        if ungrounded:
            checks["citation_grounding"] = "FAIL"
        else:
            checks["citation_grounding"] = "PASS"

        # 1b. Claim relevance — overlap lessicale claim↔testo fonte citata.
        # Valuta solo le citazioni già grounded (source_id nel packet): non è
        # un secondo check di grounding, è un check di pertinenza topica.
        irrelevant = self._check_claim_relevance(
            cited_claims or [], research_packet, phase_sources_metadata, ungrounded,
        )
        if irrelevant:
            checks["claim_relevance"] = "WARN"
            warnings.append(
                f"Citazioni formalmente corrette ma topicamente sospette "
                f"(scarso overlap claim↔fonte): {irrelevant}"
            )
        else:
            checks["claim_relevance"] = "PASS"

        # 2. Vigenza temporale
        # Fonte primaria: metadata.valid_to del Research Packet (popolato da
        # MongoDB all'ingestione). Se assente (fonte arrivata via
        # questione_expansion o metadata incompleti), fallback sul grafo
        # (GraphRetriever.is_abrogated) prima di assumere "vigente" per
        # default — non vogliamo che un buco nei metadata mascheri una
        # norma abrogata. Le due fonti usano formati data indipendenti
        # (metadata: stringa libera; grafo: nodo article.valid_to "YYYYMMDD"
        # via _is_valid) — nessun confronto incrociato tra i due formati.
        if reference_date:
            expired = []
            for src in research_packet.sources:
                if src.source_id.upper() not in {c.upper() for c in cited}:
                    continue
                valid_to = src.metadata.get("valid_to", "")
                if valid_to:
                    if valid_to < str(reference_date):
                        expired.append(src.source_id)
                elif self._graph and self._graph.is_available:
                    if self._graph.is_abrogated(src.source_id, reference_date):
                        expired.append(src.source_id)
            if expired:
                checks["temporal_validity"] = "WARN"
                warnings.append(f"Norme scadute citate: {expired}")
            else:
                checks["temporal_validity"] = "PASS"
        else:
            checks["temporal_validity"] = "PASS"

        # 3. Contrasti/abrogazioni non dichiarati (via GraphRetriever)
        if self._graph and self._graph.is_available and cited:
            graph_conflicts = self._graph.get_conflicts(list({c.upper() for c in cited}))
            if graph_conflicts:
                checks["conflict_disclosure"] = "WARN"
                conflict_summary = "; ".join(f"{a}↔{b}({t})" for a, b, t in graph_conflicts[:3])
                warnings.append(f"Norme in conflitto/abrogazione: {conflict_summary}")
            else:
                checks["conflict_disclosure"] = "PASS"
        else:
            checks["conflict_disclosure"] = "PASS"

        # 4. Grounding giurisprudenziale
        # Costruisce l'insieme degli hex16 base presenti nel packet:
        # - chunk legacy: doc_id = hex16 (e.g. "e65a598d71052357")
        # - sub-chunk Fase 1: doc_id = hex16_motivazione_NNN → estrae hex16
        # In entrambi i casi, la risposta cita solo l'hex16 base della sentenza.
        #
        # Esteso con le fonti del PhaseRetriever (Fase 2/3, _phase_ids_all/
        # packet_doc_ids) — non solo research_packet.sources (S2 iniziale):
        # senza questa estensione, una sentenza recuperata SOLO in Fase 3 (es.
        # da retrieve_giurisprudenza_multi) e citata con il suo hex16 nudo nel
        # testo (es. quando humanize_refs non trova un'etichetta leggibile e
        # lascia il source_id grezzo, vedi analyst.build_source_label) viene
        # marcata ungrounded per falso positivo — pur essendo correttamente
        # grounded per il check #1 (che usa packet_ids, già esteso sopra).
        packet_hex_ids: set[str] = set()
        for sid in {s.doc_id for s in research_packet.sources} | packet_doc_ids | _phase_ids_all:
            if not sid:
                continue
            m = _CHUNK_PREFIX_RE.match(sid.lower())
            if m:
                packet_hex_ids.add(m.group(1))

        sent_ids = _SENTENZA_ID_RE.findall(response_text)
        sent_ungrounded = [sid for sid in sent_ids if sid not in packet_hex_ids]
        if sent_ungrounded:
            ungrounded.extend(sent_ungrounded)
            checks["jurisprudence_grounding"] = "FAIL"
        else:
            checks["jurisprudence_grounding"] = "PASS"

        # 5. Link norma↔sentenza tramite grafo giurisprudenziale
        if self._jgraph is not None and self._normattiva_urns:
            for sid in sent_ids:
                if sid in packet_doc_ids and self._jgraph.sentenza_exists(sid):
                    for urn in self._jgraph.get_norme_per_sentenza(sid):
                        if urn not in self._normattiva_urns:
                            warnings.append(
                                f"Norma {urn} (citata in sentenza {sid}) assente in normattiva_docs"
                            )
                            checks[urn] = "NORMA_NOT_IN_NORMATTIVA"

        # 6. Incostituzionalità — FAIL CRITICO
        unconstitutional = []
        for src in research_packet.sources:
            if src.source_id.upper() in {c.upper() for c in cited}:
                status = src.metadata.get("status", "")
                if status.upper() == _UNCONSTITUTIONAL_STATUS:
                    unconstitutional.append(src.source_id)

        if unconstitutional:
            checks["constitutionality"] = "FAIL_CRITICO"
            logger.critical(
                f"Norma incostituzionale citata come vigente: {unconstitutional}"
            )
            return ReviewResult(
                verdict="FAIL",
                checks=checks,
                ungrounded_citations=ungrounded,
                warnings=[f"CRITICO: norma incostituzionale: {unconstitutional}"],
                action="BLOCK",
            )
        else:
            checks["constitutionality"] = "PASS"

        # Determina verdict finale
        any_grounding_fail = (
            checks["citation_grounding"] == "FAIL"
            or checks.get("jurisprudence_grounding") == "FAIL"
        )
        if any_grounding_fail:
            verdict = "FAIL"
            action = "RE_RETRIEVAL"
        elif warnings:
            verdict = "WARN"
            action = "DELIVER"
        else:
            verdict = "PASS"
            action = "DELIVER"

        return ReviewResult(
            verdict=verdict,
            checks=checks,
            ungrounded_citations=ungrounded,
            irrelevant_citations=irrelevant,
            warnings=warnings,
            action=action,
        )

    @staticmethod
    def _check_claim_relevance(
        cited_claims: list[dict],
        research_packet: ResearchPacket,
        phase_sources_metadata: dict[str, dict] | None,
        ungrounded: list[str],
    ) -> list[str]:
        """
        Per ogni {"source_id", "claim"}, verifica che il claim condivida
        vocabolario di contenuto con il testo della fonte citata.

        Ritorna la lista di "source_id::claim troncato" per le citazioni
        sospette. Citazioni già ungrounded sono saltate (gestite dal check
        di grounding); claim troppo corti per essere valutati in modo
        affidabile sono saltati (nessun falso positivo su frasi telegrafiche).
        """
        if not cited_claims:
            return []

        ungrounded_upper = {u.upper() for u in ungrounded}

        # source_id → testo completo disponibile (packet + fonti PhaseRetriever)
        text_by_source: dict[str, str] = {}
        for src in research_packet.sources:
            text_by_source[src.source_id.upper()] = src.full_text or src.snippet or ""
        for sid, meta in (phase_sources_metadata or {}).items():
            if sid.upper() not in text_by_source or not text_by_source[sid.upper()]:
                text_by_source[sid.upper()] = str((meta or {}).get("text", "") or "")

        flagged: list[str] = []
        seen: set[tuple[str, str]] = set()
        for entry in cited_claims:
            source_id = str(entry.get("source_id", "")).strip()
            claim = str(entry.get("claim", "")).strip()
            if not source_id or not claim:
                continue
            sid_upper = source_id.upper()
            if sid_upper in ungrounded_upper:
                continue  # già segnalato dal grounding check

            source_text = text_by_source.get(sid_upper, "")
            if not source_text:
                continue  # nessun testo disponibile per confrontare — non valutabile

            claim_tokens = _tokenize(claim)
            if len(claim_tokens) < _CLAIM_RELEVANCE_MIN_TOKENS:
                continue

            source_tokens = _tokenize(source_text)
            coverage = _claim_coverage(claim_tokens, source_tokens)
            if coverage < _CLAIM_RELEVANCE_MIN_COVERAGE:
                key = (sid_upper, claim[:80])
                if key not in seen:
                    seen.add(key)
                    flagged.append(f"{source_id}::{claim[:80]}")

        return flagged

    @staticmethod
    def _build_numero_anno_map(
        research_packet: ResearchPacket,
        phase_sources_metadata: dict[str, dict] | None,
    ) -> dict[str, str]:
        """Mappa "numero/anno" → source_id canonico, dalle fonti realmente recuperate."""

        def _add(m: dict[str, str], source_id: str, metadata: dict) -> None:
            numero = str((metadata or {}).get("numero") or "").strip()
            anno = str((metadata or {}).get("anno") or "").strip()
            if numero and anno:
                m[f"{numero}/{anno}"] = source_id

        mapping: dict[str, str] = {}
        for src in research_packet.sources:
            _add(mapping, src.source_id, src.metadata)
        for sid, meta in (phase_sources_metadata or {}).items():
            _add(mapping, sid, meta)
        return mapping

    @staticmethod
    def _resolve_numero_anno_citations(
        cited: list[str],
        numero_anno_map: dict[str, str],
    ) -> list[str]:
        """Sostituisce le citazioni "numero/anno" con l'id canonico se risolvibili."""
        resolved = []
        for cit in cited:
            if _NUMERO_ANNO_RE.match(cit) and cit in numero_anno_map:
                canonical = numero_anno_map[cit]
                logger.debug(f"[CitationReviewer] citazione {cit!r} normalizzata → {canonical!r}")
                resolved.append(canonical)
            else:
                resolved.append(cit)
        return resolved

    @staticmethod
    def _normalize_art_num(s: str) -> str:
        """'Art. 322-ter' / 'art322ter' / '322 ter' → '322ter' (confronto robusto)."""
        s = s.strip().lower()
        s = re.sub(r"^art\.?\s*", "", s)
        return re.sub(r"[\s\-.]", "", s)

    @classmethod
    def _build_articolo_map(
        cls,
        research_packet: ResearchPacket,
        phase_sources_metadata: dict[str, dict] | None,
    ) -> dict[tuple[str, str], str]:
        """Mappa (prefisso_atto, art_normalizzato) → source_id canonico.

        Permette di risolvere un URN "logico" (l'articolo come l'LLM lo
        ricostruisce dal pretraining) sullo stesso atto quando il corpus lo
        indicizza sotto un frammento diverso per rinumerazione storica.
        """

        def _add(m: dict[tuple[str, str], str], source_id: str, metadata: dict) -> None:
            match = _URN_ART_RE.match(source_id)
            if not match:
                return
            art_num = str((metadata or {}).get("articolo_num") or "").strip()
            if not art_num:
                return
            key = (match.group(1).lower(), cls._normalize_art_num(art_num))
            m.setdefault(key, source_id)

        mapping: dict[tuple[str, str], str] = {}
        for src in research_packet.sources:
            _add(mapping, src.source_id, src.metadata)
        for sid, meta in (phase_sources_metadata or {}).items():
            _add(mapping, sid, meta)
        return mapping

    @classmethod
    def _resolve_articolo_citations(
        cls,
        cited: list[str],
        articolo_map: dict[tuple[str, str], str],
    ) -> list[str]:
        """Sostituisce URN "logici" non grounded con l'id canonico realmente
        presente nel packet, se riferiscono lo stesso atto e lo stesso articolo
        (per nome) — non se "indovinano" un articolo diverso o un atto diverso."""
        resolved = []
        for cit in cited:
            match = _URN_ART_RE.match(cit)
            if match:
                key = (match.group(1).lower(), cls._normalize_art_num(match.group(2)))
                canonical = articolo_map.get(key)
                if canonical and canonical.upper() != cit.upper():
                    logger.debug(
                        f"[CitationReviewer] citazione {cit!r} normalizzata "
                        f"(articolo storicamente rinumerato) → {canonical!r}"
                    )
                    resolved.append(canonical)
                    continue
            resolved.append(cit)
        return resolved

    @staticmethod
    def _resolve_ref_citations(cited: list[str], ref_map: dict[str, str]) -> list[str]:
        """Sostituisce i riferimenti "F1"/"F2"… con il source_id reale che
        rappresentano. Un ref non presente in mappa (inventato, o residuo di
        un vecchio formato) passa inalterato — resta ungrounded normalmente."""
        upper_map = {k.upper(): v for k, v in ref_map.items()}
        return [upper_map.get(cit.upper(), cit) for cit in cited]

    def extract_citations(self, text: str) -> list[str]:
        """
        Estrae tutti gli identificatori di citazione dal testo.
        Rimuove la punteggiatura terminale di frase dai match URN
        (es. "urn:...~art1218." → "urn:...~art1218").
        """
        raw = _CITATION_RE.findall(text)
        cleaned = [c.rstrip(".,;:)]}'\"") for c in raw]
        return list(set(cleaned))
