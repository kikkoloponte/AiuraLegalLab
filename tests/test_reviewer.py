"""
Test Citation Reviewer [S5] — rule-based, zero LLM.
"""
import pytest
from datetime import date
from aiura_legal.core.reviewer.reviewer import CitationReviewer, ReviewResult
from aiura_legal.core.types import ResearchPacket, QueryIntent, SearchResult


def _make_packet(*source_ids: str, **metadata_overrides) -> ResearchPacket:
    sources = [
        SearchResult(
            doc_id=sid,
            score=1.0,
            snippet="...",
            source_id=sid,
            metadata=metadata_overrides.get(sid, {}),
        )
        for sid in source_ids
    ]
    return ResearchPacket(
        query_original="test query",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=sources,
    )


@pytest.fixture
def reviewer():
    return CitationReviewer()


# ------------------------------------------------------------------
# extract_citations
# ------------------------------------------------------------------

def test_extract_cc_art(reviewer):
    text = "Come da CC_ART_1218 il debitore risponde."
    cits = reviewer.extract_citations(text)
    assert "CC_ART_1218" in cits

def test_extract_cass(reviewer):
    text = "Vedi CASS_CIV_2023_12345 e CASS_PEN_2022_999."
    cits = reviewer.extract_citations(text)
    assert "CASS_CIV_2023_12345" in cits
    assert "CASS_PEN_2022_999" in cits

def test_extract_cedu(reviewer):
    cits = reviewer.extract_citations("Cfr. CEDU_VIOLA_2020.")
    assert "CEDU_VIOLA_2020" in cits

def test_extract_cost(reviewer):
    cits = reviewer.extract_citations("COST_2021_80.")
    assert "COST_2021_80" in cits

def test_extract_no_citations(reviewer):
    cits = reviewer.extract_citations("Testo senza riferimenti.")
    assert cits == []

def test_extract_deduplicates(reviewer):
    text = "CC_ART_1218 e ancora CC_ART_1218."
    cits = reviewer.extract_citations(text)
    assert cits.count("CC_ART_1218") == 1


# ------------------------------------------------------------------
# PASS — tutte le citazioni nel Packet
# ------------------------------------------------------------------

def test_pass_all_grounded(reviewer):
    packet = _make_packet("CC_ART_1218", "CC_ART_1453")
    result = reviewer.verify("Ai sensi CC_ART_1218 e CC_ART_1453.", packet)
    assert result.verdict == "PASS"
    assert result.action == "DELIVER"
    assert result.ungrounded_citations == []
    assert result.checks["citation_grounding"] == "PASS"


def test_pass_no_citations(reviewer):
    packet = _make_packet("CC_ART_1218")
    result = reviewer.verify("Testo senza citazioni formali.", packet)
    assert result.verdict == "PASS"


# ------------------------------------------------------------------
# FAIL — citazione non nel Packet
# ------------------------------------------------------------------

def test_fail_ungrounded_citation(reviewer):
    packet = _make_packet("CC_ART_1218")
    result = reviewer.verify("Vedi CC_ART_999 per dettagli.", packet)
    assert result.verdict == "FAIL"
    assert "CC_ART_999" in result.ungrounded_citations
    assert result.action == "RE_RETRIEVAL"
    assert result.checks["citation_grounding"] == "FAIL"


def test_fail_multiple_ungrounded(reviewer):
    packet = _make_packet("CC_ART_1218")
    result = reviewer.verify("CC_ART_999 e CASS_CIV_2020_000 non nel packet.", packet)
    assert result.verdict == "FAIL"
    assert len(result.ungrounded_citations) == 2


# ------------------------------------------------------------------
# WARN — norma scaduta
# ------------------------------------------------------------------

def test_warn_expired_norm(reviewer):
    packet = _make_packet("CC_ART_1218", **{"CC_ART_1218": {"valid_to": "2020-01-01"}})
    result = reviewer.verify(
        "Ai sensi CC_ART_1218.",
        packet,
        reference_date=date(2024, 1, 1),
    )
    assert result.verdict == "WARN"
    assert result.checks["temporal_validity"] == "WARN"
    assert result.action == "DELIVER"


# ------------------------------------------------------------------
# FAIL CRITICO — norma incostituzionale
# ------------------------------------------------------------------

