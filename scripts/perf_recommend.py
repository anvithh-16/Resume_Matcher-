"""NFR-10 agent / LLM workflow performance (SRS v1.2 section 4.3). Owner: Anirudh N.

Measures POST /api/v1/recommendations under load with the default configuration (no external LLM):
latency p50/p95/max, error rate, tool-call budget (exactly 4 tools), external calls (must be 0 without
consent) and repeatability (same input -> same ranking). Writes docs/evidence/nfr10_recommend_load.txt.

Usage (server must already be running on port 8000 WITHOUT --reload, on a database with 5,000 jobs):
    python scripts/perf_recommend.py --users 20 --requests 200
"""
import argparse
import platform
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
TARGET_P95 = 5.0
EXPECTED_TRACE = ["get_resume_profile", "search_jobs", "score_jobs", "rank_results"]


def setup():
    email, pw = f"perf-{uuid.uuid4().hex[:6]}@test.local", "Passw0rd!x"
    httpx.post(BASE + "/auth/register", json={"email": email, "password": pw})
    token = httpx.post(BASE + "/auth/login", json={"email": email, "password": pw}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resume = Path("tests/fixtures/resume_good.txt").read_bytes()          # fixed fixture
    r = httpx.post(BASE + "/resumes", headers=headers, files={"file": ("cv.txt", resume)})
    r.raise_for_status()
    jobs = httpx.get(BASE + "/jobs", params={"limit": 1}).json()["count"]
    return headers, r.json()["id"], jobs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=20)
    ap.add_argument("--requests", type=int, default=200)
    a = ap.parse_args()
    headers, rid, _ = setup()
    body = {"resume_id": rid, "top_k": 5}

    def one(_):
        start = time.perf_counter()
        r = httpx.post(BASE + "/recommendations", headers=headers, json=body, timeout=120)
        took = time.perf_counter() - start
        data = r.json() if r.status_code == 200 else {}
        return took, r.status_code, data.get("tool_trace"), data.get("external_calls"), \
            [x["job_id"] for x in data.get("recommendations", [])]

    with ThreadPoolExecutor(max_workers=a.users) as pool:
        results = list(pool.map(one, range(a.requests)))

    times = sorted(r[0] for r in results)
    ok = sum(1 for r in results if r[1] == 200)
    p95 = times[max(0, int(0.95 * len(times)) - 1)]
    trace_ok = all(r[2] == EXPECTED_TRACE for r in results if r[1] == 200)
    external = sum((r[3] or 0) for r in results if r[1] == 200)
    rankings = {tuple(r[4]) for r in results if r[1] == 200}
    repeatable = len(rankings) == 1
    passed = p95 <= TARGET_P95 and ok == len(results) and trace_ok and external == 0 and repeatable

    lines = [
        f"NFR-10 agent workflow load test - {datetime.now().strftime('%d %b %Y %H:%M')}",
        f"machine: {platform.system()} {platform.release()} {platform.machine()}; Python {platform.python_version()}",
        f"command: python scripts/perf_recommend.py --users {a.users} --requests {a.requests}",
        f"requests={len(results)} ok={ok} users={a.users} p50={statistics.median(times):.3f}s "
        f"p95={p95:.3f}s max={times[-1]:.3f}s (no external provider)",
        f"tool budget: every response used exactly {len(EXPECTED_TRACE)} tools in order -> {'yes' if trace_ok else 'NO'}",
        f"external calls without consent: {external} (must be 0)",
        f"repeatable ranking across all requests: {'yes' if repeatable else 'NO'} ({len(rankings)} distinct ranking(s))",
        f"error rate: {100 * (len(results) - ok) / len(results):.1f}%",
        f"target: p95 <= {TARGET_P95:.0f} s, 0% errors, 4 tools, 0 external calls, repeatable",
        "NFR-10 PASS" if passed else "NFR-10 FAIL",
    ]
    out = Path("docs/evidence/nfr10_recommend_load.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    perf = Path("docs/PERFORMANCE.md")
    if perf.exists():
        text = perf.read_text(encoding="utf-8")
        section = ("## NFR-10 Agent / LLM workflow performance (owner: Anirudh N)\n"
                   + "\n".join(f"- {x}" for x in lines[1:]) + "\n- Evidence: docs/evidence/nfr10_recommend_load.txt\n")
        start = text.find("## NFR-10")
        if start >= 0:
            end = text.find("\n## ", start + 5)
            text = text[:start] + section + (text[end + 1:] if end >= 0 else "")
        else:
            text = text.rstrip("\n") + "\n\n" + section
        perf.write_text(text, encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSaved to {out} and docs/PERFORMANCE.md")
