"""Resume upload, list, view, correct and delete (FR-03, FR-04, FR-12, NFR-07). Owner: Ankitha Revadala."""
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.config import MAX_UPLOAD_BYTES
from app.core.errors import AppError
from app.core.security import get_current_user, get_owned_or_404
from app.db.database import get_db
from app.db.models import Resume, User
from app.services.parser import ParseError, extract_text, parse_resume
from app.services.resume_service import ALLOWED, delete_file, safe_name, store_file, validate_upload
from app.services.skills import normalize_skill

router = APIRouter(prefix="/resumes", tags=["resumes"])


def resume_out(r: Resume) -> dict:
    profile = {k: v for k, v in (r.parsed_profile or {}).items() if k != "raw_text"}
    return {"id": r.id, "filename": r.original_filename_safe, "size_bytes": r.size_bytes,
            "created_at": r.created_at.isoformat(), "profile": profile}


@router.post("", status_code=201)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    ext = validate_upload(file.filename, data)
    try:
        text = extract_text(data, ext)
    except ParseError as exc:
        raise AppError(422, "parse_failed", str(exc))
    profile = parse_resume(text)
    profile["raw_text"] = text[:20000]
    resume = Resume(owner_user_id=user.id, storage_key=store_file(data),
                    original_filename_safe=safe_name(file.filename), content_type=ALLOWED[ext],
                    size_bytes=len(data), parsed_profile=profile)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume_out(resume)


@router.get("")
def list_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Resume).filter(Resume.owner_user_id == user.id).order_by(Resume.created_at.desc()).all()
    return {"resumes": [resume_out(r) for r in rows]}


@router.get("/{resume_id}")
def get_resume(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return resume_out(get_owned_or_404(db, Resume, resume_id, user))


class ProfileFix(BaseModel):
    skills: list[str] = Field(default_factory=list, max_length=100)
    education: list[str] = Field(default_factory=list, max_length=20)
    experience: list[str] = Field(default_factory=list, max_length=30)


@router.put("/{resume_id}/profile")
def correct_profile(resume_id: int, body: ProfileFix, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    r = get_owned_or_404(db, Resume, resume_id, user)
    r.parsed_profile = {**(r.parsed_profile or {}), "skills": sorted({normalize_skill(s) for s in body.skills}),
                        "education": body.education, "experience": body.experience, "warnings": []}
    db.commit()
    return resume_out(r)


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = get_owned_or_404(db, Resume, resume_id, user)
    delete_file(r.storage_key)
    db.delete(r)
    db.commit()
    audit(db, "resume_deleted", user.id, f"resume:{resume_id}")
