import os
from chromadb import Collection
from chromadb.errors import ChromaError
from database.database import Database
from openai import OpenAIError
from util.extract_text_from_pdf import extract_text_from_pdf
from service.embed_service import EmbedService
from service.llm_service import LLMService
from rich.console import Console
from rich.panel import Panel
from util.utility import get_project_root, format_context
from huggingface_hub import login
from dotenv import load_dotenv


load_dotenv()
HP_API_KEY = os.getenv("HP_API_KEY")
login(HP_API_KEY)  # Login to HuggingFace

CONVERSATION_WINDOW_COUNT = 5

db = Database()
collection = db.get_or_create_collection()
llm_client = LLMService()

console = Console()
conversation_history = []


def get_menu_choice() -> int:
    choice = 0
    while True:
        choice = int(input("Select from menu: "))

        if choice < 1 or choice > 3:
            print("INVALID MENU OPTION!")
        else:
            return choice


def embed_data(collection: Collection):
    print("Starting process...")

    DATA_PATH = get_project_root() / "data"

    pdf_count = 0
    chunks_count = 0

    for folder in DATA_PATH.glob("*"):
        if folder.is_dir():
            print(f"Processing folder: {folder.name}...")
            
            for pdf in folder.glob("*.pdf"):
                pdf_count += 1

                ids = []
                documents = []
                metadatas = []

                print(f"Extracting text from {pdf.name}...")
                document_chunks = extract_text_from_pdf(pdf)
                for j, chunk in enumerate(document_chunks):
                    chunks_count += 1

                    ids.append(f"{str(pdf.stem)}_chunk_{str(j)}")
                    metadatas.append({"title": pdf.stem, "section": chunk["section"]})
                    documents.append(chunk["document"])

                if len(ids) > 0 and len(documents) > 0 and len(metadatas) > 0:
                    collection.add(ids=ids, documents=documents, metadatas=metadatas)
                    
                print(f"Finished processing {pdf.name}...")
                
        print(f"Finished processing folder: {folder.name}...")

    print(f"{pdf_count} documents added...")
    print(f"{chunks_count} chunks added...")


def start_coversation():
    global conversation_history

    while True:
        print('Type "quit" to exit\n')

        query_text = input("Query: ")
        if query_text == "quit":
            break

        print("---")
        print("Searching for relevant results...")

        # Cotextualize user query based on history if contextualize_history is not empty
        if len(conversation_history) > 0:
            print("Contextualizing query based on conversation history...")
            query_text = llm_client.contextualize_query(
                query=query_text, conversation_history=conversation_history
            )

        # Add user query to conversation history
        append_conversation_history(role="User", context=query_text)

        results = retrieve(query_text=query_text)

        formatted_context = format_context(results)

        print("Generating the final answer...")
        generated_answer = generate_answer(
            question=query_text, context=formatted_context
        )
        print("---")
        print("ANSWER:\n")

        print(generated_answer)
        print(f"{"=" * 45}")

        # Add generated answer to conversation history
        append_conversation_history(role="Assistant", context=generated_answer)


def append_conversation_history(role: str, context: str):
    global conversation_history

    conversation_history.append({"role": role, "context": context})

    if len(conversation_history) >= CONVERSATION_WINDOW_COUNT:
        conversation_history = conversation_history[1:]


def retrieve(query_text: str):
    retrieved_chunks = {}

    # Expand query
    print("Expanding query...")
    expanded_queries = llm_client.expand_query(query=query_text)
    if not expanded_queries:
        raise RuntimeError("LLM service failed to expand query")

    for query in expanded_queries:
        # Get result for query N
        print(f"Retrieving results for expanded query: {query}...")
        results = collection.query(query_texts=[query], n_results=5)
        if not results:
            continue

        # Deduplicate query results while maintaining the metadata and distance
        print("Deduplicating query results...")
        for index, document in enumerate((results.get("documents") or [[]])[0]):
            chunk_id = results["ids"][0][index]
            metadata = (results.get("metadatas") or [[[]]])[0][index]
            distance = (results.get("distances") or [[[]]])[0][index]

            # Check if the chunk is not present or has lower distance than present in the retrieved_chunks
            if (
                chunk_id not in retrieved_chunks
                or distance < retrieved_chunks[chunk_id]["distance"]
            ):
                retrieved_chunks[chunk_id] = {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                }

    # Sort the result with the least distance first
    sorted_result = sorted(
        retrieved_chunks.values(), key=lambda chunk: chunk["distance"]
    )
    return sorted_result


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
    You are an expert legal assistant specializing in Philippine Laws, Legislations, and Supreme Court Jurisprudence. Your task is to answer the user's question accurately and objectively using only the provided context.

    ### Context:
    {context}

    ### Question:
    {question}

    ### Instructions & Rules:
    1. **Strict Context Adherence:** Base your answer *only* on the provided context. Do not use outside knowledge or assume/extrapolate details not explicitly stated.
    2. **Citations:** Whenever you reference a legal provision, statute, or case, you must include the exact citation from the context (e.g., "Article III, Section 1 of the 1987 Constitution," "Republic Act No. 11058, Section 4," or "G.R. No. XXXXXX").
    3. **Hierarchy of Laws & Repeals:** Philippine law follows a strict hierarchy (Constitution > Statutes/Republic Acts > Executive Orders > Administrative Rules). If the context presents conflicting rules (e.g., an older law vs. a newer amending Republic Act), prioritize the prevailing law or explicitly highlight the conflict as described in the context.
    4. **Strict Truthfulness (No Hallucinations):** If the provided context does not contain enough information to answer the question, state clearly: "Based on the provided context, the information required to answer this question is not available." Do not attempt to guess or give general legal advice.
    5. **Tone & Formatting:** Use a professional, objective, and analytical legal tone. Use bullet points and bold text to break down complex legal requirements or elements of a law.

    Format your response as follows:
    1. **Summary:**
    [Direct answer]

    2. **Legal Basis:**
    [List the relevant law, article, section, or provision]

    3. **Explanation:**
    [Detailed explanation based solely on the context]
    
    4. **References:**
    [List of references of the extracted information]
    """

    result = llm_client.chat(prompt=prompt)
    if result is None:
        raise RuntimeError("LLM service failed to return a valid response")

    return result


def main():
    while True:
        print(f"{"=" * 45}")
        print("     Philippine Law & Legislation Chatbot     ")
        print(f"{"=" * 45}")
        print("MENU: ")
        print("[1] Embed Data")
        print("[2] Start Conversation")
        print("[3] Exit")
        print(f"{"=" * 45}")

        choice = get_menu_choice()
        print(f"{"=" * 45}")

        if choice == 1:
            try:
                embed_data(collection)
                print("Data embeded successfully...")
            except ChromaError as ex:
                print(f"AN ERROR OCCURED WHILE EMBEDDING DATA: {ex.message}")
            except Exception as ex:
                print(f"AN ERROR OCCURED: {ex}")
        elif choice == 2:
            try:
                start_coversation()
            except OpenAIError as ex:
                print(f"AN ERROR OCCURED WHILE USING LLM SERVICE: {ex}")
            except ChromaError as ex:
                print(f"AN ERROR OCCURED WHILE EMBEDDING QUERY: {ex.message}")
            except Exception as ex:
                print(f"AN ERROR OCCURED: {ex}")
        else:
            print("Good Bye!")
            print(f"{"=" * 45}")
            break


if __name__ == "__main__":
    main()
