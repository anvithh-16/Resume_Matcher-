# Deviations from SRS / SAD / Test Plan (explained in the final demo)
| # | Area / requirement | Planned | Actual | Reason | Owner |
|---|---|---|---|---|---|
| 1 | Schedule | Backlog 12 Oct; Sprint-1 19-23 Oct | Done 29-30 Oct | WRITE THE REAL REASON THE SCHEDULE SLIPPED | All |
| 2 | Toolchain | Python 3.12, sqlalchemy==2.0.36 | Anvith's dev machine runs Python 3.14 with sqlalchemy==2.1.6 (CI still runs 3.12) | sqlalchemy 2.0.36 does not install on Python 3.14 | Anvith |
| 3 | SR-07 HTTPS | HTTPS deployment | HTTPS shown locally with a self-signed certificate (uvicorn --ssl-*), not a real hosted deployment | No hosting in scope for the prototype | Anvith |
| 4 | SR-07 secret check | Refuse only the built-in default SECRET_KEY in production | Also refuses the .env.example placeholder | Copying .env.example (as the README says) would otherwise run production with a publicly known JWT key | Anvith |
| 5 | NFR-05 browsers | Tested on latest Chrome and Firefox | Tested on Chrome only | Firefox not available on the test laptop in the time left | Ankitha |
| 6 | NFR-01 search performance | p95 <= 2 s (5,000 jobs, 20 users) | p95 4.3 s on the Windows test laptop | Laptop CPU/disk limits under 20 concurrent users (same code measured ~0.4 s on a faster machine); a stronger test machine or a server database would be needed | Ankitha |
| 7 | NFR-04 usability study | Five-user task test | Not conducted | Not enough time before the Sprint-2 deadline | Ankitha |
| 8 | FR-08 / FR-13 / SR-06 external AI | Optional external LLM provider | Mock provider (app/agent/provider.py) behind the consent gate; no real LLM | Core workflow must work offline and stay repeatable (SRS 2.6); consent flow is still fully demonstrated | Anirudh |
| 9 | FR-08 agent | Agent "decides which registered tool to call" | Fixed-policy orchestrator calling 4 allowlisted tools in order | Security and reproducibility (SAD 2.5 trade-off); prompt injection cannot add tools | Anirudh |
| 10 | FR-06 keyword similarity | "cosine similarity between normalized resume text and job description" | Bag-of-words cosine with small stop-word list, over job title + description | Deterministic, no extra dependency | Anirudh |
| 11 | SAD 5.2 endpoints | No consent endpoints listed | Added GET/PUT /api/v1/consent | Needed for SR-06 consent setting | Anirudh |
| 12 | Matching for jobs with no required skills | "documented fallback" (unspecified) | score = 100 x keyword_similarity | Avoids divide-by-zero, documented in SAD v1.1 4.2 | Anirudh |
| 13 | FR-03 resume formats | "configured supported formats" (open) | PDF, DOCX, TXT; 2 MB limit; content checked by file signature | SRS 7.1 open decision closed | Ankitha |
| 14 | SAD 5.2 endpoints (resumes/admin) | No list / correction / job update endpoints | Added GET /resumes, PUT /resumes/{id}/profile, PATCH /admin/jobs/{id} | UI needs a resume list; SAD 4.1 says parsed fields may be corrected; FR-15 update/deactivate | Ankitha |
| 15 | FR-15 import | Invalid records rejected | Whole batch rejected if any row is invalid (all-or-nothing) | Prevents half-imported datasets | Ankitha |
| 16 | GET /jobs auth | "Required or public per implementation decision" | Public | Job listings are not private data | Ankitha |
| 17 | Frontend | Optional browser client (SRS 7.1) | Plain HTML + JavaScript pages served by FastAPI | Simple, no build step | Ankitha |
| 18 | NFR-01 implementation | Not specified | Skill filter moved into SQL after a trial load run during development failed (p95 about 2.3 s) | Needed to approach the 2 s target | Ankitha |
| 19 | Sprint-2 video length | Two-minute Sprint-2 video | Video is about 75 seconds | Covers the full Sprint-2 flow; recorded under time pressure | Anirudh |
