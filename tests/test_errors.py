import logging
from fastapi.routing import APIRoute
from app.core.logging_filters import RedactFilter
from app.main import app

def test_sr04_redaction():
    rec = logging.LogRecord("t", logging.INFO, __file__, 1,
                            "login token=abc123 Authorization: Bearer eyJabc password=hunter2", None, None)
    RedactFilter().filter(rec)
    out = rec.getMessage()
    assert "abc123" not in out and "eyJabc" not in out and "hunter2" not in out

def test_tc12_unexpected_error_is_safe(client, caplog):
    def boom():
        raise RuntimeError("secret password=hunter2")
    app.router.routes.insert(0, APIRoute("/api/v1/_boom", boom))
    r = client.get("/api/v1/_boom")
    assert r.status_code == 500
    body = r.json()["error"]
    assert body["code"] == "internal_error" and body["request_id"]
    assert "Traceback" not in r.text and "hunter2" not in r.text and "hunter2" not in caplog.text

def test_tc12_validation_error_shape(client):
    r = client.post("/api/v1/auth/register", json={"email": "x"})
    assert r.status_code == 422 and set(r.json()["error"]) == {"code", "message", "request_id"}

def test_sr04_access_log_redacted_and_still_formats():
    from uvicorn.logging import AccessFormatter
    rec = logging.LogRecord("uvicorn.access", logging.INFO, __file__, 1, '%s - "%s %s HTTP/%s" %d',
                            ("127.0.0.1:1", "GET", "/api/v1/me?token=abc123", "1.1", 200), None)
    RedactFilter().filter(rec)
    out = AccessFormatter("%(message)s", use_colors=False).format(rec)
    assert "abc123" not in out and "/api/v1/me" in out
