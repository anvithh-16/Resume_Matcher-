"""Manual application tracking (FR-11, FR-12). The system never submits applications. Owner: Ankitha Revadala."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import get_current_user, get_owned_or_404
from app.db.database import get_db
from app.db.models import ApplicationRecord, Job, User

router = APIRouter(prefix="/applications", tags=["applications"])
STATUSES = ("saved", "applied", "interviewing", "offer", "rejected", "withdrawn")


class AppIn(BaseModel):
    job_id: int
    status: str = "saved"
    notes: str | None = Field(default=None, max_length=1000)


class AppPatch(BaseModel):
    status: str | None = None
    notes: str | None = Field(default=None, max_length=1000)


def check_status(status: str) -> None:
    if status not in STATUSES:
        raise AppError(422, "invalid_status", "Status must be one of: " + ", ".join(STATUSES))


def app_out(rec: ApplicationRecord, job: Job) -> dict:
    return {"id": rec.id, "job_id": job.id, "title": job.title, "company": job.company,
            "status": rec.status, "notes": rec.notes, "updated_at": rec.updated_at.isoformat()}


@router.get("")
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(ApplicationRecord, Job).join(Job, ApplicationRecord.job_id == Job.id)
            .filter(ApplicationRecord.owner_user_id == user.id).order_by(ApplicationRecord.updated_at.desc()).all())
    return {"applications": [app_out(r, j) for r, j in rows], "statuses": list(STATUSES)}


@router.post("", status_code=201)
def create_application(body: AppIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_status(body.status)
    job = db.get(Job, body.job_id)
    if job is None:
        raise AppError(404, "not_found", "Job not found.")
    if db.query(ApplicationRecord).filter_by(owner_user_id=user.id, job_id=job.id).first():
        raise AppError(409, "already_tracked", "You are already tracking this job.")
    rec = ApplicationRecord(owner_user_id=user.id, job_id=job.id, status=body.status, notes=body.notes)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return app_out(rec, job)


@router.patch("/{record_id}")
def update_application(record_id: int, body: AppPatch, user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    rec = get_owned_or_404(db, ApplicationRecord, record_id, user)
    if body.status is not None:
        check_status(body.status)
        rec.status = body.status
    if body.notes is not None:
        rec.notes = body.notes
    rec.updated_at = datetime.now(timezone.utc)
    db.commit()
    return app_out(rec, db.get(Job, rec.job_id))
