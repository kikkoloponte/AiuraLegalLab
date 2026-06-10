"""
OpenAI-compatible async client — per LMStudio (o qualsiasi endpoint /v1/).

Stessa interfaccia di OllamaClient: generate(), chat(), generate_stream(),
is_available(). Questo permette di passare da Ollama a LMStudio cambiando
solo il client nel costruttore dell'orchestratore.

Configurazione .env:
    AIURA_LLM_BACKEND=lmstudio          # oppure "ollama" (default)
    LMSTUDIO_BASE_URL=http://127.0.0.1:1234
    LMSTUDIO_MODEL=qwen2.5-7b-instruct

Circuit-breaker integrato: dopo un ConnectError, skippa i tentativi
per CIRCUIT_COOLDOWN_S secondi.
"""
from __future__ import annotations

import json
import re
import time
from typing import AsyncIterator, Optional

import httpx
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.agents.ollama_client import CIRCUIT_COOLDOWN_S

# Qwen3/QwQ e altri modelli "thinking" emettono <think>…</think> prima della
# risposta reale. Li strip qui una volta sola invece di farlo in ogni agente.
_RE_THINK = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


def _strip_think(text: str) -> str:
    """Rimuove i blocchi <think>…</think> prodotti dai modelli con reasoning mode."""
    return _RE_THINK.sub("", text).lstrip()


class LMStudioSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    lmstudio_base_url: str = "http://127.0.0.1:1234"
    lmstudio_model: str = "qwen2.5-7b-instruct"
    lmstudio_timeout: float = 300.0   # secondi — modelli 14b+ possono impiegare >2min per fase


_lm_settings = LMStudioSettings()