def test_fail_unconstitutional(reviewer):
    packet = _make_packet(
        "CC_ART_1218",
        **{"CC_ART_1218": {"status": "INCOSTITUZIONALE"}},
    )
    result = reviewer.verify("Ai sensi CC_ART_1218.", packet)
    assert result.verdict == "FAIL"
    assert result.action == "BLOCK"
    assert result.checks["constitutionality"] == "FAIL_CRITICO"
    assert "CC_ART_1218" in result.warnings[0]


# ------------------------------------------------------------------
# Case insensitivity
# ------------------------------------------------------------------

def test_case_insensitive_matching(reviewer):
    packet = _make_packet("CC_ART_1218")
    result = reviewer.verify("Vedi cc_art_1218.", packet)
    assert result.verdict == "PASS"


# ------------------------------------------------------------------
# URN Normattiva — nuovi test dopo aggiunta pattern URN
# ------------------------------------------------------------------

def test_extract_urn_normattiva(reviewer):
    """extract_citations deve trovare source_id in formato URN."""
    text = "Ai sensi urn:nir:stato:regio.decreto:1942-03-16;262~art1218."
    cits = reviewer.extract_citations(text)
    assert any("urn:nir:stato:regio.decreto:1942-03-16;262~art1218" in c for c in cits)


def test_pass_urn_in_packet(reviewer):
    """URN presente nel packet → PASS."""
    urn = "urn:nir:stato:regio.decreto:1942-03-16;262~art1218"
    packet = _make_packet(urn)
    result = reviewer.verify(f"Vedi {urn}.", packet)
    assert result.verdict == "PASS"
    assert result.ungrounded_citations == []


def test_fail_urn_not_in_packet(reviewer):
    """URN NON presente nel packet → FAIL (Citation Contract violato)."""
    urn_in_packet   = "urn:nir:stato:regio.decreto:1942-03-16;262~art1218"
    urn_hallucinated = "urn:nir:stato:regio.decreto:1930-10-19;1398~art603-ter"
    packet = _make_packet(urn_in_packet)
    # Il testo (o i source_id delle analysis_sections) contiene un URN esterno al packet
    result = reviewer.verify(f"Vedi {urn_in_packet} e {urn_hallucinated}.", packet)
    assert result.verdict == "FAIL"
    assert result.action == "RE_RETRIEVAL"
    assert any("art603-ter" in u for u in result.ungrounded_citations)


def test_fail_urn_in_analysis_sections_not_in_packet(reviewer):
    """
    Simula il caso reale: l'orchestratore appende i source_id delle
    analysis_sections al testo da verificare. Se uno è fuori packet → FAIL.
    """
    urn_packet = "urn:nir:stato:regio.decreto:1930-10-19;1398~art640"
    urn_hallucinated = "urn:nir:stato:regio.decreto:1930-10-19;1398~art603-ter"
    packet = _make_packet(urn_packet)

    # Simula text_to_review = answer + "\n" + section_citation_ids
    text = f"L'art. 640 punisce la truffa.\n{urn_packet} {urn_hallucinated}"
    result = reviewer.verify(text, packet)
    assert result.verdict == "FAIL"
    assert any("art603-ter" in u for u in result.ungrounded_citations)


# ------------------------------------------------------------------
# Grounding giurisprudenziale — sentenze
# ------------------------------------------------------------------

def _make_packet_with_sentenza(sentenza_id: str) -> ResearchPacket:
    sources = [
        SearchResult(
            doc_id=sentenza_id,
            score=1.0,
            snippet="La Cassazione ha stabilito...",
            source_id=sentenza_id,
            metadata={},
        )
    ]
    return ResearchPacket(
        query_original="test",
        query_intent=QueryIntent.GIURISPRUDENZA_SEARCH,
        sources=sources,
    )


def test_sentenza_grounded_nel_packet():
    reviewer = CitationReviewer()
    sid = "ebab1dbfae1b7d10"
    packet = _make_packet_with_sentenza(sid)
    result = reviewer.verify(f"Come da sentenza {sid}, il principio è.", packet)
    assert result.checks.get("jurisprudence_grounding") == "PASS"
    assert sid not in result.ungrounded_citations


