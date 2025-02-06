import time
from collections import defaultdict

from fastapi import FastAPI, Request, Response

from starlette.middleware.base import BaseHTTPMiddleware


def ace_middleware(app: FastAPI):
    # 打印每个请求所用的时间
    @app.middleware("http")
    async def count_times(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        print(f"Process time: {process_time}")
        return response

    @app.middleware("http")
    async def ace_logging(request: Request, call_next):
        message = f"{request.client.host}:{request.client.port} - {request.method} {request.url}"
        print(f"LOG INFO: {message}")
        response = await call_next(request)
        return response

    app.add_middleware(RateLimitMiddleware)


# 访问速率限制的中间件，使用类的形式
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.request_records: dict[str, float] = defaultdict(float)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        current_time = time.time()
        if current_time - self.request_records[ip] < 5:
            return Response(content="Rate limit exceeded", status_code=429)
        response = await call_next(request)
        self.request_records[ip] = (
            current_time  # 成功响应，就将请求ip和时间保存在字典里
        )
        return response
