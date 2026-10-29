from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.audit import audit
from app.core.config import SECRET_KEY, TOKEN_MINUTES
from app.core.errors import AppError
from app.db.database import get_db
from app.db.models import User

_hasher = PasswordHasher()
_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return _hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False

def create_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expires}, SECRET_KEY, algorithm="HS256")

def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
                     db: Session = Depends(get_db)) -> User:
    user = None
    if creds is not None:
        try:
            payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
            user = db.get(User, int(payload["sub"]))
        except (jwt.PyJWTError, KeyError, ValueError):
            user = None
    if user is None:
        raise AppError(401, "not_authenticated", "Please log in.")
    return user

def require_admin(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    if not user.is_admin:
        audit(db, "access_denied", user.id, "admin route")
        raise AppError(403, "forbidden", "Administrator access required.")
    return user

def get_owned_or_404(db: Session, model, record_id: int, user: User, owner_field: str = "owner_user_id"):
    """FR-12 / SR-01: load a private record only if the current user owns it."""
    obj = db.get(model, record_id)
    if obj is None or getattr(obj, owner_field) != user.id:
        if obj is not None:
            audit(db, "access_denied", user.id, f"{model.__tablename__}:{record_id}")
        raise AppError(404, "not_found", "Record not found.")
    return obj