def test_sentenza_non_nel_packet_fail():
    reviewer = CitationReviewer()
    sid = "ebab1dbfae1b7d10"
    packet = _make_packet("CC_ART_1218")
    result = reviewer.verify(f"La sentenza {sid} afferma.", packet)
    assert result.verdict == "FAIL"
    assert result.action == "RE_RETRIEVAL"
    assert sid in result.ungrounded_citations


def test_norma_assente_in_normattiva_warn():
    from datetime import date
    from aiura_legal.jurisprudence.graph_builder import JurisprudenceGraphBuilder
    from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        builder = JurisprudenceGraphBuilder(Path(tmp) / "g.json")
        doc = JurisprudenceDocument(
            organo=OrganoGiudicante.CASSAZIONE,
            numero="1",
            anno=2024,
            data_deposito=date(2024, 1, 1),
            sezione="",
            materia="",
            massima="",
            motivazione="",
            dispositivo="",
            norme_citate=["urn:nir:stato:codice.civile:art9999"],
        )
        builder.add_document(doc)

        normattiva_urns = {"urn:nir:stato:codice.civile:art2043"}  # art9999 assente
        reviewer = CitationReviewer(jurisprudence_graph=builder, normattiva_urns=normattiva_urns)

        sid = doc.id
        packet = _make_packet_with_sentenza(sid)
        result = reviewer.verify(f"Vedi sentenza {sid}.", packet)

        assert result.verdict == "WARN"
        assert any("art9999" in w for w in result.warnings)


def test_norma_presente_in_normattiva_pass():
    from datetime import date
    from aiura_legal.jurisprudence.graph_builder import JurisprudenceGraphBuilder
    from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        builder = JurisprudenceGraphBuilder(Path(tmp) / "g.json")
        doc = JurisprudenceDocument(
            organo=OrganoGiudicante.CASSAZIONE,
            numero="2",
            anno=2024,
            data_deposito=date(2024, 1, 1),
            sezione="",
            materia="",
            massima="",
            motivazione="",
            dispositivo="",
            norme_citate=["urn:nir:stato:codice.civile:art2043"],
        )
        builder.add_document(doc)

        normattiva_urns = {"urn:nir:stato:codice.civile:art2043"}  # presente
        reviewer = CitationReviewer(jurisprudence_graph=builder, normattiva_urns=normattiva_urns)

        sid = doc.id
        packet = _make_packet_with_sentenza(sid)
        result = reviewer.verify(f"Vedi sentenza {sid}.", packet)

        assert result.verdict == "PASS"
        assert not any("NORMA_NOT_IN_NORMATTIVA" in v for v in result.checks.values())


# ------------------------------------------------------------------
# Grounding sub-chunk Fase 1 (motivazione_{i:03d})
# ------------------------------------------------------------------

def _make_packet_with_sub_chunk(hex16: str, chunk_idx: int = 1) -> ResearchPacket:
    """Packet con un sub-chunk motivazione Fase 1."""
    chunk_id = f"{hex16}_motivazione_{chunk_idx:03d}"
    sources = [
        SearchResult(
            doc_id=chunk_id,
            score=1.0,
            snippet="Testo della motivazione...",
            source_id=chunk_id,
            metadata={"corpus": "giurisprudenza", "chunk_type": "motivazione", "chunk_index": chunk_idx},
        )
    ]
    return ResearchPacket(
        query_original="test",
        query_intent=QueryIntent.GIURISPRUDENZA_SEARCH,
        sources=sources,
    )


def test_grounding_subchunk_motivazione_pass():
    """PASS: risposta cita hex16, packet contiene {hex16}_motivazione_001."""
    reviewer = CitationReviewer()
    hex16 = "ebab1dbfae1b7d10"
    packet = _make_packet_with_sub_chunk(hex16, chunk_idx=1)
    # Il LLM cita solo l'hex16 della sentenza (non il chunk specifico)
    result = reviewer.verify(f"Come da sentenza {hex16}, il principio e' valido.", packet)
    assert result.checks.get("jurisprudence_grounding") == "PASS"
    assert hex16 not in result.ungrounded_citations


