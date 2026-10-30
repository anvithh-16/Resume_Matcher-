# Test Execution Report
Environment (fill once): OS, CPU, RAM, Python version, browser versions.
Environment (Anvith's run): Darwin 27.0.0, arm, Python 3.14.0; full suite 49 passed
Environment (Anirudh's run): Darwin 27.0.0, arm, Python 3.14.0
Environment (Ankitha's run): Windows 11, Intel64 Family 6 Model 140 Stepping 1, GenuineIntel, Python 3.13.7
Status values: Pass / Fail / Blocked / Not run. Never mark a test Pass unless it was run.

| ID | Requirement(s) | Owner | Verified by | Date | Actual result | Status | Evidence | Defect |
|---|---|---|---|---|---|---|---|---|
| TC-01 | FR-01 | Anvith | Anirudh | 30 Oct 2026 | 1/1 automated checks passed; valid registration 201, duplicate 409, invalid 422 | Pass | docs/evidence/tc01_tc02_sr02.txt |  |
| TC-02 | FR-02, SR-01 | Anvith | Anirudh | 30 Oct 2026 | 1/1 automated checks passed; valid login gets token, wrong/unknown login same 401, protected route needs token | Pass | docs/evidence/tc01_tc02_sr02.txt |  |
| SR-02 hash check | SR-02 | Anvith | Anirudh | 30 Oct 2026 | 1/1 automated checks passed; stored value is an $argon2 hash, never the plaintext password | Pass | docs/evidence/tc01_tc02_sr02.txt |  |
| TC-03 | FR-03, SR-03 | Ankitha | Anvith | 30 Oct 2026 | 2/2 automated checks passed; valid PDF/DOCX/TXT stored, unsupported/misleading/malformed/oversized rejected | Pass | docs/evidence/tc03_tc04_nfr07.txt |  |
| TC-04 | FR-04 | Ankitha | Anvith | 30 Oct 2026 | 4/4 automated checks passed; known skills/education/experience/email extracted, missing fields not invented | Pass | docs/evidence/tc03_tc04_nfr07.txt |  |
| TC-05 | FR-05, NFR-01 | Ankitha | Anvith | 30 Oct 2026 | 3/3 automated checks passed; load: p95 4.324 s over 400 requests, 20 users (misses 2 s target) | Fail | docs/evidence/tc05.txt, docs/evidence/nfr01_search_load.txt |  |
| TC-06 | FR-06 | Anirudh | Ankitha | 30 Oct 2026 | 5/5 automated checks passed; score in 0-100, repeatable, breakdown returned, no-skills fallback | Pass | docs/evidence/tc06_tc07.txt |  |
| TC-07 | FR-07, FR-09 | Anirudh | Ankitha | 30 Oct 2026 | 1/1 automated checks passed; matched/missing skills correct, explanation never claims missing skills | Pass | docs/evidence/tc06_tc07.txt |  |
| TC-08 | FR-08, SR-05 | Anirudh | Ankitha | 30 Oct 2026 | 5/5 automated checks passed; 4 allowlisted tools in fixed order, unknown tool/bad args rejected, prompt injection ignored | Pass | docs/evidence/tc08_tc13.txt |  |
| TC-09 | FR-12, SR-01 | Anvith | Anirudh | 30 Oct 2026 | 1/1 automated checks passed; other user's resume/application/bookmark/match/recommendation -> 404, no content leaked, access_denied audited | Pass | docs/evidence/tc09.txt |  |
| TC-10 | FR-10 | Anvith | Anirudh | 30 Oct 2026 | 1/1 automated checks passed; add, list, duplicate 409, remove; not visible to another user | Pass | docs/evidence/tc10.txt |  |
| TC-11 | FR-11 | Ankitha | Anvith | 30 Oct 2026 | 3/3 automated checks passed; valid status changes persist, unsupported status rejected | Pass | docs/evidence/tc11.txt |  |
| TC-12 | FR-14, SR-04 | Anvith | Anirudh | 30 Oct 2026 | 6/6 automated checks passed; unexpected error -> 500 with request ID, no stack trace or secret; parser/provider failures safe; logs redacted | Pass | docs/evidence/tc12.txt |  |
| TC-13 | FR-13, SR-06 | Anirudh | Ankitha | 30 Oct 2026 | 3/3 automated checks passed; no external call without config + consent, only minimized fields sent, failure falls back | Pass | docs/evidence/tc08_tc13.txt |  |
| TC-14 | NFR-03 | Anirudh | Ankitha | 30 Oct 2026 | 100/100 valid match results (target >= 99) | Pass | docs/evidence/tc14.txt |  |
| TC-15 | NFR-04, NFR-08 | Ankitha | Anvith | 30 Oct 2026 | Keyboard + Lighthouse: see nfr08_lighthouse.txt; usability: see USABILITY.md | <set Pass/Fail> | docs/evidence/nfr08_lighthouse.txt, docs/USABILITY.md |  |
| FR-15 import | FR-15 | Ankitha | Anvith | 30 Oct 2026 | 2/2 automated checks passed; non-admin 403, invalid batch rejected, import/update/deactivate audited | Pass | docs/evidence/fr15.txt |  |
| NFR-02 load | NFR-02 | Anirudh | Ankitha | 30 Oct 2026 | p95 1.334 s over 200 requests, 20 users, no external provider (target <= 10 s) | Pass | docs/evidence/nfr02_match_load.txt |  |
| NFR-05 browsers | NFR-05 | Ankitha | Anvith | 30 Oct 2026 | Full journey works in Chrome; Firefox not tested (see DEVIATIONS.md) | Partial | docs/evidence/nfr05_browsers.txt |  |
| NFR-06 module review | NFR-06 | Anvith | Anirudh | 30 Oct 2026 | Routes, services, data access, matching and agent in separate modules; 5 service modules, all exercised by tests except job_service | Partial | docs/evidence/nfr06_module_review.txt |  |
| NFR-07 deletion | NFR-07 | Ankitha | Anvith | 30 Oct 2026 | 1/1 automated checks passed; deleted resume returns 404 and its file is removed | Pass | docs/evidence/tc03_tc04_nfr07.txt |  |
| NFR-09 clean setup | NFR-09 | Anvith | Anirudh | 30 Oct 2026 | Fresh clone + README steps on a clean folder: 49 passed (run as python -m pytest -q)| PASS | docs/evidence/full_suite.txt |  |
| SR-07/SR-08 checklist | SR-07, SR-08 | Anvith | Anirudh | 30 Oct 2026 | <fill: see docs/SECURITY_CHECKLIST.md results> | <set Pass/Partial/Fail> | docs/SECURITY_CHECKLIST.md |  |

