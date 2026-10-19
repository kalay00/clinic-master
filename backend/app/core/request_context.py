"""
请求上下文（对齐 FastapiAdmin: app.core.request_context）
"""
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any


# ── 租户上下文 ──
current_tenant_id: ContextVar[Any] = ContextVar("current_tenant_id", default=None)


def set_current_tenant(tenant_id: Any) -> None:
    current_tenant_id.set(tenant_id)


def get_current_tenant_id() -> Any:
    return current_tenant_id.get()


def clear_current_tenant() -> None:
    current_tenant_id.set(None)


@dataclass
class RequestContext:
    """request.state.ctx 结构化字段（鉴权/日志用）"""

    jwt_payload: Any = None
    jwt_user_info: dict[str, Any] | None = None
    session_id: str | None = None
    user_id: Any = None
    user_username: str | None = None
    session_info: dict[str, Any] | None = None
