"""Settings. Kept tiny on purpose: one environment variable, two constants."""
import os

MAX_UPLOAD_BYTES = 1_000_000  # 1 MB
ALLOWED_EXTENSIONS = {".txt"}


def get_database_path() -> str:
    """Path of the SQLite file. Override with the DATABASE_PATH env variable."""
    return os.getenv("DATABASE_PATH", "documents.db")