def test_grounding_subchunk_motivazione_fail_hex_assente():
    """FAIL: risposta cita hex16 diverso da quello nel packet."""
    reviewer = CitationReviewer()
    hex16_in_packet = "ebab1dbfae1b7d10"
    hex16_inventato = "ffffffffffffffff"
    packet = _make_packet_with_sub_chunk(hex16_in_packet, chunk_idx=0)
    result = reviewer.verify(f"La sentenza {hex16_inventato} stabilisce.", packet)
    assert result.verdict == "FAIL"
    assert hex16_inventato in result.ungrounded_citations


def test_grounding_multipli_subchunk_stessa_sentenza():
    """PASS: packet con chunk 000 e 002 della stessa sentenza, risposta cita hex16."""
    reviewer = CitationReviewer()
    hex16 = "ebab1dbfae1b7d10"
    sources = [
        SearchResult(
            doc_id=f"{hex16}_motivazione_000",
            score=1.0, snippet="...", source_id=f"{hex16}_motivazione_000",
            metadata={"corpus": "giurisprudenza"},
        ),
        SearchResult(
            doc_id=f"{hex16}_motivazione_002",
            score=0.8, snippet="...", source_id=f"{hex16}_motivazione_002",
            metadata={"corpus": "giurisprudenza"},
        ),
    ]
    packet = ResearchPacket(
        query_original="test",
        query_intent=QueryIntent.GIURISPRUDENZA_SEARCH,
        sources=sources,
    )
    result = reviewer.verify(f"Come da sentenza {hex16}.", packet)
    assert result.checks.get("jurisprudence_grounding") == "PASS"


# ------------------------------------------------------------------
# Normalizzazione citazioni "numero/anno" (vedi GitHub issue: query
# dottrinale reale dove l'LLM cita "29164/2021" invece dell'hex16
# mostrato nel prompt — il reviewer bloccava una risposta corretta
# per un problema di formato, non di grounding reale)
# ------------------------------------------------------------------

def test_numero_anno_risolto_da_research_packet():
    """PASS: citazione 'numero/anno' risolta a una fonte nel Research Packet."""
    reviewer = CitationReviewer()
    hex16 = "785e6993d6e7272f"
    sources = [
        SearchResult(
            doc_id=hex16, score=1.0, snippet="...", source_id=hex16,
            metadata={"corpus": "giurisprudenza", "numero": "29164", "anno": "2021"},
        ),
    ]
    packet = ResearchPacket(
        query_original="test", query_intent=QueryIntent.GIURISPRUDENZA_SEARCH, sources=sources,
    )
    result = reviewer.verify(
        "...", packet, structured_cited_ids=["29164/2021"],
    )
    assert result.verdict == "PASS"
    assert "29164/2021" not in result.ungrounded_citations


def test_numero_anno_risolto_da_phase_sources_metadata():
    """PASS: citazione 'numero/anno' risolta tramite le fonti del PhaseRetriever
    (Fase 3 giurisprudenza), non presenti nel packet S2 iniziale."""
    reviewer = CitationReviewer()
    packet = _make_packet()  # packet S2 vuoto
    result = reviewer.verify(
        "...",
        packet,
        structured_cited_ids=["29164/2021"],
        phase_sources_metadata={
            "785e6993d6e7272f": {"corpus": "giurisprudenza", "numero": "29164", "anno": "2021"},
        },
    )
    assert result.verdict == "PASS"
    assert "29164/2021" not in result.ungrounded_citations


def test_numero_anno_non_risolvibile_resta_ungrounded():
    """FAIL: citazione 'numero/anno' che non corrisponde a nessuna fonte recuperata
    resta ungrounded — la normalizzazione non bypassa il Citation Contract."""
    reviewer = CitationReviewer()
    packet = _make_packet()
    result = reviewer.verify(
        "...", packet, structured_cited_ids=["99999/1999"],
    )
    assert result.verdict == "FAIL"


# ------------------------------------------------------------------
# Claim relevance — citazione formalmente grounded ma topicamente
# scorrelata dal claim (Bug #1: hallucination "a posteriori")
# ------------------------------------------------------------------

