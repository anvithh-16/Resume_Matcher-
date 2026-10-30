# Deviations from SRS / SAD / Test Plan (explained in the final demo)
| # | Area / requirement | Planned | Actual | Reason | Owner |
|---|---|---|---|---|---|
| 1 | Schedule | Backlog 12 Oct; Sprint-1 19-23 Oct | Done 29-30 Oct | <team writes the real reason> | All |
| 2 | Toolchain | Python 3.12, sqlalchemy==2.0.36 | Anvith's dev machine runs Python 3.14 with sqlalchemy==2.1.6 (CI still runs 3.12) | sqlalchemy 2.0.36 does not install on Python 3.14 | Anvith |
| 3 | SR-07 HTTPS | HTTPS deployment | HTTPS shown locally with a self-signed certificate (uvicorn --ssl-*), not a real hosted deployment | No hosting in scope for the prototype | Anvith |
| 4 | SR-07 secret check | Refuse only the built-in default SECRET_KEY in production | Also refuses the .env.example placeholder | Copying .env.example (as the README says) would otherwise run production with a publicly known JWT key | Anvith |
