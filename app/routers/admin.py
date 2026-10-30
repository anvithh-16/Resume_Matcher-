"""Admin job dataset management (FR-15, SR-08). Owner: Ankitha Revadala."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.errors import AppError
from app.core.security import require_admin
from app.db.database import get_db
from app.db.models import Job, User
from app.services.job_service import EMPLOYMENT_TYPES, validate_job
from app.services.skills import normalize_skill

router = APIRouter(prefix="/admin", tags=["admin"])


class ImportIn(BaseModel):
    jobs: list[dict] = Field(min_length=1, max_length=1000)


class JobPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    location: str | None = Field(default=None, max_length=200)
    required_skills: list[str] | None = None
    employment_type: str | None = None
    active: bool | None = None


@router.post("/jobs/import", status_code=201)
def import_jobs(body: ImportIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    cleaned, errors = [], []
    for i, item in enumerate(body.jobs):
        try:
            cleaned.append(validate_job(item))
        except ValueError as exc:
            errors.append(f"row {i}: {exc}")
    if errors:   # all-or-nothing: nothing is saved if any row is invalid
        raise AppError(422, "invalid_jobs", "; ".join(errors[:10]))
    db.add_all([Job(**c) for c in cleaned])
    db.commit()
    audit(db, "admin_job_import", admin.id, f"imported {len(cleaned)} jobs")
    return {"imported": len(cleaned)}


@router.patch("/jobs/{job_id}")
def update_job(job_id: int, body: JobPatch, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise AppError(404, "not_found", "Job not found.")
    changes = body.model_dump(exclude_none=True)
    if "employment_type" in changes and changes["employment_type"] not in EMPLOYMENT_TYPES:
        raise AppError(422, "invalid_job", "Unknown employment_type.")
    if "required_skills" in changes:
        changes["required_skills"] = sorted({normalize_skill(s) for s in changes["required_skills"] if s.strip()})
    for key, value in changes.items():
        setattr(job, key, value)
    db.commit()
    audit(db, "admin_job_update", admin.id, f"job:{job_id} fields:{','.join(changes)}")
    return {"id": job.id, "active": job.active}
