"""Part-3 test reports: runs the whole pytest suite once with coverage and writes

    docs/UNIT_TEST_REPORT.md         (tracker #3)
    docs/CODE_COVERAGE_REPORT.md     (tracker #4)
    docs/reports/junit.xml           raw pytest results (machine-readable evidence)
    docs/reports/coverage.json       raw coverage data (line + branch)
    docs/reports/coverage.xml        Cobertura format
    docs/reports/coverage_html/      browsable coverage pages (open index.html)

Usage (repo root, venv active, pytest-cov installed):
    python scripts/make_test_reports.py

Every number in the reports comes from this run. Nothing is typed in by hand.
"""
import ast
import datetime as dt
import importlib.metadata as md
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = DOCS / "reports"

# Which requirements each test-case ID verifies (from the Test Plan / traceability matrix).
TC_REQ = {
    "TC-01": ["FR-01"], "TC-02": ["FR-02", "SR-01"], "TC-03": ["FR-03", "SR-03"], "TC-04": ["FR-04"],
    "TC-05": ["FR-05"], "TC-06": ["FR-06"], "TC-07": ["FR-07", "FR-09"], "TC-08": ["FR-08", "SR-05"],
    "TC-09": ["FR-12", "SR-01"], "TC-10": ["FR-10"], "TC-11": ["FR-11"], "TC-12": ["FR-14", "SR-04"],
    "TC-13": ["FR-13", "SR-06"], "TC-14": ["NFR-03"],
}
# Tests whose names carry no TC/FR/SR/NFR id.
EXTRA_REQ = {
    "test_health": ["NFR-09"],
    "test_seed_loaded": ["FR-05"],
    "test_normalize_aliases_and_case": ["FR-04", "FR-07"],
    "test_extract_whole_words_only": ["FR-04"],
    "test_extract_from_team_fixture_resume": ["FR-04"],
    "test_extract_empty_text": ["FR-04"],
    "test_canonical_names_are_their_own_canon": ["FR-07"],
}
MODULE_UNDER_TEST = {
    "test_admin.py": "routers/admin.py, services/job_service.py",
    "test_agent.py": "agent/orchestrator.py, agent/tools.py, agent/provider.py, routers/consent.py",
    "test_applications.py": "routers/applications.py",
    "test_auth.py": "routers/auth.py, core/security.py",
    "test_bookmarks.py": "routers/bookmarks.py",
    "test_deploy.py": "core/config.py, main.py",
    "test_errors.py": "core/errors.py, core/logging_filters.py",
    "test_health.py": "main.py",
    "test_jobs.py": "routers/jobs.py, services/job_service.py",
    "test_matching.py": "services/matching.py, routers/matches.py",
    "test_ownership.py": "core/security.py (get_owned_or_404)",
    "test_reliability.py": "routers/matches.py, services/matching.py",
    "test_resumes.py": "routers/resumes.py, services/parser.py, services/resume_service.py",
    "test_skills.py": "services/skills.py",
}


GIT_NAMES = {"anvithh-16": "Anvith Vegi"}   # GitHub handles -> real names


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def version(pkg):
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return "not installed"


def git(*args):
    r = run(["git", *args])
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def reqs_for(name):
    ids = []
    for kind, num in re.findall(r"(tc|fr|nfr|sr)(\d+)", name.lower()):
        tag = {"tc": "TC", "fr": "FR", "nfr": "NFR", "sr": "SR"}[kind] + "-" + num.zfill(2)
        ids.extend([tag] + TC_REQ.get(tag, []) if kind == "tc" else [tag])
    ids.extend(EXTRA_REQ.get(name, []))
    return list(OrderedDict.fromkeys(ids))


