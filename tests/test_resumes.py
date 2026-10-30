"""TC-03 (FR-03, SR-03), TC-04 (FR-04), NFR-07 deletion. Owner: Ankitha Revadala."""
import io
from pathlib import Path

from docx import Document

FIX = Path(__file__).parent / "fixtures"
GOOD = (FIX / "resume_good.txt").read_text(encoding="utf-8")
URL = "/api/v1/resumes"


def docx_bytes(text):
    d = Document()
    for line in text.splitlines():
        d.add_paragraph(line)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def up(client, headers, name, data):
    return client.post(URL, headers=headers, files={"file": (name, data)})


def test_tc03_upload_validation(client, user_b):
    before = len(client.get(URL, headers=user_b).json()["resumes"])
    assert up(client, user_b, "cv.txt", GOOD.encode()).status_code == 201
    assert up(client, user_b, "cv.docx", docx_bytes(GOOD)).status_code == 201
    assert up(client, user_b, "cv.pdf", (FIX / "resume_good.pdf").read_bytes()).status_code == 201
    assert up(client, user_b, "virus.exe", b"MZ\x90\x00").status_code == 415          # unsupported
    assert up(client, user_b, "fake.pdf", b"hello there").status_code == 415         # misleading name
    assert up(client, user_b, "broken.pdf", b"%PDF-1.4 broken").status_code == 422   # malformed
    assert up(client, user_b, "big.txt", b"a" * (2 * 1024 * 1024 + 1)).status_code == 413  # oversized
    assert client.post(URL, files={"file": ("cv.txt", b"x")}).status_code == 401      # not logged in
    after = len(client.get(URL, headers=user_b).json()["resumes"])
    assert after == before + 3                                                       # only valid ones stored


def test_tc03_filename_is_sanitized(client, user_b):
    r = up(client, user_b, "../../etc/pass wd.txt", GOOD.encode())
    assert r.status_code == 201 and r.json()["filename"] == "pass_wd.txt"


def test_tc04_parsing_known_fields(client, user_b):
    p = up(client, user_b, "cv.txt", GOOD.encode()).json()["profile"]
    assert {"python", "sql", "fastapi", "git", "machine learning", "docker"} <= set(p["skills"])
    assert p["contact"]["email"] == "riya.sharma@example.com"
    assert any("B.Tech" in e for e in p["education"])
    assert any("Intern" in e for e in p["experience"])
    assert "raw_text" not in p


def test_tc04_pdf_parses_same_skills(client, user_b):
    p = up(client, user_b, "cv.pdf", (FIX / "resume_good.pdf").read_bytes()).json()["profile"]
    assert {"python", "sql", "docker"} <= set(p["skills"])


def test_tc04_missing_fields_not_invented(client, user_b):
    p = up(client, user_b, "thin.txt", b"Just a short note about hobbies like chess and music.").json()["profile"]
    assert p["education"] == [] and p["contact"]["email"] is None
    assert any("education" in w for w in p["warnings"])


def test_tc04_user_can_correct_profile(client, user_b):
    rid = up(client, user_b, "cv.txt", GOOD.encode()).json()["id"]
    r = client.put(f"{URL}/{rid}/profile", headers=user_b, json={"skills": ["Python3", "Rust"]})
    assert r.status_code == 200 and r.json()["profile"]["skills"] == ["python", "rust"]


def test_nfr07_delete_removes_data(client, user_b):
    rid = up(client, user_b, "cv.txt", GOOD.encode()).json()["id"]
    assert client.delete(f"{URL}/{rid}", headers=user_b).status_code == 204
    assert client.get(f"{URL}/{rid}", headers=user_b).status_code == 404
