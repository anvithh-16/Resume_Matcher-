"""SR-10 anti-spoofing: forged, expired, unsigned and tampered tokens are refused; login errors do not reveal
whether an account exists. Added in Part-3 (SRS v1.2). Owner: Anirudh N."""
from datetime import datetime, timedelta, timezone

import jwt

from app.core import config

ME = "/api/v1/me"


def _token(secret, minutes=60, sub="1", algorithm="HS256"):
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": sub, "exp": exp}, secret, algorithm=algorithm)


def _status(client, token):
    return client.get(ME, headers={"Authorization": f"Bearer {token}"}).status_code


def test_sr10_token_signed_with_another_key_is_refused(client, user_a):
    assert _status(client, _token("attacker-guessed-secret-" + "x" * 20)) == 401


def test_sr10_expired_token_is_refused(client, user_a):
    assert _status(client, _token(config.SECRET_KEY, minutes=-1)) == 401


def test_sr10_unsigned_alg_none_token_is_refused(client, user_a):
    unsigned = jwt.encode({"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, None, algorithm="none")
    assert _status(client, unsigned) == 401


def test_sr10_tampered_token_is_refused(client, user_a):
    good = user_a["Authorization"].split(" ", 1)[1]
    head, payload, sig = good.split(".")
    tampered = ".".join([head, payload, ("A" if sig[0] != "A" else "B") + sig[1:]])
    assert _status(client, tampered) == 401
    assert client.get(ME, headers=user_a).status_code == 200      # the real token still works


def test_sr10_login_errors_do_not_reveal_accounts(client, user_a):
    wrong_pw = client.post("/api/v1/auth/login", json={"email": "a@test.local", "password": "Wrong-pass-1"})
    no_user = client.post("/api/v1/auth/login", json={"email": "nobody@test.local", "password": "Wrong-pass-1"})
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json()["error"]["message"] == no_user.json()["error"]["message"]
