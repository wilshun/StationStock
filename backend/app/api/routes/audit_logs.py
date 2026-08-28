import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import ManagerUser
from app.db.session import get_db
from app.models.audit_log import AuditLog


router = APIRouter(prefix="/v1/audit-logs", tags=["audit"])


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    actor_user_id: uuid.UUID | None
    action: str
    target_type: str
    target_id: str | None
    event_metadata: dict[str, Any]
    created_at: datetime


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AuditLogResponse]:
    events = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()
    return [AuditLogResponse.model_validate(event) for event in events]
