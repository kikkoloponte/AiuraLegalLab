"""
Settings Router — GET/POST /settings, GET /settings/models.

Permette di leggere e modificare la configurazione LLM dal frontend.
Il POST sovrascrive le variabili nel file .env e riavvia l'API.

Sicurezza: espone SOLO le variabili configurabili della lista bianca.
Non espone mai MongoDB URI, chiavi API, segreti.
"""
from __future__ import annotations

import asyncio
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as http_status
from loguru import logger
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/settings", tags=["settings"])

# Path del file .env nella root del progetto
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

# Variabili esposte dalla whitelist — in questo ordine nel file
_WHITELIST: list[str] = [
    "AIURA_LLM_BACKEND",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL_MAIN",
    "LMSTUDIO_BASE_URL",
    "LMSTUDIO_MODEL",
    "LMSTUDIO_TIMEOUT",
    "LLM_TEMPERATURE",
    "LLM_MAX_TOKENS_PER_PHASE",
    "RETRIEVAL_TOP_K_RERANK",
    "RETRIEVAL_TOP_K_RETRIEVE",
    "QDRANT_URL",
]

_DEFAULTS: dict[str, str] = {
    "AIURA_LLM_BACKEND":        "lmstudio",
    "OLLAMA_BASE_URL":           "http://localhost:11434",
    "OLLAMA_MODEL_MAIN":         "qwen2.5:7b",
    "LMSTUDIO_BASE_URL":         "http://127.0.0.1:1234",
    "LMSTUDIO_MODEL":            "qwen2.5-7b-instruct",
    "LMSTUDIO_TIMEOUT":          "300",
    "LLM_TEMPERATURE":           "0.10",
    "LLM_MAX_TOKENS_PER_PHASE":  "1800",
    "RETRIEVAL_TOP_K_RERANK":    "6",
    "RETRIEVAL_TOP_K_RETRIEVE":  "20",
    "QDRANT_URL":                "http://localhost:6333",
}


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

class LLMSettings(BaseModel):
    aiura_llm_backend:        str   = Field("lmstudio", pattern="^(ollama|lmstudio)$")
    ollama_base_url:          str   = "http://localhost:11434"
    ollama_model_main:        str   = "qwen2.5:7b"
    lmstudio_base_url:        str   = "http://127.0.0.1:1234"
    lmstudio_model:           str   = "qwen2.5-7b-instruct"
    lmstudio_timeout:         float = Field(300.0, ge=30, le=600)
    llm_temperature:          float = Field(0.10,  ge=0.0, le=1.0)
    llm_max_tokens_per_phase: int   = Field(1800,  ge=500, le=4000)
    retrieval_top_k_rerank:   int   = Field(6,     ge=1,   le=20)
    retrieval_top_k_retrieve: int   = Field(20,    ge=5,   le=50)

    @field_validator("ollama_base_url", "lmstudio_base_url")
    @classmethod
    def must_be_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("deve essere un URL valido (http:// o https://)")
        return v.rstrip("/")


class SettingsResponse(BaseModel):
    settings: LLMSettings
    env_path: str


class ModelsResponse(BaseModel):
    models: list[str]
    backend: str
    error: Optional[str] = None


class SaveResponse(BaseModel):
    ok: bool
    message: str


# ---------------------------------------------------------------------------
# Helpers .env
# ---------------------------------------------------------------------------

def _read_env() -> dict[str, str]:
    """Legge il file .env e restituisce un dict con tutte le variabili."""
    result: dict[str, str] = {}
    if not _ENV_PATH.exists():
        return result
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            result[key.strip()] = val.strip()
    return result


