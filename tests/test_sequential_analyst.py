"""
Test SequentialAnalyst (analyze_sequential) e PhaseRetriever.

Strategia:
  - OllamaClient.generate mockato → output LLM controllato senza Ollama
  - PhaseRetriever mockato → nessun indice su disco
  - HybridRetriever mockato → nessun indice su disco
  - Zero chiamate HTTP, zero PII reali
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiura_legal.agents.analyst import AnalystAgent, PhaseResult, _format_source, _assign_refs
from aiura_legal.core.retrieval.phase_retriever import PhaseRetriever
from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source(
    doc_id: str,
    layer: str = "normativa",
    snippet: str = "Testo sintetico.",
) -> SearchResult:
    return SearchResult(
        doc_id=doc_id,
        score=1.0,
        snippet=snippet,
        source_id=doc_id,
        source_layer=layer,
        retrieval_method="hybrid_rrf",
        metadata={"corpus": layer, "titolo": "Titolo sintetico"},
    )


def _make_packet() -> ResearchPacket:
    return ResearchPacket(
        query_original="test query",
        query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
        sources=[
            _make_source("ART_43_CP", "normativa", "Art. 43 c.p. — elemento soggettivo del reato."),
            _make_source("giurisprudenza_cass_38343_2014", "giurisprudenza", "ThyssenKrupp — dolo eventuale."),
        ],
        retrieval_confidence="HIGH",
    )


def _phase_json(
    step_names: list[str],
    questione_retrieval: str = "",
    giurisprudenza_retrieval_varianti: list[str] | None = None,
) -> str:
    sections = [
        {"step": name, "content": f"Contenuto {name}.", "citations": []}
        for name in step_names
    ]
    data: dict = {
        "analysis_sections": sections,
        "overall_confidence": "MEDIUM",
        "gaps": [],
    }
    if questione_retrieval:
        data["questione_retrieval"] = questione_retrieval
        data["qualificazione_retrieval"] = questione_retrieval + " giurisprudenza"
    if giurisprudenza_retrieval_varianti is not None:
        data["giurisprudenza_retrieval_varianti"] = giurisprudenza_retrieval_varianti
    return json.dumps(data)


# ---------------------------------------------------------------------------
# Fixture: AnalystAgent con OllamaClient mockato
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ollama():
    ollama = MagicMock()
    ollama.model = "qwen2.5:7b-test"
    # generate è async — risponde con JSON per ogni fase
    call_count = {"n": 0}
    responses = [
        _phase_json(
            ["RICOSTRUZIONE_FATTO", "QUALIFICAZIONE", "QUESTIONE"],
            questione_retrieval="dolo eventuale colpa cosciente art. 43",
        ),
        _phase_json(["FONTI_NORMATIVE", "INTERPRETAZIONE"]),
        _phase_json(["GIURISPRUDENZA"]),
        _phase_json(["SUSSUNZIONE", "OBIEZIONI", "CONCLUSIONE"]),
    ]

    async def _generate(**kwargs):
        n = call_count["n"]
        call_count["n"] += 1
        return responses[n] if n < len(responses) else "{}"

    ollama.generate = _generate
    return ollama


@pytest.fixture
def analyst(mock_ollama) -> AnalystAgent:
    return AnalystAgent(ollama=mock_ollama)


@pytest.fixture
def mock_phase_retriever():
    pr = MagicMock(spec=PhaseRetriever)
    pr.retrieve_normativa.return_value = [
        _make_source("ART_43_CP_REQUERY", "normativa", "Art. 43 — requery.")
    ]
    pr.retrieve_giurisprudenza_multi.return_value = [
        _make_source("giurisprudenza_thyssen_requery", "giurisprudenza", "ThyssenKrupp requery.")
    ]
    pr.retrieve_dottrina.return_value = []
    pr.retrieve_massimario.return_value = []
    return pr


# ---------------------------------------------------------------------------
# Test analyze_sequential — fasi e struttura
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_analyze_sequential_yields_4_phases(analyst, mock_phase_retriever):
    """analyze_sequential() deve emettere esattamente 4 PhaseResult."""
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="Qual è il confine tra dolo eventuale e colpa cosciente?",
        packet=packet,
        phase_retriever=mock_phase_retriever,
    ):
        phases.append(phase)

    assert len(phases) == 4


@pytest.mark.asyncio
async def test_analyze_sequential_phase_names(analyst, mock_phase_retriever):
    """Le 4 fasi devono avere i nomi corretti nell'ordine corretto."""
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="test", packet=packet, phase_retriever=mock_phase_retriever
    ):
        phases.append(phase)

    assert [p.name for p in phases] == ["FRAMING", "NORMATIVA", "GIURISPRUDENZA", "SINTESI"]
    assert [p.phase for p in phases] == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_analyze_sequential_phase1_extracts_retrieval_queries(analyst, mock_phase_retriever):
    """Fase 1 deve estrarre questione_retrieval e qualificazione_retrieval dal JSON."""
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="test", packet=packet, phase_retriever=mock_phase_retriever
    ):
        phases.append(phase)

    phase1 = phases[0]
    assert phase1.questione_retrieval == "dolo eventuale colpa cosciente art. 43"
    assert "giurisprudenza" in phase1.qualificazione_retrieval


