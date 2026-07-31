import time
import redis.asyncio as redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Determine the key: user_id if authenticated, else IP
        client_ip = request.client.host if request.client else "unknown"
        # We can't easily extract user_id here without decoding JWT manually, 
        # but we can try to check Authorization header
        key = client_ip
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                from jose import jwt
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
                if "user_id" in payload:
                    key = payload["user_id"]
            except Exception:
                pass
                
        # Token bucket or fixed window
        current_minute = int(time.time() // 60)
        redis_key = f"rate_limit:{key}:{current_minute}"
        
        requests = await redis_client.incr(redis_key)
        if requests == 1:
            await redis_client.expire(redis_key, 60)
            
        if requests > 100:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED"}
            )
            
        response = await call_next(request)
        return response
