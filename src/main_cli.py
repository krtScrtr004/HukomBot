import os
from uuid import UUID

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import torch

from pathlib import Path
from typing import List

from model.document_model import Document, DocumentCreate, DocumentSearch
from model.chunk_model import Chunk, ChunkCreate, ChunkSearchKeyword, ChunkSearchVector
from repository.document_repository import DocumentRepository
from repository.chunk_repository import ChunkRepository

from openai import OpenAIError
from util.extract_text_from_pdf import extract_text_from_pdf
from util.timer import timer
from service.embed_service import EmbedService
from service.chatbot_service import ChatbotService
from service.reranker_service import RerankService
from util.utility import get_project_root, is_pdf
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()
HP_API_KEY = os.getenv("HP_API_KEY")
login(HP_API_KEY)  # Login to HuggingFace

DEFAULT_DATA_PATH = get_project_root() / "data"

# Repositories ----------
document_repo = DocumentRepository()
chunk_repo = ChunkRepository()
# ----------

# Services ----------
chatbot_service = ChatbotService()
embed_service = EmbedService()
reranker_service = RerankService()
# ----------


def get_options_choice(min: int = 1, max: int = 3) -> int:
    choice = 0
    while True:
        choice = int(input("Select from menu: "))

        if choice < min or choice > max:
            print("INVALID MENU OPTION!")
        else:
            return choice


def embed_data(path: str | Path = DEFAULT_DATA_PATH):
    global document_repo

    # Convert string to Path object if necessary
    path_obj = Path(path)

    # Make sure the path actually exists
    if not path_obj.exists():
        print(f"Error: Path {path_obj} does not exist.")
        return

    print("Starting Process...")

    pdf_count = 0
    chunks_count = 0

    pdf_id_created = []

    with timer("Embedding process"):
        try:

            def process_document_entry(pdf: Path):
                nonlocal pdf_id_created, chunks_count, pdf_count

                print(f"Processing file: {pdf.name}...")
                document = DocumentCreate(
                    title=pdf.stem,
                    file_type=pdf.suffix,
                )
                created_documnent = document_repo.create(
                    document
                )  # Create document instance

                pdf_id_created.append(created_documnent.id)
                chunks_count += process_pdf_chunk(pdf, created_documnent.id)
                pdf_count += 1

                torch.cuda.empty_cache()  # Free unused VRAM

            # Check if the provided path itself is a file or a folder
            if path_obj.is_file():
                # Handle single file processing
                if is_pdf(path_obj):  # or is_pdf(path_obj)
                    process_document_entry(path_obj)
                else:
                    print(f"Skipping non-PDF file: {path_obj.name}")

            elif path_obj.is_dir():
                # Handle folder processing by scanning its contents
                for item in path_obj.glob("*"):
                    # If sub-item is a subfolder, process its PDFs
                    if item.is_dir():
                        print(f"Processing folder: {item.name}...")

                        for pdf in item.glob("*.pdf"):
                            process_document_entry(pdf)

                        print(f"Finished processing folder: {item.name}...")

                    # If sub-item is a PDF file in the root of the folder
                    elif item.is_file() and is_pdf(item):
                        process_document_entry(item)

            print(f"{pdf_count} documents added...")
            print(f"{chunks_count} chunks added...")
        except Exception as ex:
            print("Something went wrong! Performing rollback operation...")
            document_repo.delete_many(
                pdf_id_created
            )  # Rollback document / chunks created
            raise ex


def process_pdf_chunk(pdf: Path, document_id: UUID):
    global chunk_repo, embed_service

    print(f"Extracting text from {pdf.name}...")

    chunks = extract_text_from_pdf(pdf)
    if not chunks:
        print(f"No text extracted from {pdf.name}.")
        return 0

    # Create the chunk models
    document_chunks = {}
    for i, chunk in enumerate(chunks):
        document_chunks[i] = ChunkCreate(
            document_id=document_id,
            chunk_number=i,
            chunk_text=chunk["document"],
            section=chunk["section"],
        )

    with timer(f"Embed {pdf.stem}"):
        print("Generating embeddings...")
        # Generate embeddings for all chunks
        texts = [chunk["document"] for chunk in chunks]
        embeddings = embed_service.embed_documents(texts)

        # Map embeddings back to the chunk models
        for i, embedding in enumerate(embeddings):
            chunk_model = document_chunks.get(i)
            if chunk_model:
                chunk_model.embedding = embedding

    print("Creating database entries...")
    chunk_repo.create_many(list(document_chunks.values()))

    return len(document_chunks)