@pytest.mark.asyncio
async def test_analyze_sequential_uses_phase_retriever(analyst, mock_phase_retriever):
    """PhaseRetriever deve essere chiamato una volta per normativa e una per giurisprudenza."""
    packet = _make_packet()
    async for _ in analyst.analyze_sequential(
        query="test", packet=packet, phase_retriever=mock_phase_retriever
    ):
        pass

    mock_phase_retriever.retrieve_normativa.assert_called_once()
    mock_phase_retriever.retrieve_giurisprudenza_multi.assert_called_once()


@pytest.mark.asyncio
async def test_fase3_massimario_blocco_separato(analyst, mock_phase_retriever):
    """Fase 3 recupera il massimario in un round dedicato (retrieve_massimario)
    e lo aggrega in phase3.sources_used accanto alla giurisprudenza — blocco
    separato, non in concorrenza con le sentenze."""
    mock_phase_retriever.retrieve_massimario.return_value = [
        _make_source("MASS_principio", "massimario", "Principio Gubert (Sez. U. 10561/2014).")
    ]
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="sequestro per equivalente terzo", packet=packet,
        phase_retriever=mock_phase_retriever,
    ):
        phases.append(phase)

    mock_phase_retriever.retrieve_massimario.assert_called_once()
    phase3 = phases[2]
    assert "MASS_principio" in phase3.sources_used
    # convivono giurisprudenza e massimario nelle fonti di fase
    assert "giurisprudenza_thyssen_requery" in phase3.sources_used


@pytest.mark.asyncio
async def test_fase3_massimario_step_separato_non_concorrente(mock_phase_retriever):
    """Quando il massimario è presente, il prompt di Fase 3 deve chiedere DUE
    step separati (GIURISPRUDENZA + MASSIMARIO) con budget di citazione
    indipendenti — non un unico step in cui il massimario compete con le
    sentenze per lo stesso budget di citations[] (vedi indicazione utente:
    i due corpus non devono concorrere nel ragionamento, non solo nel retrieval)."""
    mock_phase_retriever.retrieve_massimario.return_value = [
        _make_source("MASS_principio", "massimario", "Principio Gubert (Sez. U. 10561/2014).")
    ]
    prompts: list[str] = []
    ollama = MagicMock()
    ollama.model = "qwen2.5:7b-test"
    responses = [
        _phase_json(["RICOSTRUZIONE_FATTO", "QUALIFICAZIONE", "QUESTIONE"],
                    questione_retrieval="sequestro per equivalente terzo"),
        _phase_json(["FONTI_NORMATIVE", "INTERPRETAZIONE"]),
        _phase_json(["GIURISPRUDENZA", "MASSIMARIO"]),
        _phase_json(["SUSSUNZIONE", "OBIEZIONI", "CONCLUSIONE"]),
    ]

    async def _generate(prompt: str = "", **kwargs):
        prompts.append(prompt)
        n = len(prompts) - 1
        return responses[n] if n < len(responses) else "{}"

    ollama.generate = _generate
    analyst_local = AnalystAgent(ollama=ollama)

    packet = _make_packet()
    phases = []
    async for phase in analyst_local.analyze_sequential(
        query="sequestro per equivalente terzo", packet=packet,
        phase_retriever=mock_phase_retriever,
    ):
        phases.append(phase)

    prompt_f3 = prompts[2]
    assert "DUE step separati" in prompt_f3
    assert "MASSIMARIO" in prompt_f3
    assert "anche se hai già citato a sufficienza" in prompt_f3

    phase3 = phases[2]
    steps = [s.step for s in phase3.sections]
    assert "GIURISPRUDENZA" in steps
    assert "MASSIMARIO" in steps


