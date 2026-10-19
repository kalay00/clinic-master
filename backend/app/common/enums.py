"""
公共枚举（对齐 FastapiAdmin: app.common.enums）
仅保留本系统实际使用的部分，避免引入 FastapiAdmin 专属枚举。
"""
from enum import Enum, unique


class QueueEnum(str, Enum):
    """查询操作符枚举（build_search 使用）"""

    none = "None"
    not_none = "not None"
    date = "date"
    month = "month"
    like = "like"
    eq = "eq"
    in_ = "in"
    between = "between"
    ne = "!="
    gt = ">"
    ge = ">="
    lt = "<"
    le = "<="


class PermissionFilterStrategy(str, Enum):
    """权限过滤策略枚举（默认租户隔离即可，数据范围策略可选）"""

    DATA_SCOPE = "data_scope"
    OWN = "own"


class RET(Enum):
    """系统返回码枚举（对齐 FastapiAdmin: app.common.constant.RET）"""

    OK = (200, "成功")
    SUCCESS = (200, "操作成功")
    CREATED = (201, "创建成功")
    ERROR = (1, "请求错误")
    BAD_REQUEST = (400, "参数错误")
    UNAUTHORIZED = (401, "未授权")
    FORBIDDEN = (403, "访问受限")
    NOT_FOUND = (404, "资源不存在")
    UNPROCESSABLE_ENTITY = (422, "无法处理的实体")
    INTERNAL_SERVER_ERROR = (500, "服务器内部错误")
    DATAEXIST = (4003, "数据已存在")
    PARAMERR = (4103, "参数错误")

    def __init__(self, code: int, msg: str) -> None:
        self._code = code
        self._msg = msg

    @property
    def code(self) -> int:
        return self._code

    @property
    def msg(self) -> str:
        return self._msg


# API 日期 / 时间 / 日期时间统一展示格式（validator、jsonable_response_content、文档一致）
DATE_DISPLAY_FMT = "%Y-%m-%d"
TIME_DISPLAY_FMT = "%H:%M:%S"
DATETIME_DISPLAY_FMT = "%Y-%m-%d %H:%M:%S"
