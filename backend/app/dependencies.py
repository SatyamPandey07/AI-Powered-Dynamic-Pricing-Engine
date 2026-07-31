from fastapi import Request, HTTPException, status
from typing import Callable, Any
from functools import wraps

def get_rate_limit_key(request: Request):
    if hasattr(request.state, 'user_id') and request.state.user_id:
        return request.state.user_id
    return request.client.host if request.client else "unknown"

def require_auth(request: Request):
    if not hasattr(request.state, "user_id") or not request.state.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return request.state

def require_role(min_role: str):
    hierarchy = {"viewer": 0, "editor": 1, "admin": 2}
    def role_checker(request: Request):
        require_auth(request)
        user_role = getattr(request.state, "role", "viewer")
        if hierarchy.get(user_role, 0) < hierarchy.get(min_role, 0):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return request.state
    return role_checker

import uuid
from app.database import SessionLocal
from app.models.tenant import AuditLog

def audit_log(action: str, resource_type: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            response = await func(*args, **kwargs)
            
            if request and hasattr(request.state, 'user_id'):
                db = SessionLocal()
                try:
                    log_entry = AuditLog(
                        id=str(uuid.uuid4()),
                        org_id=request.state.org_id,
                        user_id=request.state.user_id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=None,
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent"),
                    )
                    db.add(log_entry)
                    db.commit()
                except Exception as e:
                    print(f"Error saving audit log: {e}")
                finally:
                    db.close()
            return response
        return wrapper
    return decorator