@pytest.mark.asyncio
async def test_fase3_senza_massimario_un_solo_step_istruito(mock_phase_retriever):
    """Senza fonti massimario, il prompt richiede SOLO il passo GIURISPRUDENZA
    (nessuna istruzione fantasma su un secondo step che non esiste)."""
    mock_phase_retriever.retrieve_massimario.return_value = []
    prompts: list[str] = []
    ollama = MagicMock()
    ollama.model = "qwen2.5:7b-test"
    responses = [
        _phase_json(["RICOSTRUZIONE_FATTO", "QUALIFICAZIONE", "QUESTIONE"],
                    questione_retrieval="test"),
        _phase_json(["FONTI_NORMATIVE", "INTERPRETAZIONE"]),
        _phase_json(["GIURISPRUDENZA"]),
        _phase_json(["SUSSUNZIONE", "OBIEZIONI", "CONCLUSIONE"]),
    ]

    async def _generate(prompt: str = "", **kwargs):
        prompts.append(prompt)
        n = len(prompts) - 1
        return responses[n] if n < len(responses) else "{}"

    ollama.generate = _generate
    analyst_local = AnalystAgent(ollama=ollama)

    packet = _make_packet()
    async for _ in analyst_local.analyze_sequential(
        query="test", packet=packet, phase_retriever=mock_phase_retriever,
    ):
        pass

    prompt_f3 = prompts[2]
    assert "DUE step separati" not in prompt_f3
    assert "Produci il passo GIURISPRUDENZA" in prompt_f3


@pytest.mark.asyncio
async def test_analyze_sequential_phase1_fallback_varianti_assenti(analyst, mock_phase_retriever):
    """Se il JSON di Fase 1 non contiene giurisprudenza_retrieval_varianti (caso
    di default usato dal mock_ollama fixture), il fallback è una lista con la
    sola qualificazione_retrieval — comportamento identico a prima del campo."""
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="test", packet=packet, phase_retriever=mock_phase_retriever
    ):
        phases.append(phase)

    phase1 = phases[0]
    assert phase1.giurisprudenza_retrieval_varianti == [phase1.qualificazione_retrieval]


@pytest.mark.asyncio
async def test_analyze_sequential_phase1_estrae_varianti_multiple():
    """Se il modello produce giurisprudenza_retrieval_varianti, Fase 1 le
    propaga (max 3) e Fase 3 le passa a retrieve_giurisprudenza_multi."""
    call_count = {"n": 0}
    responses = [
        _phase_json(
            ["RICOSTRUZIONE_FATTO", "QUALIFICAZIONE", "QUESTIONE"],
            questione_retrieval="sequestro preventivo per equivalente",
            giurisprudenza_retrieval_varianti=[
                "sequestro preventivo per equivalente terzo estraneo",
                "sequestro per equivalente buona fede vantaggio terzo",
                "  ",  # voce vuota, deve essere scartata
                "sequestro per equivalente Gubert",
            ],
        ),
        _phase_json(["FONTI_NORMATIVE", "INTERPRETAZIONE"]),
        _phase_json(["GIURISPRUDENZA"]),
        _phase_json(["SUSSUNZIONE", "OBIEZIONI", "CONCLUSIONE"]),
    ]

    async def _generate(**kwargs):
        n = call_count["n"]
        call_count["n"] += 1
        return responses[n] if n < len(responses) else "{}"

    ollama = MagicMock()
    ollama.model = "test"
    ollama.generate = _generate
    agent = AnalystAgent(ollama=ollama)

    pr = MagicMock(spec=PhaseRetriever)
    pr.retrieve_normativa.return_value = []
    pr.retrieve_dottrina.return_value = []
    pr.retrieve_giurisprudenza_multi.return_value = []
    pr.retrieve_massimario.return_value = []

    packet = _make_packet()
    phases = []
    async for phase in agent.analyze_sequential(
        query="test", packet=packet, phase_retriever=pr
    ):
        phases.append(phase)

    phase1 = phases[0]
    # max 3 varianti, voci vuote scartate
    assert phase1.giurisprudenza_retrieval_varianti == [
        "sequestro preventivo per equivalente terzo estraneo",
        "sequestro per equivalente buona fede vantaggio terzo",
        "sequestro per equivalente Gubert",
    ]
    pr.retrieve_giurisprudenza_multi.assert_called_once()
    call_args = pr.retrieve_giurisprudenza_multi.call_args
    assert call_args.args[0] == phase1.giurisprudenza_retrieval_varianti


@pytest.mark.asyncio
async def test_retrieve_giurisprudenza_settore_confidence_numerico(analyst, mock_phase_retriever):
    """Regressione: il 3o argomento di retrieve_giurisprudenza_multi è settore_confidence
    (float), non una seconda query — passare una stringa causava TypeError in
    _effective_filter (str >= float) quando il settore era valorizzato."""
    import inspect

    packet = _make_packet()
    async for _ in analyst.analyze_sequential(
        query="Qual è il confine tra dolo eventuale e colpa cosciente?",  # → settore penale
        packet=packet,
        phase_retriever=mock_phase_retriever,
    ):
        pass

    call = mock_phase_retriever.retrieve_giurisprudenza_multi.call_args
    bound = inspect.signature(PhaseRetriever.retrieve_giurisprudenza_multi).bind(
        mock_phase_retriever, *call.args, **call.kwargs
    )
    bound.apply_defaults()
    assert isinstance(bound.arguments["settore_confidence"], (int, float)), (
        f"settore_confidence deve essere numerico, "
        f"ricevuto {bound.arguments['settore_confidence']!r}"
    )
    assert bound.arguments["settore"] == "penale"
    assert isinstance(bound.arguments["queries"], list)


