from openai import AsyncOpenAI
from backend.app.core.settings import Settings


class LLMService:
    def __init__(self, model: str = Settings.NVIDIA_MODEL):
        self._client = AsyncOpenAI(
            api_key=Settings.NVIDIA_API_KEY or Settings.OPEN_ROUTER_API_KEY,
            base_url=Settings.NVIDIA_BASE_URL or Settings.OPEN_ROUTER_BASE_URL,
        )

    async def chat(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str | None:
        model = model or Settings.NVIDIA_MODEL or Settings.OPEN_ROUTER_MODEL
        response = await self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not response.choices:
            return None

        return response.choices[0].message.content
