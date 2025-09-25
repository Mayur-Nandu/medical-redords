from __future__ import annotations

from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[str | None] = mapped_column(String(128), index=True)
    actor_role: Mapped[str | None] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64), index=True)
    resource_type: Mapped[str] = mapped_column(String(64), index=True)
    resource_id: Mapped[str | None] = mapped_column(String(128), index=True)
    details: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    request_id: Mapped[str | None] = mapped_column(String(128), index=True)
    created_at: Mapped[DateTime] = mapped_column(server_default=func.now(), index=True)