@pytest.mark.asyncio
async def test_fase3_retrieval_con_settore_non_fallisce(analyst):
    """Regressione: con settore valorizzato e PhaseRetriever reale, il re-query
    giurisprudenza di Fase 3 non deve fallire silenziosamente (TypeError catturato
    dal try in analyst) con fallback alle fonti del packet S2."""
    mock_retriever = MagicMock()
    mock_retriever._search_round.return_value = [
        _make_source("giurisprudenza_cass_requery", "giurisprudenza")
    ]
    pr = PhaseRetriever(mock_retriever)
    packet = _make_packet()

    phases = []
    async for phase in analyst.analyze_sequential(
        query="Qual è il confine tra dolo eventuale e colpa cosciente?",  # → settore penale
        packet=packet,
        phase_retriever=pr,
    ):
        phases.append(phase)

    phase3 = phases[2]
    assert "giurisprudenza_cass_requery" in phase3.sources_used, (
        "Fase 3 deve usare le fonti del re-query, non il fallback al packet S2"
    )
    assert "giurisprudenza_cass_38343_2014" not in phase3.sources_used


@pytest.mark.asyncio
async def test_analyze_sequential_sources_used(analyst, mock_phase_retriever):
    """Fase 2 deve avere sources_used con le fonti del retrieval normativa."""
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="test", packet=packet, phase_retriever=mock_phase_retriever
    ):
        phases.append(phase)

    phase2 = phases[1]
    assert "ART_43_CP_REQUERY" in phase2.sources_used


@pytest.mark.asyncio
async def test_analyze_sequential_fallback_to_packet_sources(analyst):
    """Senza PhaseRetriever, le fasi devono usare le fonti del packet iniziale."""
    packet = _make_packet()
    phases = []
    async for phase in analyst.analyze_sequential(
        query="test", packet=packet, phase_retriever=None
    ):
        phases.append(phase)

    assert len(phases) == 4
    # Fase 2 deve aver usato le fonti normative del packet
    phase2 = phases[1]
    assert "ART_43_CP" in phase2.sources_used


@pytest.mark.asyncio
async def test_analyze_sequential_graceful_on_ollama_error():
    """Se Ollama fallisce, analyze_sequential deve continuare emettendo fasi vuote."""
    ollama = MagicMock()
    ollama.model = "test"

    async def _fail(**kwargs):
        raise ConnectionError("Ollama non disponibile")

    ollama.generate = _fail
    agent = AnalystAgent(ollama=ollama)
    packet = _make_packet()

    phases = []
    async for phase in agent.analyze_sequential(
        query="test", packet=packet, phase_retriever=None
    ):
        phases.append(phase)

    # Deve emettere tutte e 4 le fasi anche se Ollama non risponde
    assert len(phases) == 4
    for phase in phases:
        assert phase.parse_ok is False or phase.sections is not None


# ---------------------------------------------------------------------------
# Test PhaseRetriever
# ---------------------------------------------------------------------------

def test_phase_retriever_retrieve_normativa_calls_search_round():
    """retrieve_normativa() esegue 3 round: normattiva, golden Art. 43, prassi.

    La query criminal ("art. 43") attiva la golden source injection;
    il round prassi è sempre eseguito a supporto della normativa.
    """
    mock_retriever = MagicMock()
    mock_retriever._search_round.return_value = [
        _make_source("ART_1", "normativa")
    ]
    pr = PhaseRetriever(mock_retriever)

    results = pr.retrieve_normativa("dolo eventuale art. 43", top_k=4)

    calls = mock_retriever._search_round.call_args_list
    assert len(calls) == 3, f"Attesi 3 round (main+golden+prassi), eseguiti {len(calls)}"
    # Round principale e golden Art. 43 su corpus normattiva
    assert calls[0].kwargs.get("chunk_filter") == {"corpus": "normattiva"}
    assert calls[1].kwargs.get("chunk_filter") == {"corpus": "normattiva"}
    # Round supplementare su corpus prassi
    assert calls[2].kwargs.get("chunk_filter") == {"corpus": "prassi"}
    assert all(r.source_layer == "normativa" for r in results)


