"""NFR-02 matching load measurement (target: p95 <= 10 s). Owner: Anirudh N.

Usage (server must already be running, without --reload):
    python scripts/perf_match.py --users 20 --requests 200
Uses the fixed fixture tests/fixtures/resume_good.txt and the first 50 active jobs.
"""
import argparse
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000/api/v1"


def setup():
    email, pw = f"perf-{uuid.uuid4().hex[:6]}@test.local", "Passw0rd!x"
    httpx.post(BASE + "/auth/register", json={"email": email, "password": pw})
    token = httpx.post(BASE + "/auth/login", json={"email": email, "password": pw}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resume = Path("tests/fixtures/resume_good.txt").read_bytes()          # fixed fixture
    r = httpx.post(BASE + "/resumes", headers=headers, files={"file": ("cv.txt", resume)})
    r.raise_for_status()
    jobs = [j["id"] for j in httpx.get(BASE + "/jobs", params={"limit": 50}).json()["results"]]
    if not jobs:
        raise SystemExit("No jobs in the database - seed it first (python -m scripts.gen_jobs 5000).")
    return headers, r.json()["id"], jobs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=20)
    ap.add_argument("--requests", type=int, default=200)
    a = ap.parse_args()
    headers, rid, jobs = setup()

    def one(i):
        start = time.perf_counter()
        r = httpx.post(BASE + "/matches", headers=headers, timeout=60,
                       json={"resume_id": rid, "job_id": jobs[i % len(jobs)]})
        return time.perf_counter() - start, r.status_code

    with ThreadPoolExecutor(max_workers=a.users) as pool:
        results = list(pool.map(one, range(a.requests)))
    times = sorted(t for t, _ in results)
    ok = sum(1 for _, s in results if s == 200)
    p95 = times[max(0, int(0.95 * len(times)) - 1)]
    print(f"requests={len(results)} ok={ok} users={a.users} p50={statistics.median(times):.3f}s "
          f"p95={p95:.3f}s max={times[-1]:.3f}s (no external provider)")
    print("NFR-02 PASS" if p95 <= 10 and ok == len(results) else "NFR-02 FAIL")
