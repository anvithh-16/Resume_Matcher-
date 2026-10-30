"""Resume text extraction and parsing (FR-04). Never invents fields. Owner: Ankitha Revadala."""
import io
import re

from docx import Document
from pypdf import PdfReader

from app.services.skills import extract_skills


class ParseError(Exception):
    pass


EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s-]{8,14}\d")
EDU_WORDS = ("b.tech", "btech", "b.e.", "bachelor", "master", "m.tech", "university", "college", "cgpa", "school")
EXP_WORDS = ("intern", "engineer", "developer", "analyst", "worked", "experience at")


def extract_text(data: bytes, ext: str) -> str:
    try:
        if ext == ".pdf":
            text = "\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(data)).pages)
        elif ext == ".docx":
            text = "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
        else:
            text = data.decode("utf-8")
    except Exception as exc:
        raise ParseError("We could not read this file. Try exporting it again as PDF or DOCX.") from exc
    if not text.strip():
        raise ParseError("No readable text was found in this file.")
    return text


def parse_resume(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 12]
    email = EMAIL.search(text)
    phone = PHONE.search(text)
    profile = {
        "skills": extract_skills(text),
        "education": [l for l in lines if any(w in l.lower() for w in EDU_WORDS)][:5],
        "experience": [l for l in lines if any(w in l.lower() for w in EXP_WORDS)][:8],
        "contact": {"email": email.group(0) if email else None,
                    "phone": phone.group(0).strip() if phone else None},
    }
    warnings = []
    for field in ("skills", "education", "experience"):
        if not profile[field]:
            warnings.append(f"No {field} found — please check your resume or add them manually.")
    if not profile["contact"]["email"]:
        warnings.append("No email address found.")
    profile["warnings"] = warnings
    return profile
