import os
import tempfile
import uuid

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["STORAGE_DIR"] = f"{_tmp}/storage"

# email-validator rejects the reserved ".local" TLD; allow it for the fixture users only.
import email_validator  # noqa: E402
email_validator.SPECIAL_USE_DOMAIN_NAMES.remove("local")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from app.db.database import SessionLocal  # noqa: E402
from app.db.models import Job, Resume, User  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "Passw0rd!x"

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

def make_user(client, email):
    client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

@pytest.fixture(scope="session")
def user_a(client):
    return make_user(client, "a@test.local")

@pytest.fixture(scope="session")
def user_b(client):
    return make_user(client, "b@test.local")

@pytest.fixture(scope="session")
def admin(client):
    headers = make_user(client, "admin@test.local")
    db = SessionLocal()
    db.query(User).filter_by(email="admin@test.local").one().is_admin = True
    db.commit()
    db.close()
    return headers

@pytest.fixture
def create_job():
    def _make(**fields):
        data = {"title": "Python Developer", "company": "Acme", "location": "Bengaluru",
                "description": "Build REST APIs with Python and SQL", "required_skills": ["python", "sql"],
                "employment_type": "full-time", "source": "test", "active": True}
        data.update(fields)
        db = SessionLocal()
        job = Job(**data)
        db.add(job)
        db.commit()
        job_id = job.id
        db.close()
        return job_id
    return _make

@pytest.fixture
def create_resume():
    def _make(email, profile):
        db = SessionLocal()
        user = db.query(User).filter_by(email=email).one()
        r = Resume(owner_user_id=user.id, storage_key=uuid.uuid4().hex, original_filename_safe="fixture.txt",
                   content_type="text/plain", size_bytes=1, parsed_profile=profile)
        db.add(r)
        db.commit()
        rid = r.id
        db.close()
        return rid
    return _make