def _make_packet_with_text(source_id: str, full_text: str) -> ResearchPacket:
    sources = [
        SearchResult(
            doc_id=source_id,
            score=1.0,
            snippet=full_text[:200],
            source_id=source_id,
            full_text=full_text,
            metadata={},
        )
    ]
    return ResearchPacket(
        query_original="test",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=sources,
    )


def test_warn_claim_topicamente_scorrelato(reviewer):
    """
    WARN (non FAIL): il source_id è realmente nel packet (grounded), ma il
    claim associato non condivide vocabolario col testo della fonte — sintomo
    del bug osservato in produzione (citazione corretta ma irrilevante).
    """
    packet = _make_packet_with_text(
        "CC_ART_1453",
        "La risoluzione del contratto per inadempimento di una delle parti "
        "può essere domandata giudizialmente quando una delle parti non "
        "esegue le sue obbligazioni contrattuali.",
    )
    result = reviewer.verify(
        "Il termine di prescrizione decennale si applica ai diritti reali.",
        packet,
        structured_cited_ids=["CC_ART_1453"],
        cited_claims=[{
            "source_id": "CC_ART_1453",
            "claim": "il termine di prescrizione decennale per i diritti reali immobiliari",
        }],
    )
    assert result.checks["claim_relevance"] == "WARN"
    assert any("CC_ART_1453" in c for c in result.irrelevant_citations)
    assert result.verdict == "WARN"
    assert result.action == "DELIVER"  # WARN non blocca, solo segnala


def test_pass_claim_pertinente_alla_fonte(reviewer):
    """PASS: il claim condivide vocabolario di contenuto con la fonte citata."""
    packet = _make_packet_with_text(
        "CC_ART_1453",
        "La risoluzione del contratto per inadempimento di una delle parti "
        "può essere domandata giudizialmente quando una delle parti non "
        "esegue le sue obbligazioni contrattuali.",
    )
    result = reviewer.verify(
        "Si applica la risoluzione del contratto.",
        packet,
        structured_cited_ids=["CC_ART_1453"],
        cited_claims=[{
            "source_id": "CC_ART_1453",
            "claim": "risoluzione del contratto per inadempimento contrattuale",
        }],
    )
    assert result.checks["claim_relevance"] == "PASS"
    assert result.irrelevant_citations == []
    assert result.verdict == "PASS"


def test_claim_relevance_non_valuta_citazioni_ungrounded(reviewer):
    """Una citazione già ungrounded non viene anche segnalata da claim_relevance
    (eviterebbe doppio conteggio dello stesso problema sotto due check diversi)."""
    packet = _make_packet("CC_ART_1218")
    result = reviewer.verify(
        "Vedi CC_ART_999.",
        packet,
        structured_cited_ids=["CC_ART_999"],
        cited_claims=[{"source_id": "CC_ART_999", "claim": "qualcosa di completamente scorrelato"}],
    )
    assert result.checks["citation_grounding"] == "FAIL"
    assert result.irrelevant_citations == []


def test_claim_relevance_claim_troppo_corto_non_valutato(reviewer):
    """Claim troppo corti (poco token di contenuto) non sono valutabili in modo
    affidabile col semplice overlap lessicale — nessun falso positivo."""
    packet = _make_packet_with_text(
        "CC_ART_1453",
        "Testo completamente diverso su tutt'altro argomento giuridico.",
    )
    result = reviewer.verify(
        "...",
        packet,
        structured_cited_ids=["CC_ART_1453"],
        cited_claims=[{"source_id": "CC_ART_1453", "claim": "risoluzione"}],
    )
    assert result.checks["claim_relevance"] == "PASS"


def test_claim_relevance_nessun_testo_fonte_non_valutato(reviewer):
    """Se la fonte non ha testo disponibile (full_text/snippet vuoti), il check
    non può valutare la pertinenza e non genera falsi positivi."""
    packet = ResearchPacket(
        query_original="test",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=[
            SearchResult(doc_id="CC_ART_1453", score=1.0, snippet="", source_id="CC_ART_1453"),
        ],
    )
    result = reviewer.verify(
        "...",
        packet,
        structured_cited_ids=["CC_ART_1453"],
        cited_claims=[{"source_id": "CC_ART_1453", "claim": "una affermazione qualunque non verificabile"}],
    )
    assert result.checks["claim_relevance"] == "PASS"
