import pytest
from app.db.database import SessionLocal
from app.db.models import AuditEvent
from app.main import app

SECRET_SKILL = "cobol-ownership-marker"
NEEDED = {"/api/v1/resumes/{resume_id}", "/api/v1/applications", "/api/v1/matches",
          "/api/v1/recommendations", "/api/v1/bookmarks/{job_id}"}
missing = NEEDED - {getattr(r, "path", "") for r in app.routes}

# Runs automatically once Ankitha's and Anirudh's routes are merged.
@pytest.mark.skipif(bool(missing), reason=f"routes not merged yet: {sorted(missing)}")
def test_tc09_cross_user_access_denied(client, user_a, user_b, create_job, create_resume):
    jid = create_job(title="Ownership Job")
    rid = create_resume("a@test.local", {"skills": ["python", SECRET_SKILL], "raw_text": "python"})
    app_id = client.post("/api/v1/applications", headers=user_a, json={"job_id": jid}).json()["id"]
    client.post("/api/v1/bookmarks", headers=user_a, json={"job_id": jid})

    attempts = [
        client.get(f"/api/v1/resumes/{rid}", headers=user_b),
        client.delete(f"/api/v1/resumes/{rid}", headers=user_b),
        client.patch(f"/api/v1/applications/{app_id}", headers=user_b, json={"status": "offer"}),
        client.post("/api/v1/matches", headers=user_b, json={"resume_id": rid, "job_id": jid}),
        client.post("/api/v1/recommendations", headers=user_b, json={"resume_id": rid}),
        client.delete(f"/api/v1/bookmarks/{jid}", headers=user_b),
    ]
    for r in attempts:
        assert r.status_code == 404, r.text
        assert SECRET_SKILL not in r.text
    assert all(a["id"] != app_id for a in client.get("/api/v1/applications", headers=user_b).json()["applications"])
    assert client.get(f"/api/v1/resumes/{rid}", headers=user_a).status_code == 200   # owner still can
    db = SessionLocal()
    assert db.query(AuditEvent).filter_by(event_type="access_denied").count() >= 1
    assert all("Passw0rd" not in e.detail for e in db.query(AuditEvent).all())     # SR-08: no secrets
    db.close()
