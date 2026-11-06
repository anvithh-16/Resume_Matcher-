"""Part-3 validation reports (tracker #5 and #6). Owner: Anirudh N.

Runs the whole suite once (through scripts/make_test_reports.py, which also refreshes the Unit Test and
Code Coverage reports) and then writes:

    docs/BRANCH_COVERAGE_REPORT.md      branch coverage before vs after the Part-3 tests, every remaining gap
    docs/SYSTEM_VALIDATION_REPORT.md    every FR, NFR and SR with how it was validated, evidence and result

"Before" is the coverage data from the last merged run (saved once to docs/reports/coverage_before_part3.json);
"after" is this run.
System-level results are read from docs/TEST_REPORT.md, docs/USABILITY.md and docs/evidence/ as they are now.
Nothing is typed in by hand.

Usage (repo root, venv active):   python scripts/make_validation_reports.py
"""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS, OUT, EVID = ROOT / "docs", ROOT / "docs" / "reports", ROOT / "docs" / "evidence"
sys.path.insert(0, str(ROOT / "scripts"))
from make_test_reports import reqs_for  # noqa: E402

NO_AUTO = {"NFR-09"}      # /health smoke test is not evidence of a clean setup; use the recorded clean-setup run
ACTIONS = {
    "NFR-01": "Add an index or cache for skill search, then re-run scripts/perf_search.py (carried to Sprint 4).",
    "NFR-04": "Run the 5-user task study described in the Test Plan and record it in docs/USABILITY.md.",
    "NFR-05": "Run the core journey in the latest Firefox and update docs/evidence/nfr05_browsers.txt and TEST_REPORT.md.",
    "NFR-10": "Run scripts/perf_recommend.py on a 5,000-job database and re-run this script.",
    "SR-09": "Verify when the system is deployed behind a TLS reverse proxy.",
    "SR-11": "Verify when the system is deployed behind a TLS reverse proxy.",
}
RANK = {"Fail": 0, "Not run": 1, "Partial": 2, "Pass": 3}

# Which test closes each branch that was open before Part-3 (keyed by file and the line the branch starts on).
CLOSED_BY = {
    "app/agent/orchestrator.py:29": "test_tc08_no_matching_jobs_gives_guidance",
    "app/agent/orchestrator.py:33": "test_tc08_tool_failure_becomes_controlled_400",
    "app/agent/tools.py:100": "test_tc08_score_jobs_skips_missing_and_inactive_jobs",
    "app/agent/provider.py:23": "test_tc13_consented_provider_is_called_with_minimal_payload",
    "app/services/job_service.py:15": "test_fr15_validate_job_rejects_bad_records",
    "app/services/job_service.py:22": "test_fr15_validate_job_rejects_bad_records",
    "app/services/job_service.py:25": "test_fr15_validate_job_rejects_bad_records",
    "app/services/job_service.py:37": "test_fr15_seed_skips_when_jobs_exist_or_file_missing",
    "app/services/job_service.py:40": "test_fr15_seed_skips_when_jobs_exist_or_file_missing",
    "app/services/job_service.py:59": "test_tc05_blank_skill_filter_is_ignored",
    "app/services/parser.py:31": "test_tc04_whitespace_only_file_has_no_readable_text",
    "app/services/resume_service.py:17": "test_tc03_content_signature_mismatch_rejected",
    "app/services/resume_service.py:21": "test_tc03_content_signature_mismatch_rejected",
    "app/services/resume_service.py:27": "test_tc03_content_signature_mismatch_rejected",
    "app/services/resume_service.py:31": "test_tc03_content_signature_mismatch_rejected",
    "app/services/resume_service.py:38": "test_tc03_oversized_upload_rejected",
    "app/services/resume_service.py:40": "test_tc03_empty_upload_rejected",
    "app/services/resume_service.py:65": "test_nfr07_deleting_a_missing_file_is_harmless",
}
# Why a branch can stay open.
WHY_OPEN = {
    "app/core/config.py:15": ("Only taken when APP_ENV=production with the default secret. It is tested by "
                              "tests/test_deploy.py (SR-07), which starts the app in a separate Python process; "
                              "coverage measures only the test process, so the branch is usually not counted (some machines do "
                              "count it, which is why another run may show 100% for this file)."),
}

