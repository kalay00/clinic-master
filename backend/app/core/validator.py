"""
字段验证器（对齐 FastapiAdmin: app.core.validator）
"""
import re
from datetime import date, datetime, time
from typing import Annotated, Any

from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

from app.common.constant import (
    DATE_DISPLAY_FMT,
    DATETIME_DISPLAY_FMT,
    RET,
    TIME_DISPLAY_FMT,
)
from app.core.exceptions import CustomException


DateTimeStr = Annotated[
    datetime,
    AfterValidator(lambda x: datetime_validator(x)),
    PlainSerializer(
        lambda x: x.strftime(DATETIME_DISPLAY_FMT) if isinstance(x, datetime) else str(x),
        return_type=str,
        when_used="json",
    ),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

DateStr = Annotated[
    date,
    AfterValidator(lambda x: date_validator(x)),
    PlainSerializer(
        lambda x: x.strftime(DATE_DISPLAY_FMT) if isinstance(x, date) else str(x),
        return_type=str,
        when_used="json",
    ),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

TimeStr = Annotated[
    time,
    AfterValidator(lambda x: time_validator(x)),
    PlainSerializer(
        lambda x: x.strftime(TIME_DISPLAY_FMT) if isinstance(x, time) else str(x),
        return_type=str,
        when_used="json",
    ),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


def datetime_validator(value: Any) -> datetime:
    try:
        if isinstance(value, str):
            return datetime.strptime(value, DATETIME_DISPLAY_FMT)
        if isinstance(value, datetime):
            return value
    except Exception:
        raise CustomException(code=RET.ERROR.code, msg="无效的日期格式")


def date_validator(value: Any) -> date:
    try:
        if isinstance(value, str):
            return datetime.strptime(value, DATE_DISPLAY_FMT).date()
        if isinstance(value, date):
            return value
    except Exception:
        raise CustomException(code=RET.ERROR.code, msg="无效的日期格式")


def time_validator(value: Any) -> time:
    try:
        if isinstance(value, str):
            return datetime.strptime(value, TIME_DISPLAY_FMT).time()
        if isinstance(value, time):
            return value
    except Exception:
        raise CustomException(code=RET.ERROR.code, msg="无效的时间格式")
