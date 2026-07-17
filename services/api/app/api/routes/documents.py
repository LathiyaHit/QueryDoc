"""
PDF upload endpoint.

Lets a user upload their own PDF, which is chunked, embedded, and stored
in Qdrant scoped to their user_id. Subsequent queries (voice or text)
then answer from it instead of the default document.
"""
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.memory.embedder import embed
from app.services.rag.document_loader import load_pdf, split_documents
from app.services.rag.rag_vector_store import RagVectorStore
from app.utils.logger import log

router = APIRouter()
_store = RagVectorStore()


@router.post("/upload/{user_id}")
async def upload_document(user_id: str, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    await _store.ensure_collection()

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp.flush()

        pages = load_pdf(Path(tmp.name))
        for page in pages:
            page.metadata["source_file"] = file.filename

    if not pages:
        raise HTTPException(status_code=422, detail="Could not extract any text from this PDF")

    chunks = split_documents(pages)

    vectors = [await embed(chunk.text) for chunk in chunks]

    # A new upload replaces any previous one for this user
    await _store.delete_session_documents(user_id)
    point_ids = await _store.upsert_chunks(
        chunks=chunks, vectors=vectors, session_id=user_id, is_default=False
    )

    log.info("document.uploaded", user_id=user_id, filename=file.filename, chunks=len(point_ids))

    return {
        "filename": file.filename,
        "chunks_indexed": len(point_ids),
        "message": f"'{file.filename}' is now active — questions will be answered from this document.",
    }


@router.delete("/upload/{user_id}")
async def clear_uploaded_document(user_id: str):
    """Remove the user's uploaded document, reverting to the default document."""
    await _store.delete_session_documents(user_id)
    return {"message": "Uploaded document cleared. Falling back to the default document."}