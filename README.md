# Document Assistant API

A lightweight document management and question-answering REST API built with Python, FastAPI, and SQLite. Upload text documents, search their contents using keywords, and retrieve relevant sentences in response to questions.

## Features

- **Document Upload:** Upload `.txt` files through a REST API.
- **Document Management:** List, retrieve, and delete stored documents.
- **Keyword Search:** Search document contents using case-insensitive keyword matching.
- **Question Answering:** Submit a question and retrieve the most relevant sentence from stored documents.
- **SQLite Storage:** Persist document metadata and extracted text using Python's built-in `sqlite3` module.
- **REST API Documentation:** Explore and test endpoints through FastAPI's interactive Swagger UI.
- **Automated Testing:** Test text processing, search, question answering, database operations, and API behavior.

## Tech Stack

- **Language:** Python
- **Backend:** FastAPI
- **Database:** SQLite
- **Server:** Uvicorn
- **Testing:** Pytest
- **API Documentation:** Swagger UI / OpenAPI
- **CI:** GitHub Actions

## Project Structure

```text
document-assistant/
├── app/
│   ├── main.py
│   ├── text_processing.py
│   ├── search.py
│   └── ...
├── tests/
├── sample.txt
├── .github/
│   └── workflows/
├── README.md
├── LICENSE
├── .gitignore
└── requirements.txt
```

*The exact files may vary depending on the implementation.*

## Getting Started

### Prerequisites

- Python 3.11 or newer
- Git

### 1. Clone the repository

```bash
git clone https://github.com/bhoomi-gupta03/document-assistant.git
cd document-assistant
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the tests

```bash
pytest -v
```

Check that the tests pass before using or extending the application.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Open these URLs in your browser:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **OpenAPI schema:** http://127.0.0.1:8000/openapi.json

## API Capabilities

| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents` | Upload a text document |
| GET | `/documents` | List stored documents |
| GET | `/documents/search?q=keyword` | Search document contents |
| GET | `/documents/{document_id}` | Retrieve a document |
| DELETE | `/documents/{document_id}` | Delete a document |
| POST | `/ask` | Find a relevant answer to a question |

*Confirm the exact routes and request formats in `/docs`, as they depend on the implemented code.*

## Example Workflow

1. Start the API server.
2. Open Swagger UI at `/docs`.
3. Upload a `.txt` document using the document upload endpoint.
4. Search for a keyword using the search endpoint.
5. Submit a question to `/ask`.
6. Review the returned answer and its source information.

## How Question Answering Works

The current version uses **keyword-based sentence matching**, rather than a generative AI model.

At a high level, the application:

1. Processes the submitted question into searchable terms.
2. Compares those terms with sentences in stored documents.
3. Scores sentences based on keyword overlap.
4. Returns the highest-scoring relevant sentence and its source information.

This approach is simple, explainable, and useful for
