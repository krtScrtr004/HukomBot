import re
import gc
import fitz
import easyocr
import torch

from typing import cast
from pathlib import Path
from pypdf import PdfReader
from transformers import AutoTokenizer

from backend.app.util.utility import get_project_root

PROJECT_ROOT = get_project_root()
OCR_RETRY_COUNT_MAX = 1

gpu_reader = easyocr.Reader(["en"], gpu=True)
cpu_reader = easyocr.Reader(["en"], gpu=False)

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")


def chunk_text(text: str, chunk_size: int = 512, overlap=80) -> list[dict[str, str]]:
    # Split on Article/Section boundaries
    boundaries = re.split(
        r"(?=\b(?:ARTICLE|ART|SECTION|SEC|SECT)\s+[IVXLC\d]+)",
        text,
        flags=re.IGNORECASE,
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


def extract_text_with_ocr_single_page(pdf_path: Path, page_num: int) -> str:
    global gpu_reader, cpu_reader
    
    def clear_cache():
        gc.collect()
        torch.cuda.empty_cache()

    reader = cpu_reader

    image_name = f"{pdf_path.stem}_{pdf_path.suffix}_page_{page_num}.png"
    
    BIN_PATH = PROJECT_ROOT / "data/bin"
    BIN_PATH.mkdir(parents=True, exist_ok=True)
    
    image_path = BIN_PATH / image_name

    if not image_path.exists():
        # Generate image for OCR if it doesn't exist
        image_path.parent.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)
        pix.save(str(image_path))
        doc.close()
        
    clear_cache()

    text_lines = []
    for attempt in range(OCR_RETRY_COUNT_MAX + 1):            
        try:
            results = reader.readtext(str(image_path), detail=0)
            text_lines = cast(list[str], results)
            break
        except torch.OutOfMemoryError:
            # Use CPU
            if attempt < OCR_RETRY_COUNT_MAX:
                del reader
                clear_cache()
                reader = cpu_reader
            else:
                raise
        except Exception:
            raise
        finally:
            clear_cache()
            
    return "\n".join(text_lines)


def extract_text_from_pdf(pdf: Path) -> list[dict[str, str]]:
    reader = PdfReader(pdf)
    all_chunks = []

    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()

        if page_text and page_text.strip():
            chunked_texts = chunk_text(page_text)
        else:
            # No text layer found — fallback to OCR for this page
            ocr_text = extract_text_with_ocr_single_page(pdf, page_num)
            chunked_texts = chunk_text(ocr_text)

        for chunk in chunked_texts:
            all_chunks.append(chunk)

    return all_chunks
