import sys
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
    status,
    Response,
    __version__ as fastapi_version,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from config import config
from router import routers
from middleware import ace_middleware
from database.redis import redis_connect


@asynccontextmanager
async def ace_lifespan(app: FastAPI):
    # 启动时执行
    app.state.redis = await redis_connect()
    print("FastAPI is starting...")
    # 启动时可能会执行的事件
    # logger_init()  启动日志服务
    # db_init()  启动数据库
    # db_setting()  获取动态配置
    # service_init() 启动第三方服务
    # send_email()  发送邮件
    yield print("FastAPI is running...,wait for next use")
    # 停止时执行
    await app.state.redis.close()
    # 停止时可能会执行的事件
    # logger()  记录关闭日志
    # db_close() 关闭数据库连接
    # service_close() 关闭第三方服务
    # send_email()  发送邮件
    print("FastAPI is stopping...")
    
    
    

app = FastAPI(
    # docs_url=None,
    # redoc_url=None,
    debug=config.DEBUG_MODE,
    lifespan=ace_lifespan,
)


# ace_middleware(app)


# @app.middleware("http")
# async def only_for_requests(request:Request, call_next):
#     print(f"Request URL:{request.url}")
#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def only_for_responses(request:Request, call_next):    
#     response = await call_next(request)
#     print("Got response" , response)
#     return response



app.include_router(routers)

app.mount(
    config.STATIC_URL, StaticFiles(directory=config.STATIC_DIR), name=config.STATIC_NAME
)
# 创建模板实例
app.state.templates = Jinja2Templates(directory="front_end/templates")


@app.get("/server-status", include_in_schema=False)
async def run_state(response: Response, token: str | None = None):
    if token == "Ace":
        data = {
            "Status": "OK!",
            "fastapi_version": fastapi_version,
            "python_version": sys.version_info,
        }
        return data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND  # 404
        return {"detail": "Not Found"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/logo.png")
