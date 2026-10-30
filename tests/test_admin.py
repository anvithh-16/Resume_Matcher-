"""FR-15 job dataset administration. Owner: Ankitha Revadala."""
from app.db.database import SessionLocal
from app.db.models import AuditEvent

GOOD = {"title": "Imported ML Engineer", "company": "Orbit", "location": "Remote",
        "required_skills": ["Python", "PyTorch"], "employment_type": "full-time"}


def test_fr15_import_update_deactivate(client, admin, user_a):
    url = "/api/v1/admin/jobs/import"
    assert client.post(url, headers=user_a, json={"jobs": [GOOD]}).status_code == 403   # not admin
    bad = client.post(url, headers=admin, json={"jobs": [GOOD, {"title": "", "company": "X"}]})
    assert bad.status_code == 422                                                      # invalid rejected
    assert client.get("/api/v1/jobs", params={"q": "Imported ML"}).json()["count"] == 0  # nothing saved
    assert client.post(url, headers=admin, json={"jobs": [GOOD]}).json() == {"imported": 1}
    job = client.get("/api/v1/jobs", params={"q": "Imported ML"}).json()["results"][0]
    assert job["required_skills"] == ["python", "pytorch"]
    r = client.patch(f"/api/v1/admin/jobs/{job['id']}", headers=admin, json={"active": False})
    assert r.status_code == 200
    assert client.get(f"/api/v1/jobs/{job['id']}").status_code == 404                 # deactivated
    db = SessionLocal()
    types = {e.event_type for e in db.query(AuditEvent).all()}
    db.close()
    assert {"admin_job_import", "admin_job_update", "access_denied"} <= types


def test_fr15_update_validation(client, admin, create_job):
    jid = create_job(title="Admin Patch Job")
    r = client.patch(f"/api/v1/admin/jobs/{jid}", headers=admin, json={"employment_type": "volunteer"})
    assert r.status_code == 422
    r = client.patch(f"/api/v1/admin/jobs/{jid}", headers=admin, json={"required_skills": ["MySQL", " "]})
    assert r.status_code == 200
    assert client.get(f"/api/v1/jobs/{jid}").json()["required_skills"] == ["sql"]
    assert client.patch("/api/v1/admin/jobs/999999", headers=admin, json={"active": False}).status_code == 404
