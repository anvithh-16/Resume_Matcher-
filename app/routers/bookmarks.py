from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Bookmark, Job, User

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

class BookmarkIn(BaseModel):
    job_id: int

@router.get("")
def list_bookmarks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(Bookmark, Job).join(Job, Bookmark.job_id == Job.id)
            .filter(Bookmark.owner_user_id == user.id).order_by(Bookmark.created_at.desc()).all())
    return {"bookmarks": [{"job_id": j.id, "title": j.title, "company": j.company,
                           "location": j.location, "created_at": b.created_at.isoformat()} for b, j in rows]}

@router.post("", status_code=201)
def add_bookmark(body: BookmarkIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.get(Job, body.job_id)
    if job is None or not job.active:
        raise AppError(404, "not_found", "Job not found.")
    if db.query(Bookmark).filter_by(owner_user_id=user.id, job_id=job.id).first():
        raise AppError(409, "already_bookmarked", "This job is already bookmarked.")
    db.add(Bookmark(owner_user_id=user.id, job_id=job.id))
    db.commit()
    return {"job_id": job.id}

@router.delete("/{job_id}", status_code=204)
def remove_bookmark(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bm = db.query(Bookmark).filter_by(owner_user_id=user.id, job_id=job_id).first()
    if bm is None:
        raise AppError(404, "not_found", "Bookmark not found.")
    db.delete(bm)
    db.commit()
