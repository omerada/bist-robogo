# Source: Doc 10 §Faz 3 Sprint 3.1 — OpenRouter LLM istemcisi
"""OpenRouter API async istemcisi — chat completions endpoint."""

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """OpenRouter API hatası."""

    def __init__(self, status_code: int, message: str, raw: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.raw = raw or {}
        super().__init__(f"OpenRouter {status_code}: {message}")


class OpenRouterClient:
    """OpenRouter chat completions async istemcisi.

    Kullanım:
        client = OpenRouterClient()
        response = await client.chat_completion(messages=[...])
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        timeout: int | None = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.OPENROUTER_API_KEY.get_secret_value()
        self.base_url = (base_url or settings.OPENROUTER_BASE_URL).rstrip("/")
        self.model = model or settings.OPENROUTER_DEFAULT_MODEL
        self.max_tokens = max_tokens or settings.OPENROUTER_MAX_TOKENS
        self.temperature = temperature if temperature is not None else settings.OPENROUTER_TEMPERATURE
        self.timeout = timeout or settings.OPENROUTER_TIMEOUT

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bist-robogo.dev",
            "X-Title": "BIST RoboGO",
        }

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> dict[str, Any]:
        """OpenRouter chat completion isteği gönder.

        Args:
            messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
            model: Model override (opsiyonel)
            max_tokens: Max token override
            temperature: Sıcaklık override
            response_format: JSON mode vb. (opsiyonel)

        Returns:
            OpenRouter API yanıtı (dict)

        Raises:
            OpenRouterError: API hatası durumunda
        """
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }

        if response_format:
            payload["response_format"] = response_format

        url = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as http:
                resp = await http.post(url, json=payload, headers=self._headers())

            if resp.status_code != 200:
                error_body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_body.get("error", {}).get("message", resp.text[:200])
                logger.error("OpenRouter API error %s: %s", resp.status_code, error_msg)
                raise OpenRouterError(resp.status_code, error_msg, error_body)

            data = resp.json()
            logger.debug(
                "OpenRouter completion — model=%s, usage=%s",
                data.get("model"),
                data.get("usage"),
            )
            return data

        except httpx.TimeoutException:
            logger.error("OpenRouter timeout (%ss)", self.timeout)
            raise OpenRouterError(408, f"İstek zaman aşımına uğradı ({self.timeout}s)")

        except httpx.HTTPError as exc:
            logger.error("OpenRouter HTTP error: %s", exc)
            raise OpenRouterError(502, f"HTTP bağlantı hatası: {exc}")

    async def get_content(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> str:
        """Kolaylık metodu — sadece metin içeriğini döner."""
        data = await self.chat_completion(messages, **kwargs)
        choices = data.get("choices", [])
        if not choices:
            raise OpenRouterError(500, "API yanıtında seçenek yok")
        return choices[0]["message"]["content"]

    async def get_json(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> dict:
        """JSON formatında yanıt al.

        response_format={"type":"json_object"} ile çağrı yapar
        ve yanıtı parse eder.
        """
        import json

        kwargs["response_format"] = {"type": "json_object"}
        content = await self.get_content(messages, **kwargs)

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("OpenRouter JSON parse error: %s — content: %s", exc, content[:500])
            raise OpenRouterError(500, f"JSON parse hatası: {exc}")

    async def list_models(self) -> list[dict]:
        """Kullanılabilir modelleri listele."""
        url = f"{self.base_url.replace('/api/v1', '')}/api/v1/models"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as http:
                resp = await http.get(url, headers=self._headers())
            if resp.status_code != 200:
                raise OpenRouterError(resp.status_code, "Model listesi alınamadı")
            data = resp.json()
            return data.get("data", [])
        except httpx.HTTPError as exc:
            logger.error("OpenRouter models list error: %s", exc)
            raise OpenRouterError(502, f"Model listesi hatası: {exc}")
