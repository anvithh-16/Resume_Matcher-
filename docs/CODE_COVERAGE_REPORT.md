# Code Coverage Report

Project: AI-Based Resume Matching and Job Searching Platform Using Agentic AI (Resume Matcher)  
Team: the no name group — Anvith Vegi (PES1UG24AM047), Ankitha Revadala (PES1UG24AM044), Anirudh N (PES1UG24AM041)  
Deliverables Part-3, testing window 2–6 Nov 2026

## 1. Test environment

| Item | Value |
|---|---|
| Date and time | 06 Nov 2026, 10:18 (UTC+05:30) |
| Run by | AnirudhN-7 |
| Branch / commit | test/part3-validation @ fce7f89 |
| Operating system | Windows 11 (AMD64) |
| Python | 3.14.6 |
| Key packages | pytest 8.3.4, pytest-cov 6.0.0, coverage 7.17.2, fastapi 0.115.6, sqlalchemy 2.1.6, httpx 0.27.2 |
| Command | `python scripts/make_test_reports.py` (pytest + coverage with branch measurement) |

Coverage tool: coverage.py 7.17.2 through pytest-cov 6.0.0, measuring the
`app/` package (all production code) with branch measurement on. Test code is not counted.

## 2. Summary

| Measure | Covered | Total | Coverage |
|---|---|---|---|
| Statements (line coverage) | 817 | 817 | **100.0%** |
| Branches (decision outcomes) | 134 | 134 | **100.0%** |
| Combined (coverage.py total) | — | — | 100.0% |

Branches only partly taken: 0. These are analysed in docs/BRANCH_COVERAGE_REPORT.md.

Test Plan v1.1 does not set a numeric coverage target. For reference, 80% line coverage is a common
industry guideline; this run is above it.

## 3. Coverage by file

| File | Statements | Missed | Line % | Branches | Partial | Branch % | Lines not run |
|---|---|---|---|---|---|---|---|
| app/__init__.py | 0 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/agent/__init__.py | 0 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/agent/orchestrator.py | 22 | 0 | 100.0% | 4 | 0 | 100.0% | — |
| app/agent/provider.py | 19 | 0 | 100.0% | 4 | 0 | 100.0% | — |
| app/agent/tools.py | 68 | 0 | 100.0% | 8 | 0 | 100.0% | — |
| app/core/__init__.py | 0 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/core/audit.py | 7 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/core/config.py | 14 | 0 | 100.0% | 2 | 0 | 100.0% | — |
| app/core/errors.py | 38 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/core/logging_filters.py | 14 | 0 | 100.0% | 4 | 0 | 100.0% | — |
| app/core/security.py | 47 | 0 | 100.0% | 10 | 0 | 100.0% | — |
| app/db/__init__.py | 0 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/db/database.py | 15 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/db/models.py | 62 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/main.py | 31 | 0 | 100.0% | 6 | 0 | 100.0% | — |
| app/routers/__init__.py | 0 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/routers/admin.py | 49 | 0 | 100.0% | 12 | 0 | 100.0% | — |
| app/routers/applications.py | 49 | 0 | 100.0% | 10 | 0 | 100.0% | — |
| app/routers/auth.py | 36 | 0 | 100.0% | 4 | 0 | 100.0% | — |
| app/routers/bookmarks.py | 30 | 0 | 100.0% | 6 | 0 | 100.0% | — |
| app/routers/consent.py | 31 | 0 | 100.0% | 2 | 0 | 100.0% | — |
| app/routers/jobs.py | 19 | 0 | 100.0% | 2 | 0 | 100.0% | — |
| app/routers/matches.py | 20 | 0 | 100.0% | 2 | 0 | 100.0% | — |
| app/routers/recommendations.py | 16 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/routers/resumes.py | 55 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/services/__init__.py | 0 | 0 | 100.0% | 0 | 0 | 100.0% | — |
| app/services/job_service.py | 44 | 0 | 100.0% | 24 | 0 | 100.0% | — |
| app/services/matching.py | 38 | 0 | 100.0% | 8 | 0 | 100.0% | — |
| app/services/parser.py | 36 | 0 | 100.0% | 12 | 0 | 100.0% | — |
| app/services/resume_service.py | 47 | 0 | 100.0% | 14 | 0 | 100.0% | — |
| app/services/skills.py | 10 | 0 | 100.0% | 0 | 0 | 100.0% | — |

## 4. Least-covered files

- None: every line ran.

The lines not run are mostly defensive error paths and start-up code (for example seeding when the seed
file is missing). Any new tests added for them are recorded in the Branch Coverage Report.

## 5. Evidence and how to reproduce

- Browsable report: open `docs/reports/coverage_html/index.html` in a browser (per-line highlighting).
- Raw data: `docs/reports/coverage.json` and `docs/reports/coverage.xml` (Cobertura format).
- Reproduce: `python scripts/make_test_reports.py`.
