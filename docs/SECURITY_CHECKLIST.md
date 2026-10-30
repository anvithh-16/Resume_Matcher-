# Deployment Security Checklist (SR-07, SR-08) — run before release

Run by: Anvith Vegi · Date: 30 Oct 2026 · Branch: docs/anvith-final (Sprint-2 freeze candidate)

| # | Check | How verified | Result | Evidence |
|---|---|---|---|---|
| 1 | HTTPS used outside localhost | uvicorn with --ssl-keyfile/--ssl-certfile on port 8443, self-signed cert | Pass | docs/evidence/sr07_https_check.txt |
| 2 | HTTP on localhost is development-only | README deployment section | Pass | README.md (deployment section) |
| 3 | Production refuses the default SECRET_KEY | APP_ENV=production with SECRET_KEY=dev-only-secret raises RuntimeError | Pass | docs/evidence/sr07_default_secret_refused.txt |
| 4 | /docs hidden in production | APP_ENV=production: GET /docs returns 404 | Pass | terminal run, 30 Oct 2026 |
| 5 | Secrets only in .env (untracked); .env.example sanitized | git ls-files shows no .env | Pass | terminal run, 30 Oct 2026 |
| 6 | No --reload / debug in production | README states production must not use --reload | Pass | README.md (deployment section) |
| 7 | Audit events: login_failed, access_denied, admin_job_import/update, consent_changed, resume_deleted, agent_tool_rejected | all 7 found in app/ (grep); access_denied, admin and consent events also asserted in tests | Pass | tests/test_ownership.py, test_admin.py, test_agent.py |
| 8 | Audit/log lines contain no passwords, tokens or resume text | log redaction test + ownership test assert no secrets | Pass | docs/evidence/tc12.txt, docs/evidence/tc09.txt |
| 9 | Resume files stored outside app/static, named by random key | resume_service.py stores files as uuid4 hex names under STORAGE_DIR | Pass | app/services/resume_service.py |

Result: 9/9 checks passed. Development runs on HTTP localhost only; HTTPS was demonstrated locally with a
self-signed certificate rather than a real hosted deployment (see docs/DEVIATIONS.md).
