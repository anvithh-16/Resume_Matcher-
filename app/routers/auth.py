from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.core.audit import audit
from app.core.errors import AppError
from app.core.security import create_token, get_current_user, hash_password, verify_password
from app.db.database import get_db
from app.db.models import User

router = APIRouter(tags=["auth"])

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

@router.post("/auth/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    if db.query(User).filter_by(email=email).first():
        raise AppError(409, "email_taken", "This email cannot be used to register.")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}

@router.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email.strip().lower()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        audit(db, "login_failed", user.id if user else None, "bad credentials")
        # Same message whether or not the account exists (FR-02).
        raise AppError(401, "invalid_credentials", "Email or password is incorrect.")
    return {"access_token": create_token(user.id), "token_type": "bearer"}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "is_admin": user.is_admin}
