# Defect Log
| ID | Found in (TC) | Severity | Steps to reproduce | Status | Fixed in PR |
|---|---|---|---|---|---|
| D-01 | TC-12 (manual log read) | Medium | Add RedactFilter exactly as planned, run uvicorn, make any request: uvicorn.access logs "--- Logging error --- ValueError: not enough values to unpack" because the filter cleared record.args | Fixed (filter redacts uvicorn.access args one by one; regression test test_sr04_access_log_redacted_and_still_formats) | feat/14-log-redaction |