def analyze_case():
    print('Type "quit" to exit\n')

    with timer("Analyze Case"):
        case_facts = get_case_facts()
        if not case_facts:
            return

        print("---")

        # Extract legal issues
        print("Extracting legal issues...")
        legal_issues = chatbot_service.extract_issues(case_facts)
        if not legal_issues:
            raise RuntimeError(
                "Cannot extract legal issues from the case facts provided."
            )

        # Genrate legal queries
        print("Generating legal queries...")
        generated_queries = chatbot_service.generate_queries(legal_issues)
        if not generated_queries:
            raise RuntimeError(
                "Cannot generate queries from the legal issues extracted."
            )

        # Vector Search
        print("Performing vector search...")
        vector_results = retrieve_from_vector_search(generated_queries)
        print(f"Retrieve {len(vector_results)} from vector search...")
        # Keyword Search
        print("Performing keyword search...")
        keyword_result = retrieve_from_keyword_search(generated_queries)
        print(f"Retrieve {len(keyword_result)} from keyword search...")

        print("Reranking results...")
        deduplicated_result = deduplicate_results(vector_results, keyword_result)
        reranked_result = reranker_service.rerank(
            "\n".join(case_facts), deduplicated_result
        )

        print("Generating final answer...")
        final_answer = chatbot_service.generate_answer(
            "\n".join(case_facts), format_context(reranked_result[:10])
        )
        print("---")
        print("ANSWER:\n")

        print(final_answer)
        print(f"{"=" * 45}")


def get_case_facts() -> List[str] | None:
    MIN = 8
    MAX = 500

    facts = []

    counter = 1
    while True:
        print(f"{29 * "-"}")
        print(f"Enter fact no. {counter}:")
        print(f"{29 * "-"}")
        print(f"MIN = {MIN}, MAX = {MAX}")
        print("Enter an empty line to finish")
        print(f"{29 * "-"}")
        fact = input()
        if not fact:
            return facts
        elif fact == "quit":
            return None
        elif len(fact) < MIN or len(fact) > MAX:
            print(f"Fact must be between {MIN} and {MAX} only")
            continue

        facts.append(fact)
        counter += 1


def retrieve_from_vector_search(queries: list[str]):
    global chunk_repo, embed_service

    results = []
    for query in queries:
        embedding = embed_service.embed_query(query)  # Create embeddings for query
        results.extend(
            chunk_repo.search_vector(ChunkSearchVector(embeddings=embedding))
        )

    return results


def retrieve_from_keyword_search(queries: list[str]):
    global chunk_repo

    results = []
    for query in queries:
        results.extend(chunk_repo.search(ChunkSearchKeyword(text=query)))

    return results


def deduplicate_results(
    vector_results: List[Chunk], keyword_results: List[Chunk]
) -> list[Chunk]:
    unique_results = {}

    combined = vector_results + keyword_results
    for item in combined:
        if item.id not in unique_results:
            unique_results[item.id] = item

    return list(unique_results.values())


def format_context(results: List[Chunk]) -> str:
    formatted_results = []
    for result in results:
        title = result.document.title
        chunk_text = result.chunk_text
        section = result.section if result.section else "Unknown Section"

        formatted_results.append(
            f"Title: {title}\nSection: {section}\nDocument: {chunk_text}"
        )

    return "\n\n---\n\n".join(formatted_results)


def main():
    while True:
        print(f"{"=" * 45}")
        print("     Philippine Law & Legislation Chatbot     ")
        print(f"{"=" * 45}")
        print("MENU: ")
        print("[1] Embed Data")
        print("[2] Analyze Case")
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
                embed_data(path)
                print("Data embedded successfully...")
            except Exception as ex:
                print(f"AN ERROR OCCURRED: {ex}")
        elif choice == 2:
            try:
                pass
                analyze_case()
            except OpenAIError as ex:
                print(f"AN ERROR OCCURRED WHILE USING LLM SERVICE: {ex}")
            except Exception as ex:
                print(f"AN ERROR OCCURRED: {ex}")
        else:
            print("Good Bye!")
            print(f"{"=" * 45}")
            break


if __name__ == "__main__":
    main()
