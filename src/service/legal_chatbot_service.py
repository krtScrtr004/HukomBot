from service.llm_service import LLMService
from util.utility import format_conversation_history


class LegalChatbotService:
    def __init__(self):
        self.llm_service = LLMService()

    def extract_issues(self, case_facts: list[str]) -> list[str]:
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

        response = self.llm_service.chat(prompt=prompt, temprature=0.1, max_tokens=500)
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

    def generate_queries(
        self, legal_issues: list[str], query_count: int = 5
    ) -> list[str]:
        issues = "\n".join(f"- {issue}" for issue in legal_issues)

        prompt = f"""
        You are a legal search query generator for a Philippine law retrieval system.

        Task: Based on the following legal issues, generate {query_count} concise and diverse legal search queries optimized for retrieving relevant Philippine laws, jurisprudence, and legal documents.

        Legal Issues:
        {issues}

        Requirements:
        1. Preserve the core legal meaning of each issue.
        2. Use standard Philippine legal terminology (e.g., "damages," "jurisdiction," "qualified theft," "indispensable party").
        3. Include relevant legal concepts, Republic Act numbers, codal provisions, or party roles where applicable.
        4. Vary the phrasing across queries to maximize retrieval coverage.
        5. Keep each query under 15 words.
        6. Do not answer the issues or provide explanations.
        7. Return only the queries, one per line, with no numbering, bullets, or extra text.
        """

        response = self.llm_service.chat(prompt=prompt, temprature=0)
        if not response.choices:
            return [legal_issues[0]] if legal_issues else []

        content = response.choices[0].message.content or ""
        queries = [line.strip() for line in content.splitlines() if line.strip()]

        return queries if queries else legal_issues

    def contextualize_query(
        self, query: str, conversation_history: list[dict[str, str]]
    ):
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
            return query  # Just return original query if LLM fails

        return content

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
