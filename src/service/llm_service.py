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
    
    def extract_legal_issues(self, case_facts: list[str]) -> list[str]:
        facts = "\n".join(f"- {fact}" for fact in case_facts)
        
        prompt = f"""
        You are an expert legal analyst specializing in Philippine Law. Your task is to extract the specific legal issues raised by the following facts.

        ### Case Facts:
        {facts}

        ### Instructions:
        1. Identify each distinct legal issue or question of law that arises from the facts.
        2. Express each issue as a concise, standalone legal question or statement (e.g., "Whether the employer validly dismissed the employee for just cause").
        3. Focus on substantive legal issues (e.g., liability, jurisdiction, validity of a contract). Do not include procedural matters unless they are central to the case.
        4. If multiple parties are involved, specify who the issue affects (e.g., "Whether Person A is liable to Person B for damages").
        5. Return only the list of legal issues, one per line.

        ### Output Format:
        Legal Issue 1: ...
        Legal Issue 2: ...
        ...
        """
        
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )

        if not response.choices:
            return []

        content = response.choices[0].message.content or ""
        issues = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if "." in line and line.split(".", 1)[0].strip().isdigit():
                line = line.split(".", 1)[1].strip().lstrip(":").strip()
            issues.append(line)

        return issues if issues else content.splitlines()

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
    
    # TODO: Remove this
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
        
