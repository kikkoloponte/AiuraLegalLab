# LexAgent — Architettura della Piattaforma AI Legale Multi-Tenant

>
> Documento di progettazione architetturale — sessione di reasoning step-by-step  

> Stato: **Work in Progress** — STEP 0→5 completati + Deep Dive PII  

> Ultimo aggiornamento: maggio 2026
>

---

## Indice

1. [Vision e Obiettivi](#1-vision-e-obiettivi)
2. [Stack Tecnologico](#2-stack-tecnologico)
3. [STEP 0 — Tassonomia KB vs LLM](#3-step-0--tassonomia-kb-vs-llm)
4. [STEP 1 — Modellazione Grafo Legale e Pipeline di Ingestione](#4-step-1--modellazione-grafo-legale-e-pipeline-di-ingestione)
5. [STEP 2 — Architettura Multi-Agente](#5-step-2--architettura-multi-agente)
6. [STEP 3 — Ricerca Ibrida (Grafo + Vector + BM25)](#6-step-3--ricerca-ibrida-grafo--vector--bm25)
7. [STEP 4 — File System Distribuito e Multi-tenant](#7-step-4--file-system-distribuito-e-multi-tenant)
8. [STEP 5 — Diagrammi PlantUML](#8-step-5--diagrammi-plantuml)
9. [Deep Dive — Modulo di Anonimizzazione PII](#9-deep-dive--modulo-di-anonimizzazione-pii)
10. [Decisioni Architetturali Chiave](#10-decisioni-architetturali-chiave)
11. [Metriche e Target di Performance](#11-metriche-e-target-di-performance)
12. [Roadmap e Next Steps](#12-roadmap-e-next-steps)


---

## 1. Vision e Obiettivi

### 1.1 Descrizione del Sistema

LexAgent è una piattaforma di assistenza al ragionamento legale per studi legali multi-tenant. Il sistema combina tre componenti di retrieval ibrido (Knowledge Graph, Dense Retrieval vettoriale, Sparse Retrieval BM25) con un sistema multi-agente basato su LLM locali leggeri (7-8B), garantendo privacy robusta e operatività offline completa.

### 1.2 Requisiti Chiave


| Requisito            | Vincolo                         | Soluzione Adottata                                                    |
|----------------------|---------------------------------|-----------------------------------------------------------------------|
| Privacy dati clienti | Dati non escono mai dalla LAN   | LLM locali, vault PII cifrato, no API esterne per documenti sensibili |
| Multi-tenancy        | Isolamento completo tra studi   | Defense in depth: Mirage path ACL + HMAC token                        |
| Hardware leggero     | Laptop medio avvocato           | Ollama + modelli GGUF Q4 7-8B, un solo modello in VRAM                |
| Accuratezza legale   | Zero allucinazioni su citazioni | Citation Contract a 3 livelli, Reviewer rule-based                    |
| Modularità          | Qualsiasi branca del diritto    | Ontologia core + moduli verticali installabili                        |
| Offline-first        | Opera senza internet            | KB distribuita localmente, sync pull-based                            |


### 1.3 Due Workflow Principali

```
WORKFLOW A — Q&A Interattiva  
Avvocato digita query → clarification loop (max 2t) →  
hybrid retrieval → analyst CoT → reviewer → risposta con fonti  
  
WORKFLOW B — Document Intelligence  
Avvocato deposita file → pipeline asincrona automatica →  
analisi per sezione → documento annotato in output
```

---

## 2. Stack Tecnologico

### 2.1 Componenti Core


| Componente               | Tecnologia                                  | Ruolo                                                        |
|--------------------------|---------------------------------------------|--------------------------------------------------------------|
| **Agenti locali**        | [Pi](https://pi.dev/docs/latest)            | Harness agenti su laptop, sistema di Skills, provider Ollama |
| **File System Agentico** | [Mirage](https://docs.mirage.strukto.ai)    | VFS unificato multi-backend, sincronizzazione distribuita    |
| **Knowledge Graph**      | [Graphify](https://graphify.net) (adattato) | Graph RAG, Leiden clustering, MCP Server, export Neo4j       |
| **LLM locale**           | Ollama + qwen2.5:7b Q4_K_M                  | Inferenza su laptop, contesto 128K                           |
| **LLM server**           | Ollama + Qwen2.5-72B                        | Ingestione semantica, escalation task complessi              |
| **Vector Store**         | ChromaDB / Qdrant                           | Dense retrieval, similarità semantica                       |
| **Graph DB**             | Neo4j                                       | Query Cypher server-side, traversal profondo                 |
| **Keyword Search**       | BM25Okapi                                   | Sparse retrieval, precisione terminologia legale             |
| **NER Anonimizzazione**  | GLiNER (fine-tuned)                         | Estrazione PII da atti italiani                              |


### 2.2 Mirage — Backend Montati per Nodo Client

```
/docs/{tenant_id}/incoming/    DiskResource RW  — incoming documents  
/kb/public/                    DiskResource R   — norme IT+EU pubbliche  
/kb/studio/                    DiskResource R   — giurisprudenza interna studio  
/kb/{tenant_id}/               DiskResource R   — documenti privati tenant  
/results/{tenant_id}/          DiskResource RW  — output agenti  
/server/ingestion/             SSHResource W    — push verso server  
/server/distribution/          SSHResource R    — pull KB aggiornata  
/agent/scratch/                RAMResource RW   — scratchpad agenti  
/agent/state/                  RedisResource RW — coordinazione job
```

### 2.3 Modelli LLM — Selezione e Configurazione

```
LAPTOP (inference quotidiana):  
  Primario:    qwen2.5:7b Q4_K_M  — 5.5GB RAM, ctx 128K, JSON mode  
  Alternativo: mistral-nemo:12b Q4_K_S — 7.8GB, se hardware lo permette  
  
SERVER (ingestione + escalation):  
  Primario:    Qwen2.5-72B Q4_K_M — 45GB VRAM (2× A6000)  
  Alternativo: Llama-3.1-70B Q4   — fallback  
  
TEMPERATURA per agente:  
  Supervisor:  0.05  (determinismo routing)  
  Researcher:  0.10  (espansione query controllata)  
  Analyst:     0.10  (reasoning fedele ai fatti)  
  Drafter:     0.30  (variazione stilistica)  
  Reviewer:    rule-based (no LLM per il 90% dei check)
```

---

## 3. STEP 0 — Tassonomia KB vs LLM

### 3.1 Framework a Quattro Zone

```
ZONA A — FATTI POSITIVI (KB Ibrida: Obbligatorio)  
Tutto ciò che ha fonte verificabile, data, numero, effetto giuridico.  
Allucinare qui = danno professionale diretto.  

ZONA B — RAGIONAMENTO APPLICATIVO (LLM + KB grounding)  
Interpretazione, analogia, bilanciamento interessi.  
L'LLM ragiona SOLO sui fatti estratti dalla Zona A.  

ZONA C — CONOSCENZA STRUTTURALE (LLM Pregressa)  
Logica giuridica, struttura atti, brocardi latini, tecnica argomentativa.  
Non cita fatti: descrive come si ragiona.  

ZONA PII — PRE-INGESTION (Anonimizzazione obbligatoria)  
PII anonimizzate prima che il documento entri nella KB.  
Vault cifrato separato con lifecycle GDPR.
```

### 3.2 Cosa Entra in KB (Zona A)


| Categoria                             | Rappresentazione Primaria                                      | Note                                               |
|---------------------------------------|----------------------------------------------------------------|----------------------------------------------------|
| Leggi, D.Lgs., D.P.R., Regolamenti UE | BM25 (testo integrale) + Vector (contesto) + Graph (relazioni) | Granularità: articolo/comma, non legge intera     |
| Articoli singoli come nodi atomici    | Graph (`Articolo`) + BM25                                      | Con validità temporale `valid_from`/`valid_to`    |
| Sentenze pubbliche                    | Graph + Vector + BM25                                          | `massima` ufficiale indicizzata                    |
| Sentenze dello studio                 | Vector + BM25 + Graph parziale                                 | Partizione tenant-specific, alto valore strategico |
| Contratti clienti (anonimizzati)      | Vector + BM25                                                  | Metadati: tipo, clausole chiave                    |
| Dottrina citata in sentenza           | Graph (`Dottrina`)                                             | Relazione `CITATA_IN` verso sentenza               |


### 3.3 Regola d'Oro Anti-Allucinazione

>
> **Se una frase contiene un numero (articolo, comma, anno, sentenza, scadenza), deve provenire dalla KB.**
>

### 3.4 Citation Contract — 3 Livelli di Difesa

**Livello 1 — Prompt Engineering (system prompt degli agenti):**

```
REGOLA ASSOLUTA: Non puoi citare articoli di legge o sentenze  
che non siano presenti nei [RETRIEVED_CHUNKS].  
Se la KB non contiene l'informazione, rispondi:  
"Non ho trovato nella base di conoscenza una fonte verificabile.  
Si consiglia ricerca manuale su [banca dati]."
```

**Livello 2 — Reviewer Rule-Based (post-generation):**

```python
# Estrae tutte le citazioni dalla risposta  
# Pattern: art. \d+, D.Lgs. \d+/\d+, Cass. Sez. \w+ n. \d+  
# Verifica che ogni source_id sia in retrieved_source_ids  
# BLOCCA la risposta se trova citazioni non grounded
```

**Livello 3 — Structured Output con Source Binding:**

```json
{  
  "argument": "Il contratto è nullo per mancanza di causa",  
  "legal_basis": [{  
    "claim": "La causa è elemento essenziale del contratto",  
    "source_id": "CC_ART_1418_COMMA_2",  
    "confidence": "direct"  
  }],  
  "ungrounded_notes": "Valutazione del rischio: ragionamento LLM, non citazione"  
}
```

---

## 4. STEP 1 — Modellazione Grafo Legale e Pipeline di Ingestione

### 4.1 Ontologia Legale — Nodi

#### Core (presente in tutti i moduli)

```
Normativa       id, titolo, tipo[Legge|DLgs|DPR|RegUE|Circolare],  
numero, anno, gazzetta_ufficiale, valid_from, valid_to,  
jurisdiction[IT|EU|Regionale], fonte_url, hash_testo,  
tenant_visibility[PUBLIC|TENANT]  

Articolo        id, normativa_id, numero_articolo, numero_comma,  
testo_integrale, testo_vigente, rubrica,  
valid_from, valid_to, stato[VIGENTE|ABROGATO|MODIFICATO]  

Sentenza        id, organo[Cassazione|CorteCost|TAR|CdS|Appello|Tribunale],  
sezione, numero, anno, data_pubblicazione,  
massima_ufficiale, testo_integrale_hash, tipo, tenant_id  

Principio       id, nome, descrizione, tipo[Generale|Settoriale], fonte_primaria_id  

Dottrina        id, autore_anonimato, titolo, anno, rivista, abstract, tenant_id
```

#### Layer Tenant (dati privati anonimizzati)

```
Cliente         id_anonimo, tipo[PF|PG], settore, tag_strategici  
                (nessun dato PII diretto → solo riferimento cifrato nel vault)  
  
Causa           id, tipo_rito, fase[Istruttoria|Appello|Cassazione],  
                oggetto_sintetico, esito, data_inizio, tenant_id, cliente_id_anonimo  
  
Contratto       id, tipo, clausole_chiave[], data_stipula, tenant_id, cliente_id_anonimo  
  
Clausola        id, contratto_id, testo_anonimizzato, tipo,  
                rischio_valutato[Alto|Medio|Basso]
```

#### Moduli Specialistici (installabili)

```
[MOD_PENALE]         Reato, ElementoCostitutivo, Circostanza,  
PenaEdittale, Prescrizione  

[MOD_TRIBUTARIO]     Tributo, AliquotaStorica, AccertamentoTipo,  
SanzioneAmministrativa, InteresseLegale  

[MOD_LAVORO]         CCNL, Istituto, ContrattoTipo, ContenziosoTipo  

[MOD_AMMINISTRATIVO] AttoAmministrativo, Procedimento, TermineDecadenziale,  
AutoritaAmministrativa, VizioLegittimita
```

### 4.2 Ontologia Legale — Relazioni (Edges Tipizzati)

```
RELAZIONI NORMATIVE (tra Normativa/Articolo):  
  ABROGA          (Normativa_nuova) ──► (Articolo_vecchio)  
                  props: data_effetto, tipo[Espressa|Tacita]  
  MODIFICA        (Normativa) ──► (Articolo)  
                  props: data_effetto, testo_precedente  
  DEROGA          (Articolo_speciale) ──► (Articolo_generale)  
  RIMANDA_A       (Articolo) ──► (Articolo)  
                  props: tipo[Rinvio_Fisso|Rinvio_Mobile]  
  ATTUA           (DLgs) ──► (Normativa_delega)  
  
RELAZIONI GIURISPRUDENZIALI:  
  INTERPRETA      (Sentenza) ──► (Articolo)  
                  props: tipo[Estensiva|Restrittiva|Adeguatrice]  
  APPLICA         (Sentenza) ──► (Normativa|Articolo|Principio)  
  CONTRASTA       (Sentenza_A) ──► (Sentenza_B)  
                  props: data, sezione, nota_contrasto  
  CONFERMA        (Sentenza_A) ──► (Sentenza_B)  
  SUPERA          (Sentenza_SS.UU.) ──► (Sentenza_B)  
                  props: questione_risolta  
  FA_GIURISPRUDENZA_PER  (Sentenza) ──► (Principio)  
  CITATA_IN       (Sentenza_A|Dottrina) ──► (Sentenza_B)  
  
RELAZIONI TENANT:  
  BASATA_SU       (Causa) ──► (Articolo|Principio)  
  HA_PORTATO_A    (Causa) ──► (Sentenza)  
  REGOLATA_DA     (Contratto) ──► (Normativa|Articolo)  
  SIMILE_A        (Clausola_A) ──► (Clausola_B)  
                  props: similarity_score, metodo[Vector|BM25]
```

### 4.3 Adattamento di Graphify per il Dominio Legale

Graphify è nato per codebase (Tree-sitter + LLM). Per i documenti legali, la struttura è altrettanto deterministica:

```
PARSER STRUTTURALE LEGALE (sostituisce Tree-sitter)  
──────────────────────────────────────────────────  
INPUT: PDF/DOCX/TXT di legge o sentenza  

REGEX/RULE-BASED:  
Leggi:    "Art. \d+" → nodo Articolo  
"comma \d+" → sotto-nodo  
"Gazzetta Ufficiale n.\d+" → metadato  
"abrogato dall'art. X L. Y/Z" → edge ABROGA  

Sentenze: "Cass. Sez. \w+ n.\d+/\d+" → nodo Sentenza  
"ricorrente: [NOME]" → ANONIMIZZATO prima  
"visto l'art.\d+" → edge APPLICA  

LLM-SEMANTIC EXTRACTION (server, 72B):  
- Classifica tipo di principio applicato  
- Estrae massima dal corpo sentenza  
- Identifica tipo di interpretazione normativa  
- Rileva contrasti giurisprudenziali impliciti
```

**Output Graphify adattati:**


| Output             | Adattamento Legale                                | Uso nel Sistema                       |
|--------------------|---------------------------------------------------|---------------------------------------|
| `graph.json`       | Grafo legale serializzato                         | Query offline su ogni nodo via Mirage |
| Esportazione Neo4j | Graph DB server                                   | Query Cypher complesse                |
| MCP Server         | Strumenti legali per agenti                       | Pi Skills invocano tool Graphify-MCP  |
| `GRAPH_REPORT.md`  | "God nodes" = norme cardine, anomalie = contrasti | Briefing periodico per soci           |
| Cache SHA256       | Re-ingestione solo documenti modificati           | Efficienza su archivi storici         |


### 4.4 Pipeline di Ingestione Asincrona — 7 Stage

```
STAGE 1 — RICEZIONE  
  Mirage workspace server: /ingestion_queue/ (RAM/Disk)  
  Ogni documento arriva con: job_id, tenant_id, doc_type, source_node  
  
STAGE 2 — ANONIMIZZAZIONE PII  ← OBBLIGATORIO, bloccante  
  GLiNER fine-tuned su atti italiani  
  Dual-pass: regex deterministico + GLiNER contestuale  
  Entity resolution fuzzy (RapidFuzz threshold: 0.85)  
  Output: doc anonimizzato + vault entry cifrata  
  
STAGE 3 — PARSING STRUTTURALE  
  Legal Parser rule-based (regex su struttura leggi/sentenze)  
  Deterministico, veloce, zero LLM, zero allucinazioni  
  Output: entità strutturali con offset precisi  
  
STAGE 4 — SEMANTIC EXTRACTION  
  LLM 72B (solo su testo già anonimizzato)  
  Output: massime, principi, tipo interpretazione, contrasti  
  
STAGE 5 — GRAPHIFY BUILD  
  graphify --input processed/ --output kb/ --module legal_core  
  Leiden clustering per community detection  
  Export: Neo4j + MCP Server + graph.json  
  
STAGE 6 — INDEX BUILD  
  Vector: ChromaDB/Qdrant (embedding su chunk da Graphify)  
  BM25:   BM25Okapi su corpus anonimizzato  
  
STAGE 7 — PACKAGING  
  tar.zst degli indici + manifest.json (checksum, version, delta)  
  Destinazione: /server/distribution/{tenant_id}/kb_v{N}.pkg.zst
```

---

## 5. STEP 2 — Architettura Multi-Agente

### 5.1 Roster degli Agenti (Pi Skills)

```
~/.pi/skills/  
├── legal_supervisor.md    [S0] Orchestrator — routing + session mgmt  
├── legal_clarifier.md     [S1] Loop chiarimento (max 2 turni)  
├── legal_researcher.md    [S2] Hybrid Retrieval + Query Expansion  
├── legal_analyst.md       [S3] CoT Reasoning + Citation Grounding  
├── legal_drafter.md       [S4] Act/Parere Generation  
├── legal_reviewer.md      [S5] Citation Verifier (rule-based + LLM)  
└── legal_annotator.md     [S6] Document Intelligence (Workflow B)
```

### 5.2 Responsabilità per Agente


| Agente              | Modello    | Ruolo                                      | Tool Accesso           |
|---------------------|------------|--------------------------------------------|------------------------|
| **[S0] Supervisor** | 7B T=0.05  | Routing, session mgmt, escalation decision | Tutti                  |
| **[S1] Clarifier**  | 7B T=0.15  | Dialogo con avvocato, max 2 turni          | Solo chat              |
| **[S2] Researcher** | 7B T=0.10  | Query expansion, hybrid retrieval          | Mirage /kb/\*          |
| **[S3] Analyst**    | 7B T=0.10  | CoT ragionamento su Research Packet        | Ollama (no KB diretta) |
| **[S4] Drafter**    | 7B T=0.30  | Generazione atti con template              | Ollama                 |
| **[S5] Reviewer**   | Rule-based | Citation check, vigenza temporale          | KB lookup              |
| **[S6] Annotator**  | 7B T=0.15  | Analisi documento, generazione annotazioni | Mirage /docs/\*        |


### 5.3 Logica di Routing del Supervisor

```python
# Classificazione del task in ingresso  
if task_type == "QUERY":  
    if context_complete:  
        route → [S2] Researcher → [S3] Analyst  
    else:  
        route → [S1] Clarifier (max 2 turni) → [S2] Researcher  
  
elif task_type == "NEW_DOCUMENT":  
    doc_type = classify_document()  
    if doc_type in [CONTRATTO, ATTO_RICEVUTO]:  
        route → parallel([S2] Researcher, [S6] Annotator) → [S3] Analyst  
    elif doc_type == BOZZA_PROPRIA:  
        route → [S4] Drafter (revisione) → [S5] Reviewer  
  
elif complexity_score > THRESHOLD:  
    route → escalation_to_server(model="qwen2.5-72b")
```

### 5.4 Trigger di Escalation al Server 72B

```python
ESCALATION_TRIGGERS = {  
"conflicting_jurisprudence_count": 3,  
"norm_cross_references_depth": 4,  
"document_pages": 50,  
"legal_areas_involved": 3,  
"historical_norm_versions": 2,  
}  

complexity_score = (  
len(conflicting_sources) * 0.3 +  
graph_traversal_depth * 0.2 +  
document_pages * 0.01 +  
legal_areas_count * 0.25 +  
historical_versions * 0.25  
)  

if complexity_score > THRESHOLD:  
# Task inviato al server tramite Mirage SSH mount  
# /server/escalated_tasks/{job_id}  
# Risultato torna su /results/{tenant_id}/
```

### 5.5 Workflow A — Q&A Interattiva (Sequenza)

```
Avvocato ──────────────────────────────────────► [S0] Supervisor  
                                                        │  
                                         classify_intent() + check_context()  
                                                        │  
                              ┌─────────────────────────┤  
                         NO context                  context OK  
                              │                         │  
                         [S1] Clarifier           [S2] Researcher  
                              │                    query_expand()  
                         (max 2t)                 parallel retrieval  
                              │                         │  
                              └──────────────────► [S3] Analyst  
                                                   CoT reasoning  
                                                        │  
                                                   [S5] Reviewer  
                                                   citation check  
                                                        │  
                                              ┌─────────┴─────────┐  
                                           FAIL                  PASS  
                                              │                   │  
                                         re-retrieval        Avvocato  
                                              │            "Vuoi un atto?"  
                                              │          ┌───────┴──────┐  
                                              │         SÌ             NO  
                                              │          │              │  
                                              │     [S4] Drafter    response  
                                              │     [S5] Reviewer    report  
                                              └──────────────────────────►
```

### 5.6 Workflow B — Document Intelligence (Sequenza)

```
Avvocato deposita file ──► FileWatcher ──► [S0] Supervisor  
│  
classify_document()  
──► "CONTRATTO, FORNITURA"  
│  
PARALLEL PHASE  
┌─────────────┴─────────────┐  
[S2] Researcher              [S6] Annotator  
find_norms_for(CONTRATTO)    parse_structure()  
│                            │  
norms_packet{...}          sections{6, clauses:24}  
└─────────────┬─────────────┘  
│  
LOOP PER SEZIONE  
│  
[S3] Analyst  
analyze_section(chunk, norms)  
│  
[S6] Annotator  
generate_annotations()  
[COMMENTO] [RISCHIO] [SUGGERIMENTO]  
[CROSS_REF] [LACUNA]  
│  
[S5] Reviewer  
verify_all_citations()  
│  
output: documento_annotated.pdf  
notifica → Avvocato
```

### 5.7 Strategie di Ottimizzazione 7B su Laptop

```
STRATEGIA 1 — MODELLO SINGOLO IN MEMORIA  
  Un solo processo Ollama con qwen2.5:7b caricato.  
  Tutti gli agenti usano lo stesso modello con system prompt diverso.  
  Latenza per call: 500ms-2s (vs 5-10s con load/unload)  
  
STRATEGIA 2 — CONTEXT BUDGET PER AGENTE  
  Supervisor:   2K token totali  
  Analyst:      5.6K (research_packet compresso: ~1.5K + reasoning)  
  Drafter:      6.5K (analysis + draft target)  
  TOTALE PIPELINE: ~16K token (dentro ctx 128K di Qwen2.5)  
  
STRATEGIA 3 — PROMPT CACHING  
  System prompt statici → KV cache hit su ogni call  
  Solo la parte variabile (query, research packet) è rielaborata  
  Risparmio: ~40% tempo di prefill  
  
STRATEGIA 4 — PIPELINE ASINCRONA (Workflow B)  
  Researcher: retrieval I/O-bound → GPU libera → prefetch chunk successivo  
  Analyst elabora chunk N mentre Researcher fa retrieval chunk N+1  
  Throughput: 2-3x rispetto a pipeline sequenziale  
  
STRATEGIA 5 — COMPRESSION DEL RESEARCH PACKET  
  Research Packet raw: ~8.000 token (testi integrali)  
  Compression step (rule-based): mantieni source_id + snippet (max 200 token/fonte)  
  Research Packet compresso: ~1.500 token
```

---

## 6. STEP 3 — Ricerca Ibrida (Grafo + Vector + BM25)

### 6.1 Pipeline di Retrieval — 3 Stage

```
STAGE 0: QUERY INTENT CLASSIFICATION  
Classificatore leggero: rule-based (90%) + LLM fallback (10%)  
Output: intent + weight_profile dinamico  

STAGE 1: QUERY EXPANSION (differenziata per indice)  
LLM 7B → 3 espansioni diverse:  
graph_entities:   entità da cercare nel grafo (CC_ART_1453, ...)  
vector_variants:  3-5 parafrasi semantiche  
bm25_terms:       termini legali esatti, articoli, brocardi  

STAGE 2: RETRIEVAL PARALLELO (3 indici × 3 corpora)  
Graphify MCP: traverse(entity, depth, edge_types)  
ChromaDB:     similarity_search(variants, top_k=15)  
BM25Okapi:    keyword_search(terms, top_k=15)  
Su: /kb/public + /kb/studio + /kb/{tenant_id}  

STAGE 3: FUSION & RERANKING  
RRF base + 6 boost dinamici → deduplicazione → top_10
```

### 6.2 Tassonomia degli Intent e Weight Profiles


| Intent                  | BM25 | Vector | Graph | Traversal Depth | Caso d'uso                           |
|-------------------------|------|--------|-------|-----------------|--------------------------------------|
| `NORMA_LOOKUP`          | 0.70 | 0.20   | 0.10  | 1               | "Testo art. 1418 CC"                 |
| `GIURISPRUDENZA_SEARCH` | 0.25 | 0.60   | 0.15  | 2               | "Sentenze responsabilità medica"    |
| `FATTISPECIE_ANALYSIS`  | 0.15 | 0.30   | 0.55  | 4               | "Cliente sotto minaccia, tutele?"    |
| `PRECEDENTE_INTERNO`    | 0.20 | 0.60   | 0.20  | 2               | "Studio ha gestito casi simili?"     |
| `NORMA_EVOLUTION`       | 0.20 | 0.10   | 0.70  | 6               | "Come è cambiato art. X nel tempo?" |
| `RISCHIO_CONTRATTUALE`  | 0.30 | 0.35   | 0.35  | 3               | "Clausola rischiosa?"                |
| `MULTI_HOP`             | 0.10 | 0.30   | 0.60  | 5               | Query su più materie/anni           |


### 6.3 I Tre Corpora Separati

```
/kb/public/normativa/              Leggi IT + Regolamenti UE (corpus pubblico)  
/kb/public/giurisprudenza/         Sentenze pubbliche  
/kb/studio/giurisprudenza_interna/ Sentenze dei casi gestiti dallo studio (SEPARATO)  
/kb/{tenant_id}/documenti/         Contratti, atti, note private del tenant
```

**Decisione A2:** il corpus studio è separato con boost configurabile (default +30%).

### 6.4 Boost Dinamici Post-RRF

```python
BOOST_1  Gerarchia fonti del diritto  
Legge/DLgs: ×1.4 | Reg. UE: ×1.3 | SS.UU.: ×1.3 | Circolare: ×0.8  

BOOST_2  Vigenza temporale  
Norma vigente alla data rilevante: ×1.2 | Abrogata: ×0.5  

BOOST_3  Recency giurisprudenza  
score *= max(0.7, 1.3 - (age_years × 0.1))  

BOOST_4  Corpus studio interno  
Precedenti interni: ×1.3 (configurabile per tenant)  

BOOST_5  Graph centrality  
Nodi con centrality > 0.7 (norme cardine): ×1.25  

BOOST_6  Sentenze SS.UU. su contrasti noti  
SS.UU. che risolve conflitto sulla materia: ×1.5
```

### 6.5 Research Packet — Struttura Output del Researcher

```json
{  
  "query_original": "...",  
  "query_intent": "FATTISPECIE_ANALYSIS",  
  "weight_profile_used": {"bm25": 0.15, "vector": 0.30, "graph": 0.55},  
  "sources": [  
    {  
      "rank": 1,  
      "source_id": "CC_ART_1453",  
      "corpus": "public_normativa",  
      "type": "articolo",  
      "retrieval_methods": ["BM25", "Graph"],  
      "final_score": 1.186,  
      "boost_applied": ["source_hierarchy:1.4"],  
      "snippet": "Nei contratti con prestazioni corrispettive...",  
      "valid_on_date": "2024-01-01",  
      "graph_neighbors": ["CC_ART_1454", "CC_ART_1455", "CASS_2023_12345"]  
    },  
    {  
      "rank": 2,  
      "source_id": "CASS_SS_UU_2019_17867",  
      "corpus": "public_giurisprudenza",  
      "type": "sentenza",  
      "organo": "SS.UU.",  
      "final_score": 1.043,  
      "boost_applied": ["ssuu_conflict_resolution:1.5"],  
      "graph_path": "CC_ART_1453→[FA_GIURISPRUDENZA_PER]→Principio_Proporzionalità→[CONFERMATO_DA]→questa_sentenza"  
    }  
  ],  
  "graph_context": {  
    "community": "Responsabilità_Contrattuale",  
    "conflicting_jurisprudence": [],  
    "norm_evolution_notes": "Art. 1453 CC invariato dal 1942"  
  },  
  "retrieval_confidence": "HIGH",  
  "gaps": [],  
  "kb_version": {"public": 42, "studio": 17, "tenant_A": 31}  
}
```

---

## 7. STEP 4 — File System Distribuito e Multi-tenant

### 7.1 Isolamento Tenant — Defense in Depth

**Decisione A3:** doppio livello di protezione obbligatorio.

```
LIVELLO 1 — Mirage Path ACL (filesystem)  
Su Node A: nessun mount per /kb/tenant_B  
Fisicamente impossibile accedere ai dati del tenant B  

LIVELLO 2 — HMAC Token (applicativo)  
Ogni Pi Skill call porta tenant_token firmato HMAC  
TenantContextMiddleware verifica su ogni operazione  
Allowed paths: solo /kb/public + /kb/studio + /kb/{tenant_id}  

LIVELLO 3 — SSH User Linux separato per tenant  
agent_{tenant_id}@server → accesso solo a /distribution/{tenant_id}  
sync_{tenant_id}@server → read-only su /distribution/{tenant_id}  

LIVELLO 4 — Audit Log GDPR  
Ogni accesso loggato: timestamp, user, node, agent, path, outcome  
File WORM, rotazione mensile, retention 5 anni
```

### 7.2 Struttura dei Pacchetti di Distribuzione

```
/server/distribution/  
├── public/  
│   ├── kb_public_v042.pkg.zst  
│   ├── kb_public_v042.manifest.json  
│   └── kb_public_latest → v042 (symlink)  
├── studio/  
│   └── kb_studio_v017.pkg.zst  
└── tenant_{id}/  
    ├── kb_tenant_A_v031.pkg.zst  
    └── kb_tenant_A_v031.manifest.json
```

**Manifest JSON:**

```json
{  
"version": 31,  
"tenant_id": "tenant_A",  
"built_at": "2024-11-15T14:23:00Z",  
"previous_version": 30,  
"components": {  
"graph_json": {  
"checksum_sha256": "a3f7...",  
"changed": true,  
"delta_available": true,  
"delta_size_bytes": 245000  
},  
"vector_index": {"changed": false},  
"bm25_index": {"changed": true, "delta_available": true}  
},  
"documents_added": 3,  
"estimated_download_mb": 0.25  
}
```

### 7.3 KBSyncAgent — Logica Pull-Based

**Decisione A1:** pull periodico ogni 30 minuti (configurabile).  
**Decisione A2:** eventual consistency accettata.

```python
SYNC_INTERVAL_MINUTES = 30  
  
async def pull_updates():  
    for corpus in ["public", "studio", f"tenant_{TENANT_ID}"]:  
        manifest = read_server_manifest(corpus)  
        local_version = get_local_version(corpus)  
  
        if manifest.version <= local_version:  
            continue  # nessun aggiornamento  
  
        if delta_available and version_gap == 1:  
            apply_delta_update(corpus, manifest)  # scarica solo diff  
        else:  
            apply_full_update(corpus, manifest)   # scarica pacchetto completo  
  
        # Aggiornamento atomico: write su .tmp → rename  
        # Se il processo muore a metà: versione precedente intatta
```

**Eventual Consistency — Gestione:**

```
Node 1 (attivo): usa KB v30 mentre SyncAgent scarica v31  
→ OK: norme vigenti non cambiano ogni ora  
→ Dopo sync: Supervisor avvisa "KB aggiornata — ripetere la ricerca?"  

Node 2 (laptop spento): al riavvio trova v28  
→ Scarica pacchetto completo (delta non disponibile per salti multipli)  
→ Durante download: agenti operano con v28 (degraded, non broken)  

Version skew tra nodi (v31 / v30 / v29):  
→ Nessun problema: nodi non comunicano tra loro  
→ version_id incluso in ogni Research Packet per tracciabilità
```

### 7.4 Installazione Nodo — Zero Config per Avvocato

```bash
curl -fsSL https://lexagent.studio.lan/install.sh | \  
  TENANT_ID=tenant_A NODE_ID=node_007 \  
  STUDIO_SERVER=lexserver.studio.lan bash
```

Lo script esegue in sequenza:

1. Installa Pi (`npm install -g @earendil-works/pi-coding-agent`)
2. Installa Ollama + scarica `qwen2.5:7b` (~5GB)
3. Installa `mirage-ai` (`pip install mirage-ai`)
4. Genera coppia chiavi SSH per `tenant_A/node_007`
5. Registra chiave pubblica sul server (richiede auth IT)
6. Configura Mirage workspace con mount per il tenant
7. Installa Pi package `legal-suite` (Skills + modelli)
8. Prima sincronizzazione KB completa
9. Avvia FileWatcher e KBSyncAgent come servizi di sistema
10. Test di isolamento: verifica `/kb/tenant_B` non accessibile


**Durata stimata: 15-25 minuti** (dominata dal download del modello)

---

## 8. STEP 5 — Diagrammi PlantUML

I sorgenti PlantUML completi sono disponibili nel viewer interattivo (STEP 5 della sessione). Di seguito i tre diagrammi prodotti.

### 8.1 Diagram 1 — System Overview

Mostra: Server (ingestion pipeline + KB master + distribution) → Sync pull → Nodi client (Pi Skills + Mirage + Ollama + Local KB). Isolamento tenant, escalation verso server, FileWatcher per Workflow B.

### 8.2 Diagram 2 — Workflow A: Q&A Interattiva

Mostra: classificazione intent → clarification loop → query expansion → retrieval parallelo (Graphify MCP + ChromaDB + BM25) → RRF fusion → Analyst CoT → Reviewer → Drafter opzionale.

### 8.3 Diagram 3 — Workflow B: Document Intelligence

Mostra: FileWatcher trigger → classificazione documento → retrieval parallelo + parsing struttura → analisi chunked → generazione annotazioni → verifica citazioni → PDF annotato asincrono.

---

## 9. Deep Dive — Modulo di Anonimizzazione PII

### 9.1 Scelta Tecnologica: GLiNER

**Motivazioni:**

- Architettura bi-encoder: aggiungere un nuovo tipo di entità = aggiungere una descrizione testuale (no re-training)
- Inferenza CPU: 50-200ms per documento medio
- RAM: ~1.2GB (accettabile sul server)
- Supporto multilingue con pre-training europeo

**Modello base:** `urchade/gliner_large-v2.1` (560MB, 26 lingue, DeBERTa-v3-large backbone)

### 9.2 Tassonomia Entità PII Legali Italiane

#### Entità DA Anonimizzare


| Tipo                  | Descrizione                                      | Placeholder               | Livello Minimo |
|-----------------------|--------------------------------------------------|---------------------------|----------------|
| `PERSONA_FISICA`      | Nome/cognome, iniziali, soprannomi               | `[PERSONA_{seq}]`         | SEMPRE         |
| `CODICE_FISCALE`      | CF a 16 caratteri                                | `[CF_REDACTED]`           | SEMPRE         |
| `PARTITA_IVA`         | P.IVA a 11 cifre                                 | `[PIVA_REDACTED]`         | SEMPRE         |
| `DATA_NASCITA`        | Data di nascita persona fisica                   | `[DATA_NASCITA_REDACTED]` | SEMPRE         |
| `INDIRIZZO`           | Via, piazza, civico, CAP, città                 | `[INDIRIZZO_{seq}]`       | SEMPRE         |
| `EMAIL`               | Email ordinaria o PEC                            | `[EMAIL_REDACTED]`        | SEMPRE         |
| `TELEFONO`            | Fisso o mobile IT/estero                         | `[TEL_REDACTED]`          | SEMPRE         |
| `SOCIETA`             | Denominazione + forma giuridica (S.r.l., S.p.A.) | `[SOCIETA_{seq}]`         | SEMPRE         |
| `IBAN`                | Codice IBAN                                      | `[IBAN_REDACTED]`         | SEMPRE         |
| `AVVOCATO_PARTE`      | Avvocato difensore parte privata                 | `[AVV_{seq}]`             | LEVEL_1+       |
| `GIUDICE`             | Nome magistrato (atti privati)                   | `[MAGISTRATO_{seq}]`      | LEVEL_2+       |
| `NUMERO_PROCEDIMENTO` | R.G. del fascicolo interno studio                | `[PROC_{seq}]`            | LEVEL_1+       |


#### Entità DA Preservare Intatte (non-PII)

- Riferimenti normativi: `art. 1218 c.c.`, `D.Lgs. 231/2001`
- Organi giudiziari: `Tribunale di Milano`, `Corte di Cassazione`
- Sentenze pubbliche: `Cass. Sez. III n. 12345/2023`
- Enti pubblici: `Comune di Milano`, `Agenzia delle Entrate`

> 
> **Regola critica:** il modello fine-tuned deve imparare a NON toccare questi elementi. La distinzione è contestuale, non lessicale.
> 

### 9.3 Pipeline di Anonimizzazione — 7 Stage

```
STAGE A — PRE-PROCESSING  
Estrazione testo (pdfminer/python-docx)  
Normalizzazione unicode, sentence splitting (spaCy it_core_news_lg)  
Sliding window chunking (512 token, overlap: 64)  

STAGE B — DUAL-PASS NER  
PASS A: Regex deterministico (<1ms) per CF, PIVA, IBAN, Email, Tel  
PASS B: GLiNER fine-tuned (50-200ms) per PERSONA_FISICA, INDIRIZZO, SOCIETA  
MERGE: union con deduplicazione (regex vince su GLiNER per tipi strutturati)  

STAGE C — ENTITY RESOLUTION (co-reference)  
"Mario Rossi", "M. Rossi", "il sig. Rossi" → stesso placeholder  
Algoritmo: normalizzazione → fuzzy clustering (RapidFuzz threshold: 0.85)  
Attenzione: "Rossi" (persona) ≠ "Studio Rossi & Bianchi" (societa)  

STAGE D — CLASSIFICAZIONE RUOLO PARTE  
OWN_CLIENT | COUNTERPART | THIRD_PARTY | MAGISTRATE | EXPERT_WITNESS  
Basata su indicatori contestuali (±200 char attorno all'entità)  
Default conservativo: THIRD_PARTY se ambiguo  

STAGE E — SOSTITUZIONE NEL TESTO  
Ordine: più lungo prima (evita sostituzioni parziali)  
Stessa surface form → stesso placeholder in tutto il documento  

STAGE F — VAULT ENTRY CIFRATA  
DEK random per documento → cifra ogni valore (AES-256-GCM)  
Vault file salvato in /server/vault/{tenant_id}/{partition}/  
FISICAMENTE SEPARATO dalla KB  

STAGE G — SANITY CHECK  
Ricerca pattern PII residui nel testo anonimizzato  
Fallback: regex cleanup aggressivo  
Flag: [VERIFICA_MANUALE: token X] per casi ambigui
```

### 9.4 Training Data Strategy


| Track                    | Metodo                                                    | Quantità | Note                              |
|--------------------------|-----------------------------------------------------------|-----------|-----------------------------------|
| **A — Sintetica**      | LLM 72B genera atti italiani fittizi con annotazioni IOB2 | 800 doc   | Alta varietà, layout controllato |
| **B — Perturbed Real** | Name swapping su atti reali (PII originali mai esposte)   | 400 doc   | Distribuzione reale               |
| **C — Gold Annotated** | Annotazione manuale + revisione avvocato (Label Studio)   | 200 doc   | Alta qualità, hold-out test      |


**Target performance post fine-tuning:**


| Entity Type        | Precision | Recall | F1    | Note                            |
|--------------------|-----------|--------|-------|---------------------------------|
| PERSONA_FISICA     | 0.97      | 0.98   | 0.975 | Target critico: recall ≥ 0.98 |
| CODICE_FISCALE     | 0.99      | 0.99   | 0.990 | Regex assist                    |
| PARTITA_IVA        | 0.99      | 0.99   | 0.990 | Regex assist                    |
| INDIRIZZO          | 0.91      | 0.93   | 0.920 |                            |
| SOCIETA            | 0.94      | 0.92   | 0.930 |                            |
| IBAN               | 0.99      | 0.99   | 0.990 | Regex assist                    |
| AVVOCATO_PARTE     | 0.88      | 0.86   | 0.870 | Contestuale, più difficile     |
| False pos. NON-PII | < 1%   | —    | —   | Norme legali non toccate        |


### 9.5 PII Vault — Architettura Crittografica a 3 Livelli

```
LIVELLO 1 — Master Key  
  master_key = PBKDF2(password_studio, salt_tenant, 600_000_iter)  
  Usata SOLO per cifrare/decifrare i KEK  
  Non esce mai dal nodo del tenant  
  
LIVELLO 2 — Key Encryption Key (rotazione trimestrale)  
  kek_2024_Q4 = os.urandom(32)  ← 256-bit random  
  Archiviato cifrato con master_key (AES-256-GCM)  
  
LIVELLO 3 — Data Encryption Key (per-documento)  
  dek_doc_001 = os.urandom(32)  ← random per ogni vault entry  
  Usata per cifrare i valori PII  
  AES-256-GCM(valore, dek, iv_random) → ciphertext + auth_tag
```

### 9.6 Partizioni del Vault e Lifecycle

**Decisione A1:** LEVEL_1 (pseudonimizzazione reversibile) come default per tutti i documenti.


| Partizione       | Retention | Auth Deletion | Auto-Delete          | GDPR Basis                      |
|------------------|-----------|---------------|----------------------|---------------------------------|
| `own_parties/`   | 10 anni   | Single auth   | No                   | Contratto professionale         |
| `third_parties/` | 3-5 anni  | **Dual auth** | Sì (chiusura causa) | Legittimo interesse processuale |


### 9.7 De-anonimizzazione con Autenticazione

**Decisione A2:** ogni accesso al vault richiede PIN esplicito + viene loggato.

```
FLUSSO:  
Pi Agent → richiesta de-anon [PERSONA_001]  
De-Anon Gate → verifica HMAC agente + rate limiting (10/ora)  
Prompt PIN all'avvocato (non passa per LLM, stdin diretto)  
Verifica PIN (bcrypt hash locale)  
Vault lookup → decifra con DEK → risposta in sessione  
Audit log: timestamp, user, entity, doc, reason, outcome  

PRINCIPIO: L'LLM non ha mai accesso diretto al vault.  
Il valore reale esiste solo nella risposta della sessione corrente.  
Non viene salvato in nessun file persistente.
```

**Struttura Audit Log (append-only, HMAC-signed):**

```json
{  
  "event_id": "uuid",  
  "timestamp": "2024-11-15T14:23:07Z",  
  "tenant_id": "tenant_A",  
  "user_id": "avv_rossi",  
  "node_id": "node_007",  
  "agent_name": "Legal Supervisor [S0]",  
  "event_type": "DEANON_SUCCESS",  
  "placeholder": "[PERSONA_001]",  
  "entity_type": "PERSONA_FISICA",  
  "doc_id": "a3f7b2c1...",  
  "reason": "identificazione parte per verifica strategia",  
  "value_hash": "sha256(valore_reale)",  
  "outcome": "SUCCESS"  
}
```

> 
> **Nota:** Il valore reale NON è mai nel log. Solo un hash one-way per eventuale audit forense.
> 

### 9.8 Cancellazione Selettiva (Art. 17 GDPR)

**Decisione A3:** PII di terze parti entrano nel vault con cancellazione possibile su richiesta.

```python
# La cancellazione non rompe l'integrità documentale:  
# Il placeholder rimane nel documento anonimizzato e negli indici.  
# Solo il mapping nel vault viene distrutto crittograficamente.  

# PRIMA della cancellazione:  
[CONTROPARTE_001] → vault → enc(Beta S.r.l.)  

# DOPO la cancellazione (Art. 17 GDPR):  
[CONTROPARTE_001] → vault → random_bytes (sovrascrittura crittografica)  
→ status: "deleted"  
→ deletion_completed_at: timestamp  

# Cosa vede l'agente dopo la cancellazione:  
"[CONTROPARTE_001]: identità rimossa su richiesta — Art. 17 GDPR.  
Il riferimento procedurale è conservato per integrità documentale."  

# Il reasoning legale del documento rimane intatto.  
# Solo l'identità reale è stata cancellata.
```

**Dual Authorization per terze parti:**

```
Richiesta da: avv_rossi  
Autorizzazione da: avv_bianchi  ← deve essere persona diversa  
PIN di: avv_bianchi  
→ Audit log: DUAL_AUTH_DELETION_EXECUTED
```

---

## 10. Decisioni Architetturali Chiave

Registro delle decisioni prese durante la sessione di design.


| ID   | Decisione              | Scelta                                                                | Motivazione                                                       |
|------|------------------------|-----------------------------------------------------------------------|-------------------------------------------------------------------|
| D-01 | Multi-specializzazione | Ontologia core + moduli verticali installabili                        | Un sistema universale installabile in qualsiasi tipo di studio    |
| D-02 | Fonti normative        | Banche dati ufficiali (Normattiva, EUR-Lex) + documenti propri studio | Aggiornamento automatico norme pubbliche + personalizzazione      |
| D-03 | Archivio storico       | Supportato nativamente                                                | Valore strategico dei precedenti storici dello studio             |
| D-04 | Privacy PII            | Anonimizzazione obbligatoria (LEVEL_1 default)                        | Segreto professionale + GDPR                                      |
| D-05 | Hardware client        | Laptop medio (no GPU dedicata)                                        | Adottabilità realistica per qualsiasi studio                     |
| D-06 | LLM locale             | Qwen2.5-7B Q4_K_M via Ollama                                          | Migliore rapporto context/qualità a 7B, ctx 128K                 |
| D-07 | Workflow               | Q&A interattiva + Document Intelligence asincrona                 | Due bisogni diversi, stessa infrastruttura agente                 |
| D-08 | Clarification loop     | Max 2 turni, poi default + assunzioni esplicite                       | Bilanciamento tra completezza e fluidità d'uso                   |
| D-09 | Weight retrieval       | Dinamico per intent (non fisso)                                       | Il caso d'uso determina quali fonti sono più rilevanti           |
| D-10 | Corpus studio          | Separato, boost +30% configurabile                                    | Precedenti interni = valore strategico differenziale              |
| D-11 | Query expansion        | Sì, differenziata per indice                                         | Migliora recall su tutti e tre gli indici                         |
| D-12 | Sync KB                | Pull periodico ogni 30 minuti                                         | Resiliente a interruzioni, no coordinamento richiesto             |
| D-13 | Consistency            | Eventual consistency accettata                                        | Norme cambiano lentamente, gap 30min irrilevante                  |
| D-14 | Tenant isolation       | Defense in depth (L1: path ACL + L2: HMAC + L3: SSH user + L4: audit) | Violazione = violazione segreto professionale                     |
| D-15 | PII default level      | LEVEL_1 (pseudonimizzazione reversibile)                              | Vault sempre presente, de-anonimizzazione possibile               |
| D-16 | De-anonimizzazione     | Auth esplicita (PIN) + audit log immutabile                           | Tracciabilità obbligatoria, LLM mai accede al vault direttamente |
| D-17 | PII terze parti        | Vault con cancellazione selettiva (Art. 17 GDPR)                      | Needed per contentious cases, erasure su richiesta                |
| D-18 | Deletion terze parti   | Dual authorization richiesta                                          | Segregazione dei compiti, prevenzione errori                      |


---

## 11. Metriche e Target di Performance

### 11.1 Latenza per Workflow


| Operazione                                | Target    | Note                            |
|-------------------------------------------|-----------|---------------------------------|
| Q&A semplice (no clarification)       | 15-30s    | Researcher + Analyst + Reviewer |
| Q&A con clarification                 | 30-60s    | +2 turni dialogo                |
| Q&A con generazione atto              | 2-4 min   | + Drafter su documento medio    |
| Document Intelligence (contratto 10 pag.) | 3-5 min   | Background, non bloccante       |
| Document Intelligence (contratto 50 pag.) | 10-15 min | Con escalation server           |
| Sync KB (delta update)                    | 30s-2 min | Dipende da dimensione delta     |
| Query expansion (LLM)                     | ~500ms    | Con cache SHA256 → ~5ms       |
| Anonimizzazione PII (doc medio)           | 1-3s      | Regex + GLiNER CPU              |


### 11.2 Qualità Retrieval


| Metrica                        | Target    | Metodo di Misurazione                             |
|--------------------------------|-----------|---------------------------------------------------|
| Precision@10 per NORMA_LOOKUP  | > 0.92 | Gold set di query legali                          |
| Recall@10 per FATTISPECIE      | > 0.85 | Gold set con sentenze rilevanti note              |
| False positive norma come PII  | < 1%   | Test set con atti annotati                        |
| Critical PII recall (CF, PIVA) | ≥ 0.99  | Test set PII annotato                             |
| Citation grounding rate        | > 0.99 | Reviewer: citazioni verificate / citazioni totali |


### 11.3 Requisiti Hardware Minimi

**Server:**

- CPU: 8 core moderni (Intel/AMD)
- RAM: 64GB
- Storage: 1TB NVMe (KB + vault + log)
- GPU (opzionale per velocità): 2× RTX A6000 48GB per Qwen2.5-72B

**Laptop avvocato:**

- CPU: Intel i5/i7 gen 10+ o Apple M2+
- RAM: 16GB (minimo), 32GB (raccomandato per Qwen2.5-7B + sistema)
- Storage: 50GB liberi (KB locale + modello)
- GPU: non richiesta (inferenza su CPU)

---

## 12. Roadmap e Next Steps

### 12.1 Componenti da Completare (Design)

- **Legal Parser Rule-Based** — Regex e struttura per leggi italiane e sentenze (Normattiva format, DeJure format, Cass. Sez. X format)
- **Sistema di Notifiche Workflow B** — Push notification al laptop quando documento annotato è pronto
- **UI/UX del Pi Terminal** — Interfaccia avvocato: input query, visualizzazione Research Packet con link a fonti, viewer documento annotato
- **Modulo di Ingestione Archivio Storico** — Batch import di archivi esistenti con de-duplication e versioning retroattivo
- **Dashboard Admin Studio** — Stato sincronizzazione KB, statistiche utilizzo per avvocato, log audit GDPR

### 12.2 Componenti da Completare (Implementazione)

- Fine-tuning GLiNER su training set legale italiano (Track A + B + C)
- Legal Parser regex per struttura leggi IT e sentenze Cassazione
- Adattamento Graphify: ontologia legale invece di ontologia codebase
- Pi package `legal-suite`: tutte e 7 le Skills + modelli + configurazione
- KBSyncAgent: daemon con delta update atomico + alert su sync failure
- DeAnonGate: processo separato, PIN auth, audit log WORM

### 12.3 Questioni Aperte

1. **Integrazione Normattiva API** — Come mantenere sincronizzato il corpus pubblico con gli aggiornamenti ufficiali? Webhook o polling?
2. **Versioning delle ontologie** — Se il modulo `[MOD_PENALE]` evolve, come migrare il grafo esistente senza ricostruirlo da zero?
3. **Conflitti nel Grafo** — Quando due sentenze si contraddicono e nessuna è di SS.UU., come espone il sistema il contrasto all'avvocato senza indurre preferenze?
4. **Federated Learning** — In futuro, è possibile far convergere le ontologie private degli studi (senza condividere i dati) per migliorare il modello comune?
5. **Compliance GDPR audit** — Chi nell'organizzazione dello studio ha accesso al log audit? Come viene garantita la sua integrità contro manomissioni interne?


---

## Appendice A — Struttura Directory Completa del Server

```
/server/  
├── ingestion_queue/           # Mirage RAM/Disk — documenti in arrivo  
│   └── tenant_{id}/  
├── processing/                # Stage 2-6 in corso  
├── vault/                     # PII Vault — SEPARATO dalla KB  
│   └── tenant_{id}/  
│       ├── vault_index.enc  
│       ├── keys/              # KEK cifrati con master_key  
│       ├── own_parties/       # Vault entries clienti studio  
│       └── third_parties/     # Vault entries controparti e terzi  
├── kb/                        # Knowledge Base master  
│   ├── public/  
│   │   ├── normativa/  
│   │   │   ├── graph/         # graph.json + Neo4j export  
│   │   │   ├── vectors/       # ChromaDB collection  
│   │   │   └── bm25/          # BM25Okapi index serializzato  
│   │   └── giurisprudenza/  
│   ├── studio/  
│   │   └── giurisprudenza_interna/  
│   └── tenant_{id}/  
│       └── documenti/  
├── distribution/              # Pacchetti zst per distribuzione ai nodi  
│   ├── public/  
│   ├── studio/  
│   └── tenant_{id}/  
├── audit/                     # Audit log WORM per GDPR  
│   └── tenant_{id}/  
│       └── YYYY-MM.audit.log  
└── escalated_tasks/           # Job da nodi client che richiedono 72B  
└── tenant_{id}/
```

## Appendice B — Struttura Directory Nodo Client

```
~/LexAgent/  
├── incoming/  
│   └── tenant_{id}/           # Drop folder dell'avvocato  
├── kb/                        # KB locale sincronizzata (read-only per agenti)  
│   ├── public/  
│   │   ├── graph/  
│   │   ├── vectors/  
│   │   └── bm25/  
│   ├── studio/  
│   └── tenant_{id}/  
├── results/  
│   └── tenant_{id}/           # Output agenti → visibile all'avvocato  
├── scratch/                   # Scratchpad RAM agenti (volatile)  
├── config/  
│   ├── workspace.yaml         # Mirage mount configuration  
│   ├── models.json            # Pi custom model definitions (Ollama)  
│   └── .kb_versions.json      # {public: 42, studio: 17, tenant_A: 31}  
└── logs/  
    └── sync.log               # Log del KBSyncAgent
```

## Appendice C — Configurazione Pi Skills (models.json)

```json
{  
"models": [  
{  
"id": "legal-supervisor",  
"provider": "ollama",  
"model": "qwen2.5:7b",  
"baseUrl": "http://localhost:11434",  
"contextWindow": 32768,  
"options": {"temperature": 0.05, "num_ctx": 32768, "num_gpu": 99}  
},  
{  
"id": "legal-analyst",  
"provider": "ollama",  
"model": "qwen2.5:7b",  
"contextWindow": 65536,  
"options": {"temperature": 0.10, "num_ctx": 65536, "num_gpu": 99}  
},  
{  
"id": "legal-drafter",  
"provider": "ollama",  
"model": "qwen2.5:7b",  
"contextWindow": 32768,  
"options": {"temperature": 0.30, "num_ctx": 32768, "num_gpu": 99}  
}  
]  
}
```

---

*Fine documento — LexAgent Architecture v0.1*  
*Prossimi step raccomandati: Legal Parser rule-based → Notifiche Workflow B → UI/UX Pi Terminal*

---

## 13. Integrazione Normativa API

### 13.1 Gerarchia delle Fonti e Impatto sul Citation Contract

```
GERARCHIA DELLE FONTI (impatta source_authority nei nodi del grafo):  
  
[UFFICIALE]    Gazzetta Ufficiale Italiana          → fonte di verità IT  
               eur-lex.europa.eu (Reg. UE)          → fonte di verità UE  
               HUDOC (sentenze CEDU)                → fonte di verità CEDU  
               cortecostituzionale.it               → ufficiale IT  
               ItalgiureWeb / CED Cassazione        → ufficiale IT  
  
[RIFERIMENTO]  normattiva.it                        → consolidato, NON ufficiale  
               (multivigenza, machine-readable, ma GU prevale)
```

**Regola Citation Contract aggiornata**: ogni nodo `Articolo` da Normattiva porta obbligatoriamente:

- `source_authority: "NORMATTIVA"`
- `is_official: false`
- `gu_reference: "GU Serie Gen. n.X del DD/MM/YYYY"`

L'Analyst include sempre il disclaimer nella risposta.

### 13.2 Corpus Curato Iniziale — Specifica Definitiva


| Componente                              | Fonte                     | Accesso        | Volume Stimato     | Fase |
|-----------------------------------------|---------------------------|----------------|--------------------|------|
| Codice Penale                           | Normattiva REST API       | Libero         | 734 articoli       | 1    |
| Codice Procedura Penale                 | Normattiva REST API       | Libero         | 746 articoli       | 1    |
| Codice Civile (base)                    | Normattiva REST API       | Libero         | 2.969 articoli     | 1    |
| GDPR + Reg. UE correlati                | EUR-Lex CELLAR SPARQL     | Libero         | ~472 atti/articoli | 1    |
| Massime Cassazione Penale (5 anni)      | Italgiure / Cassa Forense | Abbonamento CF | ~45.000 massime    | 2    |
| Massime Cassazione Civile (5 anni)      | Italgiure / Cassa Forense | Abbonamento CF | ~40.000 massime    | 2    |
| Sentenze Corte Costituzionale (10 anni) | Italgiure COSTSN          | Abbonamento CF | ~2.000 sentenze    | 2    |
| CEDU Key Cases Italy (importanza 1)     | HUDOC API                 | Libero         | ~150 casi          | 2    |
| Massime tributarie (5 anni)             | Italgiure TRIBUT          | Abbonamento CF | ~15.000 massime    | 2    |
| Corpus storico (massime pre-5 anni)     | Italgiure                 | Abbonamento CF | ~350.000 massime   | 3    |
| Sentenze penali integrali               | Italgiure free + Cassa F. | Misto          | ~500.000 testi     | 3    |
| CGUE sentenze tributarie/civili         | EUR-Lex CELLAR            | Libero         | ~5.000 sentenze    | 3    |


**Totale corpus Fase 1+2**: ~462.000 nodi grafo, ~1.500.000 chunk vector, ~30-45 GB

### 13.3 Normattiva REST API — Endpoint Chiave

```
BASE_URL: https://api.normattiva.it/t/normattiva.api  

ENDPOINT PRINCIPALI:  
/bff-opendata/v1/api/v1/ricerca/aggiornati  
→ Atti modificati tra due date (CHANGE DETECTION INCREMENTALE)  
→ Parametri: dataAggiornamentoDa, dataAggiornamentoA, classeProvvedimento  

/bff-opendata/v1/api/v1/atto/dettaglio-atto-urn  
→ Testo atto per URN (aggiunto in revisione 10/03/2026)  
→ Parametri: urn, formato (AKN|XML|JSON|PDF), dataVigenza  

/bff-opendata/v1/api/v1/ricerca/avanzata  
→ Ricerca per anno, numero, tipo provvedimento  

FORMATO PREFERITO: AKN (Akoma Ntoso)  
→ Struttura gerarchica nativa (Part > Chapter > Article > Paragraph)  
→ lifecycle/eventRef contiene automaticamente la storia delle modifiche  
→ normattiva2md converte in Markdown -60% token  

URN FORMAT: urn:nir:stato:{tipo}:{data};{numero}  
Esempio: urn:nir:stato:regio.decreto:1930-10-19;1398 (Codice Penale)  

PARAMETRO dataVigenza: fondamentale per diritto inter-temporale  
→ Permette di recuperare la norma vigente in una data specifica  
→ L'Analyst lo usa per analisi di contratti storici
```

### 13.4 EUR-Lex CELLAR SPARQL

```
ENDPOINT: https://publications.europa.eu/webapi/rdf/sparql  
PROTOCOLLO: SPARQL 1.1 via HTTP GET/POST  
TIMEOUT: 60 secondi per query → usare LIMIT/OFFSET  
  
ONTOLOGIA: CDM (Common Data Model), FRBR-compliant OWL  
IDENTIFICATORI: CELEX (es. 32016R0679) e ELI (European Legislation Identifier)  
  
QUERY TIPO (nuovi atti da data):  
  SELECT ?work ?celex ?title ?date  
  WHERE {  
    ?work cdm:work_date_document ?date ;  
          cdm:resource_legal_id_celex ?celex .  
    FILTER(?date >= xsd:date("YYYY-MM-DD"))  
    FILTER(?type IN (REG, DIR, DEC))  
  }  
  
RELAZIONI CHIAVE:  
  cdm:work_related_to      → collega atti correlati  
  cdm:consolidated_by      → atto originale → testo consolidato  
  cdm:case_law             → per sentenze CGUE
```

### 13.5 HUDOC CEDU — Acquisizione Key Cases

```python
# Solo casi importanza 1 (Key Case) contro Italia  
HUDOC_KEY_CASES_FILTER = {  
"respondent": "ITA",  
"importance": "1",           # Key Case only (~150 totali)  
"doctype": ["GRANDCHAMBER", "CHAMBER"],  
}  

# Libreria: pip install echr-extractor  
# get_echr_extra() → metadata + full text  
# Paginazione integrata, parallelismo su threads
```

### 13.6 ItalgiureWeb via Cassa Forense

```
ARCHIVI ABBONATI:  
  SNPEN   Massime penali Cassazione        update settimanale  
  SNCIV   Massime civili Cassazione        update settimanale  
          NOTE: testi integrali civili parzialmente oscurati  
          da dic.2024 per privacy requests dei litiganti.  
          Le MASSIME rimangono disponibili e stabili.  
  COSTMS  Massime Corte Costituzionale     update mensile  
  COSTSN  Sentenze integrali Corte Cost.   update mensile  
  TRIBUT  Commissioni tributarie           update mensile  
  
AUTENTICAZIONE: SSO via cassaforense.it  
  → Session refresh ogni 50 minuti (sessione dura ~60 min)  
  → Credenziali in variabile d'ambiente server (mai agli agenti)  
  → Alert IT su failure di autenticazione  
  
EVENTO SPECIALE — DICHIARAZIONI INCOSTITUZIONALITÀ:  
  Quando una sentenza Corte Cost. dichiara illegittimità:  
  → Nodo Articolo.stato → "INCOSTITUZIONALE"  
  → Edge: (SentenzaCorteCost) -[DICHIARA_ILLEGITTIMA]→ (Articolo)  
  → Vigency Manager: valid_to = data_sentenza - 1gg
```

### 13.7 Pipeline di Traduzione CEDU Automatica

```
APPROCCIO: traduzione parziale (solo sezioni strutturali ad alto valore)  
- Holding (dispositivo)  
- Principi di diritto estratti  
- Sezione "The Law" / "En Droit"  

MODELLO: Qwen2.5-72B sul server (già disponibile)  
Prompt specializzato per terminologia CEDU ufficiale italiana  
Es: "fair trial" → "equo processo"  
"margin of appreciation" → "margine di apprezzamento"  

INDICIZZAZIONE BILINGUE:  
Vector index: contiene ENTRAMBE le versioni (originale + traduzione IT)  
L'avvocato può cercare in italiano e trovare casi originalmente in EN/FR  

DISCLAIMER OBBLIGATORIO:  
🇪🇺🤖 Fonte: HUDOC / Corte EDU (ufficiale)  
🤖 Traduzione automatica da {EN|FR} → IT (qwen2.5-72b, {data})  
⚠️ NON ufficiale — verificare originale su HUDOC: {url}
```

### 13.8 NormSync Agent — Scheduling

```python
GIORNALIERO (ore 7:00):  
  - Gazzetta Ufficiale RSS check  
  - Intercetta rettifiche e D.L. urgenti  
  - Se D.L. rilevato → trigger sync Normattiva immediato  
  
SETTIMANALE LUNEDÌ (ore 2:00-3:00):  
  - Normattiva: ricerca/aggiornati (finestra 7 giorni)  
  - Italgiure massime: tutti gli archivi  
  
SETTIMANALE MARTEDÌ (ore 2:00-3:00):  
  - EUR-Lex CELLAR: nuovi atti UE  
  - HUDOC: nuovi Key Cases contro Italia  
  
SETTIMANALE MERCOLEDÌ (ore 4:00):  
  - Rebuild indici pubblici (solo se corpus.dirty = true)  
  - Package + distribuzione ai nodi client  
  - Trigger: KBSyncAgent su nodi riceve nuova versione
```

### 13.9 Sistema di Disclaimer Integrato

```python
SOURCE_DISCLAIMERS = {  
"NORMATTIVA": {  
"icon": "⚠️",  
"text": "Fonte: normattiva.it (consolidato, NON ufficiale). "  
"Fa fede GU: {gu_reference}"  
},  
"ITALGIURE_CED": {  
"icon": "✅",  
"text": "Fonte: ItalgiureWeb / CED Cassazione (ufficiale). "  
"Sentenza n. {numero}/{anno}, Sez. {sezione}."  
},  
"CORTE_COSTITUZIONALE": {  
"icon": "✅",  
"text": "Fonte: cortecostituzionale.it (ufficiale). "  
"Sentenza/Ordinanza n. {numero}/{anno}."  
},  
"CEDU_HUDOC": {  
"icon": "🇪🇺",  
"text": "Fonte: HUDOC / Corte EDU (ufficiale). "  
"{case_name}, {judgment_date}."  
},  
"CEDU_HUDOC_AUTOTRANSLATED": {  
"icon": "🇪🇺🤖",  
"text": "Fonte: HUDOC (ufficiale). Traduzione automatica "  
"{source_language}→IT (NON ufficiale). "  
"Verificare originale: {hudoc_url}"  
},  
"EUR_LEX_CELLAR": {  
"icon": "🇪🇺",  
"text": "Fonte: EUR-Lex CELEX {celex} (ufficiale UE). "  
"Consolidato al {consolidation_date}."  
},  
}
```

### 13.10 Vigency Management — Casi Speciali

```python
CASO 1 — Modifica ordinaria (legge modifica articolo):  
  - Articolo_old.valid_to = data_effetto - 1  
  - Crea Articolo_new con stessa URN_base, version + 1  
  - Edge MODIFICA: (Normativa_modificante) → (Articolo_new)  
  - Edge VERSIONE_PRECEDENTE: (Articolo_new) → (Articolo_old)  
  
CASO 2 — Abrogazione:  
  - Articolo.valid_to = data_effetto - 1  
  - Articolo.stato = "ABROGATO"  
  - Edge ABROGA: (Normativa_abrogante) → (Articolo)  
  - Il chunk RIMANE negli indici (utile per analisi storiche)  
    con metadato valid_to per filtro del Researcher  
  
CASO 3 — Dichiarazione incostituzionalità (Corte Cost.):  
  - Articolo.stato = "INCOSTITUZIONALE"  
  - Articolo.valid_to = data_sentenza - 1  
  - Edge DICHIARA_ILLEGITTIMA: (SentenzaCorteCost) → (Articolo)  
  - Alert immediato: norme incostituzionali non possono essere  
    citate come vigenti → Reviewer blocca automaticamente  
  
CASO 4 — Rettifica GU (corrigendum):  
  - NON crea nuova versione: corregge quella esistente  
  - Aggiorna testo e hash nel nodo esistente  
  - Log corrigendum_log[]: {data, gu_ref, old_hash, new_hash}  
  - Alert: "Documenti analizzati PRIMA di {data} potrebbero  
    citare il testo precedente alla rettifica"  
  
CASO 5 — Decreto-legge non convertito (decadenza):  
  - D.L. ha valid_to = 60 giorni dalla pubblicazione (art. 77 Cost.)  
  - Se non convertito entro 60gg: stato → "DECADUTO"  
  - Edge DECADUTO_IL: (DL) → (data_decadenza)  
  - Alert agli avvocati se hanno citato il D.L. in atti pendenti  
  
PARAMETRO dataVigenza nell'API Normattiva:  
  - Permette di recuperare la versione vigente a una data specifica  
  - L'Analyst usa dataVigenza = data_stipula per contratti storici  
  - Garantisce correttezza del ragionamento inter-temporale
```

### 13.11 Questioni Aperte su Normativa API

1. **Integrazione Normattiva API** ✅ → Risolta in questa sezione
2. **Norme regionali** → Modulo futuro (§ 12.2)
3. **Versioning ontologie** → Design da completare (§ 12.1)
4. **Contrasti giurisprudenziali** → Design da completare (§ 12.1)
5. **Federated Learning** → Fase 4+ (§ 12.1)
6. **Compliance GDPR audit** → Coperta in § 9.7 (Dual Auth + WORM log)


---

*Sezione 13 aggiunta — Integrazione Normativa API**Decisioni D-19 → D-26 aggiunte al registro (vedi sotto)*

## Decisioni Architetturali D-19 → D-26


| ID   | Decisione                           | Scelta                                                   | Motivazione                                                                                 |
|------|-------------------------------------|----------------------------------------------------------|---------------------------------------------------------------------------------------------|
| D-19 | Fonte primaria normativa IT         | Normattiva REST API con AKN                              | Endpoint `ricerca/aggiornati` per change detection incrementale; AKN ha lifecycle integrato |
| D-20 | Fonte primaria normativa UE         | EUR-Lex CELLAR SPARQL                                    | Unico endpoint ufficiale strutturato con CDM ontology e relazioni consolidamento            |
| D-21 | Accesso massime Cassazione          | Italgiure via Cassa Forense                              | Unica fonte strutturata con massime ufficiali per penale + civile + tributario              |
| D-22 | Scope CEDU                          | Solo Key Cases Italia (importanza 1)                     | ~150 casi ad alto impatto vs 600 totali; ottimo rapporto rilevanza/volume                   |
| D-23 | Traduzione CEDU                     | Qwen2.5-72B + disclaimer obbligatorio                    | Server già disponibile; qualità su terminologia CEDU; mai ufficiale                       |
| D-24 | Indicizzazione bilingue CEDU        | Originale EN/FR + traduzione IT entrambi in vector index | Ricerca flessibile; avvocato può trovare con termini IT anche casi originali in EN         |
| D-25 | Disclaimer per Normattiva           | Sempre incluso nel Citation Contract                     | Non ufficialità è un dato materiale per l'avvocato che cita in atti                       |
| D-26 | Corte Costituzionale illegittimità | Nodo Articolo.stato → INCOSTITUZIONALE + alert         | Reviewer blocca citazione di norme dichiarate incostituzionali                              |


---

## 14. Gestione Credenziali nel Vault

### 14.1 Principio di Design

Le credenziali operative (Italgiure/Cassa Forense, API key Normattiva, etc.) sono gestite nella stessa infrastruttura del PII Vault, con una **terza partizione dedicata** (`credentials/`). Motivazione: condividono gli stessi requisiti (AES-256-GCM, 3-layer key management, audit trail, rotation) ma hanno un profilo di accesso diverso dai dati PII.

### 14.2 Struttura Vault Aggiornata

```python
/server/vault/  
├── tenant_A/  
│   ├── own_parties/            PII clienti (GDPR lifecycle)  
│   ├── third_parties/          PII terze parti (GDPR, dual auth)  
│   └── credentials/            ← NUOVO: credenziali operative  
│       ├── italgiure_cf.cred.enc  
│       └── normattiva_api.cred.enc  
└── _system/                    ← NUOVO: fuori dai tenant  
└── credentials/            credenziali infrastrutturali  
└── server_service.key.enc  chiave identità NormSyncAgent
```

### 14.3 Differenze PII vs Credenziali


| Aspetto           | Partizioni PII             | Partizione credentials/            |
|-------------------|----------------------------|------------------------------------|
| Accesso lettura   | Umano via PIN (DeAnonGate) | Processo server via service token  |
| Accesso scrittura | Umano via PIN              | Admin via PIN                      |
| Lifecycle GDPR    | Sì (retention, erasure)   | No                                 |
| Rotation          | Cancellazione fisica       | Versioning con grace period 15 min |
| Cache in memoria  | No (sempre decrypt)        | Sì, TTL 5 minuti                  |
| Audit trail       | Ogni de-anonimizzazione    | Ogni accesso servizio + ogni write |


### 14.4 CredentialEntry — Campi Chiave

```json
@dataclass  
class CredentialEntry:  
    credential_id: str              # "italgiure_cassa_forense"  
    credential_type: CredentialType # API_KEY | USERNAME_PASSWORD | ...  
    service_name: str               # "italgiure" | "normattiva"  
    primary_value_enc: bytes        # AES-256-GCM(password/api_key)  
    secondary_value_enc: bytes|None # AES-256-GCM(username) se serve  
    version: int                    # incrementato ad ogni rotation  
    accessible_by_services: list    # ["normsync_agent"]  
    previous_version_enc: bytes|None# vecchia cred durante grace period  
    rotation_grace_until: datetime|None  # 15 min dopo rotation  
    status: str                     # active | rotating | revoked  
    # NESSUN campo GDPR (retention_years, gdpr_basis, ecc.)
```

### 14.5 Due Path di Accesso

**Path automatico (NormSyncAgent → vault):**

```python
NormSyncAgent avvio  
→ vault.get_credential("italgiure_cassa_forense", service_token)  
→ verify service_token (JWT firmato con chiave NormSyncAgent)  
→ verifica service in accessible_by_services  
→ decrypt AES-256-GCM  
→ cache in-memory TTL 5 min  
→ audit log: SERVICE_ACCESS_SUCCESS  
→ restituisce credenziale in chiaro (solo in RAM, mai su disco)
```

**Path umano (admin IT → vault):**

```python
Admin esegue: pi run legal-admin rotate-credential --id italgiure_cf  
  → inserisce PIN admin (getpass, non passa per LLM)  
  → vault.set_credential(..., admin_pin=pin)  
  → vecchia credenziale → status: "rotating" + grace period 15 min  
  → nuova credenziale → status: "active", version+1  
  → cache invalidata per questa credenziale  
  → audit log: CREDENTIAL_ROTATED | admin_id | v{N}→v{N+1}  
  → dopo 15 min: vecchia credenziale purgata automaticamente
```

### 14.6 Integrazione con CassaForenseAuthManager

```python
# PRIMA (con os.environ — rimosso):  
CF_USERNAME = os.environ["ITALGIURE_CF_USERNAME"]  # ❌  

# DOPO (con vault — corretto):  
cred = await self.vault.get_credential(  
credential_id="italgiure_cassa_forense",  
service_token=self.SERVICE_TOKEN,  
reason="italgiure_session_auth",  
)  
username, password = cred.secondary, cred.primary  
# ... usa per autenticazione  
del username, password  # dealloca subito dopo l'uso
```

### 14.7 Credenziali nel Sistema — Inventario


| Credential ID             | Servizio        | Tipo              | Accessible By                      | Note                                          |
|---------------------------|-----------------|-------------------|------------------------------------|-----------------------------------------------|
| `italgiure_cassa_forense` | ItalgiureWeb    | USERNAME_PASSWORD | normsync_agent                     | Rotation quando password CF scade             |
| `normattiva_api_key`      | Normattiva IPZS | API_KEY           | normsync_agent, ingestion_pipeline | Attualmente non richiesta (API open)          |
| `eurlex_sparql_token`     | EUR-Lex CELLAR  | API_KEY           | normsync_agent                     | Attualmente non richiesta (endpoint pubblico) |


### 14.8 Decisioni Architetturali D-27 → D-29


| ID   | Decisione                       | Scelta                                         | Motivazione                                                                                        |
|------|---------------------------------|------------------------------------------------|----------------------------------------------------------------------------------------------------|
| D-27 | Storage credenziali             | Vault partizione credentials/ (non os.environ) | Stessa infrastruttura crittografica del PII vault; audit trail; rotation centralizzata             |
| D-28 | Accesso credenziali da processo | Service token JWT (non PIN umano)              | I processi automatici non possono chiedere un PIN; il service token prova l'identità del processo |
| D-29 | Rotation credenziali            | Grace period 15 min + versioning               | Evita interruzione di sessioni in-flight durante la rotation                                       |


---

## 15. Modello di Business SaaS e Architettura Cloud

### 15.1 Visione del Prodotto

LexAgent è un prodotto ibrido **local-first + cloud SaaS**:

```python
LAPTOP (local-first, privacy garantita):  
  Inferenza quotidiana con Ollama 7B  
  Retrieval corpus privato (mai esce)  
  Orchestrazione agenti Pi  
  Workspace isolation per caso/cliente  
  
CLOUD SAAS (due funzioni distinte):  
  Funzione 1: KB normativa condivisa (una sola copia per tutti gli studi)  
  Funzione 2: Heavy document processing (LLM 72B su GPU cloud)  
  
SEPARAZIONE DEI DATI:  
  Normativa pubblica → cloud (uguale per tutti, zero privacy issues)  
  Documenti privati  → locale (mai escono dal laptop senza anonimizzazione)
```

### 15.2 Multi-tenancy — Chiarimento Definitivo

Il Punto 5 della revisione critica (§ precedente) era parzialmente corretto:

- **Sul laptop**: workspace isolation semplice ✓ (non multi-tenancy)
- **Sul SaaS cloud**: multi-tenancy reale con isolamento crittografico ✓ (necessario)

La multi-tenancy non è stata eliminata — è stata spostata dove appartiene.

### 15.3 Query Anonymization Gateway (A2)

Prima che qualsiasi dato lasci il laptop verso il SaaS, passa per il `SaaSBoundaryGate`:

```python
REGOLA FONDAMENTALE:  
Il SaaS è un servizio di conoscenza legale generica.  
Non ha bisogno di sapere CHI è il cliente o QUALE è il caso.  

FLUSSO:  
Query normativa pura → scan sicurezza → invia as-is se pulita  
Documento per heavy processing → verifica già anonimizzato  
→ se no: anonymize() prima dell'invio  
Escalation Research Packet → sanitize query context  

PLACEHOLDER CLOUD:  
[PER_CLOUD_001], [ORG_CLOUD_001] ecc.  
Session-scoped: non entrano nel vault permanente  
Il SaaS vede solo placeholder, mai PII reali
```

### 15.4 Architettura Retrieval Ibrido

```python
# Esecuzione parallela:  
saas_results = await query_saas_normative_kb(query, intent, tenant_id)  
local_results = await query_local_private_corpus(query, intent)  
  
# Merge con boost corpus privato:  
final = merge_and_rerank(  
    saas_results,  
    local_results,  
    weights={"saas_normativa": 1.0, "local_private": 1.3}  
)
```

### 15.5 Offline Mode

```python
FUNZIONA OFFLINE:  
✅ Retrieval su cache locale KB normativa (sync periodico)  
✅ Retrieval corpus privato locale  
✅ Inferenza Ollama 7B  
✅ Workflow A e B completi  

NON FUNZIONA OFFLINE:  
❌ Aggiornamenti KB normativi in tempo reale  
❌ Heavy processing su LLM 72B cloud  
→ Accumulo in coda SQLite locale, eseguiti al reconnect  

FRESHNESS INDICATOR nel Research Packet:  
"kb_source": "saas_live" | "local_cache"  
"cache_age_hours": N  
"warning": "KB offline: ultima sync Nh fa"
```

### 15.6 Modello di Monetizzazione (Raccomandato)

**Struttura**: canone base per studio (KB normativa) + consumo heavy processing


| Tier           | Prezzo         | Target        | Incluso                                                                         |
|----------------|----------------|---------------|---------------------------------------------------------------------------------|
| **SOLO**       | €59/mese     | 1-2 avvocati  | KB normativa base, 20 doc/mese heavy, client locale                             |
| **STUDIO**     | €49/avv/mese | 3-15 avvocati | KB completa (tutti i moduli), 100 doc/mese heavy, corpus condiviso tra avvocati |
| **ENTERPRISE** | Custom         | 16+ / reti    | SLA, KB verticali custom, API integrazioni, unlimited heavy                     |


**Overage heavy processing**: €1.50/doc (SOLO), €1.00/doc (STUDIO)**Query Q&A (Workflow A)**: illimitate su tutti i tier (costo marginale trascurabile)

**Nota**: "documento" = elaborazione completa Workflow B su un file (non le query singole)

### 15.7 Progressione MVP → SaaS

```python
RING 0 — MVP locale (settimane 1-4):  
  Server = laptop in LAN dello studio pilota  
  Valida: l'avvocato usa il sistema? Quali workflow?  
  
RING 1 — Server on-premise (mese 2-4):  
  Server fisico in LAN, Tier 2 pipeline attiva  
  Valida: il heavy processing giustifica il costo?  
  
RING 2 — SaaS privato beta (mese 5-8):  
  Server migra in cloud, 2-3 studi pilota  
  Una KB condivisa per tutti i beta tester  
  Valida: la KB condivisa funziona? Quanto pesa il compute?  
  
RING 3 — SaaS pubblico (mese 9+):  
  Lancio con pricing definitivo  
  Self-service onboarding  
  NormSync completamente automatico
```

### 15.8 Moat Competitivo nel Tempo

```python
OGGI:     KB normativa pronta + inferenza locale privata  
(nessun concorrente italiano ha questa combinazione)  

ANNO 1-2: Feedback aggregato anonimizzato → reranking migliore per tutti  
Effetto rete: più studi → KB migliore → più studi  

ANNO 3+:  Dataset query legali italiane anonimizzate per fine-tuning  
→ LLM verticale legale IT proprietario  
→ asset che nessun competitor può replicare rapidamente
```

### 15.9 Decisioni Architetturali D-30 → D-34


| ID   | Decisione           | Scelta                               | Motivazione                                             |
|------|---------------------|--------------------------------------|---------------------------------------------------------|
| D-30 | SaaS funzioni       | KB condivisa + heavy compute         | Ammortizza NormSync e GPU su tutti i tenant             |
| D-31 | Multi-tenancy       | Solo SaaS cloud (non laptop)         | Su laptop è security theater; in cloud è necessaria   |
| D-32 | Query anonymization | SaaSBoundaryGate obbligatorio        | Il SaaS non deve mai vedere PII reali                   |
| D-33 | Offline mode        | Cache locale con freshness indicator | Avvocati in tribunale non hanno sempre connessione      |
| D-34 | Pricing model       | Base fisso + variabile heavy compute | Allinea ricavo al valore; accessibile per studi piccoli |

---

## 16. SPEC — Modulo Normattiva + Chunk Tipizzati

> Sessione di design: 2026-05-28  
> Stato: **Approvato** — pronto per implementazione

---

### 16.1 Motivazione

AiUra deve essere autonoma dal progetto sorgente LegalAgentLab per quanto riguarda
il corpus normativo pubblico. Obiettivi:

1. Creare `aiura_legal.normattiva_docs` — collezione dedicata, gestita da AiUra
2. Popolarla subito tramite mirror da `legal_lab.normattiva_docs` (zero re-fetch)
3. Tipizzare i chunk con tre dimensioni ortogonali (`corpus`, `fonte`, `testo_tipo`)
   per abilitare ricerche su sottoinsiemi (es. "solo codice civile", "solo studio")
4. Predisporre un client Normattiva per fetch incrementale futuro

---

### 16.2 Architettura & File

```
NUOVI:
aiura_legal/ingestion/normattiva/
  __init__.py
  connector.py        ← copiato da LegalAgentLab (sync, standalone)
                        NormattivaSearchConnector, NormattivaFetcher, NormattivaWebFetcher
  parser.py           ← adapter: dict Normattiva → schema AiUra
                        fonte_from_doc(), NormattivaDocAdapter
  pipeline.py         ← NormattivaPipeline: normattiva_docs → Chunk tipizzati

scripts/
  mirror_normattiva.py     ← CLI sync: legal_lab → aiura_legal (avvio immediato)
  fetch_normattiva.py      ← CLI sync: API Normattiva → aiura_legal (uso futuro)
  migrate_chunks_typing.py ← backfill corpus/fonte/testo_tipo su chunk esistenti

tests/
  test_normattiva_parser.py
  test_normattiva_pipeline.py

MODIFICATI:
  aiura_legal/ingestion/mongodb/models.py          ← Chunk: +corpus, +fonte, +testo_tipo
  aiura_legal/ingestion/pipeline.py                ← Tier1Pipeline: imposta corpus="studio"
  aiura_legal/core/retrieval/bm25_retriever.py     ← filtro subset via maschera numpy
  aiura_legal/core/retrieval/vector_retriever.py   ← where filter ChromaDB
  aiura_legal/core/retrieval/hybrid_retriever.py   ← propaga chunk_filter
  scripts/build_indexes.py                         ← legge da aiura_legal.chunks
```

---

### 16.3 Modello Dati

#### Nuova collezione `aiura_legal.normattiva_docs`

Schema identico a `legal_lab.normattiva_docs` (compatibilità garantita):

```
source_id, urn, act_urn, doc_type, tipo_provvedimento,
titolo, titolo_articolo, articolo_num, numero, anno,
gazzetta_anno, gazzetta_numero, data_inizio_vigenza,
codice_provvedimento, text, testo_tipo, ingested_at
```

Campo aggiunto da AiUra:
- `aiura_imported_at: datetime` — timestamp del mirror/fetch

Indici: `urn` (unique), `act_urn`, `testo_tipo`.

#### `Chunk` model — campi aggiunti

```python
corpus:     str = "studio"     # "normattiva" | "studio"
fonte:      str = "altro"      # vedi tassonomia §16.4
testo_tipo: str = "normativo"  # "normativo" | "formula"
```

I default coprono tutti i chunk esistenti e futuri del tipo "documento studio".
Nessuna breaking change per codice che non passa questi campi.

---

### 16.4 Tassonomia `fonte`

Funzione `fonte_from_doc(doc: dict) -> str` in `normattiva/parser.py`.
Match applicato in ordine di priorità (top-down):

| `fonte` | Condizione |
|---------|-----------|
| `codice_civile` | `act_urn` contains `regio.decreto:1942-03-16;262` |
| `codice_penale` | `act_urn` contains `regio.decreto:1930-10-19;1398` |
| `codice_proc_civile` | `act_urn` contains `regio.decreto:1940-10-28;1443` |
| `codice_proc_penale` | `act_urn` contains `decreto.del.presidente.della.repubblica:1988-09-22;447` |
| `legge_costituzionale` | `tipo_provvedimento` = "LEGGE COSTITUZIONALE" |
| `legge` | `tipo_provvedimento` = "LEGGE" |
| `dlgs` | `tipo_provvedimento` = "DECRETO LEGISLATIVO" |
| `dl` | `tipo_provvedimento` = "DECRETO-LEGGE" |
| `dpr` | `tipo_provvedimento` contains "PRESIDENTE DELLA REPUBBLICA" |
| `rd` | `tipo_provvedimento` = "REGIO DECRETO" |
| `dm` | `tipo_provvedimento` contains "MINISTERIALE" |
| `altro` | fallback |

Per chunk da documenti studio: `fonte = "altro"` (raffinabile in futuro).

---

### 16.5 Flusso Mirror (avvio immediato)

```
legal_lab.normattiva_docs          (pymongo sync, read-only)
  │
  ▼  scripts/mirror_normattiva.py  (batch 500, upsert by URN, idempotente)
  │
aiura_legal.normattiva_docs
  │
  ▼  NormattivaPipeline.chunk_collection()
  │    Chunker sliding window 512 tok / overlap 64
  │    corpus="normattiva", fonte=fonte_from_doc(doc), testo_tipo propagato
  │
aiura_legal.chunks
```

Flags di `mirror_normattiva.py`:
- `--dry-run` — conta senza scrivere
- `--limit N` — test su N documenti
- `--skip-chunks` — solo mirror normattiva_docs, no chunking
- `--only-chunks` — normattiva_docs già popolata, ri-chunka soltanto

---

### 16.6 Flusso Fetch da API (uso futuro)

```
Normattiva REST API + sito web (AJAX chain)
  │
  ▼  scripts/fetch_normattiva.py
  │    NormattivaSearchConnector → discover URNs per tipo/anno
  │    NormattivaFetcher / NormattivaWebFetcher → fetch articoli
  │    NormattivaDocAdapter → normalizza schema
  │
aiura_legal.normattiva_docs  (upsert by URN, salta atti già presenti)
  │
  ▼  NormattivaPipeline.chunk_collection()
  │
aiura_legal.chunks
```

Interfaccia identica a LegalAgentLab per familiarità:
`--tipo`, `--anno-da`, `--anno-a`, `--codice`, `--dry-run`, `--limit`.

---

### 16.7 Filtro Subset nel Retrieval

#### BM25Retriever

Salva `bm25_meta.json` accanto a `bm25.pkl`:
```json
{
  "doc_id_1": {"corpus": "normattiva", "fonte": "codice_civile", "testo_tipo": "normativo"},
  "doc_id_2": {"corpus": "studio",     "fonte": "altro",         "testo_tipo": "normativo"}
}
```

Filtro a search-time tramite maschera numpy (O(n), nessun re-build indice):
```python
scores = self._bm25.get_scores(tokenized_query)
if chunk_filter:
    mask = np.array([
        all(self._meta[did].get(k) == v for k, v in chunk_filter.items())
        for did in self._doc_ids
    ], dtype=bool)
    scores[~mask] = 0.0
```

#### VectorRetriever (ChromaDB)

Il parametro `where` viene passato direttamente alla collection:
```python
results = self._collection.query(
    query_embeddings=[embedding],
    where=chunk_filter or None,
    n_results=top_k,
)
```

Supporta operatori ChromaDB (`$and`, `$or`, `$in`) per filtri composti.

#### HybridRetriever — nuova firma

```python
def search(
    self,
    query: str,
    intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
    top_k_retrieve: int = 15,
    top_k_rerank: int = 7,
    valid_on: Optional[date] = None,
    chunk_filter: Optional[dict] = None,
) -> list[SearchResult]: ...

def build_research_packet(
    self, query, intent, valid_on=None,
    chunk_filter: Optional[dict] = None,
) -> ResearchPacket: ...
```

`chunk_filter=None` → comportamento invariato, zero regressioni.

---

### 16.8 Build Indexes aggiornato

`build_indexes.py` legge da `aiura_legal.chunks` (non più da `legal_lab.normattiva_docs`).
I Document.metadata includono i tre nuovi campi per ChromaDB e BM25:

```python
metadata={
    "corpus":     chunk.get("corpus", "studio"),
    "fonte":      chunk.get("fonte", "altro"),
    "testo_tipo": chunk.get("testo_tipo", "normativo"),
    # campi esistenti invariati:
    "source":     chunk.get("source_id", ""),
    "titolo":     chunk.get("titolo", ""),
    "articolo":   chunk.get("articolo_num", ""),
    "valid_from": str(chunk.get("valid_from", "") or ""),
    "valid_to":   str(chunk.get("valid_to", "") or ""),
}
```

`BM25Retriever.save()` scrive `bm25_meta.json` in parallelo a `bm25.pkl`.

---

### 16.9 Migrazione Chunk Esistenti

`scripts/migrate_chunks_typing.py` — esecuzione una tantum, idempotente:

```python
db["chunks"].update_many(
    {"corpus": {"$exists": False}},
    {"$set": {"corpus": "studio", "fonte": "altro", "testo_tipo": "normativo"}},
)
```

---

### 16.10 Aggiornamento Tier1Pipeline

In `aiura_legal/ingestion/pipeline.py`, alla creazione di ogni `Chunk`:
```python
Chunk(..., corpus="studio", fonte="altro", testo_tipo="normativo")
```

Tutti i documenti depositati dall'avvocato d'ora in avanti avranno i campi
valorizzati direttamente, senza necessità di migrazione futura.

---

### 16.11 Test Plan

| Test | File | Cosa verifica |
|------|------|---------------|
| `test_fonte_from_doc` | `test_normattiva_parser.py` | classificazione corretta per tutti gli 11 valori `fonte` |
| `test_mirror_idempotent` | `test_normattiva_pipeline.py` | due run stesso batch → stesso conteggio in DB |
| `test_chunk_typing_normattiva` | `test_normattiva_pipeline.py` | chunk da normattiva hanno corpus/fonte/testo_tipo valorizzati |
| `test_chunk_typing_studio` | `test_pipeline.py` (update) | Tier1Pipeline imposta `corpus="studio"` |
| `test_bm25_filter` | `test_retrieval.py` (update) | filtro corpus isola correttamente il subset |
| `test_vector_filter` | `test_retrieval.py` (update) | ChromaDB where filter ritorna solo chunk matching |
| `test_hybrid_filter_none` | `test_retrieval.py` (update) | `chunk_filter=None` non rompe il retrieval esistente |

Tutti i test usano mongomock-motor e dati sintetici.

---

### 16.12 Ordine di Implementazione

```
1.  models.py         — Chunk: +corpus, +fonte, +testo_tipo con defaults
2.  migrate_chunks_typing.py  — backfill chunk esistenti (eseguibile subito)
3.  pipeline.py       — Tier1Pipeline: imposta corpus="studio" sui nuovi chunk
4.  normattiva/connector.py   — copia da LegalAgentLab
5.  normattiva/parser.py      — fonte_from_doc() + test_normattiva_parser.py
6.  normattiva/pipeline.py    — NormattivaPipeline
7.  mirror_normattiva.py      — CLI mirror da legal_lab
8.  fetch_normattiva.py       — CLI fetch da API (futuro)
9.  bm25_retriever.py         — filtro subset + bm25_meta.json
10. vector_retriever.py       — where filter ChromaDB
11. hybrid_retriever.py       — chunk_filter passthrough
12. build_indexes.py          — legge da aiura_legal.chunks
13. test_normattiva_pipeline.py — mirror idempotency
```
