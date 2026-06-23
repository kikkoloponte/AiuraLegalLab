"""
GraphRetriever — neighbor expansion e conflict detection sul grafo giuridico.

Utilizzo:
    retriever = GraphRetriever(workspace_path)

    if retriever.is_available:
        # Espansione con filtro vigenza
        extra = retriever.expand(source_ids, depth=1, valid_on=date(2024,1,1))

        # Conflict detection per CitationReviewer
        conflicts = retriever.get_conflicts(source_ids)

Graceful degradation: se il backend non è disponibile → is_available=False,
expand() e get_conflicts() ritornano liste vuote senza sollevare eccezioni.

Backend: AIURA_GRAPH_BACKEND="networkx" (default, file graph.json) oppure
"neo4j" (POC migrazione — vedi docker-compose.neo4j.yml e
docs/superpowers/specs per il piano completo). Stessa interfaccia pubblica
per entrambi i backend: nessun chiamante (hybrid_retriever.py, reviewer.py)
deve cambiare per passare da uno all'altro — solo la variabile d'ambiente.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "networkx non installato. Esegui: pip install networkx>=3.3"
    ) from e

from aiura_legal.core.types import SearchResult


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

_GRAPH_FILENAME = "graph.json"
_EXPANSION_EDGE_TYPES = {"RINVIA", "ABROGA", "MODIFICA", "INTERPRETA", "APPLICATA_IN"}
_CONFLICT_EDGE_TYPES = {"CONTRASTA", "ABROGA"}
_EXPANDABLE_NODE_TYPES = {"article", "sentenza"}
_LABEL_BY_NODE_TYPE = {"article": "Articolo", "provvedimento": "Provvedimento", "sentenza": "Sentenza"}


# ---------------------------------------------------------------------------
# Soglie di staleness (guardrail "Opzione A" — vedi review architetturale)
# Si applicano solo al backend "networkx" (file-based): il backend "neo4j"
# non ha questo concetto di staleness da rebuild, è il motivo della migrazione.
#
# Baseline misurata su workspace reale (2026-06-21):
#   mio-studio:  82.3 MB, 193903 nodi, 262071 archi → load totale ~1.5s
#   normattiva:   5.9 MB,  11732 nodi,  16218 archi → load totale ~0.1s
#
# Le soglie default sono ~2x la baseline più grande osservata. Se vengono
# superate stabilmente (es. dopo l'introduzione di un KG enrichment via LLM,
# che produce molti più archi/entità), è il segnale per migrare da
# NetworkX-in-RAM-da-JSON a un graph database dedicato (Neo4j/Memgraph),
# non solo per alzare la soglia.
# ---------------------------------------------------------------------------

class GraphHealthSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    graph_max_size_mb: float = 150.0
    graph_max_load_s: float = 3.0
    graph_max_age_hours: float = 168.0  # 7 giorni


_health_settings = GraphHealthSettings()


class GraphBackendSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    aiura_graph_backend: str = "networkx"  # "networkx" | "neo4j"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "aiura-poc-pw"


@dataclass
class GraphHealth:
    """Snapshot diagnostico del grafo caricato — esposto via API/log."""
    available: bool
    path: str = ""
    size_mb: float = 0.0
    load_s: float = 0.0
    node_count: int = 0
    edge_count: int = 0
    built_at: Optional[str] = None
    age_hours: Optional[float] = None
    stale_reasons: list[str] = field(default_factory=list)
    backend: str = "networkx"

    @property
    def is_stale(self) -> bool:
        return bool(self.stale_reasons)


# ---------------------------------------------------------------------------
# GraphRetriever — facade che seleziona il backend
# ---------------------------------------------------------------------------

class GraphRetriever:
    """
    Facade: sceglie il backend (networkx o neo4j) in base a
    GraphBackendSettings e delega tutte le chiamate pubbliche.

    1. expand()       — neighbor expansion per retrieval (con filtro vigenza)
    2. get_conflicts() — trova archi CONTRASTA/ABROGA per CitationReviewer
    3. get_health()    — diagnostica (size/età per networkx, conteggi per neo4j)
    """

    def __init__(self, workspace_path: str, settings: Optional[GraphBackendSettings] = None) -> None:
        s = settings or GraphBackendSettings()
        if s.aiura_graph_backend == "neo4j":
            self._impl: _BaseBackend = _Neo4jBackend(s)
        else:
            self._impl = _NetworkXBackend(workspace_path)

    @property
    def is_available(self) -> bool:
        return self._impl.is_available

    def expand(
        self,
        source_ids: list[str],
        depth: int = 1,
        edge_types: Optional[list[str]] = None,
        max_nodes: int = 10,
        valid_on: Optional[date] = None,
    ) -> list[SearchResult]:
        return self._impl.expand(source_ids, depth=depth, edge_types=edge_types, max_nodes=max_nodes, valid_on=valid_on)

    def get_conflicts(self, source_ids: list[str]) -> list[tuple[str, str, str]]:
        return self._impl.get_conflicts(source_ids)

    def get_health(self) -> GraphHealth:
        return self._impl.get_health()


# ---------------------------------------------------------------------------
# Interfaccia comune (duck typing — niente ABC per restare leggero)
# ---------------------------------------------------------------------------

class _BaseBackend:
    is_available: bool

    def expand(self, source_ids, depth, edge_types, max_nodes, valid_on) -> list[SearchResult]:
        raise NotImplementedError

    def get_conflicts(self, source_ids: list[str]) -> list[tuple[str, str, str]]:
        raise NotImplementedError

    def get_health(self) -> GraphHealth:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Backend "networkx" — file graph.json (default, comportamento storico)
# ---------------------------------------------------------------------------

class _NetworkXBackend(_BaseBackend):

    def __init__(self, workspace_path: str) -> None:
        self._path = Path(workspace_path) / "indices" / _GRAPH_FILENAME
        self._graph: Optional[nx.DiGraph] = None
        self._loaded = False
        self._health: Optional[GraphHealth] = None
        # expand()/get_conflicts()/get_health() sono chiamati da thread diversi
        # via asyncio.to_thread() sulla stessa istanza condivisa (cache per
        # workspace) — senza lock, più thread superano "if self._loaded" prima
        # che uno dei due completi il caricamento, duplicando il parsing del
        # JSON da 150MB+ sotto query concorrenti.
        self._load_lock = threading.Lock()

    @property
    def is_available(self) -> bool:
        """True se graph.json esiste sul disco."""
        return self._path.exists()

    def expand(
        self,
        source_ids: list[str],
        depth: int = 1,
        edge_types: Optional[list[str]] = None,
        max_nodes: int = 10,
        valid_on: Optional[date] = None,
    ) -> list[SearchResult]:
        if not self.is_available:
            return []

        G = self._load_graph()
        if G is None:
            return []

        allowed_types = set(edge_types) if edge_types is not None else _EXPANSION_EDGE_TYPES
        input_set = {sid.upper() for sid in source_ids}

        # BFS manuale fino a depth hop
        visited: dict[str, int] = {}   # node_id → distanza minima
        frontier = [(sid, 0) for sid in source_ids if G.has_node(sid)]

        while frontier:
            node, dist = frontier.pop(0)
            if dist >= depth:
                continue
            for _, neighbor, edge_data in G.out_edges(node, data=True):
                if edge_data.get("edge_type") not in allowed_types:
                    continue
                if neighbor.upper() in input_set:
                    continue
                n_dist = dist + 1
                if neighbor not in visited or visited[neighbor] > n_dist:
                    visited[neighbor] = n_dist
                    frontier.append((neighbor, n_dist))

        results: list[SearchResult] = []
        for node_id, dist in sorted(visited.items(), key=lambda x: x[1]):
            if len(results) >= max_nodes:
                break

            node_attrs = G.nodes.get(node_id, {})
            node_type = node_attrs.get("node_type")
            if node_type not in _EXPANDABLE_NODE_TYPES:
                continue

            # Filtro vigenza (solo articoli — le sentenze non hanno valid_from/to)
            if node_type == "article" and valid_on is not None and not self._is_valid(node_attrs, valid_on):
                continue

            score = 1.0 / (1.0 + dist)
            if node_type == "sentenza":
                snippet = (
                    f"[graph] {node_attrs.get('organo', '')} "
                    f"n.{node_attrs.get('numero', '')}/{node_attrs.get('anno', '')}"
                ).strip()
                metadata = {
                    "corpus": "giurisprudenza",
                    "organo": node_attrs.get("organo", ""),
                    "numero": node_attrs.get("numero", ""),
                    "anno": node_attrs.get("anno", ""),
                    "materia": node_attrs.get("materia", ""),
                    "graph_distance": dist,
                }
                source_layer = "giurisprudenza"
            else:
                snippet = f"[graph] {node_attrs.get('titolo', '')} {node_attrs.get('articolo_num', '')}".strip()
                metadata = {
                    "fonte": node_attrs.get("fonte", ""),
                    "titolo": node_attrs.get("titolo", ""),
                    "articolo_num": node_attrs.get("articolo_num", ""),
                    "graph_distance": dist,
                    "valid_from": node_attrs.get("valid_from"),
                    "valid_to": node_attrs.get("valid_to"),
                }
                source_layer = "normativa"

            results.append(SearchResult(
                doc_id=node_id,
                score=round(score, 4),
                snippet=snippet,
                source_id=node_id,
                retrieval_method="graph_expansion",
                source_layer=source_layer,
                metadata=metadata,
            ))

        return results

    def get_conflicts(self, source_ids: list[str]) -> list[tuple[str, str, str]]:
        if not self.is_available:
            return []

        G = self._load_graph()
        if G is None:
            return []

        id_set = set(source_ids)
        conflicts: list[tuple[str, str, str]] = []

        for sid in source_ids:
            if not G.has_node(sid):
                continue
            for _, neighbor, edge_data in G.out_edges(sid, data=True):
                if edge_data.get("edge_type") in _CONFLICT_EDGE_TYPES:
                    if neighbor in id_set:
                        conflicts.append((sid, neighbor, edge_data["edge_type"]))

        return conflicts

    def _load_graph(self) -> Optional[nx.DiGraph]:
        """Carica il grafo in memoria (lazy, una sola volta, thread-safe)."""
        if self._loaded:
            return self._graph

        with self._load_lock:
            if self._loaded:
                return self._graph
            return self._load_graph_unlocked()

    def _load_graph_unlocked(self) -> Optional[nx.DiGraph]:
        self._loaded = True
        if not self._path.exists():
            self._graph = None
            self._health = GraphHealth(available=False, path=str(self._path))
            return None

        t0 = time.monotonic()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._graph = nx.node_link_graph(data, edges="edges")
            load_s = time.monotonic() - t0
            logger.info(
                f"[GraphRetriever] caricato: {self._graph.number_of_nodes()} nodi, "
                f"{self._graph.number_of_edges()} archi in {load_s:.2f}s"
            )
            self._health = self._compute_health(load_s)
            if self._health.is_stale:
                logger.warning(
                    f"[GraphRetriever] grafo potenzialmente stale ({self._path}): "
                    f"{'; '.join(self._health.stale_reasons)}. "
                    "Verifica se serve un rebuild (scripts/build_graph.py) o se le "
                    "soglie di GraphHealthSettings vanno alzate / è il momento di "
                    "valutare un graph database dedicato."
                )
        except Exception as exc:
            logger.warning(f"[GraphRetriever] errore caricamento graph.json: {exc}")
            self._graph = None
            self._health = GraphHealth(available=False, path=str(self._path))

        return self._graph

    def _compute_health(self, load_s: float) -> GraphHealth:
        size_mb = self._path.stat().st_size / 1e6
        built_at_raw = (self._graph.graph or {}).get("built_at") if self._graph else None

        age_hours: Optional[float] = None
        if built_at_raw:
            try:
                built_at = datetime.fromisoformat(built_at_raw)
                age_hours = (datetime.now(timezone.utc) - built_at).total_seconds() / 3600
            except ValueError:
                logger.warning(f"[GraphRetriever] built_at non parsabile: {built_at_raw!r}")

        reasons: list[str] = []
        if size_mb > _health_settings.graph_max_size_mb:
            reasons.append(f"size={size_mb:.1f}MB > soglia {_health_settings.graph_max_size_mb}MB")
        if load_s > _health_settings.graph_max_load_s:
            reasons.append(f"load_s={load_s:.2f}s > soglia {_health_settings.graph_max_load_s}s")
        if age_hours is not None and age_hours > _health_settings.graph_max_age_hours:
            reasons.append(f"age={age_hours:.1f}h > soglia {_health_settings.graph_max_age_hours}h")
        elif built_at_raw is None:
            reasons.append("built_at assente (grafo costruito prima del guardrail, o mai ricostruito)")

        return GraphHealth(
            available=True,
            path=str(self._path),
            size_mb=round(size_mb, 1),
            load_s=round(load_s, 3),
            node_count=self._graph.number_of_nodes() if self._graph else 0,
            edge_count=self._graph.number_of_edges() if self._graph else 0,
            built_at=built_at_raw,
            age_hours=round(age_hours, 1) if age_hours is not None else None,
            stale_reasons=reasons,
            backend="networkx",
        )

    def get_health(self) -> GraphHealth:
        """Snapshot diagnostico del grafo (size, età, soglie). Forza il caricamento se non già fatto."""
        self._load_graph()
        return self._health or GraphHealth(available=False, path=str(self._path))

    @staticmethod
    def _is_valid(node_attrs: dict, valid_on: date) -> bool:
        """
        Ritorna True se il nodo è vigente alla data valid_on.

        Convenzioni:
          valid_from: "YYYYMMDD" o None (→ sempre valido)
          valid_to:   "YYYYMMDD", "99999999" (vigente), o None (→ vigente)
        """
        d_str = valid_on.strftime("%Y%m%d")

        vf = node_attrs.get("valid_from")
        if vf and vf != "00000000":
            if d_str < vf:
                return False  # non ancora in vigore

        vt = node_attrs.get("valid_to")
        if vt and vt != "99999999":
            if d_str > vt:
                return False  # abrogato

        return True


# ---------------------------------------------------------------------------
# Backend "neo4j" — POC migrazione (Fase C del piano)
#
# NOTA: get_health() qui NON ha lo stesso significato del backend networkx.
# Non esiste un concetto di "rebuild" o "built_at" — i dati sono persistenti
# nel DB e aggiornati incrementalmente. size_mb/load_s sono sostituiti da
# conteggi e dalla latenza della query di health-check stessa.
# ---------------------------------------------------------------------------

class _Neo4jBackend(_BaseBackend):

    def __init__(self, settings: GraphBackendSettings) -> None:
        self._settings = settings
        self._driver = None
        self._connect_failed = False

    def _get_driver(self):
        if self._driver is not None or self._connect_failed:
            return self._driver
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                self._settings.neo4j_uri,
                auth=(self._settings.neo4j_user, self._settings.neo4j_password),
            )
            driver.verify_connectivity()
            self._driver = driver
        except Exception as exc:
            logger.warning(f"[GraphRetriever:neo4j] connessione fallita: {exc}")
            self._connect_failed = True
        return self._driver

    @property
    def is_available(self) -> bool:
        return self._get_driver() is not None

    def expand(
        self,
        source_ids: list[str],
        depth: int = 1,
        edge_types: Optional[list[str]] = None,
        max_nodes: int = 10,
        valid_on: Optional[date] = None,
    ) -> list[SearchResult]:
        driver = self._get_driver()
        if driver is None or not source_ids:
            return []

        allowed_types = list(edge_types) if edge_types is not None else list(_EXPANSION_EDGE_TYPES)
        rel_pattern = "|".join(allowed_types)

        query = (
            "UNWIND $ids AS sid "
            "MATCH (start) WHERE start.urn = sid OR start.id = sid "
            f"MATCH path = (start)-[:{rel_pattern}*1..{depth}]->(n) "
            "WHERE NOT coalesce(n.urn, n.id) IN $ids "
            "WITH n, min(length(path)) AS dist "
            "RETURN n, labels(n) AS labels, dist "
            "ORDER BY dist "
            "LIMIT $max_nodes"
        )
        try:
            with driver.session() as session:
                records = session.run(
                    query, ids=source_ids, max_nodes=max_nodes,
                ).data()
        except Exception as exc:
            logger.warning(f"[GraphRetriever:neo4j] expand() fallita: {exc}")
            return []

        results: list[SearchResult] = []
        for rec in records:
            n, labels, dist = rec["n"], rec["labels"], rec["dist"]
            node_type = "sentenza" if "Sentenza" in labels else "article"

            if node_type == "article" and valid_on is not None and not self._is_valid(n, valid_on):
                continue

            score = 1.0 / (1.0 + dist)
            node_id = n.get("urn") or n.get("id")
            if node_type == "sentenza":
                snippet = f"[graph] {n.get('organo', '')} n.{n.get('numero', '')}/{n.get('anno', '')}".strip()
                metadata = {
                    "corpus": "giurisprudenza",
                    "organo": n.get("organo", ""), "numero": n.get("numero", ""),
                    "anno": n.get("anno", ""), "materia": n.get("materia", ""),
                    "graph_distance": dist,
                }
                source_layer = "giurisprudenza"
            else:
                snippet = f"[graph] {n.get('titolo', '')} {n.get('articolo_num', '')}".strip()
                metadata = {
                    "fonte": n.get("fonte", ""), "titolo": n.get("titolo", ""),
                    "articolo_num": n.get("articolo_num", ""), "graph_distance": dist,
                    "valid_from": n.get("valid_from"), "valid_to": n.get("valid_to"),
                }
                source_layer = "normativa"

            results.append(SearchResult(
                doc_id=node_id, score=round(score, 4), snippet=snippet, source_id=node_id,
                retrieval_method="graph_expansion", source_layer=source_layer, metadata=metadata,
            ))

        return results

    def get_conflicts(self, source_ids: list[str]) -> list[tuple[str, str, str]]:
        driver = self._get_driver()
        if driver is None or not source_ids:
            return []

        rel_pattern = "|".join(_CONFLICT_EDGE_TYPES)
        query = (
            f"MATCH (a)-[r:{rel_pattern}]->(b) "
            "WHERE (a.urn IN $ids OR a.id IN $ids) AND (b.urn IN $ids OR b.id IN $ids) "
            "RETURN a.urn AS a_id, a.id AS a_id2, b.urn AS b_id, b.id AS b_id2, type(r) AS edge_type"
        )
        try:
            with driver.session() as session:
                records = session.run(query, ids=source_ids).data()
        except Exception as exc:
            logger.warning(f"[GraphRetriever:neo4j] get_conflicts() fallita: {exc}")
            return []

        return [
            (rec["a_id"] or rec["a_id2"], rec["b_id"] or rec["b_id2"], rec["edge_type"])
            for rec in records
        ]

    def get_health(self) -> GraphHealth:
        driver = self._get_driver()
        if driver is None:
            return GraphHealth(available=False, backend="neo4j")

        t0 = time.monotonic()
        try:
            with driver.session() as session:
                node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
                edge_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        except Exception as exc:
            logger.warning(f"[GraphRetriever:neo4j] get_health() fallita: {exc}")
            return GraphHealth(available=False, backend="neo4j")
        load_s = time.monotonic() - t0

        # Niente concetto di staleness qui — vedi nota di modulo.
        return GraphHealth(
            available=True,
            path=self._settings.neo4j_uri,
            load_s=round(load_s, 3),
            node_count=node_count,
            edge_count=edge_count,
            backend="neo4j",
        )

    @staticmethod
    def _is_valid(node_props: dict, valid_on: date) -> bool:
        d_str = valid_on.strftime("%Y%m%d")
        vf = node_props.get("valid_from")
        if vf and vf != "00000000" and d_str < vf:
            return False
        vt = node_props.get("valid_to")
        if vt and vt != "99999999" and d_str > vt:
            return False
        return True
