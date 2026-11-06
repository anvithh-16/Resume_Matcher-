"""Branch-coverage tests added in Part-3 for decision outcomes the original suite never took
(see docs/BRANCH_COVERAGE_REPORT.md). Owner: Anirudh N."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent import orchestrator, provider
from app.agent.tools import AgentContext, ToolError, call_tool
from app.core import config
from app.core.errors import AppError
from app.db.database import Base, SessionLocal
from app.db.models import Job, User
from app.services import job_service, resume_service
from app.services.parser import ParseError, extract_text


# ---------------------------------------------------------------- agent (FR-08, FR-13)
def test_tc08_no_matching_jobs_gives_guidance(client, user_a, create_resume):
    rid = create_resume("a@test.local", {"skills": ["zz-skill-no-job-needs"]})
    body = client.post("/api/v1/recommendations", headers=user_a, json={"resume_id": rid}).json()
    assert body["recommendations"] == []
    assert "No jobs match your skills" in body["guidance"]
    assert body["tool_trace"] == ["get_resume_profile", "search_jobs"]


def test_tc08_tool_failure_becomes_controlled_400(client, user_a, create_resume, monkeypatch):
    rid = create_resume("a@test.local", {"skills": ["python"]})

    def failing(name, args, ctx):
        raise ToolError("tool_failed")
    monkeypatch.setattr(orchestrator, "call_tool", failing)
    r = client.post("/api/v1/recommendations", headers=user_a, json={"resume_id": rid})
    assert r.status_code == 400
    assert set(r.json()["error"]) == {"code", "message", "request_id"}


def test_tc08_score_jobs_skips_missing_and_inactive_jobs(user_a, create_resume, create_job):
    rid = create_resume("a@test.local", {"skills": ["python"]})
    inactive = create_job(title="Closed Role", active=False)
    db = SessionLocal()
    try:
        ctx = AgentContext(db=db, user=db.query(User).filter_by(email="a@test.local").one())
        assert call_tool("score_jobs", {"resume_id": rid, "job_ids": [inactive, 99999999]}, ctx) == []
    finally:
        db.close()


def test_tc13_consented_provider_is_called_with_minimal_payload(monkeypatch):
    monkeypatch.setattr(config, "EXTERNAL_AI_ENABLED", True)
    rec = {"title": "Data Analyst", "matched_skills": ["sql"], "missing_skills": ["excel"],
           "explanation": ["Your resume lists sql, which this job requires."]}
    recs, calls = provider.maybe_polish([rec], consent=True)
    assert calls == 1
    assert recs[0]["explanation"] == ["Your resume lists sql, which this job requires."]


# ---------------------------------------------------------------- job dataset (FR-05, FR-15)
@pytest.mark.parametrize("item", [
    "not an object",
    {"title": "Dev", "company": "X", "required_skills": "python"},
    {"title": "Dev", "company": "X", "employment_type": "volunteer"},
], ids=["not-an-object", "skills-not-a-list", "unknown-employment-type"])
def test_fr15_validate_job_rejects_bad_records(item):
    with pytest.raises(ValueError):
        job_service.validate_job(item)


def test_fr15_seed_skips_when_jobs_exist_or_file_missing(tmp_path, monkeypatch):
    db = SessionLocal()
    try:
        before = db.query(Job).count()
        job_service.seed_if_empty(db)               # jobs already present -> nothing added
        assert db.query(Job).count() == before
    finally:
        db.close()
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    empty = sessionmaker(bind=engine)()
    monkeypatch.setattr(job_service, "BASE_DIR", tmp_path)   # no data/jobs_seed.json here
    job_service.seed_if_empty(empty)
    assert empty.query(Job).count() == 0
    empty.close()


def test_tc05_blank_skill_filter_is_ignored(create_job):
    create_job(title="Blank Filter Job")
    db = SessionLocal()
    try:
        all_jobs = job_service.search_jobs(db, limit=100)
        assert len(job_service.search_jobs(db, skills=["  ", ""], limit=100)) == len(all_jobs)
    finally:
        db.close()


# ---------------------------------------------------------------- upload checks and parsing (FR-03, FR-04, SR-03)
@pytest.mark.parametrize("name,data,code", [
    ("cv.docx", b"not a zip file", "content_mismatch"),
    ("cv.docx", b"PK\x03\x04 broken zip", "content_mismatch"),
    ("cv.txt", b"text with a \x00 null byte", "content_mismatch"),
    ("cv.txt", b"\xff\xfe\xfa invalid utf-8", "content_mismatch"),
], ids=["docx-not-zip", "docx-broken-zip", "txt-null-byte", "txt-invalid-utf8"])
def test_tc03_content_signature_mismatch_rejected(name, data, code):
    with pytest.raises(AppError) as exc:
        resume_service.validate_upload(name, data)
    assert exc.value.code == code


def test_tc03_oversized_upload_rejected():
    with pytest.raises(AppError) as exc:
        resume_service.validate_upload("cv.txt", b"a" * (config.MAX_UPLOAD_BYTES + 1))
    assert exc.value.status_code == 413


def test_tc04_whitespace_only_file_has_no_readable_text():
    with pytest.raises(ParseError):
        extract_text(b"   \n\t  ", ".txt")


def test_nfr07_deleting_a_missing_file_is_harmless():
    resume_service.delete_file("does-not-exist-" + "0" * 20)


def test_tc03_empty_upload_rejected():
    with pytest.raises(AppError) as exc:
        resume_service.validate_upload("cv.txt", b"")
    assert exc.value.code == "empty_file"
