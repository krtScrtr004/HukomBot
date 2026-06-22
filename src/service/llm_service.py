import os
from dotenv import load_dotenv
from openai import OpenAI
from util.utility import format_conversation_history

load_dotenv()


class LLMService:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
    MODEL = "openrouter/owl-alpha"

    def __init__(self):
        self.client = OpenAI(
            api_key=LLMService.OPEN_ROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    def chat(self, prompt: str) -> str | None:
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )

        if not response.choices:
            return None

        return response.choices[0].message.content

    def expand_query(self, query: str) -> list[str] | None:
        prompt = f"""
        Generate 5 alternative legal search queries for the following question.

        Requirements:
        - Preserve the original meaning.
        - Use legal terminology when appropriate.
        - Keep each query concise.
        - Return only the queries, one per line.

        Question:
        {query}
        """

        response = self.client.chat.completions.create(
            model=self.MODEL,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.choices[0].message.content
        if not content:
            return [query]
        
        generated_queries = [
            line.strip() for line in content.splitlines() if line.strip()
        ]

        return [query, *generated_queries]
    
    
    def contextualize_query(self, query: str, conversation_history: list[dict[str, str]]):
        prompt = f"""
        You are a query contextualization assistant for a Philippine legal retrieval system.

        Your task is to convert the user's latest question into a complete, standalone search query suitable for retrieving relevant legal documents.

        Requirements:

        * Preserve the user's intent.
        * Resolve all references using the conversation history.
        * Include the names of relevant laws, Republic Acts, codes, articles, sections, agencies, or legal concepts when available.
        * Use terminology likely to appear in legal documents.
        * Do not answer the question.
        * Do not explain your reasoning.
        * Return only the rewritten search query.
        * If the question already stands alone, return it unchanged.

        Conversation History:
        {format_conversation_history(conversation_history)}

        Latest User Question:
        {query}

        Standalone Search Query:
        """
        
        response = self.client.chat.completions.create(
            model=self.MODEL,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        
        content = response.choices[0].message.content
        if not content:
            return query # Just return original query if LLM fails
        
        return content
        
