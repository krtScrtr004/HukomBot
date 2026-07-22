from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIdentifierMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Retrieve or generate the request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        
        # Store it in request.state so endpoints can access it via request.state
        request.state.request_id = request_id
                
        response = await call_next(request)
        
        # Add request ID to the response header
        response.headers["X-Request-ID"] = request_id
        
        return response