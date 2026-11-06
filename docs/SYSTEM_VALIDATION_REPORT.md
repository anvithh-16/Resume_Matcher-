# System Validation Report

Project: AI-Based Resume Matching and Job Searching Platform Using Agentic AI (Resume Matcher)  
Team: the no name group — Anvith Vegi (PES1UG24AM047), Ankitha Revadala (PES1UG24AM044), Anirudh N (PES1UG24AM041)  
Deliverables Part-3, testing window 2–6 Nov 2026

## 1. Purpose and scope

This report checks the delivered system (main branch after Sprint 3) against every requirement in
SRS v1.2: functional requirements FR-01–FR-15, non-functional requirements NFR-01–NFR-10 and security
requirements SR-01–SR-11. For each requirement it records the acceptance criterion, how it was validated,
the evidence, and the result. Results come from this run's automated tests and from the system-level
results recorded in docs/TEST_REPORT.md and docs/evidence/.

## 2. Validation environment (automated run)

| Item | Value |
|---|---|
| Date and time | 06 Nov 2026, 10:18 (UTC+05:30) |
| Run by | AnirudhN-7 |
| Branch / commit | test/part3-validation @ fce7f89 |
| Operating system | Windows 11 (AMD64) |
| Python | 3.14.6 |
| Key packages | pytest 8.3.4, pytest-cov 6.0.0, coverage 7.17.2, fastapi 0.115.6, sqlalchemy 2.1.6, httpx 0.27.2 |
| Command | `python scripts/make_test_reports.py` (pytest + coverage with branch measurement) |

## 3. Summary

| Requirements | Pass | Partial | Fail | Not run |
|---|---|---|---|---|
| 36 | 31 | 1 | 1 | 3 |

Automated suite in this run: 71 of 71 tests passed. Branch coverage 100.0%
(docs/BRANCH_COVERAGE_REPORT.md).

**Verdict: Validated with known gaps: 31 of 36 requirements pass; 1 partial, 1 fail, 3 not run (listed in section 5).**

Result rule: a requirement passes only if every check linked to it passed; the worst result wins
(Fail < Not run < Partial < Pass).

## 4. Requirement-by-requirement results

