"""TC-11 (FR-11). Owner: Ankitha Revadala."""
URL = "/api/v1/applications"


def test_tc11_status_lifecycle(client, user_a, create_job):
    jid = create_job(title="Tracking Job")
    rec = client.post(URL, headers=user_a, json={"job_id": jid})
    assert rec.status_code == 201 and rec.json()["status"] == "saved"
    rid = rec.json()["id"]
    for status in ("applied", "interviewing", "offer"):
        r = client.patch(f"{URL}/{rid}", headers=user_a, json={"status": status})
        assert r.status_code == 200 and r.json()["status"] == status
    bad = client.patch(f"{URL}/{rid}", headers=user_a, json={"status": "hired!!"})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "invalid_status"
    listed = client.get(URL, headers=user_a).json()["applications"]
    assert next(a for a in listed if a["id"] == rid)["status"] == "offer"     # change persisted
    assert client.post(URL, headers=user_a, json={"job_id": jid}).status_code == 409
    assert client.post(URL, headers=user_a, json={"job_id": jid + 100000}).status_code == 404


def test_tc11_notes_and_unsupported_initial_status(client, user_a, create_job):
    jid = create_job(title="Notes Job")
    assert client.post(URL, headers=user_a, json={"job_id": jid, "status": "teleported"}).status_code == 422
    rid = client.post(URL, headers=user_a, json={"job_id": jid}).json()["id"]
    r = client.patch(f"{URL}/{rid}", headers=user_a, json={"notes": "Recruiter call on Monday"})
    assert r.json()["notes"] == "Recruiter call on Monday" and r.json()["status"] == "saved"


def test_tc11_other_user_cannot_see_or_change(client, user_a, user_b, create_job):
    jid = create_job(title="Private Tracking Job")
    rid = client.post(URL, headers=user_a, json={"job_id": jid}).json()["id"]
    assert client.patch(f"{URL}/{rid}", headers=user_b, json={"status": "offer"}).status_code == 404
    assert all(a["id"] != rid for a in client.get(URL, headers=user_b).json()["applications"])