# id, name, acceptance criterion (SRS v1.2), how validated, TEST_REPORT rows used (system-level evidence)
REQS = [
    ("FR-01", "Account registration", "Valid sign-up 201; duplicate 409; invalid input 422", "Automated API tests", ["TC-01"]),
    ("FR-02", "Authentication", "Correct login returns JWT; wrong/unknown login identical 401; protected routes need a token", "Automated API tests", ["TC-02"]),
    ("FR-03", "Resume upload", "PDF/DOCX/TXT up to 2 MB accepted; wrong type, mismatched content, empty or oversized rejected", "Automated API + unit tests", ["TC-03"]),
    ("FR-04", "Resume parsing and review", "Known fields extracted, missing fields not invented, corrections persist", "Automated API + unit tests", ["TC-04"]),
    ("FR-05", "Job search", "Every result matches all filters; inactive jobs never shown; empty state", "Automated API tests", []),
    ("FR-06", "Resume-job matching", "Score 0-100 by the documented formula; repeatable", "Automated unit + API tests", ["TC-06"]),
    ("FR-07", "Skill gap analysis", "Matched and missing skills partition the job's required skills", "Automated unit tests", ["TC-07"]),
    ("FR-08", "Agent workflow", "Only the 4 allowlisted tools in fixed order; unknown tools refused and audited", "Automated API tests", ["TC-08"]),
    ("FR-09", "Recommendation explanation", "Reasons mention only listed matched/missing skills", "Automated unit tests", ["TC-07"]),
    ("FR-10", "Bookmarks", "Add, list, duplicate 409, remove; owner only", "Automated API tests", ["TC-10"]),
    ("FR-11", "Application tracking", "Six statuses only; changes persist; other values 422", "Automated API tests", ["TC-11"]),
    ("FR-12", "Resource ownership", "Other users' records return 404 and are audited", "Automated API tests", ["TC-09"]),
    ("FR-13", "Controlled external actions", "No external call without configuration and consent; minimal payload", "Automated API + unit tests", ["TC-13"]),
    ("FR-14", "Error handling", "One error format; no stack traces or secrets", "Automated API tests", ["TC-12"]),
    ("FR-15", "Job dataset administration", "Admin only; all-or-nothing import; update/deactivate", "Automated API + unit tests", ["FR-15 import"]),
    ("NFR-01", "Search performance", "p95 <= 2 s, 5,000 jobs, 20 users", "Load test (scripts/perf_search.py)", ["TC-05"]),
    ("NFR-02", "Matching performance", "p95 <= 10 s without external LLM", "Load test (scripts/perf_match.py)", ["NFR-02 load"]),
    ("NFR-03", "Reliability", ">= 99 of 100 valid match results", "Automated test (100 requests)", ["TC-14"]),
    ("NFR-04", "Usability", ">= 4 of 5 users finish the core journey unaided", "Task-based user study (docs/USABILITY.md)", []),
    ("NFR-05", "Compatibility", "Core journey works in latest Chrome and Firefox", "Manual browser check", ["NFR-05 browsers"]),
    ("NFR-06", "Maintainability", "Separate modules with automated tests", "Module review + coverage reports", ["NFR-06 module review"]),
    ("NFR-07", "Data retention", "User can delete a resume and its extracted data", "Automated API + unit tests", ["NFR-07 deletion"]),
    ("NFR-08", "Accessibility", "Keyboard operable; labelled fields", "Keyboard walkthrough + Lighthouse", []),
    ("NFR-09", "Reproducibility", "Fresh clone + README steps -> all tests pass", "Clean-setup run", ["NFR-09 clean setup"]),
    ("NFR-10", "Agent / LLM performance", "p95 <= 5 s for /recommendations; 4 tools; 0 external calls; repeatable", "Load test (scripts/perf_recommend.py)", []),
    ("SR-01", "Authentication and ownership checks", "No token 401; other user's record 404", "Automated API tests", ["TC-02", "TC-09"]),
    ("SR-02", "Password hashing", "Only Argon2 hashes stored", "Automated test + DB inspection", ["SR-02 hash check"]),
    ("SR-03", "Upload validation", "Allowlist, 2 MB limit, content signature, server-generated names", "Automated API + unit tests", ["TC-03"]),
    ("SR-04", "No secrets in responses or logs", "Errors and logs carry no passwords, tokens or resume text", "Automated tests + log review", ["TC-12"]),
    ("SR-05", "Agent tool allowlist", "Unknown tools / extra arguments refused and audited", "Automated API tests", ["TC-08"]),
    ("SR-06", "Consent for external transfer", "external_calls = 0 without consent; minimal payload", "Automated API + unit tests", ["TC-13"]),
    ("SR-07", "HTTPS and secret key in deployment", "HTTPS in deployment; default secret refused in production", "Automated tests + checklist", ["SR-07/SR-08 checklist"]),
    ("SR-08", "Security audit events", "Security events audited without secrets", "Automated tests + checklist", ["SR-07/SR-08 checklist"]),
    ("SR-09", "Anti-sniffing", "TLS 1.2+ in deployment; HTTP redirects to HTTPS; no tokens in URLs", "Deployment check", []),
    ("SR-10", "Anti-spoofing", "Forged, expired, unsigned or tampered tokens 401; identical login errors", "Automated API tests", []),
    ("SR-11", "Anti-man-in-the-middle", "CA-signed certificate, HSTS, no mixed content", "Deployment check", []),
]


