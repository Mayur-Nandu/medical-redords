from __future__ import annotations

import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)

        try:
            actor_id = getattr(getattr(request, "user", None), "sub", None)
        except Exception:
            actor_id = None

        action = f"{request.method} {request.url.path}"
        ip_address = request.client.host if request.client else None

        db: Session = SessionLocal()
        try:
            db.add(
                AuditLog(
                    actor_id=str(actor_id) if actor_id else None,
                    actor_role=None,
                    action=action,
                    resource_type="http",
                    resource_id=None,
                    details={
                        "status_code": response.status_code,
                    },
                    ip_address=ip_address,
                    request_id=request_id,
                )
            )
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        response.headers["X-Request-ID"] = request_id
        return response

