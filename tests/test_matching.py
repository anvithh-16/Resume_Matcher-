"""TC-06 (FR-06) and TC-07 (FR-07, FR-09). Owner: Anirudh N."""
from types import SimpleNamespace

from app.services.matching import compute_match

PROFILE = {"skills": ["python", "sql", "git"], "raw_text": "Python SQL Git developer building APIs"}


def job(skills, desc="Build APIs with Python and SQL", title="Developer"):
    return SimpleNamespace(id=1, title=title, description=desc, required_skills=skills)


def test_tc06_range_repeatable_breakdown():
    a = compute_match(PROFILE, job(["python", "sql", "docker"]))
    b = compute_match(PROFILE, job(["python", "sql", "docker"]))
    assert a == b                                            # repeatable for the same input
    assert 0 <= a["score"] <= 100
    assert a["components"]["skill_overlap"] == 0.67
    assert set(a["components"]) == {"skill_overlap", "keyword_similarity"}


def test_tc06_overlap_beats_no_overlap():
    full = compute_match(PROFILE, job(["python", "sql"]))
    none = compute_match(PROFILE, job(["java", "spring"], desc="Java Spring microservices"))
    assert full["score"] > none["score"] and none["matched_skills"] == []


def test_tc06_no_required_skills_fallback():
    r = compute_match(PROFILE, job([]))
    assert 0 <= r["score"] <= 100 and r["components"]["skill_overlap"] == 0.0


def test_tc07_gap_and_evidence_only_explanation():
    r = compute_match({"skills": ["Python3", "MySQL"], "raw_text": "python mysql"},
                      job(["python", "sql", "docker", "aws"]))
    assert r["matched_skills"] == ["python", "sql"]
    assert r["missing_skills"] == ["docker", "aws"]
    present_line = r["explanation"][0]
    assert "python" in present_line and "sql" in present_line
    assert "docker" not in present_line and "aws" not in present_line   # never claims missing skills
    assert "docker and aws are required" in r["explanation"][1]


def test_tc06_api(client, user_a, create_job, create_resume):
    jid = create_job(title="Match API Job", required_skills=["python", "docker"])
    rid = create_resume("a@test.local", PROFILE)
    r = client.post("/api/v1/matches", headers=user_a, json={"resume_id": rid, "job_id": jid})
    assert r.status_code == 200
    assert r.json()["matched_skills"] == ["python"] and r.json()["missing_skills"] == ["docker"]
    assert client.post("/api/v1/matches", headers=user_a,
                       json={"resume_id": rid, "job_id": 999999}).status_code == 404


def test_tc06_api_other_users_resume_is_404(client, user_a, user_b, create_job, create_resume):
    jid = create_job(title="Ownership Match Job")
    rid = create_resume("a@test.local", PROFILE)
    r = client.post("/api/v1/matches", headers=user_b, json={"resume_id": rid, "job_id": jid})
    assert r.status_code == 404
