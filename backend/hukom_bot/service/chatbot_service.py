from typing import List

from backend.hukom_bot.database.database import Database
from backend.hukom_bot.service.llm_service import LLMService
from backend.hukom_bot.enum.case_analysis_answer_format import CaseAnalysisAnswerFormat
from backend.hukom_bot.schema.case_analysis_schema import CaseAnalysisGeneratedAnswer

from backend.hukom_bot.util.utility import format_conversation_history


class ChatbotService:
    def __init__(self, db: Database, llm_service: LLMService):
        self._db = db
        self._llm_service = llm_service

    async def extract_issues(self, case_facts: List[str]) -> List[str]:
        facts = "\n".join(f"- {fact}" for fact in case_facts)

        prompt = f"""
        You are an expert legal analyst specializing in Philippine law.

        Your task is to identify and extract the substantive legal issues that arise from the facts provided.

        ## CASE FACTS:

        ## {facts}

        INSTRUCTIONS:

        1. Identify each distinct substantive legal issue or question of law raised by the facts.

        2. Express each issue as a concise, standalone legal question beginning with "Whether...".

        3. Use standard Philippine legal terminology whenever appropriate.

        4. When reasonably supported by the facts, identify:

        * Causes of action;
        * Legal remedies;
        * Civil Code provisions;
        * Revised Penal Code provisions;
        * Republic Acts;
        * Legal doctrines;
        * Contractual relationships;
        * Party roles.

        5. Prefer legally precise issues over generic descriptions.

        Example:

        Avoid:

        * Whether there was a contract dispute.
        * Whether damages may be awarded.

        Prefer:

        * Whether the defendant substantially breached its contractual obligations.
        * Whether the plaintiff may rescind the contract under Article 1191 of the Civil Code.
        * Whether defective performance gives rise to liability for damages.

        6. Focus primarily on substantive legal issues, including:

        * Liability;
        * Validity of contracts;
        * Criminal responsibility;
        * Damages;
        * Ownership;
        * Employment rights;
        * Jurisdiction when central to the dispute.

        7. Do not include procedural matters unless they are essential to resolving the case.

        8. If multiple parties are involved, clearly identify the affected parties.

        9. Do not invent statutes, article numbers, or legal doctrines that are not reasonably supported by the facts.

        10. Return only the legal issues, one per line, with no numbering, bullets, labels, or additional text.

        OUTPUT FORMAT:

        Whether ...
        Whether ...
        Whether ...
        """

        response = await self._llm_service.chat(
            prompt=prompt, temperature=0.1, max_tokens=500
        )
        if not response:
            return []

        return [line.strip() for line in response.splitlines() if line.strip()]

    async def generate_queries(
        self, legal_issues: List[str], query_count: int = 5
    ) -> List[str]:
        issues = "\n".join(f"- {issue}" for issue in legal_issues)

        prompt = f"""
        You are a legal search query generator for a Philippine law retrieval system.

        Task:
        Generate {query_count} concise, diverse, and legally precise search queries that will maximize retrieval of relevant Philippine jurisprudence, statutes, codal provisions, and legal doctrines.

        ## LEGAL ISSUES:

        ## {issues}

        REQUIREMENTS:

        1. Preserve the original legal meaning of each issue.
        2. Use standard Philippine legal terminology and doctrine.
        3. Expand issues into related legal concepts, causes of action, remedies, defenses, codal provisions, or legal principles when reasonably supported.
        4. Include specific references to:

        * Civil Code articles
        * Revised Penal Code provisions
        * Republic Act numbers
        * Rules of Court provisions
        * Legal doctrines
            whenever clearly applicable.
        5. Prefer legally meaningful search terms over plain-language descriptions.
        6. Generate queries with varied perspectives, including:

        * Legal issues
        * Causes of action
        * Remedies
        * Elements of liability
        * Applicable statutes or codal provisions
        * Party relationships or roles
        7. Keep each query under 15 words.
        8. Do not invent statutes, article numbers, or legal doctrines.
        9. Do not answer the legal issues or provide explanations.
        10. Return only the queries, one per line, with no numbering, bullets, or additional text.

        Examples:

        Issue:
        Incomplete performance of a software development contract.

        Possible queries:
        Article 1191 rescission for reciprocal obligations
        Damages for defective performance of service contracts
        Specific performance versus rescission under Civil Code
        Recovery of damages for incomplete contractual performance
        Breach of software development service agreement Philippines
        """

        response = await self._llm_service.chat(prompt=prompt, temperature=0)
        if not response:
            return [legal_issues[0]] if legal_issues else []

        queries = [line.strip() for line in response.splitlines() if line.strip()]

        return queries if queries else legal_issues

    async def generate_answer(
        self,
        case_facts: List[str],
        context: str,
        answer_format: CaseAnalysisAnswerFormat = CaseAnalysisAnswerFormat.PLAINTEXT,
    ) -> CaseAnalysisGeneratedAnswer:
        retrieved_cases = "\n---\n".join(case_facts)

        prompt = f"""
        You are a legal research assistant specializing in Philippine law.

        Your task is to analyze the user's facts and the retrieved legal cases, then identify which cases may be relevant for legal research purposes.

        IMPORTANT RULES:

        1. Use ONLY the information contained in the retrieved legal cases.
        2. Do NOT invent or assume legal cases, citations, facts, doctrines, rulings, legal principles, or statutory provisions that do not appear in the retrieved materials.
        3. If the retrieved information is insufficient to support a conclusion, explicitly state that the information is insufficient.
        4. Base relevance primarily on factual similarities and legal issues, not merely because the cases involve the same statute, offense, or legal provision.
        5. Clearly distinguish between:
        - Facts provided by the user;
        - Facts found in the retrieved legal cases; and
        - Assumptions, uncertainties, or missing information.
        6. Do NOT provide definitive legal advice, predict case outcomes, determine liability, or recommend legal actions.
        7. Present findings objectively and professionally.
        8. Do NOT merely restate the elements of a crime or legal provision unless those elements are explicitly discussed in the retrieved cases.
        9. Every factual statement, doctrine, ruling, or legal principle must be supported by the retrieved materials.
        10. If none of the retrieved cases have meaningful factual or legal similarities to the user's facts, do not include them under "Relevant Cases." Instead, explain that no sufficiently relevant cases were identified.
        11. If a case appears only marginally related, explain why the connection is weak and assign an appropriate confidence level.
        12. Generate the answer in {answer_format.value} format.
        13. If the requested format is HTML, DO NOT include the <html>, <head>, <body>, or <footer> tags.
        14. Return ONLY a valid JSON object. Do NOT wrap the JSON in markdown code fences or include any additional commentary.

        ==========================================================================
        USER FACTS
        ==========================================================================

        {retrieved_cases}

        ==========================================================================
        RETRIEVED LEGAL CASES
        ==========================================================================

        {context}

        ==========================================================================
        OUTPUT FORMAT
        ==========================================================================

        Return a valid JSON object with EXACTLY the following structure:

        {{
            "title": "Generated title",
            "answer": "Generated answer"
        }}

        Rules for the "title":

        1. Summarize the primary legal issue or factual dispute discussed.
        2. Keep the title between 5 and 12 words.
        3. Be concise, descriptive, and neutral.
        4. Do NOT use markdown.
        5. Do NOT include quotation marks inside the title.
        6. Do NOT begin with words such as:
        - Analysis
        - Legal Research
        - Case Analysis
        - Relevant Cases
        7. If the legal issue cannot be confidently determined from the user's facts, generate a neutral descriptive title such as:
        - "Potential Labor Law Issues"
        - "Possible Criminal Law Issues"
        - "Potential Contract Law Dispute"

        Rules for the "answer":

        The value of the "answer" field must contain the complete analysis using the following structure.

        ==========================================================================
        Relevant Cases
        ==========================================================================

        For each relevant case:

        ### [Case Name]

        **Facts from the Retrieved Case**

        - Summarize only the facts contained in the retrieved materials.
        - Do not add or infer facts.

        **Why it may be relevant**

        - Identify specific factual similarities between the user's facts and the retrieved case.
        - Explain the legal issue addressed by the court.
        - Explain any important factual or legal distinctions.
        - If factual similarities cannot be established from the retrieved materials, explicitly state so.

        **Key Doctrine or Ruling**

        - Summarize the doctrine or ruling strictly from the retrieved materials.
        - If the retrieved materials do not provide sufficient information regarding the doctrine or ruling, explicitly state:

        "The retrieved materials do not provide sufficient information regarding the court's doctrine or ruling."

        **Confidence**

        Assign one of the following:

        - High — Strong factual and legal similarities supported by the retrieved materials.
        - Medium — Some similarities exist, but important distinctions or uncertainties remain.
        - Low — The connection is primarily based on a general legal topic or statute rather than closely related facts.

        --------------------------------------------------------------------------

        Overall Analysis

        ### Possible Legal Issues

        - Identify the possible legal issues suggested by the user's facts.
        - Clearly indicate when an issue is inferred rather than explicitly established.

        ### Common Themes Among Retrieved Cases

        - Describe recurring factual patterns, legal questions, or doctrines found in the retrieved cases.
        - Do not generalize beyond the retrieved materials.

        ### Limitations

        - Identify missing information in either the user's facts or the retrieved legal cases.
        - Explain any limitations that affect the reliability or completeness of the analysis.

        --------------------------------------------------------------------------

        Disclaimer

        This analysis is intended solely for legal research and informational purposes. It is based only on the retrieved legal materials provided and does not constitute legal advice or a substitute for consultation with a qualified legal professional.
        """

        response = await self._llm_service.chat(
            temperature=0,
            prompt=prompt,
        )

        if not response:
            raise RuntimeError("LLM service failed to generate the final answer")

        return CaseAnalysisGeneratedAnswer.model_validate_json(response)

    async def contextualize_query(
        self, query: str, conversation_history: List[dict[str, str]]
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

        response = await self._llm_service.chat(
            temperature=0,
            prompt=prompt,
        )
        if not response:
            return query  # Just return original query if LLM fails

        return response

    async def expand_query(self, query: str) -> List[str] | None:
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

        response = await self._llm_service.chat(
            temperature=0,
            prompt=prompt,
        )
        if not response:
            return [query]

        generated_queries = [
            line.strip() for line in response.splitlines() if line.strip()
        ]

        return [query, *generated_queries]
