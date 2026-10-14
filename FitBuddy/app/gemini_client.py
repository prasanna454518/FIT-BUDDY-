
import asyncio
from functools import lru_cache

from .config import settings


@lru_cache(maxsize=1)
def get_client():
    # Lazy import keeps DEMO_MODE and unit tests independent of the optional
    # external SDK while requirements.txt installs it for real Gemini usage.
    from google import genai

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


async def generate_structured(model: str, prompt: str, schema: type) -> str:
    def _call() -> str:
        from google.genai import types

        response = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.7,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return response.text

    return await asyncio.to_thread(_call)


async def generate_text(model: str, prompt: str) -> str:
    def _call() -> str:
        from google.genai import types

        response = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=600,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return response.text.strip()

    return await asyncio.to_thread(_call)