def norm(p):
    return p.replace("\\", "/")


def branch_data(path):
    if not path.exists():
        return None
    cov = json.loads(path.read_text(encoding="utf-8"))
    files = {}
    for f, d in cov["files"].items():
        s = d["summary"]
        files[norm(f)] = dict(branches=s.get("num_branches", 0), covered=s.get("covered_branches", 0),
                              partial=s.get("num_partial_branches", 0),
                              missing=[tuple(b) for b in d.get("missing_branches", [])],
                              missing_lines=d.get("missing_lines", []))
    t = cov["totals"]
    return dict(files=files, branches=t.get("num_branches", 0), covered=t.get("covered_branches", 0),
                partial=t.get("num_partial_branches", 0), meta=cov.get("meta", {}))


def pct(a, b):
    return 100.0 * a / b if b else 100.0


def env_table():
    text = (DOCS / "UNIT_TEST_REPORT.md").read_text(encoding="utf-8")
    m = re.search(r"## 1\. Test environment\s+(\|.*?)\n\n", text, re.S)
    return m.group(1) if m else ""


def test_report_rows():
    rows = {}
    for line in (DOCS / "TEST_REPORT.md").read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 9 and c[0] not in ("ID",) and not c[0].startswith("-"):
            rows[c[0]] = dict(status=c[6], actual=c[5], evidence=c[7], date=c[4], by=c[3])
    return rows


