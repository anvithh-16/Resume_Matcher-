# Unit Test Report

Project: AI-Based Resume Matching and Job Searching Platform Using Agentic AI (Resume Matcher)  
Team: the no name group — Anvith Vegi (PES1UG24AM047), Ankitha Revadala (PES1UG24AM044), Anirudh N (PES1UG24AM041)  
Deliverables Part-3, testing window 2–6 Nov 2026

## 1. Test environment

| Item | Value |
|---|---|
| Date and time | 05 Nov 2026, 09:43 (UTC+05:30) |
| Run by | anvithh-16 |
| Branch / commit | docs/part3-reports @ 5f84ade |
| Operating system | Darwin 27.2.0 (arm64) |
| Python | 3.14.0 |
| Key packages | pytest 8.3.4, pytest-cov 6.0.0, coverage 7.17.2, fastapi 0.115.6, sqlalchemy 2.1.6, httpx 0.27.2 |
| Command | `python scripts/make_test_reports.py` (pytest + coverage with branch measurement) |

## 2. Summary

| Total tests | Passed | Failed | Errors | Skipped | Duration | Result |
|---|---|---|---|---|---|---|
| 49 | 49 | 0 | 0 | 0 | 2.04 s | **PASS — all tests passed** |

Test levels: 13 unit tests call functions directly (for example skill normalisation and the scoring
formula); 36 component tests call the REST API in-process through FastAPI's TestClient
with a fresh temporary SQLite database per run. No test uses the network or a real AI provider.

## 3. Results by test file

| Test file | Code under test | Owner | Tests | Passed | Failed | Skipped | Time (s) |
|---|---|---|---|---|---|---|---|
| test_admin.py | routers/admin.py, services/job_service.py | Ankitha Revadala | 2 | 2 | 0 | 0 | 0.16 |
| test_agent.py | agent/orchestrator.py, agent/tools.py, agent/provider.py, routers/consent.py | Anirudh N | 8 | 8 | 0 | 0 | 0.10 |
| test_applications.py | routers/applications.py | Ankitha Revadala | 3 | 3 | 0 | 0 | 0.02 |
| test_auth.py | routers/auth.py, core/security.py | Anvith Vegi | 3 | 3 | 0 | 0 | 0.15 |
| test_bookmarks.py | routers/bookmarks.py | Anvith Vegi | 1 | 1 | 0 | 0 | 0.01 |
| test_deploy.py | core/config.py, main.py | Anvith Vegi | 2 | 2 | 0 | 0 | 0.92 |
| test_errors.py | core/errors.py, core/logging_filters.py | Anvith Vegi | 6 | 6 | 0 | 0 | 0.22 |
| test_health.py | main.py | Anvith Vegi | 1 | 1 | 0 | 0 | 0.00 |
| test_jobs.py | routers/jobs.py, services/job_service.py | Ankitha Revadala | 3 | 3 | 0 | 0 | 0.01 |
| test_matching.py | services/matching.py, routers/matches.py | Anirudh N | 6 | 6 | 0 | 0 | 0.01 |
| test_ownership.py | core/security.py (get_owned_or_404) | Anvith Vegi | 1 | 1 | 0 | 0 | 0.02 |
| test_reliability.py | routers/matches.py, services/matching.py | Anirudh N | 1 | 1 | 0 | 0 | 0.11 |
| test_resumes.py | routers/resumes.py, services/parser.py, services/resume_service.py | Ankitha Revadala | 7 | 7 | 0 | 0 | 0.05 |
| test_skills.py | services/skills.py | Anirudh N | 5 | 5 | 0 | 0 | 0.00 |

## 4. Requirement coverage by automated tests

A requirement passes here only if every automated test linked to it passed. Test case IDs come from the
Test Plan; the mapping to requirements is the one in the traceability matrix.