def test_phase_retriever_retrieve_giurisprudenza_calls_search_round():
    """retrieve_giurisprudenza() esegue 2 round: giurisprudenza + golden
    ThyssenKrupp. Il massimario NON è incluso qui — è un round dedicato
    separato (retrieve_massimario), non in concorrenza per gli slot.
    """
    mock_retriever = MagicMock()
    mock_retriever._search_round.return_value = [
        _make_source("CASS_1", "giurisprudenza")
    ]
    pr = PhaseRetriever(mock_retriever)

    results = pr.retrieve_giurisprudenza("ThyssenKrupp dolo eventuale", top_k=4)

    calls = mock_retriever._search_round.call_args_list
    assert len(calls) == 2, f"Attesi 2 round (main+golden), eseguiti {len(calls)}"
    assert calls[0].kwargs.get("chunk_filter") == {"corpus": "giurisprudenza"}
    assert calls[1].kwargs.get("chunk_filter") == {"corpus": "giurisprudenza"}
    # Nessun chunk massimario: la giurisprudenza non lo recupera
    assert all(r.source_layer == "giurisprudenza" for r in results)


def test_retrieve_massimario_round_dedicato():
    """retrieve_massimario() è un round dedicato su corpus=massimario,
    con i risultati taggati source_layer='massimario'."""
    mock_retriever = MagicMock()
    mock_retriever._search_round.return_value = [_make_source("MASS_1", "massimario")]
    pr = PhaseRetriever(mock_retriever)

    results = pr.retrieve_massimario("sequestro per equivalente terzo", top_k=3)

    calls = mock_retriever._search_round.call_args_list
    assert len(calls) == 1
    assert calls[0].kwargs.get("chunk_filter") == {"corpus": "massimario"}
    assert results and all(r.source_layer == "massimario" for r in results)


def test_retrieve_massimario_query_vuota():
    """Query vuota → lista vuota, nessuna chiamata al retriever."""
    mock_retriever = MagicMock()
    pr = PhaseRetriever(mock_retriever)
    assert pr.retrieve_massimario("  ") == []
    mock_retriever._search_round.assert_not_called()


def test_retrieve_giurisprudenza_non_recupera_massimario():
    """La giurisprudenza non deve mai interrogare il corpus massimario:
    nessun round con chunk_filter corpus=massimario."""
    mock_retriever = MagicMock()
    mock_retriever._search_round.return_value = [_make_source("CASS_1", "giurisprudenza")]
    pr = PhaseRetriever(mock_retriever)

    pr.retrieve_giurisprudenza("responsabilità medica", top_k=4)

    filters = [c.kwargs.get("chunk_filter") for c in mock_retriever._search_round.call_args_list]
    assert {"corpus": "massimario"} not in filters


def test_format_source_non_mostra_source_id_grezzo():
    """Il modello non deve mai vedere il source_id reale nel prompt: cita
    SOLO il riferimento FN, risolto al source_id reale lato sistema (vedi
    PhaseResult.ref_map + CitationReviewer._resolve_ref_citations). Elimina
    sia la copia-malfatta (bug storico "1"/"2" copiato come id) sia
    l'allucinazione di id plausibili ma non mostrati."""
    s = _make_source("urn:nir:stato:legge:2020-01-01;1", "giurisprudenza", "Testo.")
    lines = "\n".join(_format_source("F1", s))

    assert "FONTE F1" in lines
    assert "urn:nir:stato:legge:2020-01-01;1" not in lines


def test_assign_refs_progressivo_e_univoco():
    """_assign_refs assegna F{n} progressivi, senza duplicare fonti già viste
    (stesso source_id ripetuto in due liste), e prosegue da `start`."""
    a = _make_source("URN_A", "normativa")
    b = _make_source("URN_B", "normativa")
    c = _make_source("URN_A", "dottrina")  # stesso source_id di a, fonte diversa

    refs, next_i = _assign_refs([a, b])
    assert refs == {"URN_A": "F1", "URN_B": "F2"}
    assert next_i == 3

    # Una seconda lista che riusa lo stesso source_id non duplica il ref se
    # passata nella stessa chiamata; con start esplicito prosegue oltre.
    refs2, next_i2 = _assign_refs([c], start=next_i)
    assert refs2 == {"URN_A": "F3"}  # nuova chiamata = nuovo round, ref nuovo
    assert next_i2 == 4


def test_phase_retriever_empty_query_returns_empty():
    """Con query vuota, PhaseRetriever deve restituire lista vuota senza chiamare il retriever."""
    mock_retriever = MagicMock()
    pr = PhaseRetriever(mock_retriever)

    assert pr.retrieve_normativa("") == []
    assert pr.retrieve_giurisprudenza("  ") == []
    mock_retriever._search_round.assert_not_called()


def test_retrieve_giurisprudenza_multi_query_singola_delega():
    """Con una sola query, retrieve_giurisprudenza_multi deve comportarsi
    esattamente come retrieve_giurisprudenza (retro-compatibilità)."""
    mock_retriever = MagicMock()
    mock_retriever._search_round.return_value = [_make_source("CASS_1", "giurisprudenza")]
    pr = PhaseRetriever(mock_retriever)

    results = pr.retrieve_giurisprudenza_multi(["responsabilità medica"], top_k=4)

    assert len(results) == 1
    assert results[0].doc_id == "CASS_1"


