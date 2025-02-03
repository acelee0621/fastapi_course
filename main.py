import sys

from fastapi import FastAPI, status, Response
from fastapi import __version__ as fastapi_version
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles




app = FastAPI(
    # docs_url=None,
    # redoc_url=None
)
app.mount("/sub", StaticFiles(directory="static"), name="static")


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
    return FileResponse("tmp/logo.png")


son_app = FastAPI()


@son_app.get("/")  # /son/
async def root():
    return {"message": "I'm the son app!"}


@son_app.get("/info")  # /son/info
async def info():
    return {"message": "I'm the son app info!"}


app.mount("/son", son_app, name="son")


