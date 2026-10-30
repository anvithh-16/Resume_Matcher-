"""POST /api/v1/matches - score one of my resumes against one job (FR-06, FR-07). Owner: Anirudh N."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import get_current_user, get_owned_or_404
from app.db.database import get_db
from app.db.models import Job, Resume, User
from app.services.matching import compute_match

router = APIRouter(prefix="/matches", tags=["matches"])
DISCLAIMER = ("Score = 100 x (0.75 x skill overlap + 0.25 x keyword similarity). "
              "It is an assistive relevance signal, not a hiring decision.")


class MatchIn(BaseModel):
    resume_id: int
    job_id: int


@router.post("")
def match(body: MatchIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = get_owned_or_404(db, Resume, body.resume_id, user)     # FR-12: only my own resume
    job = db.get(Job, body.job_id)
    if job is None or not job.active:
        raise AppError(404, "not_found", "Job not found.")
    result = compute_match(resume.parsed_profile or {}, job)
    result.update({"title": job.title, "company": job.company, "disclaimer": DISCLAIMER})
    return result