class OpenAICompatClient:
    """
    Client async per endpoint OpenAI-compatibili (LMStudio, vLLM, LocalAI…).

    Mappa i metodi dell'interfaccia OllamaClient su /v1/chat/completions.
    `generate()` usa un singolo messaggio utente (+ system se fornito).
    `chat(messages)` passa i messaggi così come sono.
    """

    def __init__(
        self,
        base_url: str = _lm_settings.lmstudio_base_url,
        model: str = _lm_settings.lmstudio_model,
        timeout: float = _lm_settings.lmstudio_timeout,
        connect_timeout: float = 3.0,
        circuit_cooldown: float = CIRCUIT_COOLDOWN_S,
        no_think: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._timeout = timeout
        self._httpx_timeout = httpx.Timeout(timeout=timeout, connect=connect_timeout)
        # Circuit-breaker
        self._circuit_cooldown = circuit_cooldown
        self._circuit_open_until: float = 0.0
        # Qwen3/Qwen3.5: se True aggiunge /no_think ai messaggi utente
        self._no_think = no_think

    # ------------------------------------------------------------------
    # Circuit-breaker
    # ------------------------------------------------------------------

    def _circuit_is_open(self) -> bool:
        return time.monotonic() < self._circuit_open_until

    def _trip_circuit(self) -> None:
        self._circuit_open_until = time.monotonic() + self._circuit_cooldown
        logger.debug(
            f"[OpenAICompatClient] Circuit breaker aperto per {self._circuit_cooldown}s"
        )

    def _reset_circuit(self) -> None:
        if self._circuit_open_until > 0.0:
            logger.debug("[OpenAICompatClient] Circuit breaker chiuso")
        self._circuit_open_until = 0.0

    # ------------------------------------------------------------------
    # Helpers payload
    # ------------------------------------------------------------------

    def _build_messages(
        self,
        prompt: str,
        system: Optional[str] = None,
    ) -> list[dict]:
        msgs: list[dict] = []
        if system:
            msgs.append({"role": "system", "content": system})
        # Qwen3/Qwen3.5 supportano /no_think per disabilitare il reasoning mode.
        # Lo aggiungiamo all'inizio del messaggio utente per evitare che il
        # thinking budget consumi tutti i token prima della risposta reale.
        # Il prefisso viene ignorato silenziosamente da modelli che non lo capiscono.
        user_content = f"/no_think\n{prompt}" if self._no_think else prompt
        msgs.append({"role": "user", "content": user_content})
        return msgs

    def _build_payload(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
        n_ctx: int = 0,
        n_batch: int = 0,
    ) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        # n_ctx / n_batch: ignorati da LM Studio ma salvati come memo
        # e rispettati da backend compatibili (llama.cpp, vLLM con estensioni)
        if n_ctx > 0:
            payload["n_ctx"] = n_ctx
        if n_batch > 0:
            payload["n_batch"] = n_batch
        return payload

    @staticmethod
    def _extract_content(choice: dict) -> str:
        """
        Estrae il testo dalla choice LM Studio.

        LM Studio ≥ 0.3.6 con modelli Qwen3/thinking separa il ragionamento
        in `reasoning_content` e la risposta finale in `content`.
        Se `content` è vuoto (es. max_tokens esaurito nel pensiero),
        usa `reasoning_content` come fallback (meglio di risposta vuota).
        """
        msg = choice.get("message", {})
        content = msg.get("content", "") or ""
        if not content.strip():
            # Fallback: reasoning_content come risposta (caso max_tokens stretto)
            content = msg.get("reasoning_content", "") or ""
            if content:
                logger.debug(
                    "[OpenAICompatClient] content vuoto — uso reasoning_content "
                    f"({len(content)} chars)"
                )
        return _strip_think(content)

    # ------------------------------------------------------------------
    # Generate (non-streaming) — mappa su chat/completions
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        n_ctx: int = 0,
        n_batch: int = 0,
    ) -> str:
        if self._circuit_is_open():
            raise httpx.ConnectError("All connection attempts failed")

        messages = self._build_messages(prompt, system)
        payload = self._build_payload(messages, temperature, max_tokens, n_ctx=n_ctx, n_batch=n_batch)

        async with httpx.AsyncClient(timeout=self._httpx_timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                )
                resp.raise_for_status()
                self._reset_circuit()
                data = resp.json()
                return self._extract_content(data["choices"][0])
            except httpx.ConnectError:
                self._trip_circuit()
                raise
            except httpx.TimeoutException:
                logger.error(
                    f"LMStudio timeout ({self._timeout}s) per model={self.model}"
                )
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"LMStudio HTTP error: {e.response.status_code}")
                raise

    # ------------------------------------------------------------------
    # Chat (non-streaming)
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        if self._circuit_is_open():
            raise httpx.ConnectError("All connection attempts failed")

        payload = self._build_payload(messages, temperature, max_tokens)

        async with httpx.AsyncClient(timeout=self._httpx_timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                )
                resp.raise_for_status()
                self._reset_circuit()
                data = resp.json()
                return self._extract_content(data["choices"][0])
            except httpx.ConnectError:
                self._trip_circuit()
                raise
            except httpx.TimeoutException:
                logger.error("LMStudio chat timeout")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"LMStudio chat HTTP error: {e.response.status_code}")
                raise

    # ------------------------------------------------------------------
    # Generate streaming (SSE)
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        system: Optional[str] = None,
    ) -> AsyncIterator[str]:
        if self._circuit_is_open():
            raise httpx.ConnectError("All connection attempts failed")

        messages = self._build_messages(prompt, system)
        payload = self._build_payload(messages, temperature, max_tokens, stream=True)

        async with httpx.AsyncClient(timeout=self._httpx_timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    self._reset_circuit()
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        raw = line[len("data: "):]
                        if raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw)
                            delta = (
                                chunk.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            pass
            except httpx.ConnectError:
                self._trip_circuit()
                raise

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/v1/models")
                if resp.status_code == 200:
                    self._reset_circuit()
                    return True
                return False
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/v1/models")
            resp.raise_for_status()
            return [m["id"] for m in resp.json().get("data", [])]
