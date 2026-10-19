"""
异常处理组件
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class BaseAppException(Exception):
    """应用基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            code: 错误代码
            details: 详细信息
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class CustomException(Exception):
    """对齐 FastapiAdmin 的统一业务异常（msg/code/status_code）"""

    def __init__(
        self,
        msg: str = "服务器异常",
        code: int = 500,
        status_code: int = 500,
        data: Any = None,
    ) -> None:
        self.msg = msg
        self.code = code
        self.status_code = status_code
        self.data = data
        super().__init__(msg)


class BusinessException(BaseAppException):
    """业务异常"""
    
    def __init__(
        self,
        message: str,
        code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化业务异常
        
        Args:
            message: 错误消息
            code: 错误代码（默认400）
            details: 详细信息
        """
        super().__init__(message, code, details)


class ValidationException(BusinessException):
    """数据验证异常"""
    
    def __init__(
        self,
        message: str = "数据验证失败",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化验证异常
        
        Args:
            message: 错误消息
            details: 验证错误详情
        """
        super().__init__(message, 400, details)


class NotFoundException(BusinessException):
    """资源不存在异常"""
    
    def __init__(
        self,
        resource: str = "资源",
        resource_id: Optional[str] = None
    ):
        """
        初始化资源不存在异常
        
        Args:
            resource: 资源名称
            resource_id: 资源ID
        """
        message = f"{resource}不存在"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, 404, {"resource": resource, "resource_id": resource_id})


class UnauthorizedException(BaseAppException):
    """未授权异常"""
    
    def __init__(self, message: str = "未授权访问"):
        """
        初始化未授权异常
        
        Args:
            message: 错误消息
        """
        super().__init__(message, 401)


class ForbiddenException(BaseAppException):
    """权限不足异常"""
    
    def __init__(self, message: str = "权限不足"):
        """
        初始化权限不足异常
        
        Args:
            message: 错误消息
        """
        super().__init__(message, 403)


class DatabaseException(BaseAppException):
    """数据库异常"""
    
    def __init__(
        self,
        message: str = "数据库操作失败",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化数据库异常
        
        Args:
            message: 错误消息
            details: 详细信息
        """
        super().__init__(message, 500, details)


def exception_to_http_exception(exc: BaseAppException) -> HTTPException:
    """
    将应用异常转换为HTTP异常
    
    Args:
        exc: 应用异常对象
    
    Returns:
        HTTPException: FastAPI HTTP异常对象
    """
    status_code_map = {
        400: status.HTTP_400_BAD_REQUEST,
        401: status.HTTP_401_UNAUTHORIZED,
        403: status.HTTP_403_FORBIDDEN,
        404: status.HTTP_404_NOT_FOUND,
        500: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

