"""
QuestioneLoader — carica QuestioneGiuridica curate nel grafo giuridico.

Vedi docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md
e ontology/legal_kb_ontology.ttl (classe :QuestioneGiuridica).

Registro su disco: ontology/questioni_curate.yaml — stesso ciclo del registro
istituti (proposta con evidenza osservabile -> review umana -> trascrizione).
Ogni voce ha uno stato: "proposto" (default, in attesa di review) |
"approvato" | "rifiutato" (review fatta, scartata — resta nel file per essere
visibile in un tab "Rifiutate" della UI di gestione, non viene eliminata).
Solo le voci con stato="approvato" vengono scritte nel grafo da write_to_graph()
(tramite load_curated(only_approved=True), il default).

Nodi creati:
  QuestioneGiuridica  ID = id (slug stabile dal YAML)
                       attrs: node_type="questione", formulazione, materia,
                              parole_chiave (lista)
Archi creati:
  PERTINENTE_A   article  -> QuestioneGiuridica
  RISOLVE        sentenza -> QuestioneGiuridica

IMPORTANTE — risoluzione norme_pertinenti/decisioni_pertinenti:
il suffisso numerico dell'URN normattiva non sempre corrisponde
all'articolo_num reale del nodo (rinumerazioni storiche del Codice Civile,
vedi commit 8831b82 "normalizzazione URN rinumerati"). load_curated() quindi
NON si fida del suffisso URN: verifica che ogni id dichiarato esista
esattamente come nodo nel grafo target, e fallisce rumorosamente (ValueError)
altrimenti — niente fallback silenzioso che linkerebbe la questione
all'articolo sbagliato.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "networkx non installato. Esegui: pip install networkx>=3.3"
    ) from e

from aiura_legal.core.graph.builder import LegalGraphBuilder

_DEFAULT_REGISTRY_PATH = Path("ontology") / "questioni_curate.yaml"

STATO_PROPOSTO = "proposto"
STATO_APPROVATO = "approvato"
STATO_RIFIUTATO = "rifiutato"
_STATI_VALIDI = (STATO_PROPOSTO, STATO_APPROVATO, STATO_RIFIUTATO)


@dataclass
class QuestioneGiuridica:
    id: str
    formulazione: str
    materia: str
    parole_chiave: list[str] = field(default_factory=list)
    norme_pertinenti: list[str] = field(default_factory=list)
    decisioni_pertinenti: list[str] = field(default_factory=list)
    stato: str = STATO_PROPOSTO


class QuestioneRegistryError(ValueError):
    """Voce del registro malformata o che referenzia un nodo inesistente nel grafo."""


class QuestioneLoader:
    """
    Carica QuestioneGiuridica dal registro YAML curato e le scrive nel grafo
    come nodi + archi PERTINENTE_A/RISOLVE.

    Utilizzo tipico:
        loader = QuestioneLoader()
        questioni = loader.load_curated("ontology/questioni_curate.yaml")
        loader.write_to_graph(questioni, workspace_path="workspaces/mio-studio")
    """

    # --------------------------------------------------------------
    # Lettura registro
    # --------------------------------------------------------------

    def load_curated(
        self,
        path: str | Path = _DEFAULT_REGISTRY_PATH,
        *,
        only_approved: bool = True,
    ) -> list[QuestioneGiuridica]:
        """
        Legge il registro YAML, valida lo schema minimo di ogni voce.

        Args:
            path: percorso del registro (default ontology/questioni_curate.yaml)
            only_approved: se True (default) scarta le voci con stato diverso
                da "approvato" (proposto o rifiutato) — non vanno scritte nel
                grafo di produzione finché l'avvocato non le valida.

        Raises:
            QuestioneRegistryError: voce con campi obbligatori mancanti, id
                duplicato, o stato non in proposto|approvato|rifiutato.
        """
        p = Path(path)
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or []
        if not isinstance(raw, list):
            raise QuestioneRegistryError(f"{p}: il registro deve essere una lista YAML, trovato {type(raw)}")

        questioni: list[QuestioneGiuridica] = []
        seen_ids: set[str] = set()
        for entry in raw:
            q = self._parse_entry(entry, source=p)
            if q.id in seen_ids:
                raise QuestioneRegistryError(f"{p}: id duplicato '{q.id}'")
            seen_ids.add(q.id)
            if only_approved and q.stato != STATO_APPROVATO:
                logger.debug(f"[QuestioneLoader] '{q.id}' stato={q.stato!r}, escluso (only_approved=True)")
                continue
            questioni.append(q)

        logger.info(f"[QuestioneLoader] caricate {len(questioni)} questioni da {p} (only_approved={only_approved})")
        return questioni

    @staticmethod
    def _parse_entry(entry: dict, *, source: Path) -> QuestioneGiuridica:
        missing = [k for k in ("id", "formulazione", "materia") if not entry.get(k)]
        if missing:
            raise QuestioneRegistryError(f"{source}: voce senza campi obbligatori {missing}: {entry}")
        stato = str(entry.get("stato", STATO_PROPOSTO))
        if stato not in _STATI_VALIDI:
            raise QuestioneRegistryError(
                f"{source}: voce '{entry.get('id')}' ha stato={stato!r} non valido "
                f"(consentiti: {_STATI_VALIDI})"
            )
        return QuestioneGiuridica(
            id=str(entry["id"]),
            formulazione=str(entry["formulazione"]).strip(),
            materia=str(entry["materia"]),
            parole_chiave=list(entry.get("parole_chiave", [])),
            norme_pertinenti=list(entry.get("norme_pertinenti", [])),
            decisioni_pertinenti=list(entry.get("decisioni_pertinenti", [])),
            stato=stato,
        )

    # --------------------------------------------------------------
    # Scrittura nel grafo
    # --------------------------------------------------------------

    def write_to_graph(
        self,
        questioni: list[QuestioneGiuridica],
        workspace_path: str,
        *,
        builder: Optional[LegalGraphBuilder] = None,
    ) -> dict:
        """
        Scrive nodi QuestioneGiuridica + archi PERTINENTE_A/RISOLVE nel
        graph.json del workspace. Idempotente: rerun sullo stesso registro
        non duplica nodi/archi (nx.DiGraph.add_node/add_edge sono no-op se
        l'id/coppia esiste già con gli stessi attributi aggiornati).

        Verifica che ogni id in norme_pertinenti/decisioni_pertinenti esista
        come nodo nel grafo target PRIMA di scrivere — fallisce rumorosamente
        (QuestioneRegistryError) su un riferimento rotto, non lo scarta in
        silenzio (vedi nota su rinumerazione URN in cima al modulo).

        Returns:
            Statistiche: questioni_scritte, archi_pertinente_a, archi_risolve.
        """
        b = builder or LegalGraphBuilder()
        path = b._graph_path(workspace_path)  # noqa: SLF001 — stesso path resolver del builder
        G: nx.DiGraph = b._load(path) if path.exists() else nx.DiGraph()  # noqa: SLF001

        stats = {"questioni_scritte": 0, "archi_pertinente_a": 0, "archi_risolve": 0}

        for q in questioni:
            self._validate_refs_exist(G, q)

            G.add_node(
                q.id,
                node_type="questione",
                formulazione=q.formulazione,
                materia=q.materia,
                parole_chiave=q.parole_chiave,
            )
            stats["questioni_scritte"] += 1

            for norma_id in q.norme_pertinenti:
                if not G.has_edge(norma_id, q.id):
                    G.add_edge(norma_id, q.id, edge_type="PERTINENTE_A")
                    stats["archi_pertinente_a"] += 1

            for decisione_id in q.decisioni_pertinenti:
                if not G.has_edge(decisione_id, q.id):
                    G.add_edge(decisione_id, q.id, edge_type="RISOLVE")
                    stats["archi_risolve"] += 1

        path.parent.mkdir(parents=True, exist_ok=True)
        b._save(G, path)  # noqa: SLF001

        logger.info(f"[QuestioneLoader] write_to_graph: {stats} -> {path}")
        return stats

    @staticmethod
    def _validate_refs_exist(G: "nx.DiGraph", q: QuestioneGiuridica) -> None:
        missing = [
            ref
            for ref in (*q.norme_pertinenti, *q.decisioni_pertinenti)
            if not G.has_node(ref)
        ]
        if missing:
            raise QuestioneRegistryError(
                f"questione '{q.id}': riferimenti inesistenti nel grafo target: {missing}. "
                "Verifica il nodo reale (fonte, articolo_num) nel grafo invece di fidarti "
                "del suffisso URN — vedi nota in cima a questo modulo."
            )
