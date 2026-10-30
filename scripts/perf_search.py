"""NFR-01 search load test (target: p95 <= 2 s with 5,000 jobs and 20 concurrent users).

Usage (server must already be running, without --reload):
    python scripts/perf_search.py --users 20 --requests 400
Owner: Ankitha Revadala.
"""
import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
QUERIES = ["/jobs?q=python", "/jobs?skill=sql", "/jobs?location=Bengaluru",
           "/jobs?q=developer&employment_type=full-time", "/jobs?skill=react&location=Remote"]


def one(i):
    start = time.perf_counter()
    r = httpx.get(BASE + QUERIES[i % len(QUERIES)], timeout=30)
    return time.perf_counter() - start, r.status_code


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=20)
    ap.add_argument("--requests", type=int, default=400)
    a = ap.parse_args()
    with ThreadPoolExecutor(max_workers=a.users) as pool:
        results = list(pool.map(one, range(a.requests)))
    times = sorted(t for t, _ in results)
    ok = sum(1 for _, s in results if s == 200)
    p95 = times[max(0, int(0.95 * len(times)) - 1)]
    print(f"requests={len(results)} ok={ok} users={a.users} p50={statistics.median(times):.3f}s "
          f"p95={p95:.3f}s max={times[-1]:.3f}s")
    print("NFR-01 PASS" if p95 <= 2.0 and ok == len(results) else "NFR-01 FAIL")
