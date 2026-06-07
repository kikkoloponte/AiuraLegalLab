# Piano di Implementazione — Jurisprudence Pipeline
**Data:** 2026-06-01  
**Spec di riferimento:** `2026-06-01-jurisprudence-pipeline-design.md`

---

## Fasi e task

### Fase 1 — Modello dati e struttura modulo
1. Crea `aiura_legal/jurisprudence/__init__.py`
2. Crea `aiura_legal/jurisprudence/models.py`
   - `OrganoGiudicante` enum
   - `SourceChannel` enum
   - `RawSentenza` dataclass
   - `JurisprudenceDocument` dataclass
3. Aggiungi test `tests/test_jurisprudence_models.py` — verifica id hashing, campi obbligatori

### Fase 2 — Parser
4. Crea `aiura_legal/jurisprudence/parser.py`
   - `parse_html(raw: RawSentenza) -> JurisprudenceDocument`
   - `parse_pdf(raw: RawSentenza) -> JurisprudenceDocument`
   - estrazione regex massima/motivazione/dispositivo
   - dipendenze: `beautifulsoup4`, `pdfplumber`
5. Aggiungi test `tests/test_jurisprudence_parser.py` — fixture HTML/PDF sintetici

### Fase 3 — Scraper base e 4 implementazioni
6. Crea `aiura_legal/jurisprudence/scrapers/__init__.py`
7. Crea `aiura_legal/jurisprudence/scrapers/base.py` — `BaseScraper` ABC
8. Crea `aiura_legal/jurisprudence/scrapers/cassazione.py`
9. Crea `aiura_legal/jurisprudence/scrapers/giustizia_amm.py`
10. Crea `aiura_legal/jurisprudence/scrapers/corte_cost.py`
11. Crea `aiura_legal/jurisprudence/scrapers/corte_conti.py`
12. Test per ogni scraper con `respx` (mock HTTP) e fixture HTML/PDF

### Fase 4 — Anonymizer bridge
13. Crea `aiura_legal/jurisprudence/anonymizer_bridge.py`
    - chiama anonymizer esistente
    - no-op per `SourceChannel.SCRAPING`
    - scrive in `pii_vault` per `SourceChannel.UPLOAD_STUDIO`
14. Test con mongomock-motor

### Fase 5 — Coordinator
15. Crea `aiura_legal/jurisprudence/coordinator.py`
    - dedup per id su MongoDB
    - genera 3 `Document` per `JurisprudenceDocument`
    - chiama `bm25_retriever.add_documents_batch()`
    - chiama `vector_retriever.add_documents_batch()`
    - aggiorna `sync_state` per fonte
16. Test idempotenza con mongomock-motor

### Fase 6 — Graph builder
17. Crea `aiura_legal/jurisprudence/graph_builder.py`
    - aggiunge nodi `sentenza` al grafo NetworkX esistente
    - archi `interpreta`, `cita`, `applicata_in`
    - risolve URN norme verso `normattiva_docs`
18. Test grafo sintetico (5 norme + 3 sentenze)

### Fase 7 — Estensione Reviewer S5
19. Aggiorna `aiura_legal/core/reviewer/` per verificare:
    - sentenza nel `ResearchPacket`
    - norma citata esiste in `normattiva_docs`
    - coerenza grafo vs draft
20. Test blocco citazione non-grounded e gap norma mancante

### Fase 8 — Batch script e endpoint upload
21. Crea `scripts/sync_jurisprudence.py` — orchestrazione batch completa
22. Aggiungi endpoint `POST /jurisprudence/upload` in `aiura_legal/api/`
23. Test end-to-end con mongomock-motor

---

## Dipendenze Python da aggiungere
- `beautifulsoup4`
- `pdfplumber`
- `respx` (solo dev/test)

## Ordine consigliato
Le fasi sono sequenziali: ogni fase dipende dalla precedente. Fase 6 (grafo) può procedere in parallelo con Fase 7 (Reviewer) dopo che Fase 5 è completata.
