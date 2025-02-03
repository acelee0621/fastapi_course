import dbm
import hashlib
import sys
from enum import Enum


from fastapi import (
    FastAPI,
    Query,
    Request,
    status,
    Response,
    UploadFile,
    Path,
    __version__ as fastapi_version,
)
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import config

app = FastAPI(
    # docs_url=None,
    # redoc_url=None,
    debug=config.DEBUG_MODE,
)
app.mount(
    config.STATIC_URL, StaticFiles(directory=config.STATIC_DIR), name=config.STATIC_NAME
)


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


class TypeName(str, Enum):
    blog: str = "blog"
    news: str = "news"
    page: str = "page"


# default path parameter
@app.get("/post/{type_name}")
async def post(
    request: Request,
    type_name: TypeName = Path(title="Type Name", description="Type of the post"),
):
    data = None
    if type_name == "blog":
        data = {"title": "Blog Post", "content": "This is a blog post"}
    elif type_name == "news":
        data = {"title": "News Post", "content": "This is a news post"}
    elif type_name == "page":
        data = {"title": "Page Post", "content": "This is a page post"}
    else:
        data = {"title": "Post", "content": "This is a post"}
    return data


# 包含路径的参数
@app.get("/post/{file_path:path}")
async def post_file(file_path: str):
    return {"file_path": file_path}


# 范围验证
@app.get("/test/{test_id}")
async def post_id(
    test_id: int = Path(..., gt=0, lt=2, title="Post ID", description="ID of the post"),
):
    return {"test_id": test_id}


# 短链接服务
class PostItem(BaseModel):
    origin_url: str


URL_DB = "url_db"


@app.post("/short/")
async def short_url(url: PostItem):
    short_url = short_random(original_str=url.origin_url)
    store_short_url(short_url, url.origin_url)
    return {"short_url": short_url}


@app.get("/short/{short_key}")
async def redirect_short_url(short_key: str):
    url = get_url_by_key(short_key)
    # return {"origin_url": url}
    return RedirectResponse(f"https://{url}")


def get_url_by_key(key: str):
    db = dbm.open(URL_DB, "c")
    url = db[key].decode("utf-8")
    db.close()
    return url


def short_random(*, original_str: str, length: int = 8):
    random_str = hashlib.md5(original_str.encode()).hexdigest()[:length]
    return random_str


def store_short_url(short_url: str, origin_url: str):
    db = dbm.open(URL_DB, "c")
    db[short_url] = origin_url.encode("utf-8")
    db.close()


@app.post("/upload_file/{path_var}", summary="Upload a file")
async def upload_file(
    *,
    file: UploadFile,
    path_var: str | None = None,
    code: str | None = Query(None, min_length=4, max_length=8, alias="token"),
):
    file_local = await save_files(file)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "path_var": path_var,
        "code": code,
        "file_local": file_local,
    }


async def save_files(file):
    path = "files"
    res = await file.read()
    hash_name = hashlib.md5(file.filename.encode()).hexdigest()[:8]
    file_name = f"{hash_name}.{file.filename.rsplit('.',1)[-1]}"
    full_file = f"{path}/{file_name}"
    with open(full_file, "wb") as f:
        f.write(res)
    return full_file