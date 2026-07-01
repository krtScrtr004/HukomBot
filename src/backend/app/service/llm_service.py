import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMService:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
    MODEL = "openrouter/owl-alpha"

    def __init__(self):
        self.client = OpenAI(
            api_key=LLMService.OPEN_ROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    def chat(
        self,
        prompt: str,
        model: str = MODEL,
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str | None:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not response.choices:
            return None

        return response.choices[0].message.content