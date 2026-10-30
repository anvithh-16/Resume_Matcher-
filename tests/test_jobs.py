"""TC-05 (FR-05) functional part. Owner: Ankitha Revadala."""
TAG = "Qxzv"   # unusual word so seeded jobs never match


def test_tc05_search_obeys_filters(client, create_job):
    create_job(title=f"{TAG} Data Analyst", location="Pune", required_skills=["excel", "tableau"],
               employment_type="internship")
    create_job(title=f"{TAG} Backend Engineer", location="Chennai", required_skills=["java", "spring"])
    r = client.get("/api/v1/jobs", params={"q": TAG}).json()
    assert r["count"] == 2
    r = client.get("/api/v1/jobs", params={"q": TAG, "skill": "tableau"}).json()
    assert [j["title"] for j in r["results"]] == [f"{TAG} Data Analyst"]
    r = client.get("/api/v1/jobs", params={"q": TAG, "location": "chennai"}).json()
    assert r["count"] == 1 and r["results"][0]["location"] == "Chennai"
    r = client.get("/api/v1/jobs", params={"q": TAG, "employment_type": "internship"}).json()
    assert r["count"] == 1 and r["results"][0]["employment_type"] == "internship"
    empty = client.get("/api/v1/jobs", params={"q": "no-such-job-xyz"}).json()
    assert empty == {"count": 0, "results": []}
    assert client.get("/api/v1/jobs/999999").status_code == 404


def test_tc05_skill_aliases_match(client, create_job):
    create_job(title="Qxzw Alias Job", required_skills=["sql"])
    r = client.get("/api/v1/jobs", params={"q": "Qxzw", "skill": "PostgreSQL"}).json()
    assert [j["title"] for j in r["results"]] == ["Qxzw Alias Job"]


def test_seed_loaded(client):
    assert client.get("/api/v1/jobs", params={"limit": 100}).json()["count"] >= 30
