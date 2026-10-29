import logging
from app.db.models import AuditEvent

log = logging.getLogger("audit")

def audit(db, event_type: str, user_id: int | None = None, detail: str = "") -> None:
    """Record a security event. Never pass passwords, tokens, API keys or resume text."""
    db.add(AuditEvent(event_type=event_type, user_id=user_id, detail=detail[:500]))
    db.commit()
    log.info("audit event=%s user_id=%s detail=%s", event_type, user_id, detail[:200])
