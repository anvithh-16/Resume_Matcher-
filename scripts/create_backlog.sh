#!/usr/bin/env bash
set -e
A=anvithh-16; B=ankitharevadal; C=AnirudhN-7
P="Resume Matcher Board"
for l in FR NFR SR sprint-1 sprint-2; do gh label create "$l" --force; done
# Falls back to no assignee if the user has not accepted the collaborator invite yet.
mk() { gh issue create --title "$1" --body "$2" --label "$3" --assignee "$4" --project "$P" 2>/dev/null \
       || { echo "  (could not assign $4 to: $1)"; gh issue create --title "$1" --body "$2" --label "$3" --project "$P"; }; }
# ---- Sprint 1 ----
mk "[NFR-06] Modular project skeleton (2 SP)"        "Layered modules per SAD 2.1. Verify: code review." "NFR,sprint-1" $A
mk "[FR-01] Account registration (2 SP)"             "SRS FR-01. Verify: TC-01." "FR,sprint-1" $A
mk "[FR-02] Login with JWT (3 SP)"                   "SRS FR-02. Verify: TC-02." "FR,sprint-1" $A
mk "[SR-01] Auth required on protected endpoints (2 SP)" "SRS SR-01. Verify: TC-02." "SR,sprint-1" $A
mk "[SR-02] Argon2 password hashing (1 SP)"          "SRS SR-02. Verify: TC-02 + hash inspection." "SR,sprint-1" $A
mk "[FR-03] Resume upload (3 SP)"                    "SRS FR-03. Verify: TC-03." "FR,sprint-1" $B
mk "[SR-03] Upload validation (3 SP)"                "SRS SR-03. Verify: TC-03." "SR,sprint-1" $B
mk "[FR-04] Resume parsing (5 SP)"                   "SRS FR-04. Verify: TC-04." "FR,sprint-1" $B
mk "[FR-05] Job search + seed dataset (3 SP)"        "SRS FR-05. Verify: TC-05." "FR,sprint-1" $B
mk "[NFR-05] Core web pages (3 SP)"                  "Resume + jobs pages. Verify: browser check." "NFR,sprint-1" $B
mk "[FR-06] Resume-job match score (5 SP)"           "SRS FR-06, SAD 4.2. Verify: TC-06." "FR,sprint-1" $C
mk "[FR-07] Skill gap analysis (3 SP)"               "SRS FR-07. Verify: TC-07." "FR,sprint-1" $C
# ---- Sprint 2 ----
mk "[FR-12] Resource ownership checks (3 SP)"        "SRS FR-12. Verify: TC-09." "FR,sprint-2" $A
mk "[FR-14] Consistent error handling (2 SP)"        "SRS FR-14. Verify: TC-12." "FR,sprint-2" $A
mk "[SR-04] No secrets/stack traces in responses or logs (2 SP)" "SRS SR-04. Verify: TC-12." "SR,sprint-2" $A
mk "[SR-08] Audit events (2 SP)"                     "SRS SR-08. Verify: security checklist." "SR,sprint-2" $A
mk "[SR-07] HTTPS / deployment configuration (1 SP)" "SRS SR-07. Verify: security checklist." "SR,sprint-2" $A
mk "[FR-10] Bookmarks (2 SP)"                        "SRS FR-10. Verify: TC-10." "FR,sprint-2" $A
mk "[NFR-09] Reproducible setup + README (2 SP)"     "SRS NFR-09. Verify: clean setup run." "NFR,sprint-2" $A
mk "[FR-11] Application tracking (2 SP)"             "SRS FR-11. Verify: TC-11." "FR,sprint-2" $B
mk "[FR-15] Job dataset administration (3 SP)"       "SRS FR-15. Verify: import validation test." "FR,sprint-2" $B
mk "[NFR-07] Resume deletion (2 SP)"                 "SRS NFR-07. Verify: deletion check." "NFR,sprint-2" $B
mk "[NFR-01] Search performance 5k jobs / 20 users (2 SP)" "SRS NFR-01. Verify: TC-05 load run." "NFR,sprint-2" $B
mk "[NFR-04] Usability evaluation, 5 users (2 SP)"   "SRS NFR-04. Verify: TC-15." "NFR,sprint-2" $B
mk "[NFR-08] Keyboard + labels accessibility (2 SP)" "SRS NFR-08. Verify: TC-15." "NFR,sprint-2" $B
mk "[NFR-05] Chrome + Firefox compatibility (1 SP)"  "SRS NFR-05. Verify: browser checklist." "NFR,sprint-2" $B
mk "[FR-08] Agent orchestrator workflow (5 SP)"      "SRS FR-08. Verify: TC-08." "FR,sprint-2" $C
mk "[SR-05] Tool registry / allowlist (3 SP)"        "SRS SR-05. Verify: TC-08." "SR,sprint-2" $C
mk "[FR-09] Evidence-linked explanations (3 SP)"     "SRS FR-09. Verify: TC-07." "FR,sprint-2" $C
mk "[FR-13] No external actions by default (2 SP)"   "SRS FR-13. Verify: TC-13." "FR,sprint-2" $C
mk "[SR-06] External transfer consent gate (3 SP)"   "SRS SR-06. Verify: TC-13." "SR,sprint-2" $C
mk "[NFR-02] Matching performance run (2 SP)"        "SRS NFR-02. Verify: load measurement." "NFR,sprint-2" $C
mk "[NFR-03] Matching reliability 99/100 (1 SP)"     "SRS NFR-03. Verify: TC-14." "NFR,sprint-2" $C
