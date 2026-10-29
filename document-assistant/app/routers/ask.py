import sqlite3
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import repository
from app.database import get_db
from app.schemas import AskRequest, AskResponse
from app.search import answer_question
from app.text_processing import extract_keywords

router = APIRouter(tags=["ask"])
DbConn = Annotated[sqlite3.Connection, Depends(get_db)]


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, conn: DbConn):
    """Extractive answer: returns the most relevant sentence(s) from your
    documents. This is keyword matching, not an AI language model."""
    if not extract_keywords(body.question):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Please ask a more specific question"
        )

    if body.document_id is not None:
        document = repository.get_document(conn, body.document_id)
        if document is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
        documents = [document]
    else:
        documents = repository.get_all_documents(conn)

    passages = answer_question(documents, body.question)
    return {
        "question": body.question,
        "answer": passages[0].sentence if passages else None,
        "sources": [asdict(p) for p in passages],
    }
