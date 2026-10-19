"""
文件上传接口（对齐 FastapiAdmin: module_common.file）

- POST /api/v1/upload/image   上传图片，返回可访问地址 /uploads/...
- DELETE /api/v1/upload/image?url=...  按访问地址删除已上传图片

前端约定（src/api/upload.js）：
- uploadImage(file) -> POST /upload/image（multipart，字段名 file）
- deleteImage(url)  -> DELETE /upload/image?url=...
"""
from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import get_current_user
from app.utils.upload_util import delete_by_url, upload_image

router = APIRouter()


@router.post("/image", summary="上传图片")
async def upload_image_api(
    file: UploadFile = File(..., description="图片文件"),
    request: Request = None,
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    """
    上传图片，仅支持 settings 中配置的图片扩展名与大小。
    file_url 返回带 host 的绝对地址（基于 request.base_url），前端可直接用作 <img src>。
    """
    base_url = str(request.base_url) if request is not None else None
    result = upload_image(file, base_url=base_url)
    return SuccessResponse(data=result, msg="上传成功")


@router.delete("/image", summary="删除图片")
async def delete_image_api(
    url: str,
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    """
    根据访问地址删除已上传图片（前端调用 deleteImage(url)）。
    """
    deleted = delete_by_url(url)
    return SuccessResponse(
        data={"deleted": deleted},
        msg="删除成功" if deleted else "文件不存在或无法删除",
    )
