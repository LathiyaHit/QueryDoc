"""
Ingest the default fallback PDF into Qdrant.

This PDF is used to answer questions when a user hasn't uploaded
their own document for the session.

Run: python scripts/ingest_default_pdf.py
Re-run any time you replace the PDF in data/rag_docs/default/.
"""
import asyncio
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/api"))

from app.core.config import settings
from app.services.memory.embedder import embed
from app.services.rag.document_loader import load_all_pdfs, split_documents
from app.services.rag.rag_vector_store import RagVectorStore

DEFAULT_PDF_DIR = os.path.join(
    os.path.dirname(__file__), "..", settings.RAG_DOCS_DIR, "default"
)


async def ingest_default():
    store = RagVectorStore()
    await store.ensure_collection()

    print(f"Loading PDFs from: {DEFAULT_PDF_DIR}")
    pages = load_all_pdfs(DEFAULT_PDF_DIR)
    if not pages:
        print("No PDFs found — add a PDF to data/rag_docs/default/ and re-run.")
        return

    chunks = split_documents(pages)

    print(f"Embedding {len(chunks)} chunks...")
    vectors = []
    for i, chunk in enumerate(chunks):
        vector = await embed(chunk.text)
        vectors.append(vector)
        if (i + 1) % 10 == 0:
            print(f"  embedded {i + 1}/{len(chunks)}")

    print("Clearing any previously ingested default document...")
    await store.delete_default_documents()

    print("Upserting into Qdrant...")
    point_ids = await store.upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        session_id=None,
        is_default=True,
    )
    print(f"Done. Ingested {len(point_ids)} chunks as the default document.")


if __name__ == "__main__":
    asyncio.run(ingest_default())