import sqlite3
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status

from app import repository
from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES
from app.database import get_db
from app.schemas import DocumentDetail, DocumentList, DocumentOut, SearchResponse
from app.search import parse_query, search_documents
from app.text_processing import count_words, decode_text, split_sentences

router = APIRouter(prefix="/documents", tags=["documents"])
DbConn = Annotated[sqlite3.Connection, Depends(get_db)]


def clean_filename(name: str | None) -> str:
    """Keep only the last path part, so '../../x.txt' becomes 'x.txt'."""
    return (name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(conn: DbConn, file: Annotated[UploadFile, File()]):
    filename = clean_filename(file.filename)
    if not filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Only these file types are allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # Read one byte over the limit so oversized files are detected
    # without loading a huge upload into memory.
    raw = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File is larger than {MAX_UPLOAD_BYTES} bytes",
        )
    try:
        text = decode_text(raw)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    return repository.create_document(
        conn,
        filename=filename,
        size_bytes=len(raw),
        content=text,
        word_count=count_words(text),
        sentence_count=len(split_sentences(text)),
    )


@router.get("", response_model=DocumentList)
def list_documents(
    conn: DbConn,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return {
        "total": repository.count_documents(conn),
        "limit": limit,
        "offset": offset,
        "items": repository.list_documents(conn, limit, offset),
    }


# /search must be declared BEFORE /{document_id}; otherwise FastAPI would
# try to read the word "search" as a document ID.
@router.get("/search", response_model=SearchResponse)
def search(
    conn: DbConn,
    q: Annotated[str, Query(min_length=2, max_length=200, description="Keywords")],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    if not parse_query(q):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Query contains no searchable words")
    hits = search_documents(repository.get_all_documents(conn), q)
    return {"query": q, "total": len(hits), "results": [asdict(h) for h in hits[:limit]]}


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, conn: DbConn):
    document = repository.get_document(conn, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, conn: DbConn):
    if not repository.delete_document(conn, document_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
