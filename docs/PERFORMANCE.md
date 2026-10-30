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
