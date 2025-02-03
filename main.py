<<<<<<< Updated upstream
from fastapi import FastAPI
=======
import sys

from fastapi import FastAPI, status, Response
from fastapi import __version__ as fastapi_version
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


>>>>>>> Stashed changes


app = FastAPI()


@app.get("/")
async def run_state():
    return {"Status": "OK!"}

<<<<<<< Updated upstream
=======

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("tmp/logo.png")



>>>>>>> Stashed changes
