import sys

from fastapi import (
    FastAPI,
    status,
    Response,
    __version__ as fastapi_version,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from config import config
from router import routers


app = FastAPI(
    # docs_url=None,
    # redoc_url=None,
    debug=config.DEBUG_MODE,
)

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
