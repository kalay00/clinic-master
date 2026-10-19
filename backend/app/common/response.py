"""
统一响应（对齐 FastapiAdmin: app.common.response，Python 3.12+ / PEP 695）
ResponseSchema[Data] + SuccessResponse / ErrorResponse。
"""
import datetime
from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.common.constant import DATETIME_DISPLAY_FMT, DATE_DISPLAY_FMT, RET, TIME_DISPLAY_FMT

_JSON_DATETIME_CUSTOM_ENCODER: dict[type, Any] = {
    datetime.datetime: lambda d: d.strftime(DATETIME_DISPLAY_FMT),
    datetime.date: lambda d: d.strftime(DATE_DISPLAY_FMT),
    datetime.time: lambda t: t.strftime(TIME_DISPLAY_FMT),
}


def jsonable_response_content(content: Any) -> Any:
    return jsonable_encoder(content, custom_encoder=_JSON_DATETIME_CUSTOM_ENCODER)


class ResponseSchema[T](BaseModel):
    """响应模型"""

    code: int = Field(default=RET.OK.code, description="业务状态码")
    msg: str = Field(default=RET.OK.msg, description="响应消息")
    data: T = Field(default=None, description="响应数据")
    status_code: int = Field(default=status.HTTP_200_OK, description="HTTP状态码")
    success: bool = Field(default=True, description="操作是否成功")


class SuccessResponse(JSONResponse):
    """成功响应类"""

    def __init__(
        self,
        data: Any = None,
        msg: str = RET.OK.msg,
        code: int = RET.OK.code,
        status_code: int = status.HTTP_200_OK,
        success: bool = True,
    ) -> None:
        content = ResponseSchema(
            code=code, msg=msg, data=data, status_code=status_code, success=success
        ).model_dump()
        super().__init__(content=jsonable_response_content(content), status_code=status_code)
        self.headers["Content-Type"] = "application/json; charset=utf-8"


class ErrorResponse(JSONResponse):
    """错误响应类"""

    def __init__(
        self,
        data: Any = None,
        msg: str = RET.ERROR.msg,
        code: int = RET.ERROR.code,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        success: bool = False,
    ) -> None:
        content = ResponseSchema(
            code=code, msg=msg, data=data, status_code=status_code, success=success
        ).model_dump()
        super().__init__(content=jsonable_response_content(content), status_code=status_code)
        self.headers["Content-Type"] = "application/json; charset=utf-8"
