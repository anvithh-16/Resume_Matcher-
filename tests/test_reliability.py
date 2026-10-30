"""TC-14 (NFR-03): at least 99 of 100 consecutive valid match requests succeed. Owner: Anirudh N."""
PROFILE = {"skills": ["python", "sql"], "raw_text": "python sql developer"}


def test_tc14_100_consecutive_valid_matches(client, user_a, create_job, create_resume):
    jid = create_job(title="Reliability Job", required_skills=["python", "docker"])
    rid = create_resume("a@test.local", PROFILE)
    valid = 0
    for _ in range(100):
        r = client.post("/api/v1/matches", headers=user_a, json={"resume_id": rid, "job_id": jid})
        if r.status_code == 200:
            b = r.json()
            if 0 <= b["score"] <= 100 and {"matched_skills", "missing_skills", "components"} <= b.keys():
                valid += 1
    print(f"NFR-03 valid results: {valid}/100")
    assert valid >= 99