def test_retrieve_giurisprudenza_multi_unisce_e_deduplica():
    """Con più varianti, i risultati devono essere fusi per doc_id e ordinati
    per score decrescente, senza duplicati."""
    mock_retriever = MagicMock()
    pr = PhaseRetriever(mock_retriever)

    def _fake_single(query, top_k=6, settore=None, settore_confidence=0.0):
        if query == "variante A":
            return [_make_source("DOC_1", "giurisprudenza"), _make_source("DOC_2", "giurisprudenza")]
        return [_make_source("DOC_2", "giurisprudenza"), _make_source("DOC_3", "giurisprudenza")]

    pr.retrieve_giurisprudenza = _fake_single  # type: ignore[method-assign]

    results = pr.retrieve_giurisprudenza_multi(["variante A", "variante B"], top_k=6)

    doc_ids = [r.doc_id for r in results]
    assert doc_ids == ["DOC_1", "DOC_2", "DOC_3"], "deduplicato per doc_id, niente DOC_2 ripetuto"


def test_retrieve_giurisprudenza_multi_lista_vuota():
    """Lista di query vuota (o solo stringhe vuote) → [] senza chiamare il retriever."""
    mock_retriever = MagicMock()
    pr = PhaseRetriever(mock_retriever)

    assert pr.retrieve_giurisprudenza_multi([]) == []
    assert pr.retrieve_giurisprudenza_multi(["  ", ""]) == []
    mock_retriever._search_round.assert_not_called()


def test_retrieve_giurisprudenza_multi_rispetta_top_k():
    """Con più varianti che producono più risultati del top_k, il risultato finale
    deve essere troncato a top_k."""
    mock_retriever = MagicMock()
    pr = PhaseRetriever(mock_retriever)

    def _fake_single(query, top_k=6, settore=None, settore_confidence=0.0):
        idx = query[-1]
        return [_make_source(f"DOC_{idx}_{i}", "giurisprudenza") for i in range(4)]

    pr.retrieve_giurisprudenza = _fake_single  # type: ignore[method-assign]

    results = pr.retrieve_giurisprudenza_multi(["v1", "v2"], top_k=3)
    assert len(results) == 3


# ---------------------------------------------------------------------------
# Test full-text nel prompt (AIURA_FULLTEXT_CONTEXT) — anti-regressione 0.2
# ---------------------------------------------------------------------------

_MARKER = "MARCATORE_OLTRE_TRECENTO_CARATTERI"


def _capture_ollama(captured: list[dict]) -> MagicMock:
    """OllamaClient mock che registra i kwargs di ogni generate()."""
    ollama = MagicMock()
    ollama.model = "test"
    responses = [
        _phase_json(
            ["RICOSTRUZIONE_FATTO", "QUALIFICAZIONE", "QUESTIONE"],
            questione_retrieval="clausola penale riduzione giudice",
        ),
        _phase_json(["FONTI_NORMATIVE", "INTERPRETAZIONE"]),
        _phase_json(["GIURISPRUDENZA"]),
        _phase_json(["SUSSUNZIONE", "OBIEZIONI", "CONCLUSIONE"]),
    ]

    async def _generate(**kwargs):
        captured.append(kwargs)
        n = len(captured) - 1
        return responses[n] if n < len(responses) else "{}"

    ollama.generate = _generate
    return ollama


async def test_analyze_sequential_tutte_le_4_fasi_temperature_zero(monkeypatch):
    """
    Regressione Bug #3 (instabilità di verdetto su query equivalenti): prima
    del fix solo la Fase 2 era deterministica (temperature=0.0), mentre
    Fase 1/3/4 usavano il default ~0.10 — varianza pura di sampling che si
    propagava al re-retrieval (Fase 1 genera la QUESTIONE usata in Fase 2/3)
    e alle citazioni finali (Fase 4). Tutte le 4 fasi devono essere
    deterministiche.
    """
    captured: list[dict] = []
    agent = AnalystAgent(ollama=_capture_ollama(captured))

    phases = []
    async for phase in agent.analyze_sequential(
        query="clausola penale", packet=_packet_with_full_text(), phase_retriever=None
    ):
        phases.append(phase)

    assert len(captured) == 4
    assert [kwargs["temperature"] for kwargs in captured] == [0.0, 0.0, 0.0, 0.0]


def _packet_with_full_text() -> ResearchPacket:
    """Packet con full_text lungo: il marcatore compare solo dopo il 300o char."""
    norm = _make_source("ART_1382_CC", "normativa", snippet="A" * 300)
    norm.full_text = "B" * 320 + f" {_MARKER} " + "C" * 400
    giuri = _make_source("giurisprudenza_cass_1_2020", "giurisprudenza", snippet="D" * 300)
    giuri.full_text = "E" * 320 + f" {_MARKER}_GIURI " + "F" * 400
    return ResearchPacket(
        query_original="clausola penale",
        query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
        sources=[norm, giuri],
        retrieval_confidence="HIGH",
    )


