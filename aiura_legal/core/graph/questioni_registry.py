"""
QuestioniRegistry — CRUD sul registro ontology/questioni_curate.yaml per la
UI di revisione (avvocato approva/modifica/rifiuta senza editare YAML a mano).

Vedi docs/superpowers/specs/2026-06-26-questioni-review-ui-design.md.

Distinzione rispetto a QuestioneLoader:
  QuestioneLoader   — lettura per scrivere nel grafo (only_approved filter,
                       validazione referenziale, write_to_graph)
  QuestioniRegistry — lettura/scrittura per la UI di gestione (vede TUTTE le
                       voci indipendentemente dallo stato, supporta update
                       con optimistic concurrency control)

QuestioniRegistry dipende da QuestioneLoader per il parsing/validazione delle
voci — non duplica quella logica.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from loguru import logger

from aiura_legal.core.graph.questione_loader import (
    QuestioneGiuridica,
    QuestioneLoader,
    QuestioneRegistryError,
    _STATI_VALIDI,
    _DEFAULT_REGISTRY_PATH,
)

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "networkx non installato. Esegui: pip install networkx>=3.3"
    ) from e

from aiura_legal.core.graph.builder import LegalGraphBuilder

_EDITABLE_FIELDS = frozenset({
    "formulazione", "materia", "parole_chiave",
    "norme_pertinenti", "decisioni_pertinenti", "stato",
})


class VersionConflictError(ValueError):
    """expected_version non coincide con la versione attuale del file."""


class QuestioneNotFoundError(KeyError):
    """id non presente nel registro."""


class QuestioniRegistry:
    """
    Utilizzo tipico (router FastAPI):
        registry = QuestioniRegistry()
        questioni = registry.list(stato="proposto")
        questione, version = registry.get("q1")
        questione, version = registry.update("q1", {"stato": "approvato"}, expected_version=version)
    """

    def __init__(
        self,
        path: str | Path = _DEFAULT_REGISTRY_PATH,
        *,
        workspace_path: str = "workspaces/mio-studio",
        loader: QuestioneLoader | None = None,
    ) -> None:
        self._path = Path(path)
        self._workspace_path = workspace_path
        self._loader = loader or QuestioneLoader()

    # ------------------------------------------------------------------
    # Lettura
    # ------------------------------------------------------------------

    def current_version(self) -> str:
        """
        Versione attuale del file (hash dell'intero contenuto). Il lock è a
        livello di file, non per voce: tutte le QuestioneGiuridica condividono
        questa versione in un dato istante — usata come expected_version per
        qualunque update(), indipendentemente da quale voce si stia modificando.

        Ritorna "" se il file non esiste (nessuna voce da bloccare).
        """
        if not self._path.exists():
            return ""
        return self._compute_version(self._read_raw_text())

    def list(self, stato: str | None = None) -> list[QuestioneGiuridica]:
        """
        Tutte le voci del registro (nessun filtro only_approved — a
        differenza di QuestioneLoader.load_curated, questa è la vista di
        gestione: deve mostrare anche proposto/rifiutato).

        Ritorna [] (con log warning) se il file non esiste o è vuoto —
        la UI deve mostrare "nessuna voce", non rompersi.
        """
        if not self._path.exists():
            logger.warning(f"[QuestioniRegistry] registro assente: {self._path}")
            return []
        try:
            questioni = self._loader.load_curated(self._path, only_approved=False)
        except QuestioneRegistryError as exc:
            logger.warning(f"[QuestioniRegistry] registro non leggibile: {exc}")
            return []
        if stato is not None:
            questioni = [q for q in questioni if q.stato == stato]
        return questioni

    def get(self, id: str) -> tuple[QuestioneGiuridica, str]:
        """Raises QuestioneNotFoundError se id non esiste."""
        raw_text = self._read_raw_text()
        for q in self._loader.load_curated(self._path, only_approved=False):
            if q.id == id:
                return q, self._compute_version(raw_text)
        raise QuestioneNotFoundError(id)

    # ------------------------------------------------------------------
    # Scrittura
    # ------------------------------------------------------------------

    def update(
        self,
        id: str,
        changes: dict,
        expected_version: str,
    ) -> tuple[QuestioneGiuridica, str]:
        """
        Applica changes (merge per campo) alla voce id, con optimistic
        concurrency control: se il file è cambiato da quando il chiamante
        ha letto expected_version, nessuna scrittura — VersionConflictError.

        Se changes tocca norme_pertinenti/decisioni_pertinenti, valida i
        nuovi id contro il grafo (stessa logica di
        QuestioneLoader._validate_refs_exist) PRIMA di scrivere —
        QuestioneRegistryError su id inesistente, nessuna scrittura parziale.

        Raises:
            QuestioneNotFoundError: id non nel registro.
            VersionConflictError: expected_version obsoleta.
            QuestioneRegistryError: changes con stato non valido o id
                referenziato inesistente nel grafo.
        """
        unknown_fields = set(changes) - _EDITABLE_FIELDS
        if unknown_fields:
            raise QuestioneRegistryError(f"campi non modificabili: {unknown_fields}")

        raw_text = self._read_raw_text()
        entries = yaml.safe_load(raw_text) or []
        target_index = next((i for i, e in enumerate(entries) if e.get("id") == id), None)
        if target_index is None:
            raise QuestioneNotFoundError(id)

        current_version = self._compute_version(raw_text)
        if expected_version != current_version:
            raise VersionConflictError(
                f"questione '{id}': il registro è stato modificato da quando è stato letto "
                f"(expected_version={expected_version!r}, attuale={current_version!r})"
            )

        updated_entry = {**entries[target_index], **changes}
        if updated_entry.get("stato") not in _STATI_VALIDI:
            raise QuestioneRegistryError(
                f"questione '{id}': stato={updated_entry.get('stato')!r} non valido "
                f"(consentiti: {_STATI_VALIDI})"
            )

        questione = self._loader._parse_entry(updated_entry, source=self._path)  # noqa: SLF001
        self._validate_refs_if_changed(questione, changes)

        entries[target_index] = updated_entry
        new_raw_text = yaml.safe_dump(entries, allow_unicode=True, sort_keys=False)
        self._path.write_text(new_raw_text, encoding="utf-8")

        logger.info(f"[QuestioniRegistry] update '{id}': {list(changes.keys())}")
        return questione, self._compute_version(new_raw_text)

    def _validate_refs_if_changed(self, questione: QuestioneGiuridica, changes: dict) -> None:
        """Valida norme_pertinenti/decisioni_pertinenti contro il grafo SOLO se modificati."""
        if "norme_pertinenti" not in changes and "decisioni_pertinenti" not in changes:
            return

        builder = LegalGraphBuilder()
        graph_path = builder._graph_path(self._workspace_path)  # noqa: SLF001
        if not graph_path.exists():
            logger.warning(
                f"[QuestioniRegistry] grafo assente ({graph_path}), salto validazione "
                f"referenziale per '{questione.id}' — verrà comunque validata da "
                "QuestioneLoader.write_to_graph al momento della scrittura nel grafo."
            )
            return

        G: nx.DiGraph = builder._load(graph_path)  # noqa: SLF001
        self._loader._validate_refs_exist(G, questione)  # noqa: SLF001

    # ------------------------------------------------------------------
    # Utilità
    # ------------------------------------------------------------------

    def _read_raw_text(self) -> str:
        if not self._path.exists():
            raise QuestioneRegistryError(f"registro assente: {self._path}")
        return self._path.read_text(encoding="utf-8")

    @staticmethod
    def _compute_version(raw_text: str) -> str:
        return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()[:16]
