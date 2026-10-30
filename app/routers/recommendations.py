"""POST /api/v1/recommendations - run the bounded agent workflow (FR-08, FR-09, FR-13). Owner: Anirudh N."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agent.orchestrator import recommend
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import ConsentSetting, User

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendIn(BaseModel):
    resume_id: int
    location: str | None = Field(default=None, max_length=100)
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("")
def get_recommendations(body: RecommendIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    setting = db.query(ConsentSetting).filter_by(user_id=user.id).first()
    consent = bool(setting and setting.external_ai_enabled)
    return recommend(db, user, body.resume_id, body.location, body.top_k, consent=consent)
