from app.db.database import SessionLocal
from app.db.models import User

REG, LOGIN = "/api/v1/auth/register", "/api/v1/auth/login"
PW = "Passw0rd!x"

def test_tc01_register_valid_then_duplicate(client):
    r = client.post(REG, json={"email": "new@test.local", "password": PW})
    assert r.status_code == 201 and r.json()["email"] == "new@test.local"
    dup = client.post(REG, json={"email": "NEW@test.local", "password": PW})
    assert dup.status_code == 409 and dup.json()["error"]["code"] == "email_taken"
    bad = client.post(REG, json={"email": "not-an-email", "password": "short"})
    assert bad.status_code == 422

def test_tc02_login_and_protected_endpoint(client):
    client.post(REG, json={"email": "login@test.local", "password": PW})
    ok = client.post(LOGIN, json={"email": "login@test.local", "password": PW})
    assert ok.status_code == 200 and ok.json()["access_token"]
    wrong = client.post(LOGIN, json={"email": "login@test.local", "password": "WrongPass1"})
    ghost = client.post(LOGIN, json={"email": "nobody@test.local", "password": PW})
    assert wrong.status_code == ghost.status_code == 401
    assert wrong.json()["error"]["message"] == ghost.json()["error"]["message"]  # no account disclosure
    assert client.get("/api/v1/me").status_code == 401
    assert client.get("/api/v1/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    me = client.get("/api/v1/me", headers={"Authorization": "Bearer " + ok.json()["access_token"]})
    assert me.status_code == 200

def test_sr02_password_stored_only_as_argon2_hash(client):
    client.post(REG, json={"email": "hash@test.local", "password": PW})
    db = SessionLocal()
    stored = db.query(User).filter_by(email="hash@test.local").one().password_hash
    db.close()
    assert stored != PW and PW not in stored and stored.startswith("$argon2")