async def test_prompt_normativa_contiene_testo_oltre_300_char(monkeypatch):
    """Con il flag attivo, il prompt della fase NORMATIVA contiene testo
    della fonte oltre il 300o carattere (non solo lo snippet)."""
    monkeypatch.setenv("AIURA_FULLTEXT_CONTEXT", "1")
    captured: list[dict] = []
    agent = AnalystAgent(ollama=_capture_ollama(captured))

    async for _ in agent.analyze_sequential(
        query="clausola penale", packet=_packet_with_full_text(), phase_retriever=None
    ):
        pass

    prompt_fase2 = captured[1]["prompt"]
    assert _MARKER in prompt_fase2, (
        "il prompt NORMATIVA deve contenere il full_text della fonte, non lo snippet"
    )


async def test_prompt_flag_off_usa_snippet(monkeypatch):
    """Con AIURA_FULLTEXT_CONTEXT=0 il comportamento storico (snippet) e ripristinato."""
    monkeypatch.setenv("AIURA_FULLTEXT_CONTEXT", "0")
    captured: list[dict] = []
    agent = AnalystAgent(ollama=_capture_ollama(captured))

    async for _ in agent.analyze_sequential(
        query="clausola penale", packet=_packet_with_full_text(), phase_retriever=None
    ):
        pass

    prompt_fase2 = captured[1]["prompt"]
    assert _MARKER not in prompt_fase2
    assert "A" * 200 in prompt_fase2  # snippet presente


async def test_prompt_anti_overflow_token_budget(monkeypatch):
    """Token totali (system+prompt) di ogni fase <= n_ctx - max_tokens fase,
    anche con fonti dal full_text enorme."""
    import tiktoken
    from aiura_legal.agents.analyst import _llm_settings

    monkeypatch.setenv("AIURA_FULLTEXT_CONTEXT", "1")
    enc = tiktoken.get_encoding("cl100k_base")

    huge = "parola giuridica ricorrente " * 4000  # >> budget per fonte

    def _huge_source(doc_id: str, layer: str) -> SearchResult:
        s = _make_source(doc_id, layer, snippet="x" * 300)
        s.full_text = huge
        return s

    pr = MagicMock(spec=PhaseRetriever)
    pr.retrieve_normativa.return_value = [
        _huge_source(f"NORM_{i}", "normativa") for i in range(6)
    ]
    pr.retrieve_dottrina.return_value = [
        _huge_source(f"DOTT_{i}", "dottrina") for i in range(4)
    ]
    pr.retrieve_giurisprudenza_multi.return_value = [
        _huge_source(f"giurisprudenza_{i}", "giurisprudenza") for i in range(6)
    ]
    pr.retrieve_massimario.return_value = [
        _huge_source(f"massimario_{i}", "massimario") for i in range(3)
    ]

    captured: list[dict] = []
    agent = AnalystAgent(ollama=_capture_ollama(captured))

    async for _ in agent.analyze_sequential(
        query="responsabilita contrattuale", packet=_packet_with_full_text(),
        phase_retriever=pr,
    ):
        pass

    assert len(captured) == 4
    for n, kwargs in enumerate(captured, 1):
        total = len(enc.encode(kwargs.get("system", ""))) + len(enc.encode(kwargs["prompt"]))
        budget = _llm_settings.llm_n_ctx - kwargs["max_tokens"]
        assert total <= budget, (
            f"fase {n}: prompt {total} token > budget {budget} "
            f"(n_ctx={_llm_settings.llm_n_ctx} - max_tokens={kwargs['max_tokens']})"
        )


# ---------------------------------------------------------------------------
# Test classificazione istituto — fallback LLM quando il match lessicale fallisce
# ---------------------------------------------------------------------------

class _FakeIstituto:
    def __init__(self, id_, norme_urn=(), settore="penale"):
        self.id = id_
        self.norme_urn = norme_urn
        self.settore = settore
        self.sentenze_pilota = ()


class _FakeRegistryNoLexicalMatch:
    """match_query non trova mai nulla — forza il path del fallback LLM."""
    def match_query(self, text, top_k=3):
        return []

    def by_id(self, istituto_id):
        if istituto_id == "istituto_valido_test":
            return _FakeIstituto("istituto_valido_test", norme_urn=("urn:test:art1",))
        return None

    def vocabolario(self):
        return [("istituto_valido_test", "Istituto Valido Test")]


