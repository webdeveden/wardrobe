from functools import lru_cache

from openai import AsyncOpenAI

from app.config import settings


class LLMNotConfiguredError(RuntimeError):
    pass


@lru_cache
def get_llm_client() -> AsyncOpenAI:
    """Shared OpenRouter client (OpenAI-compatible API)."""
    if not settings.openrouter_api_key:
        raise LLMNotConfiguredError("OPENROUTER_API_KEY is not configured")
    return AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        default_headers={
            "HTTP-Referer": settings.frontend_origin,
            "X-Title": "Wardrobe Catalog",
        },
    )
