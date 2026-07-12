from openai import AsyncOpenAI
from backend.app.core.settings import Settings


class LLMService:
    __model: str|None = None
    
    def __init__(self, model: str = Settings.LLM_MODEL):
        self.__client = AsyncOpenAI(
            api_key=Settings.LLM_API_KEY,
            base_url=Settings.LLM_BASE_URL,
        )
        LLMService.__model = model

    async def chat(
        self,
        prompt: str,
        model: str = __model,
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str | None:
        response = await self.__client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not response.choices:
            return None

        return response.choices[0].message.content