"""
Middleware for AI Keyboard API
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.logger import log_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        log_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration
        )
        
        return response