def _write_env(updates: dict[str, str]) -> None:
    """
    Aggiorna le variabili in whitelist nel file .env.
    Preserva commenti, ordine e variabili non in whitelist.
    Fa backup in .env.bak prima di scrivere.
    """
    # Backup
    if _ENV_PATH.exists():
        try:
            backup = _ENV_PATH.with_suffix(".bak")
            backup.write_text(_ENV_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as exc:
            logger.warning(f"[Settings] backup .env fallito: {exc}")

    # Leggi le righe originali
    original_lines: list[str] = []
    if _ENV_PATH.exists():
        original_lines = _ENV_PATH.read_text(encoding="utf-8").splitlines()

    # Aggiorna o aggiungi le variabili
    updated_keys: set[str] = set()
    new_lines: list[str] = []

    for line in original_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        if "=" in stripped:
            key = stripped.partition("=")[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                updated_keys.add(key)
                continue
        new_lines.append(line)

    # Aggiungi le variabili non ancora presenti
    for key in _WHITELIST:
        if key in updates and key not in updated_keys:
            new_lines.append(f"{key}={updates[key]}")

    _ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    logger.info(f"[Settings] .env aggiornato: {list(updates.keys())}")


def _settings_from_env() -> LLMSettings:
    """Costruisce LLMSettings leggendo .env (con fallback ai default)."""
    env = _read_env()

    def g(key: str) -> str:
        return env.get(key, _DEFAULTS.get(key, ""))

    return LLMSettings(
        aiura_llm_backend        = g("AIURA_LLM_BACKEND"),
        ollama_base_url          = g("OLLAMA_BASE_URL"),
        ollama_model_main        = g("OLLAMA_MODEL_MAIN"),
        lmstudio_base_url        = g("LMSTUDIO_BASE_URL"),
        lmstudio_model           = g("LMSTUDIO_MODEL"),
        lmstudio_timeout         = float(g("LMSTUDIO_TIMEOUT") or 300),
        llm_temperature          = float(g("LLM_TEMPERATURE") or 0.10),
        llm_max_tokens_per_phase = int(g("LLM_MAX_TOKENS_PER_PHASE") or 1800),
        retrieval_top_k_rerank   = int(g("RETRIEVAL_TOP_K_RERANK") or 6),
        retrieval_top_k_retrieve = int(g("RETRIEVAL_TOP_K_RETRIEVE") or 20),
    )


# ---------------------------------------------------------------------------
# Riavvio API
# ---------------------------------------------------------------------------

def _do_restart() -> None:
    """Lancia un nuovo processo API e termina quello corrente."""
    logger.info("[Settings] Riavvio API in corso...")
    subprocess.Popen(
        [sys.executable, "-m", "aiura_legal.api"],
        cwd=str(Path(__file__).resolve().parent.parent.parent),
    )
    os._exit(0)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    """Restituisce la configurazione LLM corrente letta da .env."""
    return SettingsResponse(
        settings=_settings_from_env(),
        env_path=str(_ENV_PATH),
    )


@router.get("/models", response_model=ModelsResponse)
async def get_models() -> ModelsResponse:
    """
    Interroga il backend LLM attivo per la lista dei modelli disponibili.
    Restituisce lista vuota (non errore) se il backend non è raggiungibile.
    """
    env = _read_env()
    backend = env.get("AIURA_LLM_BACKEND", "lmstudio").lower()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if backend == "ollama":
                base_url = env.get("OLLAMA_BASE_URL", "http://localhost:11434")
                resp = await client.get(f"{base_url}/api/tags")
                resp.raise_for_status()
                models = [m["name"] for m in resp.json().get("models", [])]
            else:
                base_url = env.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
                resp = await client.get(f"{base_url}/v1/models")
                resp.raise_for_status()
                models = [m["id"] for m in resp.json().get("data", [])]

        return ModelsResponse(models=sorted(models), backend=backend)

    except Exception as exc:
        logger.warning(f"[Settings] lista modelli non disponibile: {exc}")
        return ModelsResponse(models=[], backend=backend, error=str(exc))


def _require_api_key(request: Request) -> None:
    """Verifica Bearer token se AIURA_API_KEY è impostata nell'env."""
    expected = os.environ.get("AIURA_API_KEY", "").strip()
    if not expected:
        return   # API key non configurata → endpoint aperto (dev locale)
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header mancante (Bearer token richiesto)",
        )
    token = auth[len("Bearer "):]
    if token != expected:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="API key non valida",
        )


@router.post("", response_model=SaveResponse)
async def save_settings(
    request: Request,
    body: LLMSettings,
    _auth: None = Depends(_require_api_key),
) -> SaveResponse:
    """
    Salva la configurazione nel file .env e riavvia l'API.
    Il riavvio avviene 0.8s dopo la risposta per permettere al client di riceverla.
    Richiede Authorization: Bearer <AIURA_API_KEY> se la variabile è impostata.
    """
    # Mappa dal modello Pydantic alle variabili .env
    updates: dict[str, str] = {
        "AIURA_LLM_BACKEND":        body.aiura_llm_backend,
        "OLLAMA_BASE_URL":           body.ollama_base_url,
        "OLLAMA_MODEL_MAIN":         body.ollama_model_main,
        "LMSTUDIO_BASE_URL":         body.lmstudio_base_url,
        "LMSTUDIO_MODEL":            body.lmstudio_model,
        "LMSTUDIO_TIMEOUT":          str(int(body.lmstudio_timeout)),
        "LLM_TEMPERATURE":           f"{body.llm_temperature:.2f}",
        "LLM_MAX_TOKENS_PER_PHASE":  str(body.llm_max_tokens_per_phase),
        "RETRIEVAL_TOP_K_RERANK":    str(body.retrieval_top_k_rerank),
        "RETRIEVAL_TOP_K_RETRIEVE":  str(body.retrieval_top_k_retrieve),
    }

    try:
        _write_env(updates)
    except Exception as exc:
        logger.error(f"[Settings] scrittura .env fallita: {exc}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Impossibile scrivere .env: {exc}",
        )

    # Schedula riavvio dopo aver inviato la risposta
    loop = asyncio.get_running_loop()
    loop.call_later(0.8, _do_restart)

    return SaveResponse(
        ok=True,
        message="Configurazione salvata. Riavvio API in corso...",
    )
