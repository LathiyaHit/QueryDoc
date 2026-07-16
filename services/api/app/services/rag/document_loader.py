"""
PDF loading and chunking for the RAG knowledge base.

Ports the logic from pdf_loader.ipynb (PyPDFLoader + RecursiveCharacterTextSplitter)
to use pypdf and a lightweight custom splitter, so we avoid adding full LangChain
as a dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

from app.core.config import settings


@dataclass
class DocChunk:
    """A single chunk of text ready to be embedded."""
    text: str
    metadata: dict = field(default_factory=dict)


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Recursive character splitter — same strategy as LangChain's
    RecursiveCharacterTextSplitter: split on paragraph breaks first,
    then lines, then words, then hard-cut as a last resort.
    """
    separators = ["\n\n", "\n", " ", ""]

    def split(chunk_text: str, seps: list[str]) -> list[str]:
        if len(chunk_text) <= chunk_size:
            return [chunk_text] if chunk_text.strip() else []

        sep = seps[0]
        rest = seps[1:]

        if sep == "":
            return [chunk_text[i:i + chunk_size] for i in range(0, len(chunk_text), chunk_size)]

        parts = chunk_text.split(sep)
        pieces: list[str] = []
        current = ""

        for part in parts:
            candidate = current + sep + part if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    pieces.append(current)
                if len(part) > chunk_size:
                    pieces.extend(split(part, rest))
                    current = ""
                else:
                    current = part
        if current:
            pieces.append(current)
        return pieces

    raw_chunks = split(text, separators)

    if chunk_overlap <= 0 or len(raw_chunks) <= 1:
        return raw_chunks

    overlapped = [raw_chunks[0]]
    for i in range(1, len(raw_chunks)):
        prev_tail = raw_chunks[i - 1][-chunk_overlap:]
        overlapped.append(prev_tail + raw_chunks[i])
    return overlapped


def load_pdf(pdf_path: Path) -> list[DocChunk]:
    """Load a single PDF, one raw chunk per page (pre-splitting)."""
    reader = PdfReader(str(pdf_path))
    pages: list[DocChunk] = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        pages.append(
            DocChunk(
                text=text,
                metadata={
                    "source_file": pdf_path.name,
                    "file_type": "pdf",
                    "page": page_num,
                },
            )
        )
    return pages


def load_all_pdfs(pdf_directory: str | Path) -> list[DocChunk]:
    """Load every PDF found recursively under pdf_directory."""
    pdf_dir = Path(pdf_directory)
    pdf_files = sorted(pdf_dir.glob("**/*.pdf"))

    print(f"Found {len(pdf_files)} PDF files to process")

    all_pages: list[DocChunk] = []
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        try:
            pages = load_pdf(pdf_file)
            all_pages.extend(pages)
            print(f"  loaded {len(pages)} pages")
        except Exception as e:
            print(f"  error loading {pdf_file.name}: {e}")

    print(f"Total pages loaded: {len(all_pages)}")
    return all_pages


def split_documents(
    documents: list[DocChunk],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[DocChunk]:
    """Split page-level documents into smaller overlapping chunks."""
    chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.RAG_CHUNK_OVERLAP

    split_docs: list[DocChunk] = []
    for doc in documents:
        pieces = _split_text(doc.text, chunk_size, chunk_overlap)
        for i, piece in enumerate(pieces):
            split_docs.append(
                DocChunk(text=piece, metadata={**doc.metadata, "chunk_index": i})
            )

    print(f"Split {len(documents)} pages into {len(split_docs)} chunks")
    return split_docs