| ID | Requirement | Acceptance criterion | How validated | Actual result | Evidence | Result |
|---|---|---|---|---|---|---|
| FR-01 | Account registration | Valid sign-up 201; duplicate 409; invalid input 422 | Automated API tests | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc01_tc02_sr02.txt | **Pass** |
| FR-02 | Authentication | Correct login returns JWT; wrong/unknown login identical 401; protected routes need a token | Automated API tests | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc01_tc02_sr02.txt | **Pass** |
| FR-03 | Resume upload | PDF/DOCX/TXT up to 2 MB accepted; wrong type, mismatched content, empty or oversized rejected | Automated API + unit tests | 8/8 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc03_tc04_nfr07.txt | **Pass** |
| FR-04 | Resume parsing and review | Known fields extracted, missing fields not invented, corrections persist | Automated API + unit tests | 9/9 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc03_tc04_nfr07.txt | **Pass** |
| FR-05 | Job search | Every result matches all filters; inactive jobs never shown; empty state | Automated API tests | 4/4 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md | **Pass** |
| FR-06 | Resume-job matching | Score 0-100 by the documented formula; repeatable | Automated unit + API tests | 5/5 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc06_tc07.txt | **Pass** |
| FR-07 | Skill gap analysis | Matched and missing skills partition the job's required skills | Automated unit tests | 3/3 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc06_tc07.txt | **Pass** |
| FR-08 | Agent workflow | Only the 4 allowlisted tools in fixed order; unknown tools refused and audited | Automated API tests | 8/8 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc08_tc13.txt | **Pass** |
| FR-09 | Recommendation explanation | Reasons mention only listed matched/missing skills | Automated unit tests | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc06_tc07.txt | **Pass** |
| FR-10 | Bookmarks | Add, list, duplicate 409, remove; owner only | Automated API tests | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc10.txt | **Pass** |
| FR-11 | Application tracking | Six statuses only; changes persist; other values 422 | Automated API tests | 3/3 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc11.txt | **Pass** |
| FR-12 | Resource ownership | Other users' records return 404 and are audited | Automated API tests | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc09.txt | **Pass** |
| FR-13 | Controlled external actions | No external call without configuration and consent; minimal payload | Automated API + unit tests | 4/4 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc08_tc13.txt | **Pass** |
| FR-14 | Error handling | One error format; no stack traces or secrets | Automated API tests | 4/4 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc12.txt | **Pass** |
| FR-15 | Job dataset administration | Admin only; all-or-nothing import; update/deactivate | Automated API + unit tests | 6/6 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/fr15.txt | **Pass** |
| NFR-01 | Search performance | p95 <= 2 s, 5,000 jobs, 20 users | Load test (scripts/perf_search.py) | p95 4.324 s over 400 requests, 20 users (misses 2 s target) | docs/evidence/tc05.txt, docs/evidence/nfr01_search_load.txt | **Fail** |
| NFR-02 | Matching performance | p95 <= 10 s without external LLM | Load test (scripts/perf_match.py) | p95 1.334 s over 200 requests, 20 users, no external provider (target <= 10 s) | docs/evidence/nfr02_match_load.txt | **Pass** |
| NFR-03 | Reliability | >= 99 of 100 valid match results | Automated test (100 requests) | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc14.txt | **Pass** |
| NFR-04 | Usability | >= 4 of 5 users finish the core journey unaided | Task-based user study (docs/USABILITY.md) | 5-user study not conducted (docs/USABILITY.md, docs/DEVIATIONS.md) | docs/USABILITY.md | **Not run** |
| NFR-05 | Compatibility | Core journey works in latest Chrome and Firefox | Manual browser check | Full journey works in Chrome; Firefox not tested (see DEVIATIONS.md) | docs/evidence/nfr05_browsers.txt | **Partial** |
| NFR-06 | Maintainability | Separate modules with automated tests | Module review + coverage reports | Routes, services, data access, matching and agent in separate modules; all 5 service modules covered by tests (job_service via test_jobs.py and test_admin.py API tests) | docs/evidence/nfr06_module_review.txt | **Pass** |
| NFR-07 | Data retention | User can delete a resume and its extracted data | Automated API + unit tests | 2/2 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc03_tc04_nfr07.txt | **Pass** |
| NFR-08 | Accessibility | Keyboard operable; labelled fields | Keyboard walkthrough + Lighthouse | Keyboard-only journey OK; Lighthouse accessibility 100 (see evidence file for date and pages) | docs/evidence/nfr08_lighthouse.txt | **Pass** |
| NFR-09 | Reproducibility | Fresh clone + README steps -> all tests pass | Clean-setup run | Fresh clone + README steps on a clean folder: 49 passed (run as python -m pytest -q) | docs/evidence/full_suite.txt | **Pass** |
| NFR-10 | Agent / LLM performance | p95 <= 5 s for /recommendations; 4 tools; 0 external calls; repeatable | Load test (scripts/perf_recommend.py) | p95 1.332 s; 4 tools, 0 external calls, repeatable | docs/evidence/nfr10_recommend_load.txt | **Pass** |
| SR-01 | Authentication and ownership checks | No token 401; other user's record 404 | Automated API tests | 2/2 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc01_tc02_sr02.txt, docs/evidence/tc09.txt | **Pass** |
| SR-02 | Password hashing | Only Argon2 hashes stored | Automated test + DB inspection | 1/1 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc01_tc02_sr02.txt | **Pass** |
| SR-03 | Upload validation | Allowlist, 2 MB limit, content signature, server-generated names | Automated API + unit tests | 8/8 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc03_tc04_nfr07.txt | **Pass** |
| SR-04 | No secrets in responses or logs | Errors and logs carry no passwords, tokens or resume text | Automated tests + log review | 6/6 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc12.txt | **Pass** |
| SR-05 | Agent tool allowlist | Unknown tools / extra arguments refused and audited | Automated API tests | 8/8 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc08_tc13.txt | **Pass** |
| SR-06 | Consent for external transfer | external_calls = 0 without consent; minimal payload | Automated API + unit tests | 4/4 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/evidence/tc08_tc13.txt | **Pass** |
| SR-07 | HTTPS and secret key in deployment | HTTPS in deployment; default secret refused in production | Automated tests + checklist | 2/2 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md, docs/SECURITY_CHECKLIST.md | **Pass** |
| SR-08 | Security audit events | Security events audited without secrets | Automated tests + checklist | 9/9 deployment security checks passed (see SECURITY_CHECKLIST.md) | docs/SECURITY_CHECKLIST.md | **Pass** |
| SR-09 | Anti-sniffing | TLS 1.2+ in deployment; HTTP redirects to HTTPS; no tokens in URLs | Deployment check | Deployment requirement: the prototype runs only on localhost over HTTP, so TLS, HSTS and certificate checks cannot be performed yet | SRS v1.2 §5.2 | **Not run** |
| SR-10 | Anti-spoofing | Forged, expired, unsigned or tampered tokens 401; identical login errors | Automated API tests | 5/5 automated tests passed (this run) | docs/UNIT_TEST_REPORT.md | **Pass** |
| SR-11 | Anti-man-in-the-middle | CA-signed certificate, HSTS, no mixed content | Deployment check | Deployment requirement: the prototype runs only on localhost over HTTP, so TLS, HSTS and certificate checks cannot be performed yet | SRS v1.2 §5.2 | **Not run** |

