"""
文件上传工具（对齐 FastapiAdmin: app.utils.upload_util，适配本项目配置）

- 仅支持图片（扩展名/大小由 settings 控制）
- 保存目录：{backend 根}/uploads/YYYY/MM/DD/<uuid>.<ext>
  与 main.py 中 StaticFiles 挂载的 /uploads 目录一致，保存后可直接通过
  /uploads/<相对路径> 访问。
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import CustomException

# __file__ = /backend/app/utils/upload_util.py → parents[2] = /backend
_UPLOAD_ROOT = Path(__file__).resolve().parents[2] / settings.UPLOAD_DIR


def get_upload_root() -> Path:
    """返回上传根目录（/backend/uploads），确保目录存在"""
    _UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    return _UPLOAD_ROOT


def _validate(file: UploadFile) -> tuple[str, bytes]:
    """校验扩展名与大小，返回 (扩展名, 文件内容)"""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    allowed = {e.lower() for e in settings.ALLOWED_IMAGE_EXTENSIONS}
    if ext not in allowed:
        raise CustomException(
            msg=f"不支持的文件类型: {ext or '空'}", code=10400, status_code=400
        )
    content = file.file.read()
    if not content:
        raise CustomException(msg="文件内容为空", code=10400, status_code=400)
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise CustomException(
            msg=f"文件大小超出限制（最大 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB）",
            code=10400,
            status_code=400,
        )
    return ext, content


def upload_image(file: UploadFile, subdir: str = "", base_url: str | None = None) -> dict:
    """
    保存图片文件。

    Args:
        base_url: 请求的基础地址（如 http://localhost:9000/），传入则 file_url 返回
            带 host 的绝对地址（http://localhost:9000/uploads/...），前端无需再拼接；
            不传则返回相对路径 /uploads/...。

    Returns:
        {
            "file_url": "/uploads/2026/07/24/xxx.png" 或 "http://host/uploads/...",
            "file_path": "2026/07/24/xxx.png",          # 相对上传根目录的路径（用于删除）
            "file_name": "xxx.png",                     # 存储文件名
            "origin_name": "原文件名.png",               # 原始文件名
        }
    """
    ext, content = _validate(file)
    date_dir = datetime.now().strftime("%Y/%m/%d")
    save_dir = get_upload_root() / date_dir
    if subdir:
        save_dir = save_dir / subdir
    save_dir.mkdir(parents=True, exist_ok=True)

    new_name = f"{uuid.uuid4().hex}{ext}"
    save_path = save_dir / new_name
    with open(save_path, "wb") as f:
        f.write(content)

    rel = save_path.relative_to(get_upload_root()).as_posix()
    raw_url = f"/uploads/{rel}"
    file_url = urljoin(base_url, raw_url) if base_url else raw_url
    return {
        "file_url": file_url,
        "file_path": rel,
        "file_name": new_name,
        "origin_name": file.filename,
    }


def delete_by_url(url: str) -> bool:
    """
    根据访问地址删除已上传文件（仅允许删除 uploads 目录内文件，防目录穿越）。
    兼容相对路径（/uploads/...）与带 host 的绝对地址（http://host/uploads/...）。

    Returns:
        True 表示已删除；文件不存在或非法地址返回 False。
    """
    if not url:
        return False
    url = url.split("?")[0].split("#")[0]
    path = urlparse(url).path  # 提取路径部分，去掉 scheme/host
    prefix = "/uploads/"
    if not path.startswith(prefix):
        return False
    rel = path[len(prefix):]
    rel_path = Path(rel)
    if ".." in rel_path.parts or rel_path.is_absolute():
        return False

    root = get_upload_root().resolve()
    target = (root / rel_path).resolve()
    if target == root or root not in target.parents:
        return False
    if target.exists() and target.is_file():
        target.unlink()
        return True
    return False