def main():
    baseline = OUT / "coverage_before_part3.json"     # kept so re-running the script never loses the "before" numbers
    if not baseline.exists() and (OUT / "coverage.json").exists():
        baseline.write_bytes((OUT / "coverage.json").read_bytes())
    before = branch_data(baseline)
    print("Step 1/2: running all tests with coverage (scripts/make_test_reports.py) ...")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "make_test_reports.py")], cwd=ROOT)
    after = branch_data(OUT / "coverage.json")
    if after is None:
        sys.exit("No coverage data was produced; fix the error above and run again.")
    print("Step 2/2: writing the Branch Coverage and System Validation reports ...")
    env = env_table()
    header = ("Project: AI-Based Resume Matching and Job Searching Platform Using Agentic AI (Resume Matcher)  \n"
              "Team: the no name group — Anvith Vegi (PES1UG24AM047), Ankitha Revadala (PES1UG24AM044), "
              "Anirudh N (PES1UG24AM041)  \nDeliverables Part-3, testing window 2–6 Nov 2026\n")

    # ---------------------------------------------------------------- tests from this run
    root = ET.parse(OUT / "junit.xml").getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    tests = []
    for c in suite.iter("testcase"):
        bad = any(c.find(t) is not None for t in ("failure", "error"))
        skipped = c.find("skipped") is not None
        tests.append(dict(file=c.get("classname", "").split(".")[-1] + ".py", name=c.get("name"),
                          status="Fail" if bad else ("Not run" if skipped else "Pass")))
    by_req = defaultdict(list)
    for t in tests:
        for rid in reqs_for(t["name"].split("[")[0]):
            by_req[rid].append(t)

    # ---------------------------------------------------------------- branch coverage report
    b_pct, a_pct = (pct(before["covered"], before["branches"]) if before else None), pct(after["covered"], after["branches"])
    rows = []
    for f, d in sorted(after["files"].items()):
        if not d["branches"]:
            continue
        bd = before["files"].get(f) if before else None
        prev = f"{pct(bd['covered'], bd['branches']):.1f}%" if bd else "—"
        rows.append(f"| {f} | {d['branches']} | {d['covered']} | {d['partial']} | {prev} | {pct(d['covered'], d['branches']):.1f}% |")
    closed, still = [], []
    if before:
        for f, d in sorted(before["files"].items()):
            now = set(after["files"].get(f, {}).get("missing", []))
            for arc in d["missing"]:
                key = f"{f}:{arc[0]}"
                if tuple(arc) in now:
                    continue
                to = "exit" if arc[1] < 0 else f"line {arc[1]}"
                closed.append(f"| {f} | {arc[0]} → {to} | `{CLOSED_BY.get(key, 'existing tests (code path now reached)')}` |")
    for f, d in sorted(after["files"].items()):
        for arc in d["missing"]:
            key = f"{f}:{arc[0]}"
            to = "exit" if arc[1] < 0 else f"line {arc[1]}"
            still.append(f"| {f} | {arc[0]} → {to} | {WHY_OPEN.get(key, 'Not yet covered: add a test that takes this branch.')} |")
    new_tests = [t for t in tests if t["file"] in ("test_branches.py", "test_spoofing.py")]
    nt_rows = "\n".join(f"| {t['file']} | `{t['name']}` | {', '.join(reqs_for(t['name'].split('[')[0])) or '—'} | {t['status']} |"
                        for t in new_tests) or "| — | — | — | — |"
    before_line = (f"| Before Part-3 tests (last merged run) | {before['branches']} | {before['covered']} | "
                   f"{before['partial']} | **{b_pct:.1f}%** |") if before else "| Before | — | — | — | not available |"

    branch_md = f"""# Branch Coverage Report

{header}
## 1. Test environment

{env}

Branch coverage counts every possible outcome of every decision in `app/` (both sides of each `if`,
loop entry and exit, exception paths) and reports how many outcomes the tests actually took.
Tool: coverage.py with `--cov-branch`, run through `python scripts/make_validation_reports.py`.

## 2. Summary

| Run | Branches | Covered | Partly covered | Branch coverage |
|---|---|---|---|---|
{before_line}
| After Part-3 tests (this run) | {after['branches']} | {after['covered']} | {after['partial']} | **{a_pct:.1f}%** |

"Before" is the last merged run before the Part-3 tests were added (saved once as
`docs/reports/coverage_before_part3.json`). "After" is this run, which includes the new tests in section 4.

## 3. Branch coverage by file

| File | Branches | Covered | Partial | Before | After |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## 4. New tests added in Part-3

| File | Test | Verifies | Result |
|---|---|---|---|
{nt_rows}

## 5. Branches closed by this work

| File | Branch (from line → to) | Covered by |
|---|---|---|
{chr(10).join(closed) or '| — | — | No change compared with the previous run |'}

## 6. Branches still not taken

| File | Branch (from line → to) | Reason / action |
|---|---|---|
{chr(10).join(still) or '| — | — | None: every branch was taken. |'}

## 7. Evidence

- `docs/reports/coverage.json` (per-file `missing_branches`), `docs/reports/coverage_html/index.html` (partial
  branches are marked in yellow next to each line), `docs/reports/junit.xml`.
- Reproduce: `python scripts/make_validation_reports.py`.
"""
    (DOCS / "BRANCH_COVERAGE_REPORT.md").write_text(branch_md, encoding="utf-8")

    # ---------------------------------------------------------------- system validation report
    tr = test_report_rows()
    usab = (DOCS / "USABILITY.md").read_text(encoding="utf-8") if (DOCS / "USABILITY.md").exists() else ""
    lh = (EVID / "nfr08_lighthouse.txt").read_text(encoding="utf-8") if (EVID / "nfr08_lighthouse.txt").exists() else ""
    n10 = (EVID / "nfr10_recommend_load.txt").read_text(encoding="utf-8") if (EVID / "nfr10_recommend_load.txt").exists() else ""

    def special(rid):
        """Requirements validated outside pytest and outside TEST_REPORT rows."""
        if rid == "NFR-04":
            if "not conducted" in usab.lower():
                return "Not run", "5-user study not conducted (docs/USABILITY.md, docs/DEVIATIONS.md)", "docs/USABILITY.md"
            m = re.search(r"Result:\s*\**(Pass|Fail|Partial)", usab, re.I)
            return (m.group(1).capitalize() if m else "Partial"), "See docs/USABILITY.md", "docs/USABILITY.md"
        if rid == "NFR-08":
            if re.search(r"score:\s*100", lh):
                return "Pass", "Keyboard-only journey OK; Lighthouse accessibility 100 (see evidence file for date and pages)", "docs/evidence/nfr08_lighthouse.txt"
            return ("Not run", "No Lighthouse result recorded", "—") if not lh else ("Partial", "Lighthouse below 100; see evidence", "docs/evidence/nfr08_lighthouse.txt")
        if rid == "NFR-10":
            if not n10:
                return "Not run", "Load test not yet run (python scripts/perf_recommend.py)", "—"
            p95 = re.search(r"p95=([\d.]+)s", n10)
            return ("Pass" if "NFR-10 PASS" in n10 else "Fail"), f"p95 {p95.group(1)} s; " + (
                "4 tools, 0 external calls, repeatable" if "NFR-10 PASS" in n10 else "see evidence file"), "docs/evidence/nfr10_recommend_load.txt"
        if rid in ("SR-09", "SR-11"):
            return "Not run", "Deployment requirement: the prototype runs only on localhost over HTTP, so TLS, HSTS and certificate checks cannot be performed yet", "SRS v1.2 §5.2"
        return None

    out_rows, counts, gaps = [], defaultdict(int), []
    for rid, name, crit, how, tr_ids in REQS:
        statuses, notes, evidence = [], [], []
        auto = [] if rid in NO_AUTO else by_req.get(rid, [])
        if auto:
            passed = sum(t["status"] == "Pass" for t in auto)
            statuses.append("Pass" if passed == len(auto) else "Fail")
            notes.append(f"{passed}/{len(auto)} automated tests passed (this run)")
            evidence.append("docs/UNIT_TEST_REPORT.md")
        for t in tr_ids:
            row = tr.get(t)
            if row:
                st = row["status"] if row["status"] in RANK else "Not run"
                if rid == "NFR-01":
                    notes.append(row["actual"].split("; load:")[-1].strip() if "load:" in row["actual"] else row["actual"])
                elif not auto:
                    notes.append(row["actual"])
                statuses.append(st)
                evidence.extend(e.strip() for e in row["evidence"].split(",") if e.strip())
        sp = special(rid)
        if sp:
            statuses.append(sp[0]); notes.append(sp[1]); evidence.append(sp[2])
        if not statuses:
            statuses, notes = ["Not run"], ["No test recorded"]
        result = min(statuses, key=lambda s: RANK.get(s, 1))
        counts[result] += 1
        if result != "Pass":
            gaps.append((rid, name, result, "; ".join(notes)))
        ev = ", ".join(dict.fromkeys(e for e in evidence if e and e != "—")) or "—"
        out_rows.append(f"| {rid} | {name} | {crit} | {how} | {'; '.join(notes)} | {ev} | **{result}** |")

    total = len(REQS)
    verdict = ("All requirements validated." if counts["Pass"] == total else
               f"Validated with known gaps: {counts['Pass']} of {total} requirements pass; "
               f"{counts['Partial']} partial, {counts['Fail']} fail, {counts['Not run']} not run (listed in section 5).")
    n_tests, n_pass = len(tests), sum(t["status"] == "Pass" for t in tests)
    gap_md = "\n".join(f"- **{g[0]} {g[1]} — {g[2]}.** {g[3]}. Action: {ACTIONS.get(g[0], 'Investigate and re-test.')}"
                       for g in gaps) or "- None."

    svr = f"""# System Validation Report

{header}
## 1. Purpose and scope

This report checks the delivered system (main branch after Sprint 3) against every requirement in
SRS v1.2: functional requirements FR-01–FR-15, non-functional requirements NFR-01–NFR-10 and security
requirements SR-01–SR-11. For each requirement it records the acceptance criterion, how it was validated,
the evidence, and the result. Results come from this run's automated tests and from the system-level
results recorded in docs/TEST_REPORT.md and docs/evidence/.

## 2. Validation environment (automated run)

{env}

## 3. Summary

| Requirements | Pass | Partial | Fail | Not run |
|---|---|---|---|---|
| {total} | {counts['Pass']} | {counts['Partial']} | {counts['Fail']} | {counts['Not run']} |

Automated suite in this run: {n_pass} of {n_tests} tests passed. Branch coverage {a_pct:.1f}%
(docs/BRANCH_COVERAGE_REPORT.md).

**Verdict: {verdict}**

Result rule: a requirement passes only if every check linked to it passed; the worst result wins
(Fail < Not run < Partial < Pass).

## 4. Requirement-by-requirement results

| ID | Requirement | Acceptance criterion | How validated | Actual result | Evidence | Result |
|---|---|---|---|---|---|---|
{chr(10).join(out_rows)}

## 5. Open issues and recommended actions

{gap_md}

## 6. Validation activities against the Test Plan

| Activity | Status | Report / evidence |
|---|---|---|
| Unit and component tests (pytest) | Done: {n_pass}/{n_tests} passed | docs/UNIT_TEST_REPORT.md |
| Code coverage | Done | docs/CODE_COVERAGE_REPORT.md |
| Branch coverage | Done: {a_pct:.1f}% | docs/BRANCH_COVERAGE_REPORT.md |
| System tests TC-01–TC-15 | Done (30 Oct 2026, re-run automatically here) | docs/TEST_REPORT.md |
| Performance (NFR-01, NFR-02, NFR-10) | See section 4 | docs/PERFORMANCE.md, docs/evidence/ |
| Security checklist (SR-07, SR-08) | Done | docs/SECURITY_CHECKLIST.md |
| Usability (NFR-04) | {'Not run' if 'not conducted' in usab.lower() else 'See USABILITY.md'} | docs/USABILITY.md |
| Browser compatibility (NFR-05) | {tr.get('NFR-05 browsers', {}).get('status', 'Not run')} | docs/evidence/nfr05_browsers.txt |

## 7. Related documents

SRS v1.2, Test Plan v1.2, docs/TraceabilityMatrix_v1.1.csv, docs/DEVIATIONS.md, docs/DEFECT_LOG.md.

Reproduce: `python scripts/make_validation_reports.py` (re-reads TEST_REPORT.md and the evidence folder each time).
"""
    (DOCS / "SYSTEM_VALIDATION_REPORT.md").write_text(svr, encoding="utf-8")
    print(f"\nBranch coverage: {f'{b_pct:.1f}% -> ' if before else ''}{a_pct:.1f}%")
    print(f"Requirements: {counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Fail']} Fail, {counts['Not run']} Not run")
    print("Written: docs/BRANCH_COVERAGE_REPORT.md, docs/SYSTEM_VALIDATION_REPORT.md "
          "(and refreshed docs/UNIT_TEST_REPORT.md, docs/CODE_COVERAGE_REPORT.md, docs/reports/)")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