| Requirement | Tests | Passed | Status |
|---|---|---|---|
| FR-01 | 1 | 1 | Pass |
| FR-02 | 1 | 1 | Pass |
| FR-03 | 2 | 2 | Pass |
| FR-04 | 8 | 8 | Pass |
| FR-05 | 3 | 3 | Pass |
| FR-06 | 5 | 5 | Pass |
| FR-07 | 3 | 3 | Pass |
| FR-08 | 5 | 5 | Pass |
| FR-09 | 1 | 1 | Pass |
| FR-10 | 1 | 1 | Pass |
| FR-11 | 3 | 3 | Pass |
| FR-12 | 1 | 1 | Pass |
| FR-13 | 3 | 3 | Pass |
| FR-14 | 4 | 4 | Pass |
| FR-15 | 2 | 2 | Pass |
| NFR-03 | 1 | 1 | Pass |
| NFR-07 | 1 | 1 | Pass |
| NFR-09 | 1 | 1 | Pass |
| SR-01 | 2 | 2 | Pass |
| SR-02 | 1 | 1 | Pass |
| SR-03 | 2 | 2 | Pass |
| SR-04 | 6 | 6 | Pass |
| SR-05 | 5 | 5 | Pass |
| SR-06 | 3 | 3 | Pass |
| SR-07 | 2 | 2 | Pass |

Requirements not listed are verified by other means (load tests, browser checks, manual review);
see docs/TEST_REPORT.md, docs/PERFORMANCE.md and the System Validation Report.

## 5. All test cases

