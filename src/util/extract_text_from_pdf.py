import re
import gc
import fitz
import easyocr
import torch
from typing import cast
from pypdf import PdfReader
from transformers import AutoTokenizer
from util.utility import get_project_root
from util.timer import timer

PROJECT_ROOT = get_project_root()
OCR_RETRY_COUNT_MAX = 1

gpu_reader = easyocr.Reader(["en"], gpu=True)
cpu_reader = easyocr.Reader(["en"], gpu=False)
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")


def chunk_text(text: str, chunk_size: int = 512, overlap=80) -> list[dict[str, str]]:
    # Split on Article/Section boundaries
    boundaries = re.split(
        r"(?=\b(?:ARTICLE|ART|SECTION|SEC|SECT)\s+[IVXLC\d]+)", text, flags=re.IGNORECASE
    )

    chunks = []
    for segment in boundaries:
        header_match = re.match(
            r"(ARTICLE|ART|SECTION|SEC|SECT)\s+\S+", segment, re.IGNORECASE
        )
        header = header_match.group(0) if header_match else "Preamble"

        # Further split oversized segments by token count
        tokens = tokenizer.encode(segment, add_special_tokens=False)
        for i in range(0, len(tokens), chunk_size):
            overlapping_chunk_count = (i + chunk_size) - overlap
            chunk_tokens = tokens[i:overlapping_chunk_count]
            chunks.append(
                {"document": tokenizer.decode(chunk_tokens), "section": header}
            )

    return chunks


def extract_text_with_ocr_single_page(pdf_path, page_num: int) -> str:
    global gpu_reader, cpu_reader
    
    reader = gpu_reader    
    with timer(f"OCR {pdf_path.stem}"):
        image_name = f"{pdf_path.stem}_page_{page_num}.png"
        image_path = PROJECT_ROOT / "data/bin" / image_name

        if image_path.exists():
            print(f"Image for page {page_num} already exists. Skipping generation...")
        else:
            # Generate image for OCR if it doesn't exist
            print(f"Generating image for OCR from page {page_num}...")
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            pix = page.get_pixmap(dpi=300)
            pix.save(str(image_path))
            doc.close()
                        
        print(f"Performing OCR on page {page_num}...")
        text_lines = []
        for attempt in range(OCR_RETRY_COUNT_MAX + 1):
            try:
                results = reader.readtext(str(image_path), detail=0)
                text_lines = cast(list[str], results)
                break
            except torch.OutOfMemoryError:
                # Use CPU
                if attempt < OCR_RETRY_COUNT_MAX:
                    print(f"GPU OOM on page {page_num}, falling back to CPU...")
                    del reader
                    gc.collect()
                    torch.cuda.empty_cache()
                    reader = cpu_reader
                else:
                    raise
            except Exception:
                raise

    return "\n".join(text_lines)


def extract_text_from_pdf(pdf) -> list[dict[str, str]]:
    with timer(f"Chunk {pdf.stem}"):
        reader = PdfReader(pdf)
        all_chunks = []

        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()

            print(f"Chunking page {page_num}...")
            if page_text and page_text.strip():
                chunked_texts = chunk_text(page_text)
            else:
                # No text layer found — fallback to OCR for this page
                print(f"No text found on page {page_num}. Using OCR...")
                ocr_text = extract_text_with_ocr_single_page(pdf, page_num)
                chunked_texts = chunk_text(ocr_text)

            for chunk in chunked_texts:
                all_chunks.append(chunk)

            print(f"Page {page_num} processed with {len(chunked_texts)} chunks...")

        return all_chunks
