"""Job dataset: validation, seeding and search (FR-05, FR-15). Owner: Ankitha Revadala (PES1UG24AM044)."""
import json

from sqlalchemy import String, cast, or_

from app.core.config import BASE_DIR
from app.db.models import Job
from app.services.skills import normalize_skill

EMPLOYMENT_TYPES = {"full-time", "part-time", "internship", "contract"}


def validate_job(item: dict) -> dict:
    """Clean one job record or raise ValueError (used by seed and admin import)."""
    if not isinstance(item, dict):
        raise ValueError("each job must be an object")
    title = str(item.get("title", "")).strip()
    company = str(item.get("company", "")).strip()
    if not title or not company or len(title) > 200 or len(company) > 200:
        raise ValueError("title and company are required (max 200 characters)")
    skills = item.get("required_skills", [])
    if not isinstance(skills, list) or not all(isinstance(s, str) and s.strip() for s in skills):
        raise ValueError("required_skills must be a list of skill names")
    etype = str(item.get("employment_type", "full-time")).strip().lower()
    if etype not in EMPLOYMENT_TYPES:
        raise ValueError("employment_type must be one of " + ", ".join(sorted(EMPLOYMENT_TYPES)))
    return {"title": title, "company": company,
            "location": str(item.get("location", "Remote")).strip()[:200] or "Remote",
            "description": str(item.get("description", ""))[:5000],
            "required_skills": sorted({normalize_skill(s) for s in skills}),
            "employment_type": etype, "source": str(item.get("source", "curated"))[:100],
            "active": bool(item.get("active", True))}


def seed_if_empty(db) -> None:
    """Load data/jobs_seed.json the first time the app starts on an empty database."""
    if db.query(Job).count() > 0:
        return
    path = BASE_DIR / "data" / "jobs_seed.json"
    if not path.exists():
        return
    for item in json.loads(path.read_text(encoding="utf-8")):
        db.add(Job(**validate_job(item)))
    db.commit()


def search_jobs(db, q=None, skills=None, location=None, employment_type=None, limit=50):
    """Active jobs matching all given filters; `skills` matches if the job needs ANY of them."""
    query = db.query(Job).filter(Job.active.is_(True))
    if q and q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Job.title.ilike(like), Job.description.ilike(like), Job.company.ilike(like)))
    if location and location.strip():
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))
    if employment_type:
        query = query.filter(Job.employment_type == employment_type.strip().lower())
    if skills:
        wanted = sorted({normalize_skill(s) for s in skills if s and s.strip()})
        if wanted:
            # required_skills is stored as JSON text like ["python", "sql"]; match the quoted name exactly.
            # Done in SQL (not Python) so 5,000-job searches stay under NFR-01's 2 s target.
            stored = cast(Job.required_skills, String)
            query = query.filter(or_(*[stored.like(f'%"{s}"%') for s in wanted]))
    return query.order_by(Job.id).limit(max(1, min(int(limit), 100))).all()