| # | File | Test | Level | Verifies | Result | Time (s) |
|---|---|---|---|---|---|---|
| 1 | test_admin.py | `test_fr15_import_update_deactivate` | Component (API) | FR-15 | Pass | 0.153 |
| 2 | test_admin.py | `test_fr15_update_validation` | Component (API) | FR-15 | Pass | 0.006 |
| 3 | test_agent.py | `test_tc08_workflow_runs_planned_tools` | Component (API) | TC-08, FR-08, SR-05 | Pass | 0.008 |
| 4 | test_agent.py | `test_tc08_unknown_tool_and_bad_arguments_rejected` | Component (API) | TC-08, FR-08, SR-05 | Pass | 0.003 |
| 5 | test_agent.py | `test_tc08_prompt_injection_changes_nothing` | Component (API) | TC-08, FR-08, SR-05 | Pass | 0.004 |
| 6 | test_agent.py | `test_tc08_no_skills_gives_guidance` | Component (API) | TC-08, FR-08, SR-05 | Pass | 0.002 |
| 7 | test_agent.py | `test_tc08_other_users_resume_is_404` | Component (API) | TC-08, FR-08, SR-05 | Pass | 0.056 |
| 8 | test_agent.py | `test_tc13_no_external_transfer_without_consent` | Component (API) | TC-13, FR-13, SR-06 | Pass | 0.015 |
| 9 | test_agent.py | `test_tc13_provider_failure_falls_back` | Component (API) | TC-13, FR-13, SR-06 | Pass | 0.008 |
| 10 | test_agent.py | `test_tc13_consent_defaults_off_and_is_audited` | Component (API) | TC-13, FR-13, SR-06 | Pass | 0.007 |
| 11 | test_applications.py | `test_tc11_status_lifecycle` | Component (API) | TC-11, FR-11 | Pass | 0.014 |
| 12 | test_applications.py | `test_tc11_notes_and_unsupported_initial_status` | Component (API) | TC-11, FR-11 | Pass | 0.005 |
| 13 | test_applications.py | `test_tc11_other_user_cannot_see_or_change` | Component (API) | TC-11, FR-11 | Pass | 0.005 |
| 14 | test_auth.py | `test_tc01_register_valid_then_duplicate` | Component (API) | TC-01, FR-01 | Pass | 0.030 |
| 15 | test_auth.py | `test_tc02_login_and_protected_endpoint` | Component (API) | TC-02, FR-02, SR-01 | Pass | 0.083 |
| 16 | test_auth.py | `test_sr02_password_stored_only_as_argon2_hash` | Component (API) | SR-02 | Pass | 0.032 |
| 17 | test_bookmarks.py | `test_tc10_bookmark_lifecycle` | Component (API) | TC-10, FR-10 | Pass | 0.013 |
| 18 | test_deploy.py | `test_sr07_production_refuses_default_or_example_secret` | Unit | SR-07 | Pass | 0.475 |
| 19 | test_deploy.py | `test_sr07_production_starts_with_real_secret_and_hides_docs` | Unit | SR-07 | Pass | 0.445 |
| 20 | test_errors.py | `test_sr04_redaction` | Unit | SR-04 | Pass | 0.000 |
| 21 | test_errors.py | `test_tc12_unexpected_error_is_safe` | Component (API) | TC-12, FR-14, SR-04 | Pass | 0.002 |
| 22 | test_errors.py | `test_tc12_validation_error_shape` | Component (API) | TC-12, FR-14, SR-04 | Pass | 0.002 |
| 23 | test_errors.py | `test_sr04_access_log_redacted_and_still_formats` | Unit | SR-04 | Pass | 0.190 |
| 24 | test_errors.py | `test_tc12_parser_failure_is_safe` | Component (API) | TC-12, FR-14, SR-04 | Pass | 0.011 |
| 25 | test_errors.py | `test_tc12_provider_timeout_falls_back` | Component (API) | TC-12, FR-14, SR-04 | Pass | 0.017 |
| 26 | test_health.py | `test_health` | Component (API) | NFR-09 | Pass | 0.001 |
| 27 | test_jobs.py | `test_tc05_search_obeys_filters` | Component (API) | TC-05, FR-05 | Pass | 0.011 |
| 28 | test_jobs.py | `test_tc05_skill_aliases_match` | Component (API) | TC-05, FR-05 | Pass | 0.002 |
| 29 | test_jobs.py | `test_seed_loaded` | Component (API) | FR-05 | Pass | 0.002 |
| 30 | test_matching.py | `test_tc06_range_repeatable_breakdown` | Unit | TC-06, FR-06 | Pass | 0.000 |
| 31 | test_matching.py | `test_tc06_overlap_beats_no_overlap` | Unit | TC-06, FR-06 | Pass | 0.000 |
| 32 | test_matching.py | `test_tc06_no_required_skills_fallback` | Unit | TC-06, FR-06 | Pass | 0.000 |
| 33 | test_matching.py | `test_tc07_gap_and_evidence_only_explanation` | Unit | TC-07, FR-07, FR-09 | Pass | 0.000 |
| 34 | test_matching.py | `test_tc06_api` | Component (API) | TC-06, FR-06 | Pass | 0.005 |
| 35 | test_matching.py | `test_tc06_api_other_users_resume_is_404` | Component (API) | TC-06, FR-06 | Pass | 0.003 |
| 36 | test_ownership.py | `test_tc09_cross_user_access_denied` | Component (API) | TC-09, FR-12, SR-01 | Pass | 0.017 |
| 37 | test_reliability.py | `test_tc14_100_consecutive_valid_matches` | Component (API) | TC-14, NFR-03 | Pass | 0.112 |
| 38 | test_resumes.py | `test_tc03_upload_validation` | Component (API) | TC-03, FR-03, SR-03 | Pass | 0.029 |
| 39 | test_resumes.py | `test_tc03_filename_is_sanitized` | Component (API) | TC-03, FR-03, SR-03 | Pass | 0.002 |
| 40 | test_resumes.py | `test_tc04_parsing_known_fields` | Component (API) | TC-04, FR-04 | Pass | 0.003 |
| 41 | test_resumes.py | `test_tc04_pdf_parses_same_skills` | Component (API) | TC-04, FR-04 | Pass | 0.003 |
| 42 | test_resumes.py | `test_tc04_missing_fields_not_invented` | Component (API) | TC-04, FR-04 | Pass | 0.002 |
| 43 | test_resumes.py | `test_tc04_user_can_correct_profile` | Component (API) | TC-04, FR-04 | Pass | 0.004 |
| 44 | test_resumes.py | `test_nfr07_delete_removes_data` | Component (API) | NFR-07 | Pass | 0.005 |
| 45 | test_skills.py | `test_normalize_aliases_and_case` | Unit | FR-04, FR-07 | Pass | 0.000 |
| 46 | test_skills.py | `test_extract_whole_words_only` | Unit | FR-04 | Pass | 0.000 |
| 47 | test_skills.py | `test_extract_from_team_fixture_resume` | Unit | FR-04 | Pass | 0.000 |
| 48 | test_skills.py | `test_extract_empty_text` | Unit | FR-04 | Pass | 0.000 |
| 49 | test_skills.py | `test_canonical_names_are_their_own_canon` | Unit | FR-07 | Pass | 0.001 |

## 6. Failures and defects

None. Every test passed in this run.

Previously found defects and their fixes are logged in docs/DEFECT_LOG.md.

## 7. Evidence and how to reproduce

- Raw results: `docs/reports/junit.xml` (JUnit XML written by pytest in this run).
- Reproduce: activate the venv, then `python -m pip install -r requirements.txt` and
  `python scripts/make_test_reports.py`.
- The same suite runs automatically on every push and pull request in GitHub Actions (`.github/workflows/ci.yml`).
