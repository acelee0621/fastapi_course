import os
import hashlib
import uuid


UPLOAD_DIR = "upload_files"


# 生成唯一命名
def unique_generator(*, length: int = 8):
    unique_name = hashlib.md5(str(uuid.uuid4()).encode("utf-8")).hexdigest()[:length]
    return unique_name


# 保存文件
async def save_files(file):
    # 检测文件夹是否存在，不存在则创建
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    res = await file.read()
    # 生成唯一文件名
    unique_name = unique_generator()
    file_name = f"{unique_name}.{file.filename.rsplit('.', 1)[-1]}"
    file_path = f"{UPLOAD_DIR}/{file_name}"
    with open(file_path, "wb") as f:
        f.write(res)
    return unique_name