def test_info():
    """Owner (from each file's docstring) and level (API via TestClient vs pure unit) for every test."""
    owners, level = {}, {}
    for f in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree) or ""
        m = re.search(r"Owner:\s*([^.\n]+)", doc)
        if m:
            owners[f.name] = m.group(1).strip()
        else:   # no "Owner:" line in the docstring: use whoever first added the file to git
            first = git("log", "--diff-filter=A", "--format=%an", "--", str(f.relative_to(ROOT))).splitlines()
            name = first[-1].strip('"“” ') if first else ""
            owners[f.name] = GIT_NAMES.get(name, name) or "—"
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                args = {a.arg for a in node.args.args}
                api = bool(args & {"client", "user_a", "user_b", "admin"})
                level[(f.name, node.name)] = "Component (API)" if api else "Unit"
    return owners, level


def pct(a, b):
    return 100.0 * a / b if b else 100.0


def main():
    try:
        import pytest_cov  # noqa: F401
    except ImportError:
        sys.exit("pytest-cov is missing. Run:  python -m pip install pytest-cov==6.0.0   then run this script again.")

    OUT.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUT / "coverage_html", ignore_errors=True)
    for stale in (ROOT / "app.db", ROOT / ".coverage"):
        if stale.exists():
            stale.unlink()

    started = dt.datetime.now().astimezone()
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           f"--junitxml={OUT / 'junit.xml'}",
           "--cov=app", "--cov-branch",
           f"--cov-report=json:{OUT / 'coverage.json'}",
           f"--cov-report=xml:{OUT / 'coverage.xml'}",
           f"--cov-report=html:{OUT / 'coverage_html'}",
           "--cov-report=term"]
    print("Running:", " ".join(Path(c).name if i == 0 else c for i, c in enumerate(cmd)))
    res = run(cmd)
    print(res.stdout[-1500:])
    if not (OUT / "junit.xml").exists():
        print(res.stderr[-3000:])
        sys.exit("pytest did not produce results; fix the error above and run again.")
    (OUT / "coverage_html" / ".gitignore").unlink(missing_ok=True)   # coverage.py adds one; we want the pages in git
    for stale in (ROOT / ".coverage",):
        if stale.exists():
            stale.unlink()

    env = OrderedDict([
        ("Date and time", started.strftime("%d %b %Y, %H:%M") + " (UTC" + started.strftime("%z")[:3] + ":" + started.strftime("%z")[3:] + ")"),
        ("Run by", git("config", "user.name")),
        ("Branch / commit", f"{git('rev-parse', '--abbrev-ref', 'HEAD')} @ {git('rev-parse', '--short', 'HEAD')}"),
        ("Operating system", f"{platform.system()} {platform.release()} ({platform.machine()})"),
        ("Python", platform.python_version()),
        ("Key packages", ", ".join(f"{p} {version(p)}" for p in
                                   ["pytest", "pytest-cov", "coverage", "fastapi", "sqlalchemy", "httpx"])),
        ("Command", "`python scripts/make_test_reports.py` (pytest + coverage with branch measurement)"),
    ])
    env_md = "| Item | Value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in env.items())
    header = ("Project: AI-Based Resume Matching and Job Searching Platform Using Agentic AI (Resume Matcher)  \n"
              "Team: the no name group — Anvith Vegi (PES1UG24AM047), Ankitha Revadala (PES1UG24AM044), "
              "Anirudh N (PES1UG24AM041)  \nDeliverables Part-3, testing window 2–6 Nov 2026\n")

    # ------------------------------------------------------------------ unit test report
    owners, level = test_info()
    root = ET.parse(OUT / "junit.xml").getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    cases = []
    for c in suite.iter("testcase"):
        file = c.get("classname", "").split(".")[-1] + ".py"
        status, msg = "Pass", ""
        for tag, label in (("failure", "Fail"), ("error", "Error"), ("skipped", "Skipped")):
            el = c.find(tag)
            if el is not None:
                status, msg = label, (el.get("message") or el.text or "").strip().splitlines()[0][:200] if (el.get("message") or el.text) else label
        cases.append(dict(file=file, name=c.get("name"), time=float(c.get("time", 0)), status=status, msg=msg,
                          reqs=reqs_for(c.get("name")), level=level.get((file, c.get("name")), "—")))
    total = len(cases)
    count = {s: sum(1 for c in cases if c["status"] == s) for s in ("Pass", "Fail", "Error", "Skipped")}
    duration = float(suite.get("time", sum(c["time"] for c in cases)))
    verdict = "PASS — all tests passed" if count["Pass"] == total else f"FAIL — {total - count['Pass']} test(s) did not pass"

    by_file = defaultdict(list)
    for c in cases:
        by_file[c["file"]].append(c)
    file_rows = "\n".join(
        f"| {f} | {MODULE_UNDER_TEST.get(f, '—')} | {owners.get(f, '—')} | {len(cs)} | "
        f"{sum(c['status'] == 'Pass' for c in cs)} | {sum(c['status'] in ('Fail', 'Error') for c in cs)} | "
        f"{sum(c['status'] == 'Skipped' for c in cs)} | {sum(c['time'] for c in cs):.2f} |"
        for f, cs in sorted(by_file.items()))
    case_rows = "\n".join(
        f"| {i} | {c['file']} | `{c['name']}` | {c['level']} | {', '.join(c['reqs']) or '—'} | {c['status']} | {c['time']:.3f} |"
        for i, c in enumerate(cases, 1))
    req_tests = defaultdict(list)
    for c in cases:
        for r in c["reqs"]:
            if not r.startswith("TC-"):
                req_tests[r].append(c)

    def req_key(r):
        k, n = r.split("-")
        return ({"FR": 0, "NFR": 1, "SR": 2}.get(k, 3), int(n))
    req_rows = "\n".join(
        f"| {r} | {len(cs)} | {sum(c['status'] == 'Pass' for c in cs)} | "
        f"{'Pass' if all(c['status'] == 'Pass' for c in cs) else 'Fail'} |"
        for r, cs in sorted(req_tests.items(), key=lambda kv: req_key(kv[0])))
    fails = [c for c in cases if c["status"] in ("Fail", "Error")]
    fail_md = ("None. Every test passed in this run." if not fails else
               "\n".join(f"- `{c['file']}::{c['name']}` — {c['status']}: {c['msg']}" for c in fails))
    n_unit = sum(c["level"] == "Unit" for c in cases)

    unit = f"""# Unit Test Report

{header}
## 1. Test environment

{env_md}

## 2. Summary

| Total tests | Passed | Failed | Errors | Skipped | Duration | Result |
|---|---|---|---|---|---|---|
| {total} | {count['Pass']} | {count['Fail']} | {count['Error']} | {count['Skipped']} | {duration:.2f} s | **{verdict}** |

Test levels: {n_unit} unit tests call functions directly (for example skill normalisation and the scoring
formula); {total - n_unit} component tests call the REST API in-process through FastAPI's TestClient
with a fresh temporary SQLite database per run. No test uses the network or a real AI provider.

## 3. Results by test file

| Test file | Code under test | Owner | Tests | Passed | Failed | Skipped | Time (s) |
|---|---|---|---|---|---|---|---|
{file_rows}

## 4. Requirement coverage by automated tests

A requirement passes here only if every automated test linked to it passed. Test case IDs come from the
Test Plan; the mapping to requirements is the one in the traceability matrix.

| Requirement | Tests | Passed | Status |
|---|---|---|---|
{req_rows}

Requirements not listed are verified by other means (load tests, browser checks, manual review);
see docs/TEST_REPORT.md, docs/PERFORMANCE.md and the System Validation Report.

## 5. All test cases

| # | File | Test | Level | Verifies | Result | Time (s) |
|---|---|---|---|---|---|---|
{case_rows}

## 6. Failures and defects

{fail_md}

Previously found defects and their fixes are logged in docs/DEFECT_LOG.md.

## 7. Evidence and how to reproduce

- Raw results: `docs/reports/junit.xml` (JUnit XML written by pytest in this run).
- Reproduce: activate the venv, then `python -m pip install -r requirements.txt` and
  `python scripts/make_test_reports.py`.
- The same suite runs automatically on every push and pull request in GitHub Actions (`.github/workflows/ci.yml`).
"""
    (DOCS / "UNIT_TEST_REPORT.md").write_text(unit, encoding="utf-8")

    # ------------------------------------------------------------------ code coverage report
    cov = json.loads((OUT / "coverage.json").read_text(encoding="utf-8"))
    t = cov["totals"]
    stm, miss = t["num_statements"], t["missing_lines"]
    br, br_cov, br_part = t.get("num_branches", 0), t.get("covered_branches", 0), t.get("num_partial_branches", 0)
    line_pct, br_pct = pct(stm - miss, stm), pct(br_cov, br)

    def ranges(nums):
        out, nums = [], sorted(nums)
        i = 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            out.append(str(nums[i]) if i == j else f"{nums[i]}–{nums[j]}")
            i = j + 1
        return ", ".join(out)

    rows, low = [], []
    for path, fdata in sorted(cov["files"].items()):
        s = fdata["summary"]
        name = path.replace("\\", "/")
        lp = pct(s["num_statements"] - s["missing_lines"], s["num_statements"])
        bp = pct(s.get("covered_branches", 0), s.get("num_branches", 0))
        rows.append(f"| {name} | {s['num_statements']} | {s['missing_lines']} | {lp:.1f}% | "
                    f"{s.get('num_branches', 0)} | {s.get('num_partial_branches', 0)} | {bp:.1f}% | "
                    f"{ranges(fdata.get('missing_lines', [])) or '—'} |")
        if s["missing_lines"]:
            low.append((lp, name, s["missing_lines"], ranges(fdata.get("missing_lines", []))))
    low.sort()
    low_md = "\n".join(f"- **{n}** — {p:.1f}% ({m} line{'s' if m != 1 else ''} not run: {r})" for p, n, m, r in low[:6]) or "- None: every line ran."

    cover = f"""# Code Coverage Report

{header}
## 1. Test environment

{env_md}

Coverage tool: coverage.py {version('coverage')} through pytest-cov {version('pytest-cov')}, measuring the
`app/` package (all production code) with branch measurement on. Test code is not counted.

## 2. Summary

| Measure | Covered | Total | Coverage |
|---|---|---|---|
| Statements (line coverage) | {stm - miss} | {stm} | **{line_pct:.1f}%** |
| Branches (decision outcomes) | {br_cov} | {br} | **{br_pct:.1f}%** |
| Combined (coverage.py total) | — | — | {t['percent_covered']:.1f}% |

Branches only partly taken: {br_part}. These are analysed in docs/BRANCH_COVERAGE_REPORT.md.

Test Plan v1.1 does not set a numeric coverage target. For reference, 80% line coverage is a common
industry guideline; this run is {'above' if line_pct >= 80 else 'below'} it.

## 3. Coverage by file

| File | Statements | Missed | Line % | Branches | Partial | Branch % | Lines not run |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## 4. Least-covered files

{low_md}

The lines not run are mostly defensive error paths and start-up code (for example seeding when the seed
file is missing). Any new tests added for them are recorded in the Branch Coverage Report.

## 5. Evidence and how to reproduce

- Browsable report: open `docs/reports/coverage_html/index.html` in a browser (per-line highlighting).
- Raw data: `docs/reports/coverage.json` and `docs/reports/coverage.xml` (Cobertura format).
- Reproduce: `python scripts/make_test_reports.py`.
"""
    (DOCS / "CODE_COVERAGE_REPORT.md").write_text(cover, encoding="utf-8")

    for stale in (ROOT / "app.db",):
        if stale.exists():
            stale.unlink()
    print(f"\nTests: {count['Pass']}/{total} passed   Line coverage: {line_pct:.1f}%   Branch coverage: {br_pct:.1f}%")
    print("Written: docs/UNIT_TEST_REPORT.md, docs/CODE_COVERAGE_REPORT.md, docs/reports/ (junit.xml, coverage.json, coverage.xml, coverage_html/)")
    sys.exit(0 if count["Pass"] == total else 1)


if __name__ == "__main__":
    main()
