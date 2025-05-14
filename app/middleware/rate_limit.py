from fastapi import FastAPI, Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int, window: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        window_start = current_time - self.window

        # Limpar requisições antigas
        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if timestamp > window_start]

        # Contar requisições no período
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

        # Adicionar nova requisição
        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response