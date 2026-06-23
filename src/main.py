import os
from pathlib import Path
from chromadb import Collection
from chromadb.errors import ChromaError
from database.database import Database
from openai import OpenAIError
from util.extract_text_from_pdf import extract_text_from_pdf
from service.embed_service import EmbedService
from service.llm_service import LLMService
from rich.console import Console
from rich.panel import Panel
from util.utility import get_project_root, format_context, is_pdf
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()
HP_API_KEY = os.getenv("HP_API_KEY")
login(HP_API_KEY)  # Login to HuggingFace

CONVERSATION_WINDOW_COUNT = 5
DEFAULT_DATA_PATH = get_project_root() / "data"

db = Database()
collection = db.get_or_create_collection()
llm_client = LLMService()

console = Console()
conversation_history = []


def get_options_choice(min: int = 1, max: int = 3) -> int:
    choice = 0
    while True:
        choice = int(input("Select from menu: "))

        if choice < min or choice > max:
            print("INVALID MENU OPTION!")
        else:
            return choice


def embed_data(collection: Collection, path: str | Path = DEFAULT_DATA_PATH):
    # Convert string to Path object if necessary
    path_obj = Path(path)

    # Make sure the path actually exists
    if not path_obj.exists():
        print(f"Error: Path {path_obj} does not exist.")
        return
    
    print("Starting process...")
    
    pdf_count = 0
    chunks_count = 0

    # Check if the provided path itself is a file or a folder
    if path_obj.is_file():
        # Handle single file processing
        if is_pdf(path_obj):  # or is_pdf(path_obj)
            print(f"Processing file: {path_obj.name}...")
            chunks_count += process_pdf(path_obj, collection)
            pdf_count += 1
        else:
            print(f"Skipping non-PDF file: {path_obj.name}")

    elif path_obj.is_dir():
        # Handle folder processing by scanning its contents
        for item in path_obj.glob("*"):
            # If sub-item is a subfolder, process its PDFs
            if item.is_dir():
                print(f"Processing folder: {item.name}...")

                for pdf in item.glob("*.pdf"):
                    chunks_count += process_pdf(pdf, collection)
                    pdf_count += 1

                print(f"Finished processing folder: {item.name}...")

            # If sub-item is a PDF file in the root of the folder
            elif item.is_file() and is_pdf(item):
                print(f"Processing file: {item.name}...")
                chunks_count += process_pdf(item, collection)
                pdf_count += 1

    print(f"{pdf_count} documents added...")
    print(f"{chunks_count} chunks added...")


def process_pdf(pdf: Path, collection: Collection) -> int:
    chunk_count = 0

    ids = []
    documents = []
    metadatas = []

    print(f"Extracting text from {pdf.name}...")
    document_chunks = extract_text_from_pdf(pdf)
    for j, chunk in enumerate(document_chunks):
        chunk_count += 1

        ids.append(f"{str(pdf.stem)}_chunk_{str(j)}")
        metadatas.append({"title": pdf.stem, "section": chunk["section"]})
        documents.append(chunk["document"])

    if len(ids) > 0 and len(documents) > 0 and len(metadatas) > 0:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    print(f"Finished processing {pdf.name}...")

    return chunk_count


def start_conversation():
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

        choice = get_options_choice()
        print(f"{"=" * 45}")

        if choice == 1:
            try:
                path = input(
                    "Use absolute path -> leave blank to use default data folder\nEnter path to file / folder: "
                )
                if not path:
                    path = DEFAULT_DATA_PATH

                print(f"{"=" * 45}")
                embed_data(collection, path)
                print("Data embedded successfully...")
            except ChromaError as ex:
                print(f"AN ERROR OCCURRED WHILE EMBEDDING DATA: {ex.message}")
            except Exception as ex:
                print(f"AN ERROR OCCURRED: {ex}")
        elif choice == 2:
            try:
                start_conversation()
            except OpenAIError as ex:
                print(f"AN ERROR OCCURRED WHILE USING LLM SERVICE: {ex}")
            except ChromaError as ex:
                print(f"AN ERROR OCCURRED WHILE EMBEDDING QUERY: {ex.message}")
            except Exception as ex:
                print(f"AN ERROR OCCURRED: {ex}")
        else:
            print("Good Bye!")
            print(f"{"=" * 45}")
            break


if __name__ == "__main__":
    main()
