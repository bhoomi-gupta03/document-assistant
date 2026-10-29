from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_database_path
from app.database import init_db
from app.routers import ask, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(get_database_path())  # create the table on startup if missing
    yield


app = FastAPI(
    title="Document Assistant API",
    description="Upload .txt documents, search them by keyword and ask questions "
    "answered with the most relevant sentences. No AI model is used yet.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents.router)
app.include_router(ask.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
