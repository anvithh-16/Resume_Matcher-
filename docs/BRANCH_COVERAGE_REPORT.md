# Branch Coverage Report

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

Branch coverage counts every possible outcome of every decision in `app/` (both sides of each `if`,
loop entry and exit, exception paths) and reports how many outcomes the tests actually took.
Tool: coverage.py with `--cov-branch`, run through `python scripts/make_validation_reports.py`.

## 2. Summary

| Run | Branches | Covered | Partly covered | Branch coverage |
|---|---|---|---|---|
| Before Part-3 tests (last merged run) | 134 | 121 | 13 | **90.3%** |
| After Part-3 tests (this run) | 134 | 134 | 0 | **100.0%** |

"Before" is the last merged run before the Part-3 tests were added (saved once as
`docs/reports/coverage_before_part3.json`). "After" is this run, which includes the new tests in section 4.

## 3. Branch coverage by file

| File | Branches | Covered | Partial | Before | After |
|---|---|---|---|---|---|
| app/agent/orchestrator.py | 4 | 4 | 0 | 75.0% | 100.0% |
| app/agent/provider.py | 4 | 4 | 0 | 100.0% | 100.0% |
| app/agent/tools.py | 8 | 8 | 0 | 87.5% | 100.0% |
| app/core/config.py | 2 | 2 | 0 | 100.0% | 100.0% |
| app/core/logging_filters.py | 4 | 4 | 0 | 100.0% | 100.0% |
| app/core/security.py | 10 | 10 | 0 | 100.0% | 100.0% |
| app/main.py | 6 | 6 | 0 | 100.0% | 100.0% |
| app/routers/admin.py | 12 | 12 | 0 | 100.0% | 100.0% |
| app/routers/applications.py | 10 | 10 | 0 | 100.0% | 100.0% |
| app/routers/auth.py | 4 | 4 | 0 | 100.0% | 100.0% |
| app/routers/bookmarks.py | 6 | 6 | 0 | 100.0% | 100.0% |
| app/routers/consent.py | 2 | 2 | 0 | 100.0% | 100.0% |
| app/routers/jobs.py | 2 | 2 | 0 | 100.0% | 100.0% |
| app/routers/matches.py | 2 | 2 | 0 | 100.0% | 100.0% |
| app/services/job_service.py | 24 | 24 | 0 | 75.0% | 100.0% |
| app/services/matching.py | 8 | 8 | 0 | 100.0% | 100.0% |
| app/services/parser.py | 12 | 12 | 0 | 91.7% | 100.0% |
| app/services/resume_service.py | 14 | 14 | 0 | 71.4% | 100.0% |

## 4. New tests added in Part-3

| File | Test | Verifies | Result |
|---|---|---|---|
| test_branches.py | `test_tc08_no_matching_jobs_gives_guidance` | TC-08, FR-08, SR-05 | Pass |
| test_branches.py | `test_tc08_tool_failure_becomes_controlled_400` | TC-08, FR-08, SR-05 | Pass |
| test_branches.py | `test_tc08_score_jobs_skips_missing_and_inactive_jobs` | TC-08, FR-08, SR-05 | Pass |
| test_branches.py | `test_tc13_consented_provider_is_called_with_minimal_payload` | TC-13, FR-13, SR-06 | Pass |
| test_branches.py | `test_fr15_validate_job_rejects_bad_records[not-an-object]` | FR-15 | Pass |
| test_branches.py | `test_fr15_validate_job_rejects_bad_records[skills-not-a-list]` | FR-15 | Pass |
| test_branches.py | `test_fr15_validate_job_rejects_bad_records[unknown-employment-type]` | FR-15 | Pass |
| test_branches.py | `test_fr15_seed_skips_when_jobs_exist_or_file_missing` | FR-15 | Pass |
| test_branches.py | `test_tc05_blank_skill_filter_is_ignored` | TC-05, FR-05 | Pass |
| test_branches.py | `test_tc03_content_signature_mismatch_rejected[docx-not-zip]` | TC-03, FR-03, SR-03 | Pass |
| test_branches.py | `test_tc03_content_signature_mismatch_rejected[docx-broken-zip]` | TC-03, FR-03, SR-03 | Pass |
| test_branches.py | `test_tc03_content_signature_mismatch_rejected[txt-null-byte]` | TC-03, FR-03, SR-03 | Pass |
| test_branches.py | `test_tc03_content_signature_mismatch_rejected[txt-invalid-utf8]` | TC-03, FR-03, SR-03 | Pass |
| test_branches.py | `test_tc03_oversized_upload_rejected` | TC-03, FR-03, SR-03 | Pass |
| test_branches.py | `test_tc04_whitespace_only_file_has_no_readable_text` | TC-04, FR-04 | Pass |
| test_branches.py | `test_nfr07_deleting_a_missing_file_is_harmless` | NFR-07 | Pass |
| test_branches.py | `test_tc03_empty_upload_rejected` | TC-03, FR-03, SR-03 | Pass |
| test_spoofing.py | `test_sr10_token_signed_with_another_key_is_refused` | SR-10 | Pass |
| test_spoofing.py | `test_sr10_expired_token_is_refused` | SR-10 | Pass |
| test_spoofing.py | `test_sr10_unsigned_alg_none_token_is_refused` | SR-10 | Pass |
| test_spoofing.py | `test_sr10_tampered_token_is_refused` | SR-10 | Pass |
| test_spoofing.py | `test_sr10_login_errors_do_not_reveal_accounts` | SR-10 | Pass |

## 5. Branches closed by this work

| File | Branch (from line → to) | Covered by |
|---|---|---|
| app/agent/orchestrator.py | 29 → line 30 | `test_tc08_no_matching_jobs_gives_guidance` |
| app/agent/tools.py | 100 → line 98 | `test_tc08_score_jobs_skips_missing_and_inactive_jobs` |
| app/services/job_service.py | 15 → line 16 | `test_fr15_validate_job_rejects_bad_records` |
| app/services/job_service.py | 22 → line 23 | `test_fr15_validate_job_rejects_bad_records` |
| app/services/job_service.py | 25 → line 26 | `test_fr15_validate_job_rejects_bad_records` |
| app/services/job_service.py | 37 → line 38 | `test_fr15_seed_skips_when_jobs_exist_or_file_missing` |
| app/services/job_service.py | 40 → line 41 | `test_fr15_seed_skips_when_jobs_exist_or_file_missing` |
| app/services/job_service.py | 59 → line 64 | `test_tc05_blank_skill_filter_is_ignored` |
| app/services/parser.py | 31 → line 32 | `test_tc04_whitespace_only_file_has_no_readable_text` |
| app/services/resume_service.py | 17 → line 18 | `test_tc03_content_signature_mismatch_rejected` |
| app/services/resume_service.py | 27 → line 28 | `test_tc03_content_signature_mismatch_rejected` |
| app/services/resume_service.py | 40 → line 41 | `test_tc03_empty_upload_rejected` |
| app/services/resume_service.py | 65 → exit | `test_nfr07_deleting_a_missing_file_is_harmless` |

## 6. Branches still not taken

| File | Branch (from line → to) | Reason / action |
|---|---|---|
| — | — | None: every branch was taken. |

## 7. Evidence

- `docs/reports/coverage.json` (per-file `missing_branches`), `docs/reports/coverage_html/index.html` (partial
  branches are marked in yellow next to each line), `docs/reports/junit.xml`.
- Reproduce: `python scripts/make_validation_reports.py`.
