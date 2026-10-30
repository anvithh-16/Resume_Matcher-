# Deviations from SRS / SAD / Test Plan (explained in the final demo)
| # | Area / requirement | Planned | Actual | Reason | Owner |
|---|---|---|---|---|---|
| 1 | Schedule | Backlog 12 Oct; Sprint-1 19-23 Oct | Done 29-30 Oct | <team writes the real reason> | All |
| 2 | Toolchain | Python 3.12, sqlalchemy==2.0.36 | Anvith's dev machine runs Python 3.14 with sqlalchemy==2.1.6 (CI still runs 3.12) | sqlalchemy 2.0.36 does not install on Python 3.14 | Anvith |
| 3 | SR-07 HTTPS | HTTPS deployment | HTTPS shown locally with a self-signed certificate (uvicorn --ssl-*), not a real hosted deployment | No hosting in scope for the prototype | Anvith |
| 4 | SR-07 secret check | Refuse only the built-in default SECRET_KEY in production | Also refuses the .env.example placeholder | Copying .env.example (as the README says) would otherwise run production with a publicly known JWT key | Anvith |
| 5 | NFR-05 browsers | Tested on latest Chrome and Firefox | Tested on Chrome only | Firefox not available on the test laptop in the time left | Ankitha |
| 6 | NFR-01 search performance | p95 <= 2 s (5,000 jobs, 20 users) | p95 4.3 s on the Windows test laptop | Laptop CPU/disk limits under 20 concurrent users (same code measured ~0.4 s on a faster machine); a stronger test machine or a server database would be needed | Ankitha |
| 7 | NFR-04 usability study | Five-user task test | Not conducted | Not enough time before the Sprint-2 deadline | Ankitha |