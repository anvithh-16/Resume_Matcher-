# Performance results

## NFR-01 Search performance (owner: Ankitha Revadala)
- Date: 30 Oct 2026
- Machine: Windows 11, Intel64 Family 6 Model 140 Stepping 1, GenuineIntel; Python 3.13.7
- Dataset: 5,000 synthetic jobs (python -m scripts.gen_jobs 5000, seed 42), perf.db
- Load: 20 concurrent users, 400 GET /api/v1/jobs requests over 5 query mixes
- Command: python scripts/perf_search.py --users 20 --requests 400
- Result: p50 = 3.881 s, p95 = 4.324 s, max = 4.642 s, ok = 400/400
- Target: p95 <= 2 s -> FAIL
- Note: skill filtering runs in SQL with a SQL LIMIT; an earlier version that filtered skills in Python failed a trial load run during development (p95 about 2.3 s), so the filter was moved into SQL.
- Evidence: docs/evidence/nfr01_search_load.txt

## NFR-02 Matching performance (owner: Anirudh N)
- Date: 30 Oct 2026
- Machine: Darwin 27.0.0, arm; Python 3.14.0
- Dataset: 5,000 synthetic jobs (python -m scripts.gen_jobs 5000, seed 42), perf.db
- Fixture: tests/fixtures/resume_good.txt; first 50 active jobs, round-robin
- Load: 20 concurrent users, 200 POST /api/v1/matches requests; external provider disabled (baseline)
- Command: python scripts/perf_match.py --users 20 --requests 200
- Result: p50 = 1.175 s, p95 = 1.334 s, max = 1.708 s, ok = 200/200
- Target: p95 <= 10 s -> PASS
- Evidence: docs/evidence/nfr02_match_load.txt

## NFR-03 Matching reliability (owner: Anirudh N)
- Test: tests/test_reliability.py (TC-14), 100 consecutive valid match requests
- Result: 100/100 valid (target >= 99) -> PASS
- Evidence: docs/evidence/tc14.txt
