"""GET /api/v1/jobs and /api/v1/jobs/{id} - public job search (FR-05). Owner: Ankitha Revadala."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.database import get_db
from app.db.models import Job
from app.services.job_service import search_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


def job_out(j: Job) -> dict:
    return {"id": j.id, "title": j.title, "company": j.company, "location": j.location,
            "description": j.description, "required_skills": j.required_skills,
            "employment_type": j.employment_type, "source": j.source}


@router.get("")
def list_jobs(q: str | None = None, skill: list[str] | None = Query(None), location: str | None = None,
              employment_type: str | None = None, limit: int = Query(50, ge=1, le=100),
              db: Session = Depends(get_db)):
    jobs = search_jobs(db, q=q, skills=skill, location=location, employment_type=employment_type, limit=limit)
    return {"count": len(jobs), "results": [job_out(j) for j in jobs]}


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None or not job.active:
        raise AppError(404, "not_found", "Job not found.")
    return job_out(job)
