import os
from typing import List, Dict
from pathlib import Path

import pdfplumber


# -----------------------------
# Document Loader
# -----------------------------

def load_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Load text from a PDF file page by page.

    Returns a list of dicts:
    [
        {
            "page_num": 1,
            "text": "..."
        }
    ]
    """
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append({
                    "page_num": i + 1,
                    "text": text.strip()
                })

    return pages


def load_text_from_txt(txt_path: str) -> str:
    """
    Load text from a plain text file.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------
# Chunking Logic
# -----------------------------

def chunk_text(
    text: str,
    document_id: str,
    chunk_size: int = 1000,
    overlap: int = 100
) -> List[Dict]:
    """
    Chunk text into overlapping segments.

    Returns:
    [
        {
            "chunk_id": "...",
            "document_id": "...",
            "text": "..."
        }
    ]
    """

    chunks = []
    start = 0
    chunk_index = 1

    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk_text = text[start:end]

        chunks.append({
            "chunk_id": f"{document_id}_chunk_{chunk_index}",
            "document_id": document_id,
            "text": chunk_text.strip()
        })

        start = end - overlap
        chunk_index += 1

    return chunks


def chunk_pages(
    pages: List[Dict],
    document_id: str,
    chunk_size: int = 1000,
    overlap: int = 100
) -> List[Dict]:
    """
    Chunk PDF pages while preserving page metadata.
    """

    all_chunks = []

    for page in pages:
        page_chunks = chunk_text(
            text=page["text"],
            document_id=f"{document_id}_page_{page['page_num']}",
            chunk_size=chunk_size,
            overlap=overlap
        )

        for chunk in page_chunks:
            chunk["page_num"] = page["page_num"]

        all_chunks.extend(page_chunks)

    return all_chunks


# -----------------------------
# Unified Loader Interface
# -----------------------------

def load_and_chunk_document(file_path: str) -> List[Dict]:
    """
    Load a document (PDF or TXT) and return chunks.
    """

    file_path = Path(file_path)
    document_id = file_path.stem

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    if file_path.suffix.lower() == ".pdf":
        pages = load_text_from_pdf(str(file_path))
        chunks = chunk_pages(pages, document_id=document_id)

    elif file_path.suffix.lower() == ".txt":
        text = load_text_from_txt(str(file_path))
        chunks = chunk_text(text, document_id=document_id)

    else:
        raise ValueError("Unsupported file type. Use PDF or TXT.")

    return chunks
