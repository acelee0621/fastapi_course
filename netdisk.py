from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    Security,
    status,
    UploadFile,
    Form,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import SecurityScopes

from utils import unique_generator, save_files, UPLOAD_DIR
from FakeDB import file_db


router = APIRouter(prefix="/netdisk", tags=["NetDisk"])


ALL_USERS = {
    "jack": ["admin", "users"],
    "rose": ["admin", "users"],
    "tom": ["users"],
    "jerry": ["users"],
}

ROLE_PERMISSIONS = {
    "admin": ["upload"],
    "users": ["visit", "download"],
}


def get_user_token(user_name: str | None = Cookie(default=None)):
    if user_name is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user_name is required"
        )
    return user_name


# 返回角色(role)对应的所有权限(scopes)
def get_role_permissions(role_name: list[str]):
    permissions = []
    for role in role_name:
        for permission in ROLE_PERMISSIONS[role]:
            permissions.append(permission)
    return permissions


# 获取用户所有的scopes,也就是获取角色对应的所有权限
def get_user_permissions(token: str = Depends(get_user_token)):
    if token in ALL_USERS:
        return get_role_permissions(ALL_USERS[token])
    return None


def check_user(
    security_scopes: SecurityScopes,
    user_permission: str = Depends(get_user_permissions),
):
    for scope in security_scopes.scopes:
        # 检查路径接口需要的权限是否在用户对应的所有权限里
        if scope not in user_permission:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You have no authorization",
            )


@router.get("/login", summary="Login")
async def set_cookie(response: Response, token: str):
    response.set_cookie(key="user_name", value=token, expires=600)
    return {"message": "Cookie set Successful"}


@router.post(
    "/upload_file",
    summary="Upload a file",
    dependencies=[Security(check_user, scopes=["upload"])],
)
async def upload_file(*, file: UploadFile, request: Request):
    # 保存文件
    unique_name = await save_files(file)
    # 将文件信息保存到数据库
    file_db.create_file(unique_name, file.filename)
    # 生成分享码，并保存到数据库
    share_code = unique_generator(length=6)
    file_db.create_share_code(unique_name, share_code)

    return {
        "file name": file.filename,
        "unique_name": unique_name,
        "code": share_code,
        "url": request.url_for("file_page", unique_name=unique_name).path,
    }


@router.get(
    "/share",
    summary="Get all shared file",
    dependencies=[Security(check_user, scopes=["visit"])],
)
async def share_file(request: Request):
    all_files = file_db.get_all_files()
    data = {"all_files": all_files}
    return request.app.state.templates.TemplateResponse(
        request=request, name="share.html", context=data
    )


@router.get(
    "/file/{unique_name}",
    summary="File Downing Page",
    dependencies=[Security(check_user, scopes=["visit"])],
)
async def file_page(
    request: Request,
    unique_name: str,
    share_code: str | None = Query(None, min_length=6),
):
    # 查询文件是否存在
    file_name = file_db.get_file(unique_name)
    # 没有找到对应的下载文件，返回404响应
    if file_name is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "File Not Found"}
        )
    if share_code is None:
        share_code = ""

    data = {
        "file_name": str(file_name, encoding="utf-8"),
        "unique_name": unique_name,
        "share_code": share_code,
    }
    return request.app.state.templates.TemplateResponse(
        request=request, name="file.html", context=data
    )


@router.post(
    "/download/{unique_name}",
    summary="Download File",
    dependencies=[Security(check_user, scopes=["download"])],
)
async def download_file(unique_name: str, share: str = Form()):
    code = str(file_db.get_share_code(unique_name), "utf-8")
    if code != share:
        return {"Validation Error": "Wrong Share Code,You have no authorization"}

    file_name = str(file_db.get_file(unique_name), "utf-8")
    download_file = f"{unique_name}.{file_name.rsplit('.', 1)[-1]}"
    file_path = UPLOAD_DIR + "/" + download_file
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )


@router.get("/set-cookie", summary="Set Cookie")
async def set_cookies(response: Response):
    response.set_cookie(key="netdisk_token", value="Ace_admin", expires=60)
    return {"message": "Cookie Set"}