def _mock_ollama_with_istituto_id(istituto_id_value) -> MagicMock:
    ollama = MagicMock()
    ollama.model = "qwen2.5:7b-test"
    call_count = {"n": 0}

    def _fase1_json():
        data = {
            "analysis_sections": [
                {"step": "RICOSTRUZIONE_FATTO", "content": "x", "citations": []},
                {"step": "QUALIFICAZIONE", "content": "x", "citations": []},
                {"step": "QUESTIONE", "content": "x", "citations": []},
            ],
            "overall_confidence": "MEDIUM",
            "gaps": [],
            "questione_retrieval": "questione test",
            "qualificazione_retrieval": "qualificazione test",
        }
        if istituto_id_value is not None:
            data["istituto_id"] = istituto_id_value
        return json.dumps(data)

    responses = [
        _fase1_json(),
        _phase_json(["FONTI_NORMATIVE", "INTERPRETAZIONE"]),
        _phase_json(["GIURISPRUDENZA"]),
        _phase_json(["SUSSUNZIONE", "OBIEZIONI", "CONCLUSIONE"]),
    ]

    async def _generate(**kwargs):
        n = call_count["n"]
        call_count["n"] += 1
        return responses[n] if n < len(responses) else "{}"

    ollama.generate = _generate
    return ollama


@pytest.mark.asyncio
async def test_istituto_fallback_llm_usato_se_lessicale_fallisce(mock_phase_retriever):
    """Se match_query() non trova nulla, l'istituto_id prodotto dal modello in
    Fase 1 (stessa chiamata, nessun round-trip aggiuntivo) viene usato come
    fallback, validato contro il registro, e la sua norma cardine iniettata."""
    agent = AnalystAgent(ollama=_mock_ollama_with_istituto_id("istituto_valido_test"))

    with patch("aiura_legal.agents.analyst.get_registry", return_value=_FakeRegistryNoLexicalMatch()), \
         patch(
             "aiura_legal.agents.analyst.fetch_sources_by_source_id",
             return_value=[_make_source("urn:test:art1", "normativa", "Norma cardine iniettata.")],
         ) as mock_fetch:
        phases = []
        async for phase in agent.analyze_sequential(
            query="test", packet=_make_packet(), phase_retriever=mock_phase_retriever
        ):
            phases.append(phase)

    mock_fetch.assert_called_once()
    called_urns = mock_fetch.call_args[0][0]
    assert list(called_urns) == ["urn:test:art1"]

    phase2 = phases[1]
    assert "urn:test:art1" in phase2.sources_used


@pytest.mark.asyncio
async def test_istituto_fallback_llm_ignora_id_non_nel_vocabolario(mock_phase_retriever):
    """Un istituto_id inventato dal modello (non presente nel registro) viene
    ignorato — mai fidarsi di un id fuori dal vocabolario chiuso."""
    agent = AnalystAgent(ollama=_mock_ollama_with_istituto_id("id_inventato_non_esistente"))

    with patch("aiura_legal.agents.analyst.get_registry", return_value=_FakeRegistryNoLexicalMatch()), \
         patch("aiura_legal.agents.analyst.fetch_sources_by_source_id") as mock_fetch:
        async for _ in agent.analyze_sequential(
            query="test", packet=_make_packet(), phase_retriever=mock_phase_retriever
        ):
            pass

    mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_istituto_fallback_llm_non_usato_se_null(mock_phase_retriever):
    """istituto_id assente/null → nessun fallback, comportamento invariato."""
    agent = AnalystAgent(ollama=_mock_ollama_with_istituto_id(None))

    with patch("aiura_legal.agents.analyst.get_registry", return_value=_FakeRegistryNoLexicalMatch()), \
         patch("aiura_legal.agents.analyst.fetch_sources_by_source_id") as mock_fetch:
        async for _ in agent.analyze_sequential(
            query="test", packet=_make_packet(), phase_retriever=mock_phase_retriever
        ):
            pass

    mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_vocabolario_iniettato_nel_prompt_fase1():
    """Il blocco VOCABOLARIO ISTITUTI compare nel prompt di Fase 1 quando il
    registro ha voci, con l'id e la label esatti."""
    captured: list[dict] = []

    def _capture_ollama(store):
        ollama = MagicMock()
        ollama.model = "qwen2.5:7b-test"

        async def _generate(**kwargs):
            store.append(kwargs)
            return "{}"

        ollama.generate = _generate
        return ollama

    agent = AnalystAgent(ollama=_capture_ollama(captured))

    with patch("aiura_legal.agents.analyst.get_registry", return_value=_FakeRegistryNoLexicalMatch()):
        async for _ in agent.analyze_sequential(
            query="test", packet=_make_packet(), phase_retriever=None
        ):
            pass

    prompt_f1 = captured[0]["prompt"]
    assert "VOCABOLARIO ISTITUTI" in prompt_f1
    assert "istituto_valido_test: Istituto Valido Test" in prompt_f1
