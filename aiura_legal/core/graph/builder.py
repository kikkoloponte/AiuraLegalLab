"""
LegalGraphBuilder — costruisce e aggiorna il grafo giuridico NetworkX.

Struttura del grafo (nx.DiGraph):
  Nodi article    : ID = source_id (URN)
                    attrs: node_type, fonte, titolo, articolo_num,
                           testo_tipo, valid_from, valid_to
  Nodi provvedimento: ID = "PROV:{fonte}:{titolo}"
                    attrs: node_type, fonte, titolo
  Archi:
    RINVIA      A → B  (rimando esplicito o generico)
    ABROGA      X → A  (X abroga A)
    MODIFICA    X → A  (X modifica A)
    CONTRASTA   A ↔ B  (bidirezionale, inserito manualmente o da LLM)
    APPARTIENE_A article → provvedimento

File su disco: {workspace_path}/indices/graph.json (NetworkX node-link JSON)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from loguru import logger

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "networkx non installato. Esegui: pip install networkx>=3.3"
    ) from e

from aiura_legal.core.graph.extractor import ReferenceExtractor


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

_GRAPH_FILENAME = "graph.json"
_PROV_PREFIX = "PROV"


# ---------------------------------------------------------------------------
# LegalGraphBuilder
# ---------------------------------------------------------------------------

class LegalGraphBuilder:
    """
    Costruisce e aggiorna il grafo giuridico su disco.

    Utilizzo tipico:
        builder = LegalGraphBuilder()

        # Build completo da MongoDB
        G = builder.build(workspace_path, chunks_iterable)
        # → scrive {workspace_path}/indices/graph.json

        # Update incrementale (dopo ingestione di un nuovo chunk)
        builder.update(chunk_dict, workspace_path)
    """

    def __init__(self) -> None:
        self._extractor = ReferenceExtractor()

    # ------------------------------------------------------------------
    # API pubblica
    # ------------------------------------------------------------------

    def build(
        self,
        workspace_path: str,
        chunks: list[dict],
    ) -> nx.DiGraph:
        """
        Build completo da zero: crea un nuovo grafo, itera su tutti i chunk,
        salva graph.json. Sovrascrive il file esistente.

        Args:
            workspace_path: path alla directory workspace (es. workspaces/default)
            chunks:         lista di dict chunk (da MongoDB o fixture)

        Returns:
            Il nx.DiGraph costruito (anche per uso nei test).
        """
        G: nx.DiGraph = nx.DiGraph()
        lookup: dict[tuple[str, str], str] = {}

        # Prima passata: aggiunge tutti i nodi (popola il lookup)
        for chunk in chunks:
            self._add_article_node(G, chunk)
            self._index_chunk(lookup, chunk)

        # Seconda passata: aggiunge archi (lookup completo)
        for chunk in chunks:
            self._add_edges(G, chunk, lookup)

        path = self._graph_path(workspace_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._save(G, path)

        logger.info(
            f"[GraphBuilder] build: {G.number_of_nodes()} nodi, "
            f"{G.number_of_edges()} archi → {path}"
        )
        return G

    def update(self, chunk: dict, workspace_path: str) -> None:
        """
        Aggiornamento incrementale: carica graph.json (o crea grafo vuoto),
        aggiunge nodo + archi del chunk, salva.

        Idempotente: se il nodo esiste già, gli attributi vengono aggiornati
        e gli archi vengono aggiunti solo se non presenti.

        Args:
            chunk:          dict chunk MongoDB (deve avere source_id, fonte, ecc.)
            workspace_path: path alla directory workspace
        """
        path = self._graph_path(workspace_path)
        G = self._load(path) if path.exists() else nx.DiGraph()
        lookup = self._build_lookup(G)

        self._add_article_node(G, chunk)

        # Aggiorna lookup con il nuovo nodo
        self._index_chunk(lookup, chunk)

        self._add_edges(G, chunk, lookup)

        path.parent.mkdir(parents=True, exist_ok=True)
        self._save(G, path)

    def update_batch(self, chunks: list[dict], workspace_path: str) -> None:
        """
        Aggiorna il grafo con una lista di chunk in una sola operazione load/save.
        Più efficiente di chiamare update() N volte.

        Usato dai pipeline hook dopo ogni flush batch.
        """
        if not chunks:
            return
        path = self._graph_path(workspace_path)
        G = self._load(path) if path.exists() else nx.DiGraph()
        lookup = self._build_lookup(G)

        # Prima aggiunge tutti i nodi (popola lookup)
        for chunk in chunks:
            self._add_article_node(G, chunk)
            self._index_chunk(lookup, chunk)

        # Poi aggiunge gli archi (lookup completo)
        for chunk in chunks:
            self._add_edges(G, chunk, lookup)

        path.parent.mkdir(parents=True, exist_ok=True)
        self._save(G, path)
        logger.debug(
            f"[GraphBuilder] update_batch: {len(chunks)} chunk → "
            f"{G.number_of_nodes()} nodi, {G.number_of_edges()} archi"
        )

    def reset(self, workspace_path: str) -> None:
        """Cancella graph.json per forzare un rebuild completo."""
        path = self._graph_path(workspace_path)
        if path.exists():
            path.unlink()
            logger.info(f"[GraphBuilder] reset: {path} rimosso")

    # ------------------------------------------------------------------
    # Nodi
    # ------------------------------------------------------------------

    def _add_article_node(self, G: nx.DiGraph, chunk: dict) -> None:
        """Aggiunge/aggiorna il nodo article e il nodo provvedimento collegato."""
        source_id = chunk.get("source_id", "")
        if not source_id:
            return

        fonte = chunk.get("fonte", "altro")
        titolo = chunk.get("titolo", "")

        # Nodo articolo
        G.add_node(
            source_id,
            node_type="article",
            fonte=fonte,
            titolo=titolo,
            articolo_num=chunk.get("articolo_num", ""),
            testo_tipo=chunk.get("testo_tipo", "normativo"),
            valid_from=chunk.get("valid_from"),
            valid_to=chunk.get("valid_to"),
        )

        # Nodo provvedimento (super-nodo)
        prov_id = f"{_PROV_PREFIX}:{fonte}:{titolo}"
        if not G.has_node(prov_id):
            G.add_node(prov_id, node_type="provvedimento", fonte=fonte, titolo=titolo)

        # Arco APPARTIENE_A
        if not G.has_edge(source_id, prov_id):
            G.add_edge(source_id, prov_id, edge_type="APPARTIENE_A")

    # ------------------------------------------------------------------
    # Archi
    # ------------------------------------------------------------------

    def _add_edges(
        self,
        G: nx.DiGraph,
        chunk: dict,
        lookup: dict[tuple[str, str], str],
    ) -> None:
        """
        Estrae rimandi dal testo del chunk e aggiunge archi al grafo.

        Strategia lookup a due livelli (priorità decrescente):
          1. (act_urn_base, artnum) — intra-atto esatto (es. tutti gli art. di c.c.)
          2. (fonte, artnum)        — fallback cross-atto sulla stessa categoria
        """
        source_id = chunk.get("source_id", "")
        text = chunk.get("text", "")
        fonte = chunk.get("fonte", "")
        act_urn_base = self._act_urn_base(source_id)

        if not source_id or not text:
            return

        refs = self._extractor.extract(text, fonte=fonte)
        for ref in refs:
            # Lookup a due livelli
            target_id = (
                lookup.get((act_urn_base, ref.articolo_num))
                or lookup.get((fonte, ref.articolo_num))
            )
            if not target_id or target_id == source_id:
                continue

            if not G.has_node(target_id):
                continue

            if ref.edge_type == "ABROGA":
                if not G.has_edge(source_id, target_id):
                    G.add_edge(source_id, target_id, edge_type="ABROGA")
            elif ref.edge_type == "MODIFICA":
                if not G.has_edge(source_id, target_id):
                    G.add_edge(source_id, target_id, edge_type="MODIFICA")
            else:  # RINVIA
                if not G.has_edge(source_id, target_id):
                    G.add_edge(source_id, target_id, edge_type="RINVIA")

    # ------------------------------------------------------------------
    # Lookup {(act_urn_base|fonte, articolo_num) → source_id}
    # ------------------------------------------------------------------

    def _build_lookup(self, G: nx.DiGraph) -> dict[tuple[str, str], str]:
        """Costruisce il lookup dai nodi article esistenti nel grafo."""
        lookup: dict[tuple[str, str], str] = {}
        for node_id, attrs in G.nodes(data=True):
            if attrs.get("node_type") != "article":
                continue
            fonte = attrs.get("fonte", "")
            art_num = self._norm_num(attrs.get("articolo_num", ""))
            act_urn_base = self._act_urn_base(str(node_id))
            if art_num:
                if act_urn_base:
                    lookup[(act_urn_base, art_num)] = str(node_id)
                if fonte:
                    # Fallback (non sovrascrive se già presente per altra chiave uguale)
                    lookup.setdefault((fonte, art_num), str(node_id))
        return lookup

    def _index_chunk(self, lookup: dict[tuple[str, str], str], chunk: dict) -> None:
        """Aggiunge le chiavi di lookup per un singolo chunk."""
        source_id = chunk.get("source_id", "")
        fonte = chunk.get("fonte", "")
        art_num = self._norm_num(chunk.get("articolo_num", ""))
        act_urn_base = self._act_urn_base(source_id)
        if art_num:
            if act_urn_base:
                lookup[(act_urn_base, art_num)] = source_id
            if fonte:
                lookup.setdefault((fonte, art_num), source_id)

    @staticmethod
    def _act_urn_base(source_id: str) -> str:
        """Estrae il prefisso URN dell'atto (tutto prima di '~artN').
        Es.: 'urn:nir:stato:regio.decreto:1942-03-16;262~art1218' → 'urn:nir:...;262'
        """
        if not source_id:
            return ""
        return source_id.split("~")[0]

    # ------------------------------------------------------------------
    # Serializzazione
    # ------------------------------------------------------------------

    @staticmethod
    def _graph_path(workspace_path: str) -> Path:
        return Path(workspace_path) / "indices" / _GRAPH_FILENAME

    @staticmethod
    def _save(G: nx.DiGraph, path: Path) -> None:
        data = nx.node_link_data(G, edges="edges")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=None), encoding="utf-8")

    @staticmethod
    def _load(path: Path) -> nx.DiGraph:
        data = json.loads(path.read_text(encoding="utf-8"))
        return nx.node_link_graph(data, edges="edges")

    # ------------------------------------------------------------------
    # Utilità
    # ------------------------------------------------------------------

    @staticmethod
    def _norm_num(raw: str) -> str:
        """
        Normalizza articolo_num per il lookup.
        - Rimuove prefisso 'Art.' / 'art.' (presente nei chunk da Normattiva)
        - Rimuove punteggiatura finale (es. "Art. 8." → "8")
        - strip, lowercase, normalizza spazi attorno al trattino
        Esempi: "Art. 18-bis" → "18-bis", "Art. 8." → "8", "1" → "1"
        """
        import re
        s = re.sub(r"^\s*art\.?\s*", "", raw.strip(), flags=re.I)
        s = s.rstrip(".,;:")          # rimuove punteggiatura finale
        return re.sub(r"\s*-\s*", "-", s).lower()
