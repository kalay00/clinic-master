"""
路由类（对齐 FastapiAdmin: app.core.router_class）
操作日志路由：异步采集请求/响应（轻量版，不依赖 OperationLogService）。
"""
import time
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from fastapi.routing import APIRoute

from app.core.logger import logger


class OperationLogRoute(APIRoute):
    """操作日志路由 — 自动记录请求/响应（轻量采集，失败不影响主流程）"""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start = time.time()
            response: Response = await original_route_handler(request)
            try:
                route: APIRoute = request.scope.get("route", None)
                ctx = getattr(request.state, "ctx", None)
                current_user_id = ctx.user_id if ctx else None
                logger.info(
                    "OPERATION_LOG path=%s method=%s status=%s cost=%.2fs user=%s",
                    request.url.path,
                    request.method,
                    response.status_code,
                    time.time() - start,
                    current_user_id,
                )
            except Exception:
                logger.warning("操作日志采集异常: %s", request.url.path, exc_info=True)
            return response

        return custom_route_handler
