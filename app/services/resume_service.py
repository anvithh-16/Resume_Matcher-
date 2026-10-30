"""Upload validation and safe file storage (FR-03, SR-03, NFR-07). Owner: Ankitha Revadala."""
import io
import re
import uuid
import zipfile
from pathlib import Path

from app.core.config import MAX_UPLOAD_BYTES, STORAGE_DIR
from app.core.errors import AppError

ALLOWED = {".pdf": "application/pdf",
           ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
           ".txt": "text/plain"}


def _is_docx(data: bytes) -> bool:
    if not data.startswith(b"PK\x03\x04"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            return "word/document.xml" in z.namelist()
    except zipfile.BadZipFile:
        return False


def _is_text(data: bytes) -> bool:
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def validate_upload(filename: str | None, data: bytes) -> str:
    """Return the file extension if the upload is acceptable, else raise AppError."""
    if len(data) > MAX_UPLOAD_BYTES:
        raise AppError(413, "file_too_large", "The file is larger than 2 MB.")
    if not data:
        raise AppError(400, "empty_file", "The file is empty.")
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise AppError(415, "unsupported_type", "Please upload a PDF, DOCX or TXT file.")
    ok = ((ext == ".pdf" and data.startswith(b"%PDF-")) or (ext == ".docx" and _is_docx(data))
          or (ext == ".txt" and _is_text(data)))
    if not ok:
        raise AppError(415, "content_mismatch", "The file content does not match its type.")
    return ext


def safe_name(filename: str | None) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename or "resume").name)[:100]


def store_file(data: bytes) -> str:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    key = uuid.uuid4().hex          # server-generated name; the client filename is never used as a path
    (STORAGE_DIR / key).write_bytes(data)
    return key


def delete_file(key: str) -> None:
    path = STORAGE_DIR / key
    if path.exists():
        path.unlink()
