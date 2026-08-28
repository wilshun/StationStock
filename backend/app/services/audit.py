import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


SENSITIVE_KEYS = {"password", "password_hash", "token", "secret", "authorization", "cookie"}


def record_audit(
    db: Session,
    action: str,
    target_type: str,
    *,
    actor_user_id: uuid.UUID | None = None,
    target_id: str | uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    safe_metadata = {
        key: value for key, value in (metadata or {}).items() if key.lower() not in SENSITIVE_KEYS
    }
    event = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        event_metadata=safe_metadata,
    )
    db.add(event)
    return event
