def test_tc10_bookmark_lifecycle(client, user_a, user_b, create_job):
    jid = create_job(title="Bookmark Test Job")
    assert client.post("/api/v1/bookmarks", headers=user_a, json={"job_id": jid}).status_code == 201
    assert client.post("/api/v1/bookmarks", headers=user_a, json={"job_id": jid}).status_code == 409
    mine = client.get("/api/v1/bookmarks", headers=user_a).json()["bookmarks"]
    assert any(b["job_id"] == jid for b in mine)
    theirs = client.get("/api/v1/bookmarks", headers=user_b).json()["bookmarks"]
    assert all(b["job_id"] != jid for b in theirs)            # not visible to another user
    assert client.delete(f"/api/v1/bookmarks/{jid}", headers=user_b).status_code == 404
    assert client.delete(f"/api/v1/bookmarks/{jid}", headers=user_a).status_code == 204
    mine = client.get("/api/v1/bookmarks", headers=user_a).json()["bookmarks"]
    assert all(b["job_id"] != jid for b in mine)
    assert client.post("/api/v1/bookmarks", headers=user_a, json={"job_id": 999999}).status_code == 404
