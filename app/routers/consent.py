"""GET/PUT /api/v1/consent - external-AI data-transfer consent (FR-13, SR-06, SR-08). Owner: Anirudh N."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core import config
from app.core.audit import audit
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import ConsentSetting, User

router = APIRouter(prefix="/consent", tags=["consent"])
NOTICE = ("If you allow it, only job titles and matched/missing skill names are sent to the configured AI "
          "provider to rewrite explanations. Your resume text and contact details are never sent.")


class ConsentIn(BaseModel):
    external_ai_enabled: bool


def _setting(db: Session, user: User) -> ConsentSetting:
    s = db.query(ConsentSetting).filter_by(user_id=user.id).first()
    if s is None:
        s = ConsentSetting(user_id=user.id, external_ai_enabled=False)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def _out(s: ConsentSetting) -> dict:
    return {"external_ai_enabled": s.external_ai_enabled, "provider_configured": config.EXTERNAL_AI_ENABLED,
            "notice": NOTICE}


@router.get("")
def read_consent(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _out(_setting(db, user))


@router.put("")
def update_consent(body: ConsentIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = _setting(db, user)
    s.external_ai_enabled = body.external_ai_enabled
    db.commit()
    audit(db, "consent_changed", user.id, f"external_ai_enabled={body.external_ai_enabled}")
    return _out(s)
