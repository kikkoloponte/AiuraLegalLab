"""
Ollama async client — httpx-based.
Non usa la libreria ollama ufficiale per avere pieno controllo async.

Circuit-breaker integrato: dopo il primo ConnectError, skippa i tentativi
per CIRCUIT_COOLDOWN_S secondi (default 30s) per evitare latenza inutile
quando Ollama non è avviato.
"""
from __future__ import annotations
import json
import time
from typing import AsyncIterator, Optional
import httpx
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model_main: str = "qwen2.5:7b"


_settings = OllamaSettings()

# Secondi di "riposo" dopo un ConnectError prima di ritentare
CIRCUIT_COOLDOWN_S: float = 30.0


class OllamaClient:
    """
    Client async per Ollama.
    Supporta generate (streaming e non) e chat.

    Circuit-breaker:
        Dopo il primo ConnectError, i metodi generate/chat rilanciano
        immediatamente httpx.ConnectError per CIRCUIT_COOLDOWN_S secondi,
        invece di attendere il TCP timeout ad ogni chiamata.
        Quando il cooldown scade, si ritenta la connessione reale.
    """

    def __init__(
        self,
        base_url: str = _settings.ollama_base_url,
        model: str = _settings.ollama_model_main,
        timeout: float = 120.0,
        connect_timeout: float = 3.0,
        circuit_cooldown: float = CIRCUIT_COOLDOWN_S,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._timeout = timeout
        # Timeout separati: connect breve (fail-fast), read lungo (LLM risposta).
        self._httpx_timeout = httpx.Timeout(timeout=timeout, connect=connect_timeout)
        # Circuit-breaker state
        self._circuit_cooldown = circuit_cooldown
        self._circuit_open_until: float = 0.0   # monotonic time quando riaprire

    # ------------------------------------------------------------------
    # Circuit-breaker helpers
    # ------------------------------------------------------------------

    def _circuit_is_open(self) -> bool:
        """True se il circuit breaker è aperto (non tentare la connessione)."""
        return time.monotonic() < self._circuit_open_until

    def _trip_circuit(self) -> None:
        """Apre il circuit breaker per CIRCUIT_COOLDOWN_S secondi."""
        self._circuit_open_until = time.monotonic() + self._circuit_cooldown
        logger.debug(
            f"[OllamaClient] Circuit breaker aperto per {self._circuit_cooldown}s"
        )

    def _reset_circuit(self) -> None:
        """Chiude il circuit breaker (Ollama ora disponibile)."""
        if self._circuit_open_until > 0.0:
            logger.debug("[OllamaClient] Circuit breaker chiuso — Ollama disponibile")
        self._circuit_open_until = 0.0

    # ------------------------------------------------------------------
    # Generate (non-streaming)
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        system: Optional[str] = None,
    ) -> str:
        if self._circuit_is_open():
            raise httpx.ConnectError("All connection attempts failed")

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self._httpx_timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                resp.raise_for_status()
                self._reset_circuit()
                return resp.json().get("response", "")
            except httpx.ConnectError:
                self._trip_circuit()
                raise
            except httpx.TimeoutException:
                logger.error(f"Ollama timeout ({self._timeout}s) per model={self.model}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama HTTP error: {e.response.status_code}")
                raise

    # ------------------------------------------------------------------
    # Chat (non-streaming)
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        if self._circuit_is_open():
            raise httpx.ConnectError("All connection attempts failed")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        async with httpx.AsyncClient(timeout=self._httpx_timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                resp.raise_for_status()
                self._reset_circuit()
                data = resp.json()
                return data.get("message", {}).get("content", "")
            except httpx.ConnectError:
                self._trip_circuit()
                raise
            except httpx.TimeoutException:
                logger.error("Ollama chat timeout")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama chat HTTP error: {e.response.status_code}")
                raise

    # ------------------------------------------------------------------
    # Generate streaming
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        system: Optional[str] = None,
    ) -> AsyncIterator[str]:
        if self._circuit_is_open():
            raise httpx.ConnectError("All connection attempts failed")

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self._httpx_timeout) as client:
            try:
                async with client.stream(
                    "POST", f"{self.base_url}/api/generate", json=payload
                ) as resp:
                    resp.raise_for_status()
                    self._reset_circuit()
                    async for line in resp.aiter_lines():
                        if line.strip():
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                            if data.get("done"):
                                break
            except httpx.ConnectError:
                self._trip_circuit()
                raise

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    self._reset_circuit()
                    return True
                return False
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
