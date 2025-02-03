from fastapi import (
    APIRouter,
    Query,
    Request,
    status,
    UploadFile,
    Form,
)
from fastapi.responses import FileResponse, JSONResponse

from utils import unique_generator, save_files, UPLOAD_DIR
from FakeDB import file_db



router = APIRouter(prefix="/netdisk", tags=["NetDisk"])





@router.post("/upload_file", summary="Upload a file")
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


@router.get("/share", summary="Get all shared file")
async def share_file(request: Request):
    all_files = file_db.get_all_files()
    data = {"all_files": all_files}
    return request.app.state.templates.TemplateResponse(
        request=request, name="share.html", context=data
    )


@router.get("/file/{unique_name}", summary="File Downing Page")
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


@router.post("/download/{unique_name}", summary="Download File")
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
