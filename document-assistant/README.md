# Document Assistant API

A REST API where you upload plain-text documents, search them by keyword, and ask questions that are answered with the most relevant sentences from your documents.

> **Honest scope:** version 1 uses classic text processing (tokenizing, keyword matching, scoring). It does **not** use an AI model, embeddings or a vector database. AI is listed under *Future improvements*.

## Features

| Feature | Endpoint |
|---|---|
| Upload `.txt` files (UTF-8, max 1 MB) with validation | `POST /documents` |
| Metadata: filename, size, word count, sentence count, upload time | stored in SQLite |
| List documents (paginated, newest first) | `GET /documents` |
| Get one document with its text | `GET /documents/{id}` |
| Delete a document | `DELETE /documents/{id}` |
| Keyword search with ranked results and snippets | `GET /documents/search?q=...` |
| Ask a question, get the best matching sentence(s) and sources | `POST /ask` |
| Health check | `GET /health` |

Errors use clear status codes: 400 (empty/binary/non-UTF-8 file), 404, 413 (too large), 415 (not `.txt`), 422 (invalid input).

## Tech stack

Python 3.11+, FastAPI, Uvicorn, SQLite (built-in `sqlite3`), pytest, GitHub Actions.

## Project structure

```
app/
  main.py             App setup, startup (creates the table), routers
  config.py           Upload limits and database path
  database.py         SQLite connection, schema, get_db dependency
  repository.py       All SQL queries (parameterized)
  text_processing.py  Decode, tokenize, split sentences, keywords
  search.py           Keyword search and extractive question answering
  schemas.py          Pydantic request/response models
  routers/
    documents.py      Upload, list, search, get, delete
    ask.py            POST /ask
tests/                pytest tests (temporary database per test)
samples/sample.txt    Example document to try
```

## Setup (Windows PowerShell)

```powershell
git clone https://github.com/<your-username>/document-assistant.git
cd document-assistant
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI. On macOS/Linux activate with `source .venv/bin/activate`.
The database file `documents.db` is created automatically. To use another location, set `DATABASE_PATH`.

## Run the tests

```powershell
pytest -v
```

Tests use a temporary SQLite file, never your real `documents.db`.

## Try it

In Swagger UI: `POST /documents` → upload `samples/sample.txt` → `GET /documents/search?q=fastapi` → `POST /ask` with `{"question": "What is SQLite?"}`.

With curl (PowerShell: use `curl.exe`):

```bash
curl -X POST http://127.0.0.1:8000/documents -F "file=@samples/sample.txt"
curl "http://127.0.0.1:8000/documents/search?q=python"
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "What is FastAPI built for?"}'
```

Example `/ask` response:

```json
{
  "question": "What is FastAPI built for?",
  "answer": "It is built for creating REST APIs quickly.",
  "sources": [{"document_id": 1, "filename": "sample.txt", "sentence": "It is built for creating REST APIs quickly.", "score": 1.0}]
}
```

## How it works

- **Upload:** check extension → read at most 1 MB + 1 byte → decode UTF-8 → reject empty/binary → count words and sentences → save in SQLite.
- **Search:** lowercase, whole-word match. Every query word must appear in a document; results are ranked by total occurrences.
- **Ask:** remove stop words from the question, then score each sentence by the share of question keywords it contains (with simple plural handling). The best sentence is the answer; the top 3 are returned as sources. It copies existing sentences and never invents text.

## Design decisions

- **`sqlite3` instead of an ORM:** fewer dependencies and visible SQL. All queries use `?` placeholders, so user input cannot become SQL.
- **Pure logic modules:** `text_processing.py` and `search.py` know nothing about FastAPI or the database, so they are easy to test.
- **One connection per request** via a FastAPI dependency, always closed.
- **Route order:** `/documents/search` is declared before `/documents/{document_id}`.
- **Filenames are cleaned** (`../../x.txt` becomes `x.txt`). Files are stored in the database, not on disk.

## Known limitations

- No authentication: anyone who can reach the API can see all documents.
- Search and ask load all documents into memory, which is fine for small collections but does not scale.
- Sentence splitting is simple (abbreviations such as "Dr." split incorrectly).
- No synonyms or meaning: "car" will not match "automobile".
- Only `.txt` files; no PDF or DOCX.
- No migrations; the schema is created with `CREATE TABLE IF NOT EXISTS`.

## Future improvements

1. SQLite FTS5 for faster, ranked full-text search
2. PDF/DOCX extraction
3. JWT authentication with per-user documents
4. Optional AI step: embeddings plus an LLM that answers from the retrieved sentences
