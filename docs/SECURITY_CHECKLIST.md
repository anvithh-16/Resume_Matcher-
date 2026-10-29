# Deployment Security Checklist (SR-07, SR-08) — run before release
Run on 30 Oct 2026 against branch feat/17-deploy-config (self-signed certificate, localhost).

| # | Check | How verified | Result | Evidence |
|---|---|---|---|---|
| 1 | HTTPS used outside localhost | uvicorn --ssl-keyfile/--ssl-certfile on 8443; curl over https | Pass — health 200 over https; plain HTTP to the TLS port is rejected. Browser padlock screenshot still to take | docs/evidence/sr07_https_check.txt, docs/evidence/sr07_https.png (to add) |
| 2 | HTTP on localhost is development-only | README note | Pass — README "Deployment" section | README.md |
| 3 | Production refuses default SECRET_KEY | start with APP_ENV=production, no SECRET_KEY (and with the .env.example placeholder) | Pass — RuntimeError "Set a real SECRET_KEY" for both | docs/evidence/sr07_default_secret_refused.txt, tests/test_deploy.py |
| 4 | /docs hidden in production | GET /docs and /openapi.json -> 404 | Pass — both 404. Browser screenshot still to take | docs/evidence/sr07_https_check.txt, docs/evidence/sr07_no_docs.png (to add) |
| 5 | Secrets only in .env (untracked); .env.example sanitized | git ls-files shows no .env, *.pem or app.db | Pass | `git ls-files` output |
| 6 | No --reload / debug in production | run command in README | Pass — README production command has no --reload | README.md |
| 7 | Audit events written: login_failed, access_denied, admin_job_import/update, consent_changed, resume_deleted, agent_tool_rejected | tests + sqlite3 app.db "select event_type,count(*) from audit_events group by 1" | Partial — login_failed and access_denied implemented; the other five depend on Ankitha's and Anirudh's Sprint-2 routes | re-run after their PRs merge |
| 8 | Audit/log lines contain no passwords, tokens, resume text | test_ownership.py + tests/test_errors.py + manual log read | Pass for logs (test_errors.py; live server log after login shows no password/token). Audit part re-checked by TC-09 once routes merge | tests/test_errors.py |
| 9 | Resume files stored outside app/static, named by random key | ls storage/ | Not run — resume upload (Ankitha, FR-03) not merged yet | |
