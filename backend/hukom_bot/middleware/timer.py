from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.hukom_bot.util.timer import Timer

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = None
        
        with Timer() as elapsed_time:
            response = await call_next(request)

        # Add elapsed time (in seconds) to response header
        response.headers["X-Elapsed-Time"] = f"{elapsed_time.elapsed:.4f}s"
        
        return response