## 5. Open issues and recommended actions

- **NFR-01 Search performance — Fail.** p95 4.324 s over 400 requests, 20 users (misses 2 s target). Action: Add an index or cache for skill search, then re-run scripts/perf_search.py (carried to Sprint 4).
- **NFR-04 Usability — Not run.** 5-user study not conducted (docs/USABILITY.md, docs/DEVIATIONS.md). Action: Run the 5-user task study described in the Test Plan and record it in docs/USABILITY.md.
- **NFR-05 Compatibility — Partial.** Full journey works in Chrome; Firefox not tested (see DEVIATIONS.md). Action: Run the core journey in the latest Firefox and update docs/evidence/nfr05_browsers.txt and TEST_REPORT.md.
- **SR-09 Anti-sniffing — Not run.** Deployment requirement: the prototype runs only on localhost over HTTP, so TLS, HSTS and certificate checks cannot be performed yet. Action: Verify when the system is deployed behind a TLS reverse proxy.
- **SR-11 Anti-man-in-the-middle — Not run.** Deployment requirement: the prototype runs only on localhost over HTTP, so TLS, HSTS and certificate checks cannot be performed yet. Action: Verify when the system is deployed behind a TLS reverse proxy.

## 6. Validation activities against the Test Plan

| Activity | Status | Report / evidence |
|---|---|---|
| Unit and component tests (pytest) | Done: 71/71 passed | docs/UNIT_TEST_REPORT.md |
| Code coverage | Done | docs/CODE_COVERAGE_REPORT.md |
| Branch coverage | Done: 100.0% | docs/BRANCH_COVERAGE_REPORT.md |
| System tests TC-01–TC-15 | Done (30 Oct 2026, re-run automatically here) | docs/TEST_REPORT.md |
| Performance (NFR-01, NFR-02, NFR-10) | See section 4 | docs/PERFORMANCE.md, docs/evidence/ |
| Security checklist (SR-07, SR-08) | Done | docs/SECURITY_CHECKLIST.md |
| Usability (NFR-04) | Not run | docs/USABILITY.md |
| Browser compatibility (NFR-05) | Partial | docs/evidence/nfr05_browsers.txt |

## 7. Related documents

SRS v1.2, Test Plan v1.2, docs/TraceabilityMatrix_v1.1.csv, docs/DEVIATIONS.md, docs/DEFECT_LOG.md.

Reproduce: `python scripts/make_validation_reports.py` (re-reads TEST_REPORT.md and the evidence folder each time).
