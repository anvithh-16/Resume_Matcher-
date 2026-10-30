# Resume Matcher

A web application that matches job seekers' resumes to job postings. Candidates upload a resume, the system parses it into skills, and jobs are ranked by match score. Admins manage the job catalogue.

Built as the Software Engineering mini-project (PES University, Semester 5).

## Team

| Name | SRN | GitHub | Area |
|---|---|---|---|
| Anvith | PES1UG24AM047 | [@anvithh-16](https://github.com/anvithh-16) | Skeleton, auth, security, CI |
| Ankitha Revadala | PES1UG24AM044 | [@ankitharevadal](https://github.com/ankitharevadal) | Resumes, jobs, admin, applications, UI |
| Anirudh N | PES1UG24AM041 | [@AnirudhN-7](https://github.com/AnirudhN-7) | Matching, agent, consent |

## Tech stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Auth:** JWT (PyJWT), Argon2 password hashing
- **Parsing:** pypdf, python-docx
- **Frontend:** Plain HTML/CSS/JS served by FastAPI (`app/static`)
- **Testing / CI:** pytest, GitHub Actions

## Project structure

```
app/
  main.py        FastAPI app, router registration, static frontend
  core/          config, security (JWT/hashing), error handlers, audit log
  db/            database session and ORM models
  routers/       API endpoints (auth, resumes, jobs, matches, recommendations,
                 bookmarks, applications, consent, admin) under /api/v1
  services/      business logic (parsing, skills, matching, jobs, resumes)
  agent/         recommendation agent (orchestrator, tools, AI provider)
  static/        web UI
tests/           pytest suite
scripts/         make_admin.py, create_backlog.sh
docs/            test report, defect log, deviations, evidence
```

## Getting started

```bash
git clone https://github.com/anvithh-16/Resume_Matcher-.git
cd Resume_Matcher-
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then set SECRET_KEY
uvicorn app.main:app --reload
```

- Web UI: http://127.0.0.1:8000/
- API docs (Swagger): http://127.0.0.1:8000/docs (disabled when `APP_ENV=production`)
- Health check: `GET /api/v1/health`

The SQLite database is created and seeded with sample jobs on first start.

### Make a user an admin

Register through the UI or API first, then:

```bash
python -m scripts.make_admin you@example.com
```

## Configuration

Set in `.env` (see `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `development` | `production` hides `/docs` and requires a real `SECRET_KEY` |
| `SECRET_KEY` | — | JWT signing key |
| `DATABASE_URL` | `sqlite:///./app.db` | SQLAlchemy database URL |
| `STORAGE_DIR` | `./storage` | Where uploaded resumes are stored |
| `MAX_UPLOAD_BYTES` | `2097152` | Max resume upload size (2 MB) |
| `TOKEN_MINUTES` | `60` | JWT lifetime |
| `EXTERNAL_AI_ENABLED` | `false` | Allow the agent to call an external AI provider |

## Deployment (SR-07)

`uvicorn app.main:app --reload` over plain HTTP is for local development only. Any non-localhost deployment must use HTTPS, `APP_ENV=production` and a real `SECRET_KEY`, and must not use `--reload`:

```bash
export APP_ENV=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
uvicorn app.main:app --port 8443 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

In production the app refuses to start with the default or `.env.example` secret, and `/docs` is hidden. See [docs/SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md).

## Running tests

```bash
pytest -q
python -m pytest -q        # use this form if another pytest is installed globally
```

CI runs the same command on every pull request and on pushes to `main`.

## Contributing

1. Pick an issue from the project board (labelled `FR` / `NFR` / `SR` and by sprint).
2. Branch from `main`: `feat/<issue>-<short-name>`.
3. Open a PR using the template — reference the requirement ID (e.g. `FR-03`) and test case (`TC-03`), and note any deviations in [docs/DEVIATIONS.md](docs/DEVIATIONS.md).
4. A reviewer is assigned automatically; merge once CI passes and it is approved.

## Documentation

- [Test report](docs/TEST_REPORT.md)
- [Defect log](docs/DEFECT_LOG.md)
- [Deviations from SRS / SAD / Test Plan](docs/DEVIATIONS.md)
- [Deployment security checklist](docs/SECURITY_CHECKLIST.md)
