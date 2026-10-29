import logging
import pytest
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

ROUTES = {getattr(r, "path", "") for r in app.routes}
needs = lambda *paths: pytest.mark.skipif(not set(paths) <= ROUTES,  # noqa: E731
                                          reason=f"routes not merged yet: {sorted(set(paths) - ROUTES)}")

@needs("/api/v1/resumes")
def test_tc12_parser_failure_is_safe(client, user_a):
    r = client.post("/api/v1/resumes", headers=user_a, files={"file": ("cv.pdf", b"%PDF-1.4 broken")})
    assert r.status_code == 422 and r.json()["error"]["code"] == "parse_failed"
    assert "Traceback" not in r.text

@needs("/api/v1/consent", "/api/v1/recommendations")
def test_tc12_provider_timeout_falls_back(client, user_a, create_job, create_resume, monkeypatch):
    def timeout(_payload):
        raise TimeoutError("provider slow")
    monkeypatch.setattr("app.agent.provider._call_provider", timeout)
    monkeypatch.setattr("app.core.config.EXTERNAL_AI_ENABLED", True)
    create_job(title="Timeout Job", required_skills=["python"])
    rid = create_resume("a@test.local", {"skills": ["python"], "raw_text": "python developer"})
    client.put("/api/v1/consent", headers=user_a, json={"external_ai_enabled": True})
    r = client.post("/api/v1/recommendations", headers=user_a, json={"resume_id": rid})
    client.put("/api/v1/consent", headers=user_a, json={"external_ai_enabled": False})
    assert r.status_code == 200 and "Traceback" not in r.text
    assert any(rec.get("warnings") for rec in r.json()["recommendations"])
